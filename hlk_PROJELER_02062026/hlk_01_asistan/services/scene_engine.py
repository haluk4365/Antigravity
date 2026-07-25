"""
AR-002_28 Conversation Scene Engine — Gerçek Implementasyon

STATE_ACTIVE_CONVERSATION oluştuğunda:
1. FD-008_1'den aktif sahneyi bul
2. Constitution Cache'ten Flow Diagram davranışlarını oku (MASTER-008)
3. Scene içeriğini oluştur
4. ScenePayload üret
5. AR-002_36 Scene Delivery'e gönder
6. Teslim sonucunu raporla
"""

import asyncio
import logging
import uuid

from services.scene_delivery import scene_delivery, ScenePayload, DeliveryStatus
from services.scene_registry import get_scene_for_state
from services.voice_generator import ahu_voice_generator
from utils.state_engine import UserState, StateEngine, UserEvent

logger = logging.getLogger(__name__)

# ── State → Flow Diagram Sahne Referans Haritası ─────────────────────────
# Bu harita yalnızca bir yönlendirme tablosudur (routing table).
# Operasyonel davranışları tanımlamaz. Tek kaynak 08_HLK_FLOW_DIAGRAM.md'dir.
# MASTER-008: Flow Diagram, State Engine ve diğer kaynaklarla birlikte
# değerlendirilerek tek bir proje modeli oluşturulur.
_STATE_TO_FLOW_SCENE: dict[str, str] = {
    "STATE_ACTIVE_CONVERSATION": "SAHNE-02",
    "STATE_COLLECT_PRODUCT_MATERIALS": "SAHNE-02",
    "STATE_PLATFORM_SELECTION": "SAHNE-02",
    "STATE_VIDEO_SETTINGS": "SAHNE-03",
    "STATE_VIDEO_RESOLUTION_SELECTION": "SAHNE-04",
    "STATE_VIDEO_DURATION_SELECTION": "SAHNE-05",
    "STATE_STYLE_SELECTION": "SAHNE-06",
    "STATE_TARGET_AUDIENCE_SELECTION": "SAHNE-07",
    "STATE_AUDIO_SELECTION": "SAHNE-08",
    "STATE_VOICE_LANGUAGE": "SAHNE-09",
    "STATE_VOICE_CHARACTER": "SAHNE-10",
    "STATE_EMPHASIS": "SAHNE-11",
    "STATE_BRIEF_REVIEW": "SAHNE-12",
    "STATE_BRIEF_COMPLETED": "SAHNE-13",
    "STATE_SCENARIO_APPROVAL": "SAHNE-13",
}


