"""AR-002_76 Production Pipeline — Gerçek üretim task handler'ları.

Bu modül, üretim yaşam döngüsünün GERÇEK iş adımlarını (görsel, ses,
video, teslim) Production Executor'un task handler'ları olarak tanımlar.

Delegasyon Refaktörü (AR-002_70):
- Bu kod daha önce handlers/website.py içinde inline pipeline olarak
  yaşıyordu. Production Runtime'ın üretim yaşam döngüsünün TEK sahibi
  olabilmesi için Executor katmanına taşınmıştır.
- website.py artık yalnızca üretim talebini Production Runtime'a devreder.

Karar Devri Refaktörü (MASTER-013 / AR-002_81):
- Bu modül HİÇBİR KOŞULDA karar üretmez.
- Görevi yalnızca; teknik yürütme, provider ile haberleşme, sonuç toplama,
  Event üretme ve HLK Runtime tarafından verilen kararları eksiksiz
  uygulamaktır.
- PASS/FAIL, timeout, retry, provider kabul/red, provider değiştirme,
  kullanıcı bilgilendirmesi ve completion kararları üretemez.
- Karar gerektiren her durumda yürütme durdurulur, Karar Talebi
  (DecisionRequest) HLK Runtime'a iletilir, HLK Runtime kararını verir ve
  yürütme bu karara göre devam eder (AR-002_81 Karar Talep Protokolü).
- Tereddüt halinde karar üretmek yasaktır; tereddüt AMBIGUITY kategorisi
  ile HLK Runtime'a iletilir.
- Tüm sayısal değerler GC parametrelerinden okunur (AR-002_81 Sayısal
  Değer Yasağı, 01_Global_Configuration.md).

Mimari Dayanak:
- MASTER-013: HLK Karar Otoritesi ve Üretim Yürütücüsü Rol Ayrımı
- AR-002_81: HLK Runtime Karar Otoritesi ve Karar Talep Protokolü
- AR-002_70: STATE_VIDEO_PRODUCTION Runtime Architecture
- AR-002_76: Production Execution Architecture
- AR-002_22: Constitutional Feedback Loop
- AR-002_75: Production Service Selection
- OR-004_12: Üretim Sırasında Karar Talebi Operasyon Kuralı
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

from services.decision_packet import DecisionPacket
from services.hlk_runtime import (
    DecisionCategory,
    DecisionRequest,
    hlk_runtime,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# GC Parameters — 01_Global_Configuration.md (AR-002_81: Sayısal Değer Yasağı)
# ═══════════════════════════════════════════════════════════════════════════════

_GC_PROVIDER_HTTP_TIMEOUT = float(os.getenv("GC_PROVIDER_HTTP_TIMEOUT", "30"))
_GC_PROVIDER_STATUS_TIMEOUT = float(os.getenv("GC_PROVIDER_STATUS_TIMEOUT", "10"))
_GC_PROVIDER_POLL_COUNT = int(os.getenv("GC_PROVIDER_POLL_COUNT", "10"))
_GC_IMAGE_POLL_INTERVAL = float(os.getenv("GC_IMAGE_POLL_INTERVAL", "3"))
_GC_VIDEO_POLL_INTERVAL = float(os.getenv("GC_VIDEO_POLL_INTERVAL", "5"))


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PRODUCTION REQUEST — website.py'nin Production Runtime'a devrettiği talep
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProductionRequest:
    """Üretim talebi — handler katmanından Production Runtime'a devredilir.

    website.py yalnızca bu nesneyi oluşturur ve production_runtime.launch()
    ile devreder. Üretim yaşam döngüsünü YÖNETMEZ (AR-002_70).
    """
    chat_id: int
    user_id: int
    url: str = ""
    product_name: str = "urununuz"
    brand: str = "Marka"
    duration: int = 15
    voice_lang: str = "tr"
    bot: object = None                       # telegram.Bot — teslim için
    user_data: dict = field(default_factory=dict)  # PTB user_data referansı


@dataclass
class PipelineContext:
    """PID'ye bağlı çalışma bağlamı — task handler'ların ortak verisi."""
    request: ProductionRequest = None
    decision_packet: DecisionPacket = None
    prod_context: object = None              # decision_engine.ProductionContext
    img_path: Optional[str] = None
    voice_path: Optional[str] = None
    video_path: Optional[str] = None
    cost_report: dict = field(default_factory=dict)
    delivered: bool = False


# PID → PipelineContext (Production Runtime tarafından set edilir)
_contexts: dict[str, PipelineContext] = {}


def set_context(pid: str, ctx: PipelineContext) -> None:
    """Production Runtime, Executor başlamadan önce bağlamı kaydeder."""
    _contexts[pid] = ctx


def get_context(pid: str) -> Optional[PipelineContext]:
    return _contexts.get(pid)


def clear_context(pid: str) -> None:
    _contexts.pop(pid, None)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. KARAR TALEPLERİ — MASTER-013 / AR-002_81 (pipeline karar ÜRETMEZ)
# ═══════════════════════════════════════════════════════════════════════════════

def _request_provider_result_decision(
    pid: str,
    requester: str,
    category: str,
    provider: str,
    artifact: str,
    error: str,
    remaining_candidates: int,
):
    """AR-002_81 PROVIDER_RESULT: kabul/red kararını HLK Runtime'dan ister.

    Pipeline yalnızca ham teknik kanıtı iletir; kabul, red ve sıradaki
    provider'a geçiş kararları HLK Runtime'ındır.
    """
    return hlk_runtime.request_decision(DecisionRequest(
        pid=pid,
        category=DecisionCategory.PROVIDER_RESULT.value,
        requester=requester,
        context={
            "category": category,
            "provider": provider,
            "artifact": artifact or "",
            "error": error or "",
            "remaining_candidates": remaining_candidates,
        },
    ))


def _request_failure_decision(
    pid: str,
    requester: str,
    decision_packet: DecisionPacket,
    prod_context,
    category: str,
    failed_provider: str,
    failure_detail: str,
    has_fallback: bool,
):
    """AR-002_81 EXECUTION_FAILURE: süreklilik kararını HLK Runtime'dan ister.

    Retry sınırı değerlendirmesi, yeniden değerlendirme ve eskalasyon
    kararlarının tamamı HLK Runtime'da üretilir (AR-002_22, AR-002_79).
    """
    return hlk_runtime.request_decision(DecisionRequest(
        pid=pid,
        category=DecisionCategory.EXECUTION_FAILURE.value,
        requester=requester,
        context={
            "decision_packet": decision_packet,
            "prod_context": prod_context,
            "category": category,
            "failed_provider": failed_provider,
            "failure_detail": failure_detail,
            "has_fallback": has_fallback,
        },
    ))


def trigger_feedback_loop(
    decision_packet: DecisionPacket,
    prod_context,
    category: str,
    failed_provider: str,
    failure_detail: str,
) -> DecisionPacket | None:
    """AR-002_22 başarısızlık akışı — karar HLK Runtime'a devredilmiştir.

    MASTER-013 / AR-002_81 uyarınca bu fonksiyon karar ÜRETMEZ; yalnızca
    Karar Talebini HLK Runtime'a iletir ve verilen kararı uygular.
    (Geriye dönük uyumlu sarmalayıcı.)

    Returns:
        Yeni DecisionPacket (HLK Runtime RE_EVALUATE kararı verdiyse)
        veya None (eskalasyon/bekletme kararlarında).
    """
    decision = _request_failure_decision(
        pid=getattr(prod_context, "pid", ""),
        requester="production_pipeline.trigger_feedback_loop",
        decision_packet=decision_packet,
        prod_context=prod_context,
        category=category,
        failed_provider=failed_provider,
        failure_detail=failure_detail,
        has_fallback=True,
    )
    if decision.verdict == "RE_EVALUATE":
        return decision.params.get("new_packet")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# 3. TASK HANDLER'LAR — Production Executor tarafından çağrılır (AR-002_76)
# ═══════════════════════════════════════════════════════════════════════════════

async def task_image(task: dict, pid: str) -> dict:
    """ADIM 1: Görsel üretimi — HLK Runtime kararlarına göre.

    Pipeline provider'larla yalnızca HABERLEŞİR ve ham sonucu toplar.
    Kabul/red, sıradaki provider'a geçiş ve başarısızlık sonrası süreklilik
    kararları HLK Runtime'dan istenir (MASTER-013, AR-002_81).
    """
    ctx = get_context(pid)
    if ctx is None:
        raise RuntimeError(f"Pipeline context bulunamadı: {pid}")

    req = ctx.request
    decision_packet = ctx.decision_packet
    tmp = tempfile.gettempdir()
    import requests as _r

    image_providers = decision_packet.get_provider_list("image")
    for idx, img_choice in enumerate(image_providers):
        provider_name = img_choice.provider
        remaining = len(image_providers) - idx - 1
        attempt_error = ""
        logger.info(
            f"🎯 [Provider Selected] image → {provider_name} "
            f"(oncelik={img_choice.priority}, guven={img_choice.confidence:.0%})"
        )

        if provider_name == "fal.ai":
            fal_key = os.getenv("FAL_KEY", "")
            if not fal_key:
                attempt_error = "FAL_KEY tanımlı değil"
            else:
                try:
                    logger.info(f"🎨 [Production/1] Fal.ai deneniyor...")
                    resp = _r.post("https://queue.fal.run/fal-ai/fast-sdxl",
                        headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"},
                        json={"prompt": f"professional product photo of {req.brand} {req.product_name}, studio lighting, white background, high quality"},
                        timeout=_GC_PROVIDER_HTTP_TIMEOUT)
                    logger.info(
                        f"🎨 [Production/1] Fal.ai response: HTTP {resp.status_code}, "
                        f"body={resp.text[:300]}"
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        req_id = data.get("request_id")
                        if req_id:
                            poll_failed = False
                            for poll_n in range(_GC_PROVIDER_POLL_COUNT):
                                await asyncio.sleep(_GC_IMAGE_POLL_INTERVAL)
                                st = _r.get(f"https://queue.fal.run/fal-ai/fast-sdxl/requests/{req_id}/status",
                                    headers={"Authorization": f"Key {fal_key}"},
                                    timeout=_GC_PROVIDER_STATUS_TIMEOUT)
                                if st.status_code == 200:
                                    st_data = st.json()
                                    fal_status = st_data.get("status", "")
                                    logger.info(
                                        f"🎨 [Production/1] Fal.ai poll {poll_n+1}/{_GC_PROVIDER_POLL_COUNT}: "
                                        f"status={fal_status}"
                                    )
                                    if fal_status == "COMPLETED":
                                        images = st_data.get("response", {}).get("images", [])
                                        if images:
                                            img_url = images[0].get("url", "")
                                            if img_url:
                                                img_path = os.path.join(tmp, f"hlk_img_{req.user_id}.png")
                                                urllib.request.urlretrieve(img_url, img_path)
                                                ctx.img_path = img_path
                                                ctx.cost_report["services"]["fal.ai"] = "ok"
                                                logger.info(f"✅ [Production] Fal.ai görsel indirildi: {img_path}")
                                        break
                                    if fal_status in ("FAILED", "CANCELLED"):
                                        poll_failed = True
                                        attempt_error = f"fal.ai status={fal_status}"
                                        logger.warning(f"⚠️ [Production] Fal.ai {fal_status}")
                                        break
                                    # IN_QUEUE, IN_PROGRESS → poll devam
                            else:
                                # Poll döngüsü COMPLETED/FAILED olmadan tükendi
                                if not attempt_error:
                                    attempt_error = (
                                        f"fal.ai polling tükendi ({_GC_PROVIDER_POLL_COUNT} deneme), "
                                        f"son durum COMPLETED değil"
                                    )
                        else:
                            attempt_error = "fal.ai response'da request_id bos"
                            logger.warning(
                                f"⚠️ [Production] Fal.ai request_id bos: "
                                f"body={resp.text[:300]}"
                            )
                    else:
                        attempt_error = f"fal.ai HTTP {resp.status_code}: {resp.text[:200]}"
                except Exception as e:
                    attempt_error = f"{type(e).__name__}: {e}"
                    logger.warning(f"⚠️ [Production] Fal.ai basarisiz: {e}")

        elif provider_name == "kie.ai":
            try:
                kie_key = os.getenv("KIE_AI_API_KEY", "")
                logger.info(f"🎨 [Production/1] Kie AI deneniyor (key: {bool(kie_key)})...")
                if not kie_key:
                    attempt_error = "KIE_AI_API_KEY tanımlı değil"
                else:
                    # AR-002_88 FIX: kie.ai API request formatı düzeltildi
                    # prompt → input.prompt, aspect_ratio eklendi (zorunlu alan)
                    import json as _json
                    resp = _r.post("https://api.kie.ai/api/v1/jobs/createTask",
                        headers={"Authorization": f"Bearer {kie_key}", "Content-Type": "application/json"},
                        json={
                            "model": "z-image",
                            "input": {
                                "prompt": f"{req.brand} {req.product_name} product photo, clean background",
                                "aspect_ratio": "1:1",
                            },
                        },
                        timeout=_GC_PROVIDER_HTTP_TIMEOUT)
                    logger.info(
                        f"🎨 [Production/1] Kie createTask: HTTP {resp.status_code}, "
                        f"body={resp.text[:300]}"
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        # AR-002_88 FIX: API body code kontrolü (kie.ai HTTP 200 dönerken body'de hata olabilir)
                        body_code = data.get("code", 200)
                        if body_code != 200:
                            attempt_error = f"kie.ai API error code={body_code} msg={data.get('msg', '')}"
                            logger.warning(f"⚠️ [Production] Kie AI API hatasi: {attempt_error}")
                        else:
                            task_id = data.get("data", {})
                            if isinstance(task_id, dict):
                                task_id = task_id.get("taskId", "")
                            if task_id:
                                for _ in range(_GC_PROVIDER_POLL_COUNT):
                                    await asyncio.sleep(_GC_IMAGE_POLL_INTERVAL)
                                    st = _r.get(
                                        f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                                        headers={"Authorization": f"Bearer {kie_key}"},
                                        timeout=_GC_PROVIDER_STATUS_TIMEOUT)
                                    if st.status_code == 200:
                                        st_data = st.json()
                                        inner = st_data.get("data", {})
                                        if isinstance(inner, dict):
                                            # AR-002_88 FIX: state alanı (status değil)
                                            state = inner.get("state", "")
                                            logger.info(
                                                f"🎨 [Production/1] Kie poll: "
                                                f"state={state} progress={inner.get('progress', '?')}% "
                                                f"taskId={task_id}"
                                            )
                                            if state == "fail":
                                                fail_code = inner.get("failCode", "")
                                                fail_msg = inner.get("failMsg", "")
                                                attempt_error = (
                                                    f"kie.ai generation failed: "
                                                    f"failCode={fail_code} failMsg={fail_msg}"
                                                )
                                                logger.warning(
                                                    f"⚠️ [Production] Kie AI fail: "
                                                    f"{attempt_error}"
                                                )
                                                break
                                            if state == "success":
                                                # AR-002_88 FIX: resultJson parse edilip resultUrls[0] alınır
                                                result_json_str = inner.get("resultJson", "{}")
                                                try:
                                                    result_obj = _json.loads(result_json_str)
                                                    result_urls = result_obj.get("resultUrls", [])
                                                    img_url = result_urls[0] if result_urls else ""
                                                except Exception:
                                                    img_url = ""
                                                if img_url:
                                                    img_path = os.path.join(
                                                        tmp, f"hlk_img_{req.user_id}.png"
                                                    )
                                                    urllib.request.urlretrieve(img_url, img_path)
                                                    ctx.img_path = img_path
                                                    ctx.cost_report["services"]["kie.ai"] = "ok"
                                                    logger.info(
                                                        f"✅ [Production] Kie AI görsel "
                                                        f"indirildi: {img_path}"
                                                    )
                                                else:
                                                    attempt_error = (
                                                        "kie.ai success ama resultUrls bos"
                                                    )
                                                break
                                            # waiting, queuing, generating → poll devam
                            else:
                                attempt_error = "kie.ai createTask response'da taskId bos"
                                logger.warning(
                                    f"⚠️ [Production] Kie AI taskId bos: "
                                    f"response={resp.text[:300]}"
                                )
                    else:
                        attempt_error = (
                            f"kie.ai HTTP {resp.status_code}: {resp.text[:200]}"
                        )
            except Exception as e:
                attempt_error = f"{type(e).__name__}: {e}"
                logger.warning(f"⚠️ [Production] Kie AI basarisiz: {e}")

        else:
            # Tereddüt: bilinmeyen provider — karar HLK Runtime'ındır (MASTER-013)
            amb = hlk_runtime.request_decision(DecisionRequest(
                pid=pid,
                category=DecisionCategory.AMBIGUITY.value,
                requester="production_pipeline.task_image",
                context={"reason": "unsupported_provider", "provider": provider_name},
            ))
            if amb.params.get("action") == "SKIP":
                continue
            break

        # AR-002_81 PROVIDER_RESULT: kabul/red kararı HLK Runtime'ındır
        decision = _request_provider_result_decision(
            pid=pid,
            requester="production_pipeline.task_image",
            category="image",
            provider=provider_name,
            artifact=ctx.img_path or "",
            error=attempt_error,
            remaining_candidates=remaining,
        )
        if decision.verdict == "ACCEPT":
            logger.info(f"✅ [Provider Accepted] {provider_name} → {ctx.img_path}")
            break
        if decision.params.get("action") == "NEXT_PROVIDER":
            continue
        break  # REPORT_FAILURE — döngü sonlandırılır, karar aşağıda istenir

    # Görsel üretilemedi — süreklilik kararı HLK Runtime'ındır (AR-002_79)
    if not ctx.img_path:
        logger.warning("⚠️ [Production] Gorsel uretilemedi — sesli teslim yapilacak")
        ctx.cost_report["services"]["image"] = "failed"
        _request_failure_decision(
            pid=pid,
            requester="production_pipeline.task_image",
            decision_packet=decision_packet,
            prod_context=ctx.prod_context,
            category="image",
            failed_provider=(
                decision_packet.primary_image_provider.provider
                if decision_packet.primary_image_provider else "unknown"
            ),
            failure_detail="Tüm görsel provider'ları başarısız oldu",
            has_fallback=decision_packet.has_image_fallback,
        )

    return {
        "task_id": task.get("task_id"),
        "generated": bool(ctx.img_path),
        "artifact": ctx.img_path or "",
    }


async def task_voice(task: dict, pid: str) -> dict:
    """ADIM 2: Ses üretimi — HLK Runtime kararlarına göre.

    Seslendirme metni yaratıcı içeriktir (AR-002_77) ve pipeline
    tarafından üretilemez; CREATIVE_CONTENT kararı HLK Runtime'dan istenir.
    """
    ctx = get_context(pid)
    if ctx is None:
        raise RuntimeError(f"Pipeline context bulunamadı: {pid}")

    req = ctx.request
    decision_packet = ctx.decision_packet

    voice_choice = decision_packet.primary_voice_provider
    if voice_choice and voice_choice.provider == "elevenlabs":
        logger.info(
            f"🎯 [Provider Selected] voice → elevenlabs "
            f"(oncelik={voice_choice.priority}, guven={voice_choice.confidence:.0%})"
        )
        attempt_error = ""
        try:
            from services.voice_generator import ahu_voice_generator

            # AR-002_81 CREATIVE_CONTENT: metin kararı HLK Runtime'ındır
            script_decision = hlk_runtime.request_decision(DecisionRequest(
                pid=pid,
                category=DecisionCategory.CREATIVE_CONTENT.value,
                requester="production_pipeline.task_voice",
                context={
                    "kind": "voice_script",
                    "brand": req.brand,
                    "product_name": req.product_name,
                    "voice_lang": req.voice_lang,
                },
            ))
            voice_text = script_decision.params.get("voice_text", "")
            if script_decision.verdict == "PROVIDE" and voice_text:
                voice_path = ahu_voice_generator.generate(
                    voice_text, language=req.voice_lang
                )
                if voice_path:
                    ctx.voice_path = voice_path
                    ctx.cost_report["services"]["elevenlabs"] = "ok"
        except Exception as e:
            attempt_error = f"{type(e).__name__}: {e}"
            logger.warning(f"⚠️ [Production] ElevenLabs basarisiz: {e}")

        # AR-002_81 PROVIDER_RESULT: kabul/red kararı HLK Runtime'ındır
        decision = _request_provider_result_decision(
            pid=pid,
            requester="production_pipeline.task_voice",
            category="voice",
            provider="elevenlabs",
            artifact=str(ctx.voice_path) if ctx.voice_path else "",
            error=attempt_error,
            remaining_candidates=0,
        )
        if decision.verdict == "ACCEPT":
            logger.info(f"✅ [Provider Accepted] elevenlabs → {ctx.voice_path}")

    return {
        "task_id": task.get("task_id"),
        "generated": bool(ctx.voice_path),
        "artifact": str(ctx.voice_path) if ctx.voice_path else "",
    }


async def task_video(task: dict, pid: str) -> dict:
    """ADIM 3: Video üretimi — HLK Runtime kararlarına göre.

    Kabul/red, provider değişimi ve başarısızlık sonrası süreklilik
    kararları HLK Runtime'dan istenir (MASTER-013, AR-002_81).
    """
    ctx = get_context(pid)
    if ctx is None:
        raise RuntimeError(f"Pipeline context bulunamadı: {pid}")

    req = ctx.request
    decision_packet = ctx.decision_packet
    tmp = tempfile.gettempdir()
    import requests as _r

    if ctx.voice_path and ctx.img_path:
        video_providers = decision_packet.get_provider_list("video")
        for idx, vid_choice in enumerate(video_providers):
            provider_name = vid_choice.provider
            remaining = len(video_providers) - idx - 1
            attempt_error = ""
            logger.info(
                f"🎯 [Provider Selected] video → {provider_name} "
                f"(oncelik={vid_choice.priority}, guven={vid_choice.confidence:.0%})"
            )

            if provider_name == "hedra":
                try:
                    from services.hedra_generator import HedraGenerator
                    hedra = HedraGenerator()
                    video_path = os.path.join(tmp, f"hlk_video_{req.user_id}.mp4")
                    ok = await asyncio.to_thread(
                        hedra.create_lipsync_video, ctx.img_path, str(ctx.voice_path), video_path
                    )
                    if ok:
                        ctx.video_path = video_path
                        ctx.cost_report["services"]["hedra"] = "ok"
                    else:
                        attempt_error = "Hedra lipsync üretimi sonuç döndürmedi"
                except Exception as e:
                    attempt_error = f"{type(e).__name__}: {e}"
                    logger.warning(f"⚠️ [Production] Hedra basarisiz: {e}")

            elif provider_name == "higgsfield":
                try:
                    hf_key_id = os.getenv("HIGGSFIELD_KEY_ID", "")
                    hf_key_secret = os.getenv("HIGGSFIELD_KEY_SECRET", "")
                    if not (hf_key_id and hf_key_secret):
                        attempt_error = "HIGGSFIELD anahtarları tanımlı değil"
                    else:
                        with open(ctx.img_path, "rb") as f:
                            up_resp = _r.post("https://platform.higgsfield.ai/v1/files/upload",
                                headers={"Authorization": f"Key {hf_key_id}:{hf_key_secret}"},
                                files={"file": f}, timeout=_GC_PROVIDER_HTTP_TIMEOUT)
                        if up_resp.status_code == 200:
                            file_url = up_resp.json().get("url", "")
                            gen_resp = _r.post("https://platform.higgsfield.ai/higgsfield-ai/seedance/standard",
                                headers={"Authorization": f"Key {hf_key_id}:{hf_key_secret}", "Content-Type": "application/json"},
                                json={"image_url": file_url, "duration": req.duration},
                                timeout=_GC_PROVIDER_HTTP_TIMEOUT)
                            if gen_resp.status_code == 200:
                                req_id = gen_resp.json().get("request_id", "")
                                for _ in range(_GC_PROVIDER_POLL_COUNT):
                                    await asyncio.sleep(_GC_VIDEO_POLL_INTERVAL)
                                    st = _r.get(f"https://platform.higgsfield.ai/requests/{req_id}/status",
                                        headers={"Authorization": f"Key {hf_key_id}:{hf_key_secret}"},
                                        timeout=_GC_PROVIDER_STATUS_TIMEOUT)
                                    if st.status_code == 200 and st.json().get("status") == "completed":
                                        vid_url = st.json().get("output_url", "")
                                        if vid_url:
                                            video_path = os.path.join(tmp, f"hlk_video_{req.user_id}.mp4")
                                            urllib.request.urlretrieve(vid_url, video_path)
                                            ctx.video_path = video_path
                                            ctx.cost_report["services"]["higgsfield"] = "ok"
                                        break
                        else:
                            attempt_error = f"HTTP {up_resp.status_code}"
                except Exception as e:
                    attempt_error = f"{type(e).__name__}: {e}"
                    logger.warning(f"⚠️ [Production] Higgsfield basarisiz: {e}")

            else:
                # Tereddüt: bilinmeyen provider — karar HLK Runtime'ındır
                amb = hlk_runtime.request_decision(DecisionRequest(
                    pid=pid,
                    category=DecisionCategory.AMBIGUITY.value,
                    requester="production_pipeline.task_video",
                    context={"reason": "unsupported_provider", "provider": provider_name},
                ))
                if amb.params.get("action") == "SKIP":
                    continue
                break

            # AR-002_81 PROVIDER_RESULT: kabul/red kararı HLK Runtime'ındır
            decision = _request_provider_result_decision(
                pid=pid,
                requester="production_pipeline.task_video",
                category="video",
                provider=provider_name,
                artifact=ctx.video_path or "",
                error=attempt_error,
                remaining_candidates=remaining,
            )
            if decision.verdict == "ACCEPT":
                logger.info(f"✅ [Provider Accepted] {provider_name} → {ctx.video_path}")
                break
            if decision.params.get("action") == "NEXT_PROVIDER":
                continue
            break  # REPORT_FAILURE

    # Video üretilemedi — süreklilik kararı HLK Runtime'ındır (AR-002_79)
    if not ctx.video_path and ctx.img_path and ctx.voice_path:
        logger.warning("⚠️ [Production] Tum video provider'lari basarisiz")
        ctx.cost_report["services"]["video"] = "failed"
        failure_decision = _request_failure_decision(
            pid=pid,
            requester="production_pipeline.task_video",
            decision_packet=decision_packet,
            prod_context=ctx.prod_context,
            category="video",
            failed_provider=(
                decision_packet.primary_video_provider.provider
                if decision_packet.primary_video_provider else "unknown"
            ),
            failure_detail="Tüm video provider'ları başarısız oldu",
            has_fallback=decision_packet.has_video_fallback,
        )
        if failure_decision.verdict == "RE_EVALUATE":
            new_packet = failure_decision.params.get("new_packet")
            if new_packet:
                ctx.decision_packet = new_packet
                req.user_data["decision_packet"] = new_packet.to_dict()

    return {
        "task_id": task.get("task_id"),
        "generated": bool(ctx.video_path),
        "artifact": ctx.video_path or "",
    }


async def task_delivery(task: dict, pid: str) -> dict:
    """ADIM 4: Teslim — HLK Runtime DELIVERY kararına göre (AR-002_36).

    Teslim şekli ve kullanıcıya gönderilecek mesaj içeriği HLK Runtime
    tarafından kararlaştırılır (MASTER-013: pipeline kullanıcıya süreç
    kararı içeren mesaj üretemez). Pipeline onaylanan mesajı değiştirmeden
    iletir.

    Teslim başarısız olursa exception fırlatır — Executor retry uygular,
    tüm denemeler tükenirse Production Runtime failure yolunu işletir.
    """
    ctx = get_context(pid)
    if ctx is None:
        raise RuntimeError(f"Pipeline context bulunamadı: {pid}")

    req = ctx.request
    video_available = bool(ctx.video_path and os.path.exists(ctx.video_path))

    # AR-002_81 DELIVERY: teslim şekli ve mesaj içeriği HLK Runtime'ındır
    delivery_decision = hlk_runtime.request_decision(DecisionRequest(
        pid=pid,
        category=DecisionCategory.DELIVERY.value,
        requester="production_pipeline.task_delivery",
        context={
            "video_available": video_available,
            "brand": req.brand,
            "product_name": req.product_name,
            "duration": req.duration,
            "voice_lang": req.voice_lang,
        },
    ))

    if delivery_decision.verdict == "DELIVER_VIDEO":
        with open(ctx.video_path, "rb") as vf:
            await req.bot.send_video(
                chat_id=req.chat_id, video=vf,
                caption=delivery_decision.params.get("caption", ""),
                parse_mode=delivery_decision.params.get("parse_mode", "HTML"),
            )
        logger.info(f"✅ [Production] VIDEO GONDERILDI: {pid}")
    else:
        # DELIVER_INFO — ses/video oynaticisi GONDERILMEZ; onaylı metin iletilir
        await req.bot.send_message(
            chat_id=req.chat_id,
            text=delivery_decision.params.get("text", ""),
            parse_mode=delivery_decision.params.get("parse_mode", "HTML"),
        )
        logger.info(f"✅ [Production] BILGILENDIRME: {pid}")

    # Yalnızca gerçek video teslimi yapıldıysa delivered=True
    # (DELIVER_INFO metin bildirimi teslim sayılmaz — AR-002_84)
    if delivery_decision.verdict == "DELIVER_VIDEO":
        ctx.delivered = True  # Teknik sonuç kaydı — karar değildir (AR-002_76 Adım 6)
    return {
        "task_id": task.get("task_id"),
        "delivered": delivery_decision.verdict == "DELIVER_VIDEO",
        "video": bool(ctx.video_path),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. HANDLER KAYDI — Production Executor'a bağlama
# ═══════════════════════════════════════════════════════════════════════════════

# Task Package agent adı → gerçek handler eşlemesi
PIPELINE_AGENTS = {
    "ImageGenerator": task_image,
    "VoiceGenerator": task_voice,
    "VideoRenderer": task_video,
    "DeliveryAgent": task_delivery,
}


def register_handlers() -> None:
    """Gerçek üretim handler'larını Production Executor'a kaydeder.

    Production Runtime tarafından üretim başlamadan önce çağrılır.
    İdempotenttir — tekrarlı çağrı zarar vermez.
    """
    from services.production_executor import production_executor

    for agent, handler in PIPELINE_AGENTS.items():
        production_executor.register_handler(agent, handler)
    logger.info(
        f"🔗 [Pipeline] {len(PIPELINE_AGENTS)} gerçek task handler "
        f"Production Executor'a kaydedildi"
    )
