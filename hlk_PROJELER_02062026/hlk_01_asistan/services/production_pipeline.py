"""AR-002_76 Production Pipeline — Gerçek üretim task handler'ları.

Bu modül, üretim yaşam döngüsünün GERÇEK iş adımlarını (görsel, ses,
video, teslim) Production Executor'un task handler'ları olarak tanımlar.

Delegasyon Refaktörü (AR-002_70):
- Bu kod daha önce handlers/website.py içinde inline pipeline olarak
  yaşıyordu. Production Runtime'ın üretim yaşam döngüsünün TEK sahibi
  olabilmesi için Executor katmanına taşınmıştır.
- website.py artık yalnızca üretim talebini Production Runtime'a devreder.

Bu modül:
- Karar vermez (MASTER-004) — yalnızca Decision Packet'i uygular
- Servis seçmez (AR-002_75) — HLK Decision Engine'in seçtiği provider'ı kullanır
- Provider başarısızlığında Feedback Loop'u tetikler (AR-002_22)
- Her adımı Production Runtime kapsamında, PID ile ilişkili yürütür

Mimari Dayanak:
- AR-002_70: STATE_VIDEO_PRODUCTION Runtime Architecture
- AR-002_76: Production Execution Architecture
- AR-002_22: Constitutional Feedback Loop
- AR-002_75: Production Service Selection
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass, field
from typing import Optional

from services.decision_packet import DecisionPacket

logger = logging.getLogger(__name__)


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
# 2. FEEDBACK LOOP — AR-002_22 (website.py'den taşındı)
# ═══════════════════════════════════════════════════════════════════════════════

def trigger_feedback_loop(
    decision_packet: DecisionPacket,
    prod_context,
    category: str,
    failed_provider: str,
    failure_detail: str,
) -> DecisionPacket | None:
    """AR-002_22 Adım 2-6: Automatic Provider Switch + Escalation.

    1. ReEvaluationContext oluşturur (karar/öneri İÇERMEZ)
    2. Decision Engine'i yeniden değerlendirmeye çağırır
    3. Maksimum retry limitini kontrol eder (GC_MAX_RE_EVALUATION_COUNT)
    4. Limit aşılırsa Escalation Engine'i tetikler

    Returns:
        Yeni DecisionPacket veya None (eskalasyon tetiklendiyse).
    """
    from services.decision_engine import decision_engine as de
    from services.decision_packet import ReEvaluationContext, ReEvaluationReason

    retry_count = decision_packet.re_evaluation_count + 1
    max_retry = int(os.getenv("GC_MAX_RE_EVALUATION_COUNT", "3"))

    if retry_count > max_retry:
        logger.error(
            f"🚨 [FeedbackLoop] Maksimum retry asildi ({max_retry}) — "
            f"Escalation Engine tetikleniyor. Kategori={category}, "
            f"basarisiz={failed_provider}"
        )
        from services.escalation_engine import escalation_engine as esc, EscalationReason
        esc.escalate(
            pid=prod_context.pid,
            reason=EscalationReason.ALL_PROVIDERS_FAILED.value,
            detail=f"Kategori={category}, basarisiz={failed_provider}: {failure_detail}",
            failed_providers=[failed_provider],
            retry_count=retry_count,
        )
        return None

    logger.info(
        f"🔄 [Feedback Loop Started] kategori={category}, "
        f"basarisiz={failed_provider}, retry={retry_count}/{max_retry}"
    )

    re_ctx = ReEvaluationContext(
        original_decision_id=decision_packet.decision_id,
        trigger_event="EXECUTOR_FAILED",
        re_evaluation_reason=ReEvaluationReason.EXECUTION_FAILED.value,
        current_state="STATE_VIDEO_PRODUCTION",
        re_evaluation_count=retry_count,
        failure_detail=failure_detail,
        failed_provider=failed_provider,
    )

    try:
        new_packet = de.re_evaluate(re_ctx, prod_context)
        logger.info(
            f"✅ [FeedbackLoop] Yeni karar: {new_packet.decision_id} "
            f"(re-eval of {decision_packet.decision_id}, retry={retry_count})"
        )
        return new_packet
    except Exception as e:
        logger.error(f"❌ [FeedbackLoop] Re-evaluation basarisiz: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# 3. TASK HANDLER'LAR — Production Executor tarafından çağrılır (AR-002_76)
# ═══════════════════════════════════════════════════════════════════════════════

async def task_image(task: dict, pid: str) -> dict:
    """ADIM 1: Görsel üretimi — HLK Decision Engine kararına göre.

    Provider başarısızlığı üretimi durdurmaz (AR-002_79 süreklilik);
    görsel olmadan devam edilir ve Feedback Loop tetiklenir.
    """
    ctx = get_context(pid)
    if ctx is None:
        raise RuntimeError(f"Pipeline context bulunamadı: {pid}")

    req = ctx.request
    decision_packet = ctx.decision_packet
    tmp = tempfile.gettempdir()
    import requests as _r

    image_providers = decision_packet.get_provider_list("image")
    for img_choice in image_providers:
        provider_name = img_choice.provider
        logger.info(
            f"🎯 [Provider Selected] image → {provider_name} "
            f"(oncelik={img_choice.priority}, guven={img_choice.confidence:.0%})"
        )

        if provider_name == "fal.ai":
            fal_key = os.getenv("FAL_KEY", "")
            if fal_key:
                try:
                    logger.info(f"🎨 [Production/1] Fal.ai deneniyor...")
                    resp = _r.post("https://queue.fal.run/fal-ai/fast-sdxl",
                        headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json"},
                        json={"prompt": f"professional product photo of {req.brand} {req.product_name}, studio lighting, white background, high quality"},
                        timeout=30)
                    logger.info(f"🎨 [Production/1] Fal.ai response: {resp.status_code}")
                    if resp.status_code == 200:
                        data = resp.json()
                        req_id = data.get("request_id")
                        if req_id:
                            for _ in range(8):
                                await asyncio.sleep(3)
                                st = _r.get(f"https://queue.fal.run/fal-ai/fast-sdxl/requests/{req_id}/status",
                                    headers={"Authorization": f"Key {fal_key}"}, timeout=10)
                                if st.status_code == 200:
                                    st_data = st.json()
                                    if st_data.get("status") == "COMPLETED":
                                        images = st_data.get("response", {}).get("images", [])
                                        if images:
                                            img_url = images[0].get("url", "")
                                            if img_url:
                                                img_path = os.path.join(tmp, f"hlk_img_{req.user_id}.png")
                                                _r.urlretrieve(img_url, img_path)
                                                ctx.img_path = img_path
                                                logger.info(f"✅ [Provider Accepted] fal.ai → {img_path}")
                                                ctx.cost_report["services"]["fal.ai"] = "ok"
                                        break
                except Exception as e:
                    logger.warning(f"⚠️ [Production] Fal.ai basarisiz: {e}")
            if ctx.img_path:
                break  # Başarılı — sonraki provider'a geçme

        elif provider_name == "kie.ai":
            try:
                kie_key = os.getenv("KIE_AI_API_KEY", "")
                logger.info(f"🎨 [Production/1] Kie AI deneniyor (key: {bool(kie_key)})...")
                if kie_key:
                    resp = _r.post("https://api.kie.ai/api/v1/jobs/createTask",
                        headers={"Authorization": f"Bearer {kie_key}", "Content-Type": "application/json"},
                        json={"model": "z-image", "prompt": f"{req.brand} {req.product_name} product photo, clean background"},
                        timeout=30)
                    logger.info(f"🎨 [Production/1] Kie createTask: {resp.status_code}")
                    if resp.status_code == 200:
                        data = resp.json()
                        task_id = data.get("data", {})
                        if isinstance(task_id, dict):
                            task_id = task_id.get("taskId", "")
                        if task_id:
                            for _ in range(10):
                                await asyncio.sleep(3)
                                st = _r.get(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                                    headers={"Authorization": f"Bearer {kie_key}"}, timeout=10)
                                if st.status_code == 200:
                                    st_data = st.json()
                                    inner = st_data.get("data", {})
                                    if isinstance(inner, dict):
                                        status = inner.get("status", "")
                                        img_url = inner.get("result_url") or inner.get("image_url") or inner.get("output_url", "")
                                        if status in ("completed", "success") and img_url:
                                            img_path = os.path.join(tmp, f"hlk_img_{req.user_id}.png")
                                            _r.urlretrieve(img_url, img_path)
                                            ctx.img_path = img_path
                                            logger.info(f"✅ [Provider Accepted] kie.ai → {img_path}")
                                            ctx.cost_report["services"]["kie.ai"] = "ok"
                                            break
            except Exception as e:
                logger.warning(f"⚠️ [Production] Kie AI basarisiz: {e}")
            if ctx.img_path:
                break  # Başarılı

    # Hicbiri olmadiysa gorsel OLMADAN devam et (AR-002_79 — üretim durmaz)
    if not ctx.img_path:
        logger.warning("⚠️ [Production] Gorsel uretilemedi — sesli teslim yapilacak")
        ctx.cost_report["services"]["image"] = "failed"
        # AR-002_22: FEEDBACK LOOP — Görsel provider'ı başarısız
        if decision_packet.has_image_fallback:
            trigger_feedback_loop(
                decision_packet, ctx.prod_context, "image",
                failed_provider=decision_packet.primary_image_provider.provider if decision_packet.primary_image_provider else "unknown",
                failure_detail="Tüm görsel provider'ları başarısız oldu",
            )

    return {
        "task_id": task.get("task_id"),
        "generated": bool(ctx.img_path),
        "artifact": ctx.img_path or "",
    }


async def task_voice(task: dict, pid: str) -> dict:
    """ADIM 2: Ses üretimi — HLK Decision Engine kararına göre."""
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
        try:
            from services.voice_generator import ahu_voice_generator
            if req.voice_lang == "tr":
                voice_text = (
                    f"{req.brand} {req.product_name} urununu simdi kesfedin. "
                    f"Kalite ve uygun fiyat bir arada. Hemen siparis vermek icin tiklayin."
                )
            else:
                voice_text = (
                    f"Discover {req.brand} {req.product_name} now. "
                    f"Quality and affordable price together. Order now!"
                )
            voice_path = ahu_voice_generator.generate(voice_text, language=req.voice_lang)
            if voice_path:
                ctx.voice_path = voice_path
                logger.info(f"✅ [Provider Accepted] elevenlabs → {voice_path}")
                ctx.cost_report["services"]["elevenlabs"] = "ok"
        except Exception as e:
            logger.warning(f"⚠️ [Production] ElevenLabs basarisiz: {e}")

    return {
        "task_id": task.get("task_id"),
        "generated": bool(ctx.voice_path),
        "artifact": str(ctx.voice_path) if ctx.voice_path else "",
    }


async def task_video(task: dict, pid: str) -> dict:
    """ADIM 3: Video üretimi — HLK Decision Engine kararına göre."""
    ctx = get_context(pid)
    if ctx is None:
        raise RuntimeError(f"Pipeline context bulunamadı: {pid}")

    req = ctx.request
    decision_packet = ctx.decision_packet
    tmp = tempfile.gettempdir()
    import requests as _r

    if ctx.voice_path and ctx.img_path:
        video_providers = decision_packet.get_provider_list("video")
        for vid_choice in video_providers:
            provider_name = vid_choice.provider
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
                        logger.info(f"✅ [Provider Accepted] hedra → {video_path}")
                        ctx.cost_report["services"]["hedra"] = "ok"
                except Exception as e:
                    logger.warning(f"⚠️ [Production] Hedra basarisiz: {e}")
                if ctx.video_path:
                    break  # Başarılı — sonraki provider'a geçme

            elif provider_name == "higgsfield":
                try:
                    hf_key_id = os.getenv("HIGGSFIELD_KEY_ID", "")
                    hf_key_secret = os.getenv("HIGGSFIELD_KEY_SECRET", "")
                    if hf_key_id and hf_key_secret:
                        with open(ctx.img_path, "rb") as f:
                            up_resp = _r.post("https://platform.higgsfield.ai/v1/files/upload",
                                headers={"Authorization": f"Key {hf_key_id}:{hf_key_secret}"},
                                files={"file": f}, timeout=30)
                        if up_resp.status_code == 200:
                            file_url = up_resp.json().get("url", "")
                            gen_resp = _r.post("https://platform.higgsfield.ai/higgsfield-ai/seedance/standard",
                                headers={"Authorization": f"Key {hf_key_id}:{hf_key_secret}", "Content-Type": "application/json"},
                                json={"image_url": file_url, "duration": req.duration},
                                timeout=30)
                            if gen_resp.status_code == 200:
                                req_id = gen_resp.json().get("request_id", "")
                                for _ in range(10):
                                    await asyncio.sleep(5)
                                    st = _r.get(f"https://platform.higgsfield.ai/requests/{req_id}/status",
                                        headers={"Authorization": f"Key {hf_key_id}:{hf_key_secret}"}, timeout=10)
                                    if st.status_code == 200 and st.json().get("status") == "completed":
                                        vid_url = st.json().get("output_url", "")
                                        if vid_url:
                                            video_path = os.path.join(tmp, f"hlk_video_{req.user_id}.mp4")
                                            _r.urlretrieve(vid_url, video_path)
                                            ctx.video_path = video_path
                                            logger.info(f"✅ [Provider Accepted] higgsfield → {video_path}")
                                            ctx.cost_report["services"]["higgsfield"] = "ok"
                                        break
                except Exception as e:
                    logger.warning(f"⚠️ [Production] Higgsfield basarisiz: {e}")
                if ctx.video_path:
                    break  # Başarılı

    # AR-002_22: FEEDBACK LOOP — Video provider'ı başarısız
    if not ctx.video_path and ctx.img_path and ctx.voice_path:
        logger.warning("⚠️ [Production] Tum video provider'lari basarisiz")
        ctx.cost_report["services"]["video"] = "failed"
        if decision_packet.has_video_fallback:
            new_packet = trigger_feedback_loop(
                decision_packet, ctx.prod_context, "video",
                failed_provider=decision_packet.primary_video_provider.provider if decision_packet.primary_video_provider else "unknown",
                failure_detail="Tüm video provider'ları başarısız oldu",
            )
            if new_packet:
                ctx.decision_packet = new_packet
                req.user_data["decision_packet"] = new_packet.to_dict()

    return {
        "task_id": task.get("task_id"),
        "generated": bool(ctx.video_path),
        "artifact": ctx.video_path or "",
    }


async def task_delivery(task: dict, pid: str) -> dict:
    """ADIM 4: Teslim — video veya bilgilendirme mesajı (AR-002_36).

    Teslim başarısız olursa exception fırlatır — Executor retry uygular,
    tüm denemeler tükenirse Production Runtime failure yolunu işletir.
    """
    ctx = get_context(pid)
    if ctx is None:
        raise RuntimeError(f"Pipeline context bulunamadı: {pid}")

    req = ctx.request

    if ctx.video_path and os.path.exists(ctx.video_path):
        with open(ctx.video_path, "rb") as vf:
            await req.bot.send_video(
                chat_id=req.chat_id, video=vf,
                caption=f"🎬 <b>{req.brand} — {req.product_name}</b>\n\n"
                        f"Videonuz hazir! 📋 PID: <code>{pid}</code>",
                parse_mode="HTML",
            )
        logger.info(f"✅ [Production] VIDEO GONDERILDI: {pid}")
    else:
        # Ses/video oynaticisi GONDERILMEZ — sadece bilgilendirme metni
        await req.bot.send_message(
            chat_id=req.chat_id,
            text=f"🎬 <b>Uretim Tamamlandi!</b>\n\n"
                 f"📋 PID: <code>{pid}</code>\n"
                 f"Urun: <b>{req.brand} — {req.product_name}</b>\n"
                 f"Video suresi: {req.duration} sn | Ses: {req.voice_lang.upper()}\n\n"
                 f"Videonuz hazirlaniyor, en kisa surede gonderilecektir.\n"
                 f"<i>HLK AI Reklam Asistani</i>",
            parse_mode="HTML",
        )
        logger.info(f"✅ [Production] BILGILENDIRME: {pid}")

    ctx.delivered = True
    return {
        "task_id": task.get("task_id"),
        "delivered": True,
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
