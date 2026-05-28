"""Carousel Planner — tweet/thread metnini N slide'lık carousel'a böler.

LLM: Anthropic Claude Opus 4.7 (memory: prefill yok, temperature deprecate;
permissive schema'da sarmalama riski → explicit input_schema + tool_use kullan).

Çıktı (validated): list[SlidePlan]
"""

import json
from typing import Optional

import anthropic

from config import settings
from core.style import (
    SLIDE_ROLE,
    SlidePlan,
    SCENE_PHOTOREALISTIC_PREAMBLE,
    SCENE_NEGATIVE_PROMPT,
    SCENE_BOTTOM_THIRD_RULE,
    SCENE_COLOR_PALETTE_HINT,
    BRAND_MARK_TEXT,
)
from ops_logger import get_ops_logger

ops = get_ops_logger("Instagram_Carousel_Cron", "Planner")


SYSTEM_PROMPT = """Instagram carousel planlamacısısın. Türkçe, Tweet/thread → 5-9 slide carousel.

YAPI: Slide 1=HOOK (kapak, dikkat çek) + 2-4 ARGÜMAN (her slide bir ders) + CTA (soru, bio link).

KESİN KURALLAR:
- Em-dash (—) YASAK. Tire (-) kullan.
- HOOK: overlay_text 1-4 kelime BÜYÜK HARF (örn "AJANSA VEDA"). body_text BOŞ. Scene: ABSÜRT/AGRESİF (şok, freeze-frame, dramatik aksiyon). "Person at laptop" YASAK.
- ARGÜMAN: overlay_text 2-5 kelime başlık. body_text 3-5 cümle, 250-500 char, somut+sayısal. Marka adı YOK, kategori kullan. Cümle max 14 kelime.
- CTA: overlay_text 4-9 kelime soru. body_text BOŞ.
- SCENE: İngilizce, photorealistic, 80-120 kelime. HOOK/CTA: alt %33 sakin. ARGÜMAN: üst %33 aksiyon, alt %66 sakin (text overlayı için).
- Renk: deep navy / charcoal / cream / brass-gold (neon/pastel/mor YASAK).

Tool_use sadece döndür.
"""


PLAN_TOOL = {
    "name": "plan_carousel",
    "description": "Verilen içeriği Instagram carousel slide'larına böl ve döndür.",
    "input_schema": {
        "type": "object",
        "properties": {
            "rationale": {
                "type": "string",
                "description": "Akış mantığı (1-2 cümle): neden bu yapı, hook neyi vaat ediyor.",
            },
            "slides": {
                "type": "array",
                "minItems": 5,
                "maxItems": 9,
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer", "minimum": 1, "maximum": 9},
                        "role": {"type": "string", "enum": ["hook", "argument", "cta"]},
                        "overlay_text": {
                            "type": "string",
                            "description": "Slide üzerine basılacak Türkçe BÜYÜK HARF metin. Hook=1-4 kelime, Argument=2-5 kelime başlık, CTA=4-9 kelime soru.",
                        },
                        "body_text": {
                            "type": "string",
                            "description": "ARGUMENT slide için ZORUNLU 3-5 kısa cümle (250-500 char) bilgilendirici paragraf, Türkçe normal yazım. Hook ve CTA için BOŞ string.",
                        },
                        "sub_text": {
                            "type": "string",
                            "description": "Opsiyonel — sadece CTA için micro yönlendirme (örn 'Bio'daki linke dokun'). Diğerlerinde boş.",
                        },
                        "scene_description": {
                            "type": "string",
                            "description": "İngilizce, photorealistic, 80-120 kelime sahne tarifi. ARGUMENT için: subject ÜST 1/3'te, ALT 2/3 sakin/koyu.",
                        },
                    },
                    "required": ["index", "role", "overlay_text", "body_text", "scene_description"],
                },
            },
        },
        "required": ["rationale", "slides"],
    },
}


