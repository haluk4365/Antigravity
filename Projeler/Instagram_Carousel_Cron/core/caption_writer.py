"""Instagram caption writer.

Memory kuralları:
  - Em-dash YASAK
  - Kısa cümle (max 15 kelime)
  - Marka/ürün adı caption'da geçmesin (kategori adı kullan)
  - Claude Code öncelikli (uygunsa)

Format:
  - Hook (1 cümle, max 12 kelime)
  - 3-5 satır bullet (• yok, yeni satır + 1-2 sözcük)
  - Soru (engagement)
  - 5-8 hashtag (Türkçe + İngilizce, AI/otomasyon ekosistem)

Max 2200 karakter (Instagram limiti).
"""

from typing import Optional

import anthropic

from config import settings
from core.style import SlidePlan
from ops_logger import get_ops_logger

ops = get_ops_logger("Instagram_Carousel_Cron", "Caption")


SYSTEM_PROMPT = """Instagram caption yazarısısın. Türkçe, sade dil.

KESİN KURALLAR:
1. Em-dash (—) YASAK. Tire (-) ya da virgül kullan.
2. Cümle max 15 kelime.
3. Marka/ürün adı geçmesin. Kategori kullan (örn "AI aracı", "no-code platform").
4. Emoji max 2 (hook/soru).
5. Format:
   [HOOK — max 12 kelime] → [boş satır] → [3-5 madde, tek satır] → [boş satır] → [SORU] → [boş satır] → [HASHTAG 5-8]
6. Max 1800 karakter toplam.

Tool_use sadece döndür, düz metin yok.
"""


CAPTION_TOOL = {
    "name": "write_caption",
    "description": "Instagram carousel için caption metni döndür.",
    "input_schema": {
        "type": "object",
        "properties": {
            "caption": {
                "type": "string",
                "description": "Tam Instagram caption (hook + bullets + soru + hashtag).",
            },
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 5,
                "maxItems": 8,
                "description": "Caption'da geçen hashtag listesi (raporlama için, # dahil).",
            },
        },
        "required": ["caption", "hashtags"],
    },
}


def write(content: dict, slides: list[SlidePlan]) -> Optional[str]:
    """Tweet/thread + slide planından Instagram caption üret."""
    if settings.IS_DRY_RUN:
        ops.info("[DRY-RUN] Caption yazımı atlandı")
        return "[DRY-RUN] caption placeholder.\n\n#yapayzeka #otomasyon #ai #kobi #verimlilik"

    if settings.LLM_PROVIDER != "anthropic":
        ops.error("Şimdilik sadece anthropic destekleniyor", message=settings.LLM_PROVIDER)
        return None

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    slides_summary = "\n".join(
        f"  Slide {s.index} ({s.role}): {s.overlay_text}" for s in slides
    )
    user_msg = (
        f"Kaynak: {content.get('source', '?')}\n"
        f"Başlık: {content.get('title', '')}\n\n"
        f"--- Carousel Slide Hook'ları ---\n{slides_summary}\n\n"
        f"--- Tweet/Thread Metni ---\n"
        f"{content.get('tweet_text') or content.get('thread') or content.get('linkedin_text', '')}\n\n"
        f"Görev: Bu carousel için Instagram caption yaz. `write_caption` tool'unu çağır."
    )

    try:
        response = client.messages.create(
            model=settings.WRITER_MODEL,
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            tools=[CAPTION_TOOL],
            tool_choice={"type": "tool", "name": "write_caption"},
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        ops.error("Anthropic caption exception", exception=e)
        return None

    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and getattr(block, "name", "") == "write_caption":
            caption = (block.input.get("caption") or "").strip()
            if "—" in caption:
                ops.warning("Caption'da em-dash bulundu, replace ediliyor")
                caption = caption.replace("—", "-")
            if len(caption) > 2200:
                caption = caption[:2197] + "..."
            ops.success(f"Caption hazır ({len(caption)} char)")
            return caption

    ops.error("Caption tool_use bloğu yok")
    return None