class ConversationSceneEngine:
    """AR-002_28: Conversation Scene Engine

    FD-008_1 akışını kullanarak her state için doğru sahneyi üretir,
    ScenePayload'e çevirir ve Scene Delivery üzerinden Telegram'a gönderir.
    """

    def __init__(self):
        self._production_log: list[dict] = []
        self._active_scene_id: str | None = None

    @staticmethod
    def _translate_scene_text(scene_id: str, text: str, user_data: dict) -> str:
        """AR-002_30: Sahne metnini kullanıcının seçtiği dile çevirir.

        Sahne ID'sine göre i18n anahtarı kullanır. Çeviri yoksa orijinal metni döndürür.
        """
        import logging
        _log = logging.getLogger(__name__)
        from config.i18n import t
        lang = user_data.get("language", "tr")
        _log.info(f"🌐 [i18n] Scene '{scene_id}' -> lang='{lang}'")

        i18n_map = {
            # Tüm sahneler için çeviri anahtarları (AR-002_30)
            "scene_collect_materials_info": ("material", "prompt_has"),
            "scene_platform_selection": ("platform", "prompt"),
            "SAHNE-03": ("s03", "prompt"),
            "SAHNE-04": ("s04", "prompt"),
            "SAHNE-05": ("s05", "prompt"),
            "SAHNE-06": ("s06", "prompt"),
            "SAHNE-07": ("s07", "prompt"),
            "SAHNE-08": ("s08", "prompt"),
            "SAHNE-09": ("s09", "prompt"),
            "SAHNE-10": ("s10", "prompt"),
            "SAHNE-11": ("s11", "prompt"),
        }

        mapped = i18n_map.get(scene_id)
        if mapped:
            section, key = mapped
            translated = t(f"{section}.{key}", lang)
            _log.info(f"🌐 [i18n] key={section}.{key} translated={translated[:50]}...")
            if translated != f"{section}.{key}":
                return translated
        _log.warning(f"🌐 [i18n] Scene '{scene_id}' — ceviri bulunamadi, orijinal metin kullaniliyor")
        return text

    @staticmethod
    def _translate_buttons(buttons: list, user_data: dict) -> list:
        """AR-002_30: Buton metinlerini kullanıcının seçtiği dile çevirir."""
        from config.i18n import t
        lang = user_data.get("language", "tr")

        btn_i18n = {
            # Material scene
            "upload_material": ("material", "var"),
            "skip_material": ("material", "yok"),
            # SAHNE-03
            "format_9_16": ("s03", "vertical"),
            "format_16_9": ("s03", "horizontal"),
            "format_1_1": ("s03", "square"),
            # SAHNE-04
            "resolution_480p": ("s04", "480p"),
            "resolution_720p": ("s04", "720p"),
            "resolution_1080p": ("s04", "1080p"),
            # SAHNE-05
            "duration_hlk": ("s05", "hlk_decides"),
            # SAHNE-06
            "style_ugc": ("s06", "ugc"),
            "style_traditional": ("s06", "traditional"),
            "style_cinematic": ("s06", "cinematic"),
            "style_custom": ("s06", "custom"),
            "style_hlk": ("s06", "hlk_decides"),
            # SAHNE-07
            "audience_0_12": ("s07", "children"),
            "audience_13_17": ("s07", "teen"),
            "audience_18_24": ("s07", "young_adult"),
            "audience_25_34": ("s07", "adult"),
            "audience_35_44": ("s07", "family"),
            "audience_45_54": ("s07", "middle_age"),
            "audience_55_64": ("s07", "mature"),
            "audience_65_plus": ("s07", "senior"),
            # SAHNE-08
            "audio_toggle_voiceover": ("s08", "voiceover"),
            "audio_toggle_ambient": ("s08", "ambient"),
            "audio_toggle_music": ("s08", "music"),
            "audio_toggle_silent": ("s08", "silent"),
            "audio_devam": ("s08", "continue"),
            # SAHNE-10
            "voicechar_female": ("s10", "female"),
            "voicechar_male": ("s10", "male"),
            "voicechar_child": ("s10", "child"),
            # SAHNE-11
            "emphasis_discount": ("s11", "discount"),
            "emphasis_shipping": ("s11", "shipping"),
            "emphasis_gift": ("s11", "gift"),
            "emphasis_newseason": ("s11", "new_season"),
            "emphasis_local": ("s11", "local"),
            "emphasis_custom": ("s11", "custom"),
            "emphasis_done": ("s11", "done"),
        }

        translated = []
        for row in buttons:
            new_row = []
            for btn in row:
                new_btn = dict(btn)
                cb = btn.get("callback_data", "")
                mapped = btn_i18n.get(cb)
                if mapped:
                    section, key = mapped
                    translated_text = t(f"{section}.{key}", lang)
                    if translated_text != f"{section}.{key}":
                        # İkonu koru (varsa)
                        orig_text = btn.get("text", "")
                        if orig_text and orig_text[0] in "📱🖥️🔄🎬👥🎙️🔊🔇🎵🎭✨🏷️🚚🎁🇹🇷✏️":
                            new_btn["text"] = f"{orig_text[0]} {translated_text}" if " " not in orig_text[:3] else translated_text
                        else:
                            new_btn["text"] = translated_text
                new_row.append(new_btn)
            translated.append(new_row)
        return translated

    async def produce_and_deliver(
        self,
        user_data: dict,
        chat_id: int,
        bot,
    ) -> dict:
        """Bir sahneyi üretir ve teslim eder.

        AR-002_28 yaşam döngüsü:
        1. STATE'i belirle
        2. FD-008_1'den sahne kaydını bul
        3. Scene içeriğini oluştur
        4. ScenePayload üret
        5. Delivery'e gönder
        6. Sonucu logla
        """
        se = StateEngine(user_data)
        current_state = se.current
        scene_id = f"scene_{uuid.uuid4().hex[:8]}"

        # ADIM 0: FD-008_1 "EKRAN SİLİNİR" — garantili temizlik
        # 1. user_data'daki bilinen mesaj ID'lerini topla
        extra_ids = set()
        for key in ("material_info_msg_id", "last_material_ack_msg_id",
                     "last_typewriter_msg_id", "audio_scene_msg_id"):
            mid = user_data.pop(key, None)
            if mid:
                extra_ids.add(mid)
        # 2. Her ID'yi silmeyi dene (2 deneme)
        for mid in extra_ids:
            for _ in (1, 2):
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=mid)
                    break
                except Exception as _e:
                    await asyncio.sleep(0.3)
        # 3. Scene Delivery kayıtlı mesajları temizle
        try:
            await scene_delivery.cleanup_chat(chat_id)
        except Exception as e:
            logger.warning(f"⚠️ [SceneEngine] cleanup_chat hatası: {e}")
        logger.info(f"🧹 [SceneEngine] EKRAN SİLİNDİ: chat {chat_id} (+{len(extra_ids)} manuel)")

        log_entry = {
            "scene_id": scene_id,
            "state": current_state.value,
            "steps": [],
        }

        # ADIM 1: STATE'i belirle
        logger.info(f"🎬 [SceneEngine] STATE: {current_state.value}")
        log_entry["steps"].append({"step": "state_determined", "state": current_state.value})

        # ADIM 2: FD-008_1'den sahne kaydını bul
        scene_def = get_scene_for_state(current_state)
        if not scene_def:
            msg = f"FD-008_1'de {current_state.value} için sahne tanımı yok"
            logger.warning(f"⚠️ [SceneEngine] {msg}")
            log_entry["steps"].append({"step": "scene_lookup_failed", "reason": msg})
            self._production_log.append(log_entry)
            return log_entry

        log_entry["scene_name"] = scene_def.scene_name
        log_entry["steps"].append({"step": "scene_found", "scene_name": scene_def.scene_name})
        logger.info(f"🎬 [SceneEngine] Sahne bulundu: {scene_def.scene_name} [{scene_def.scene_id}]")

        # ── ADIM 2.5: Flow Diagram davranışlarını Constitution Cache'ten oku ──
        # FD-008_1: Flow Diagram operasyonel talimatların tek kaynağıdır.
        # MASTER-008: Her görev öncesi anayasal kaynaklar okunur.
        # Scene Engine, sahneyi üretmeden önce aktif sahnenin Flow Diagram
        # davranışlarını Constitution Cache üzerinden alır.
        flow_section = None
        try:
            from services.constitution_cache import constitution_cache
            scene_ref = _STATE_TO_FLOW_SCENE.get(current_state.value)
            if scene_ref:
                flow_section = constitution_cache.get_flow_section(scene_ref)
                if flow_section:
                    log_entry["steps"].append({
                        "step": "flow_diagram_loaded",
                        "scene_ref": scene_ref,
                        "purpose": flow_section.get("purpose"),
                        "presentation_mode": flow_section.get("presentation_mode"),
                    })
                    logger.info(
                        f"📋 [SceneEngine] Flow Diagram yüklendi: {scene_ref} | "
                        f"purpose={flow_section.get('purpose')} | "
                        f"mode={flow_section.get('presentation_mode')} | "
                        f"cleanup={flow_section.get('cleanup_rules')}"
                    )
                else:
                    log_entry["steps"].append({
                        "step": "flow_diagram_missing",
                        "scene_ref": scene_ref,
                    })
                    logger.debug(
                        f"📋 [SceneEngine] {scene_ref} Flow Diagram'da bulunamadı, "
                        f"varsayılan davranış kullanılacak"
                    )
            else:
                logger.debug(
                    f"📋 [SceneEngine] {current_state.value} için Flow Diagram "
                    f"eşleşmesi yok, varsayılan davranış kullanılacak"
                )
        except Exception as e:
            logger.warning(f"⚠️ [SceneEngine] Flow Diagram okuma hatası: {e}")
            log_entry["steps"].append({
                "step": "flow_diagram_error",
                "error": str(e),
            })

        # ADIM 3: Scene içeriğini oluştur
        # FD-008_1: Flow Diagram, HLK'ya sahneyi hatırlatmak içindir.
        # Konuşma metni HLK tarafından oluşturulur, dikte edilmez.
        # SceneDefinition.text = HLK'nın sahne için hazırladığı asıl metin.
        # Flow Diagram speech_directive = yalnızca SceneDefinition yoksa fallback.
        if scene_def and scene_def.text:
            scene_text = scene_def.text
            # AR-002_30: Sahne metnini seçilen dile çevir
            scene_text = self._translate_scene_text(scene_def.scene_id, scene_text, user_data)
            log_entry["steps"].append({
                "step": "content_from_scene_definition",
                "text_length": len(scene_text),
            })
            logger.info(
                f"📋 [SceneEngine] HLK konuşması: {scene_def.scene_name} "
                f"| length={len(scene_text)}"
            )
        elif flow_section and flow_section.get("speech_directive"):
            speech = flow_section["speech_directive"]
            categories = flow_section.get("material_categories", [])
            purpose = flow_section.get("purpose", "")

            if categories:
                cat_lines = "\n".join(f"• {c}" for c in categories)
                scene_text = f"{speech}\n\n{cat_lines}"
            else:
                scene_text = speech

            log_entry["steps"].append({
                "step": "content_from_flow_diagram_fallback",
                "text_length": len(scene_text),
                "purpose": purpose,
            })
            logger.info(
                f"📋 [SceneEngine] Flow Diagram fallback: "
                f"purpose={purpose} | length={len(scene_text)}"
            )
        else:
            scene_text = ""
            log_entry["steps"].append({
                "step": "content_empty",
            })
            logger.warning(
                f"⚠️ [SceneEngine] {scene_def.scene_name if scene_def else '?'} "
                f"için konuşma metni yok"
            )

        # ADIM 3.5: Voice Generation — AR-002_30/31/37
        # voice_enabled=True ise AHU sesi üret, MP3 yolu payload'a ekle
        audio_path = None
        if scene_def.voice_enabled:
            language = user_data.get("language", "tr")
            logger.info(
                f"🔊 [SceneEngine] Voice generation baslatiliyor: "
                f"lang={language}, scene={scene_def.scene_name}"
            )
            try:
                mp3_path = ahu_voice_generator.generate(
                    text=scene_text,
                    language=language,
                )
                if mp3_path and mp3_path.exists():
                    audio_path = str(mp3_path)
                    log_entry["steps"].append({
                        "step": "voice_generated",
                        "language": language,
                        "audio_path": audio_path,
                        "size_bytes": mp3_path.stat().st_size,
                    })
                    logger.info(f"✅ [SceneEngine] AHU sesi hazir: {audio_path}")
                else:
                    log_entry["steps"].append({
                        "step": "voice_failed",
                        "reason": "generate returned None",
                    })
                    logger.warning(f"⚠️ [SceneEngine] AHU sesi uretilemedi")
            except Exception as e:
                log_entry["steps"].append({
                    "step": "voice_failed",
                    "reason": str(e),
                })
                logger.error(f"❌ [SceneEngine] Voice generation hatasi: {e}")
        else:
            log_entry["steps"].append({
                "step": "voice_skipped",
                "reason": "voice_enabled=False",
            })

        # ADIM 4: ScenePayload üret
        payload_metadata = {
            "scene_name": scene_def.scene_name,
            "state": current_state.value,
            "next_state": scene_def.next_state.value if scene_def.next_state else None,
            "trigger_event": scene_def.trigger_event.value if scene_def.trigger_event else None,
            "voice_enabled": scene_def.voice_enabled,
        }
        # Flow Diagram davranışlarını metadata'ya ekle (FD-008_1)
        if flow_section:
            payload_metadata["flow_diagram"] = {
                "scene_id": flow_section.get("scene_id"),
                "presentation_mode": flow_section.get("presentation_mode"),
                "purpose": flow_section.get("purpose"),
                "tone": flow_section.get("tone"),
                "cleanup_rules": flow_section.get("cleanup_rules"),
                "selection_type": flow_section.get("selection_type"),
                "special_behaviors": flow_section.get("special_behaviors"),
            }

        # AR-002_30: Buton metinlerini seçilen dile çevir
        buttons = self._translate_buttons(scene_def.buttons, user_data) if scene_def.buttons else None

        payload = ScenePayload(
            scene_id=scene_id,
            chat_id=chat_id,
            text=scene_text,
            parse_mode=scene_def.parse_mode,
            audio_path=audio_path,
            buttons=buttons,
            metadata=payload_metadata,
        )
        if audio_path:
            _pt = "audio"
        elif payload.video_path or payload.video_file_id:
            _pt = "video"
        else:
            _pt = "text"
        log_entry["steps"].append({
            "step": "payload_created",
            "scene_id": scene_id,
            "payload_type": _pt,
        })
        logger.info(f"🎬 [SceneEngine] Payload oluşturuldu: {scene_id}")

        # ADIM 5: Scene Delivery'e gönder (AR-002_36)
        delivery = scene_delivery
        if not delivery._bot:
            log_entry["steps"].append({"step": "delivery_failed", "reason": "bot_not_bound"})
            log_entry["success"] = False
            self._production_log.append(log_entry)
            logger.error(f"❌ [SceneEngine] Bot bağlı değil, teslim iptal")
            return log_entry

        logger.info(f"🎬 [SceneEngine] Delivery çağrılıyor: {scene_id} → chat:{chat_id}")
        receipt = await delivery.deliver(payload)

        # ADIM 6: Sonucu logla
        log_entry["delivery_status"] = receipt.status.value
        log_entry["message_id"] = receipt.message_id
        log_entry["success"] = (receipt.status == DeliveryStatus.DELIVERED)
        log_entry["steps"].append({
            "step": "delivery_completed",
            "status": receipt.status.value,
            "message_id": receipt.message_id,
        })

        if receipt.status == DeliveryStatus.DELIVERED:
            self._active_scene_id = scene_id
            logger.info(
                f"✅ [SceneEngine] Sahne teslim edildi: {scene_def.scene_name} "
                f"(msg:{receipt.message_id})"
            )
        else:
            logger.error(
                f"❌ [SceneEngine] Sahne teslim edilemedi: {scene_def.scene_name} | "
                f"hata: {receipt.error}"
            )
            log_entry["timeout_started"] = False

        self._production_log.append(log_entry)
        return log_entry

    def get_production_log(self) -> list[dict]:
        """Üretim geçmişini döndürür."""
        return self._production_log

    def get_active_scene_id(self) -> str | None:
        return self._active_scene_id

    def get_last_delivery(self) -> dict | None:
        if not self._production_log:
            return None
        return self._production_log[-1]

    # ── Event Tabanlı Sahne İçi Konuşma Üretimi ─────────────────────────

    async def produce_scene_response(
        self,
        user_data: dict,
        chat_id: int,
        bot,
        trigger_event: str,
        event_context: dict | None = None,
    ) -> dict | None:
        """Kullanıcı event'i sonrası Flow Diagram'dan konuşma üretir.

        Handler'lar artık konuşma üretmez. Bu metod, sahne içi her türlü
        kullanıcı etkileşimi sonrası konuşmayı Flow Diagram'dan okur.

        Args:
            user_data: Kullanıcı oturum verisi
            chat_id: Telegram chat ID
            bot: Telegram bot instance
            trigger_event: Olay adı (örn: "MATERIALS_COLLECTED")
            event_context: Olay bağlamı (örn: {"count": 3, "material_type": "photo"})

        Returns:
            Teslimat log kaydı veya None
        """
        se = StateEngine(user_data)
        current_state = se.current
        scene_id = f"scene_{uuid.uuid4().hex[:8]}"

        log_entry = {
            "scene_id": scene_id,
            "state": current_state.value,
            "trigger_event": trigger_event,
            "steps": [],
        }

        # Flow Diagram'dan aktif sahneyi oku
        flow_section = None
        scene_ref = None
        try:
            from services.constitution_cache import constitution_cache
            scene_ref = _STATE_TO_FLOW_SCENE.get(current_state.value)
            if scene_ref:
                flow_section = constitution_cache.get_flow_section(scene_ref)
        except Exception as e:
            logger.warning(f"⚠️ [SceneEngine] Flow Diagram okuma hatası: {e}")

        # Event'e özel konuşmayı Flow Diagram'dan çıkar
        scene_text = None
        if flow_section:
            raw = flow_section.get("raw_section", "")
            scene_text = self._find_event_speech(raw, trigger_event, event_context)
        # Sahne bölümünde bulunamadıysa sistem event'lerinde ara
        if not scene_text:
            try:
                from services.constitution_cache import constitution_cache
                fd_entry = constitution_cache._entries.get("08_HLK_FLOW_DIAGRAM.md")
                if fd_entry and fd_entry.content:
                    sys_raw = fd_entry.content
                    scene_text = self._find_event_speech(sys_raw, trigger_event, event_context)
            except Exception as _e:
                pass
        if scene_text:
            log_entry["steps"].append({
                "step": "event_speech_from_flow",
                "event": trigger_event,
                "scene_ref": scene_ref,
            })
            logger.info(
                f"📋 [SceneEngine] Event konuşması Flow Diagram'dan: "
                f"event={trigger_event} | scene={scene_ref}"
            )
        else:
            log_entry["steps"].append({
                "step": "event_speech_not_found",
                "event": trigger_event,
            })

        # Fallback: SceneDefinition veya flow_speech_directive
        if not scene_text:
            scene_def = get_scene_for_state(current_state)
            if flow_section and flow_section.get("speech_directive"):
                scene_text = flow_section["speech_directive"]
            elif scene_def:
                scene_text = self._translate_scene_text(scene_def.scene_id, scene_def.text, user_data)
            else:
                logger.warning(f"⚠️ [SceneEngine] Event konuşması üretilemedi: {trigger_event}")
                return None
            log_entry["steps"].append({
                "step": "event_speech_fallback",
                "source": "flow_directive" if (flow_section and flow_section.get("speech_directive")) else "scene_definition",
            })

        # Butonlar: SceneDefinition'dan (state'e göre) + AR-002_30 çeviri
        scene_def = get_scene_for_state(current_state)
        buttons = scene_def.buttons if scene_def else None
        if buttons:
            buttons = self._translate_buttons(buttons, user_data)

        # Payload üret ve teslim et
        payload = ScenePayload(
            scene_id=scene_id,
            chat_id=chat_id,
            text=scene_text,
            parse_mode="HTML",
            buttons=buttons,
            metadata={
                "scene_name": scene_def.scene_name if scene_def else "",
                "state": current_state.value,
                "trigger_event": trigger_event,
                "flow_diagram": {
                    "scene_id": flow_section.get("scene_id"),
                    "purpose": flow_section.get("purpose"),
                } if flow_section else {},
            },
        )

        log_entry["steps"].append({
            "step": "payload_created",
            "scene_id": scene_id,
            "text_length": len(scene_text),
        })

        delivery = scene_delivery
        if not delivery._bot:
            logger.error(f"❌ [SceneEngine] Bot bağlı değil")
            return log_entry

        logger.info(f"🎬 [SceneEngine] Event yanıtı gönderiliyor: {trigger_event} → chat:{chat_id}")
        receipt = await delivery.deliver(payload)

        log_entry["delivery_status"] = receipt.status.value
        log_entry["message_id"] = receipt.message_id
        log_entry["success"] = (receipt.status == DeliveryStatus.DELIVERED)
        log_entry["steps"].append({
            "step": "delivery_completed",
            "status": receipt.status.value,
            "message_id": receipt.message_id,
        })

        if receipt.status == DeliveryStatus.DELIVERED:
            logger.info(f"✅ [SceneEngine] Event yanıtı teslim edildi: msg:{receipt.message_id}")
        else:
            logger.error(f"❌ [SceneEngine] Event yanıtı teslim edilemedi: {receipt.error}")

        self._production_log.append(log_entry)
        return log_entry

    def _find_event_speech(
        self,
        raw_section: str,
        event_name: str,
        context: dict | None = None,
    ) -> str | None:
        """Flow Diagram raw section içinden event'e özel konuşmayı bulur.

        Flow Diagram formatı:
            → EVENT_ADI
            -"Konuşma metni buraya {degisken} ile"

        Args:
            raw_section: Flow Diagram sahne bölümü ham metni
            event_name: Aranan event adı
            context: Değişken substitution için dict

        Returns:
            Konuşma metni veya None
        """
        if not raw_section:
            return None

        marker = f"→ {event_name}"
        idx = raw_section.find(marker)
        if idx == -1:
            return None

        # Marker'dan sonraki satırları al
        rest = raw_section[idx + len(marker):]
        # Windows/Mac/Linux satır sonlarını normalize et
        rest = rest.replace("\r\n", "\n").replace("\r", "\n")
        lines = rest.split("\n")
        speech_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue  # boş satırı atla (önceki: break yapıyordu — \r\n bug'ı)
            if stripped.startswith("→ "):
                break  # sonraki event = bu event'in sonu
            if stripped.startswith("🟦"):
                break  # sonraki sahne
            # Tire ve tırnak temizle
            clean = stripped.lstrip("-").strip()
            if clean.startswith('"') and clean.endswith('"'):
                clean = clean[1:-1]
            elif clean.startswith('"'):
                clean = clean[1:]
            if clean.endswith('"gibi') or clean.endswith('"benzer'):
                clean = clean.rsplit('"', 1)[0].strip('"')
            if clean:
                speech_lines.append(clean)

        if not speech_lines:
            return None

        speech_text = " ".join(speech_lines)
        # Flow Diagram'daki literal \n karakterlerini gerçek satır sonuna çevir
        speech_text = speech_text.replace("\\n", "\n")

        # Değişken substitution
        if context:
            for key, value in context.items():
                speech_text = speech_text.replace(f"{{{key}}}", str(value))

        # Kategori listesi varsa ekle
        if context and "{category_list}" in speech_text:
            cat_list = context.get("category_list", "")
            speech_text = speech_text.replace("{category_list}", cat_list)

        return speech_text


# Global singleton
conversation_scene_engine = ConversationSceneEngine()