def _build_user_message(content: dict) -> str:
    """Notion satırından LLM input message'ı kur."""
    parts = []
    parts.append(f"Kaynak: {content.get('source', '?')} | Skor: {content.get('score', '?')}/10")
    parts.append(f"Başlık: {content.get('title', '')}")
    if content.get("tweet_text"):
        parts.append(f"\n--- X Tweet ---\n{content['tweet_text']}")
    if content.get("thread"):
        parts.append(f"\n--- X Thread ---\n{content['thread']}")
    if content.get("linkedin_text"):
        parts.append(f"\n--- LinkedIn (uzun-form) ---\n{content['linkedin_text']}")
    if content.get("source_url"):
        parts.append(f"\nKaynak URL: {content['source_url']}")
    parts.append(
        f"\nGörev: Bu içerikten Instagram carousel planı çıkar. "
        f"Slide sayısı: {settings.SLIDE_COUNT} (içerik kısaysa 5'e in, çok zenginse 9'a çık). "
        f"`plan_carousel` tool'unu çağır."
    )
    return "\n".join(parts)


def plan(content: dict) -> Optional[list[SlidePlan]]:
    """Notion content row'undan SlidePlan listesi üret."""
    if settings.LLM_PROVIDER != "anthropic":
        ops.error("Şimdilik sadece anthropic destekleniyor", message=settings.LLM_PROVIDER)
        return None

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    user_msg = _build_user_message(content)

    try:
        response = client.messages.create(
            model=settings.WRITER_MODEL,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            tools=[PLAN_TOOL],
            tool_choice={"type": "tool", "name": "plan_carousel"},
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        ops.error("Anthropic plan exception", exception=e)
        return None

    # tool_use bloğunu yakala
    tool_input = None
    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and getattr(block, "name", "") == "plan_carousel":
            tool_input = block.input
            break

    if not tool_input:
        ops.error("Plan tool_use bloğu yok", message=str(response.content)[:300])
        return None

    raw_slides = tool_input.get("slides", [])
    if not raw_slides:
        ops.error("Plan slides boş")
        return None

    total = len(raw_slides)
    plans: list[SlidePlan] = []
    for s in raw_slides:
        body = (s.get("body_text") or "").strip()
        # Em-dash yasak (memory)
        body = body.replace("—", "-")
        plans.append(SlidePlan(
            index=int(s.get("index") or len(plans) + 1),
            total=total,
            role=s.get("role") or SLIDE_ROLE.ARGUMENT,
            overlay_text=(s.get("overlay_text") or "").strip(),
            body_text=body,
            sub_text=(s.get("sub_text") or "").strip(),
            scene_description=(s.get("scene_description") or "").strip(),
            cta_handle=BRAND_MARK_TEXT,
        ))

    ops.success(f"Plan hazır: {total} slide", message=tool_input.get("rationale", "")[:200])
    return plans


def enrich_scene_for_kie(slide: SlidePlan) -> str:
    """Slide.scene_description'ı style guide ile zenginleştirip Kie prompt'una çevir."""
    parts = [slide.scene_description.strip(), "", SCENE_PHOTOREALISTIC_PREAMBLE, SCENE_COLOR_PALETTE_HINT]

    if slide.role == SLIDE_ROLE.ARGUMENT:
        # Argüman slide: alt 2/3 tamamen sakin (uzun body metni oraya basılacak)
        parts.append(
            "CRITICAL composition rule: place subject and main action ONLY in the UPPER THIRD "
            "of the frame. The LOWER TWO-THIRDS must be visually quiet, dark, atmospheric, "
            "almost empty (e.g. dark wall, soft ambient lighting, minimal depth, blank floor). "
            "A long paragraph of overlay text will be placed in the lower two-thirds — it must "
            "be highly readable. Do not place any objects or strong details in the bottom 66%."
        )
    elif slide.role == SLIDE_ROLE.HOOK:
        # Hook = scroll-stopping shock. Absurd / aggressive / freeze-frame action.
        parts.append(
            "CRITICAL HOOK directive: this is the SCROLL-STOPPING cover. The scene MUST be "
            "absurd, aggressive, dramatic — a movie-poster freeze-frame of an extreme moment "
            "(destruction, fire, throwing, punching, protest, chaos, flying debris). Generic "
            "portraits, calm office scenes, 'person looking at phone' are FORBIDDEN. The "
            "viewer's eye should lock in 0.5 seconds because something visually shocking is "
            "frozen mid-action. Cinematic, dramatic lighting, motion blur acceptable on "
            "secondary elements but the subject pose must be crisp and dramatic."
        )
        parts.append(SCENE_BOTTOM_THIRD_RULE)
    else:
        # CTA: bottom-third sakin yeter
        parts.append(SCENE_BOTTOM_THIRD_RULE)

    parts.extend(["", SCENE_NEGATIVE_PROMPT])
    return "\n".join(parts)
