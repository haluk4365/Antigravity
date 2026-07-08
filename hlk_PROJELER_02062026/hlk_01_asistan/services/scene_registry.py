"""
FD-008_1 Flow Diagram — Machine-Readable Scene Registry
Her state için hangi sahnenin gösterileceğini, içeriğini ve geçiş koşullarını tanımlar.
"""

from dataclasses import dataclass, field
from typing import Optional

from utils.state_engine import UserState, UserEvent


@dataclass
class SceneDefinition:
    """FD-008_1: Bir konuşma sahnesinin tanımı."""
    scene_id: str
    scene_name: str
    state: UserState
    text: str
    parse_mode: str = "HTML"
    next_state: Optional[UserState] = None
    trigger_event: Optional[UserEvent] = None
    buttons: list = field(default_factory=list)
    timeout_seconds: int = 300
    voice_enabled: bool = False  # TEXT_ONLY_MODE varsayılan (GC_VOICE_ENABLED=False)


# ─── FD-008_1: Akış Diyagramı Sahne Kayıtları ─────────────────────────────────

SCENE_REGISTRY: list[SceneDefinition] = [

    # SAHNE-01: Tamamlayıcı Materyal Bilgilendirmesi
    SceneDefinition(
        scene_id="scene_collect_materials_info",
        scene_name="Tamamlayıcı Materyal Bilgilendirmesi",
        state=UserState.ACTIVE_CONVERSATION,
        text=(
            "Harika! 🎉 <b>Ürün bilgilerini</b> aldım ve analiz ediyorum.\n\n"
            "Şimdi ürününüzü daha iyi tanımak için <b>bazı detaylara</b> ihtiyacım var.\n\n"
            "Ürününüze ait <b>tamamlayıcı materyalleriniz</b> var mı?\n\n"
            "Örneğin:\n"
            "📷 <b>Fotoğraflar</b> (farklı açılardan)\n"
            "🎬 <b>Videolar</b> (ürün kullanımı)\n"
            "📄 <b>Katalog</b> veya broşür\n"
            "📋 <b>Teknik dökümanlar</b>\n"
            "📦 <b>Diğer materyaller</b>\n\n"
            "Varsa şimdi yükleyebilirsiniz. Yoksa <b>geç butonuna</b> basarak devam edebiliriz."
        ),
        next_state=UserState.COLLECT_PRODUCT_MATERIALS,
        trigger_event=UserEvent.MATERIAL_COLLECTION_COMPLETED,
        buttons=[
            [{"text": "📤 Materyal Yükle", "callback_data": "upload_material"}],
            [{"text": "⏭️ Geç", "callback_data": "skip_material"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-02: Platform Seçimi
    SceneDefinition(
        scene_id="scene_platform_selection",
        scene_name="Platform Seçimi",
        state=UserState.COLLECT_PRODUCT_MATERIALS,
        text=(
            "Teşekkürler! 🙏\n\n"
            "Şimdi reklamınızı hangi <b>platformda</b> yayınlamak istersiniz?\n\n"
            "Size en uygun platformu seçin, reklam stratejinizi ona göre hazırlayalım."
        ),
        next_state=UserState.PLATFORM_SELECTION,
        trigger_event=UserEvent.PLATFORM_SELECTED,
        buttons=[
            [{"text": "🎵 TikTok", "callback_data": "platform_tiktok"}],
            [{"text": "📸 Instagram Reels", "callback_data": "platform_instagram"}],
            [{"text": "▶️ YouTube", "callback_data": "platform_youtube"}],
            [{"text": "🔄 Diğer", "callback_data": "platform_other"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-03: Video Format Seçim Sahnesi (17_SAHNE_KAYIT_DEFTERİ.md uyumlu)
    SceneDefinition(
        scene_id="SAHNE-03",
        scene_name="Video Format Seçim Sahnesi",
        state=UserState.VIDEO_SETTINGS,
        text=(
            "Harika seçim! 🎯\n\n"
            "Sizin için en uygun reklam formatını seçelim.\n\n"
            "Her formatın kullanılabileceği platformlar:\n\n"
            "📱 <b>Dikey 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n"
            "🖥️ <b>Yatay 16:9</b> → YouTube, Facebook\n"
            "🔄 <b>Kare 1:1</b> → Instagram (Feed), Facebook\n\n"
            "Bu üç seçenekten <b>yalnızca birini</b> seçebilirsiniz.\n"
            "Seçtiğiniz formata göre reklam stratejinizi hazırlayacağım.\n\n"
            "Size en uygun olan hangisi?"
        ),
        next_state=UserState.VIDEO_RESOLUTION_SELECTION,
        trigger_event=UserEvent.VIDEO_SETTINGS_DONE,
        buttons=[
            [{"text": "📱 Dikey 9:16", "callback_data": "format_9_16"}],
            [{"text": "🖥️ Yatay 16:9", "callback_data": "format_16_9"}],
            [{"text": "🔄 Kare 1:1", "callback_data": "format_1_1"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-04: Video Çözünürlük Seçim Sahnesi (08_HLK_FLOW_DIAGRAM.md uyumlu)
    SceneDefinition(
        scene_id="SAHNE-04",
        scene_name="Video Çözünürlük Seçim Sahnesi",
        state=UserState.VIDEO_RESOLUTION_SELECTION,
        text=(
            "Teşekkürler! 📺\n\n"
            "Şimdi videonuzun <b>görüntü çözünürlüğünü</b> seçelim.\n\n"
            "<b>🟦 480p</b> — Ekonomik seçenek, temel kullanım\n"
            "<b>🟦 720p HD ⭐</b> — Önerilen, kalite ve bütçe dengesi\n"
            "<b>🟦 1080p Full HD</b> — Daha yüksek kalite, daha yüksek üretim maliyeti\n\n"
            "Hangisini tercih edersiniz?"
        ),
        next_state=UserState.VIDEO_DURATION_SELECTION,
        trigger_event=UserEvent.RESOLUTION_SELECTED,
        buttons=[
            [{"text": "480p — Ekonomik", "callback_data": "resolution_480p"}],
            [{"text": "720p HD ⭐ — Önerilen", "callback_data": "resolution_720p"}],
            [{"text": "1080p Full HD", "callback_data": "resolution_1080p"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-05: Video Süre Seçim Sahnesi (08_HLK_FLOW_DIAGRAM.md:141 uyumlu)
    SceneDefinition(
        scene_id="SAHNE-05",
        scene_name="Video Süre Seçim Sahnesi",
        state=UserState.VIDEO_DURATION_SELECTION,
        text=(
            "Teşekkürler! ⏱️\n\n"
            "Şimdi reklam videonuzun <b>süresini</b> belirleyelim.\n\n"
            "Lütfen istediğiniz video süresini <b>4 ile 30 saniye</b> "
            "arasında olacak şekilde aşağıya yazın.\n\n"
            "<i>Örnek: 15</i>"
        ),
        next_state=UserState.AUDIO_SELECTION,
        trigger_event=UserEvent.DURATION_SELECTED,
        buttons=[
            [{"text": "⭐ HLK'ya Bırak (Önerilen)", "callback_data": "duration_hlk"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-06: Tanıtım Tarzı Seçimi (08_HLK_FLOW_DIAGRAM.md uyumlu)
    SceneDefinition(
        scene_id="SAHNE-06",
        scene_name="Tanıtım Tarzı Seçimi",
        state=UserState.STYLE_SELECTION,
        text=(
            "Teşekkürler! 🎬\n\n"
            "Şimdi videonuzun <b>tanıtım tarzını</b> seçelim.\n\n"
            "<b>☐ UGC Tarzı ⭐</b> — Ürün kullanıcısı gibi, influencer videosu tarzı\n"
            "<b>☐ Geleneksel & Modern</b> — Klasik ve modernin buluşması\n"
            "<b>☐ Sanatsal / Sinematik</b> — Sinematik görsellik odaklı\n"
            "<b>☐ Kendim Yazacağım</b> — Kendi senaryonuzu gönderin\n"
            "<b>☐ HLK'ya Bırak ⭐</b> — Ürüne en uygun tarzı HLK belirlesin\n\n"
            "📌 <b>Tek seçim</b> yapılabilir."
        ),
        next_state=UserState.TARGET_AUDIENCE_SELECTION,
        trigger_event=UserEvent.STYLE_SELECTED,
        buttons=[
            [{"text": "☐ UGC Tarzı ⭐", "callback_data": "style_ugc"}],
            [{"text": "☐ Geleneksel & Modern", "callback_data": "style_traditional"}],
            [{"text": "☐ Sanatsal / Sinematik", "callback_data": "style_cinematic"}],
            [{"text": "☐ Kendim Yazacağım", "callback_data": "style_custom"}],
            [{"text": "☐ HLK'ya Bırak ⭐", "callback_data": "style_hlk"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-07: Hedef Kitle Seçimi (08_HLK_FLOW_DIAGRAM.md uyumlu)
    SceneDefinition(
        scene_id="SAHNE-07",
        scene_name="Hedef Kitle Seçimi",
        state=UserState.TARGET_AUDIENCE_SELECTION,
        text=(
            "Teşekkürler! 👥\n\n"
            "Şimdi reklamınızın <b>hedef kitlesini</b> belirleyelim.\n\n"
            "Ürün tanıtım videonuzun hedef kitlesi aşağıdakilerden hangisidir?\n\n"
            "📌 <b>Tek seçim</b> yapılabilir."
        ),
        next_state=UserState.AUDIO_SELECTION,
        trigger_event=UserEvent.TARGET_AUDIENCE_SELECTED,
        buttons=[
            [{"text": "👶 Çocuk (0-12)", "callback_data": "audience_0_12"}],
            [{"text": "🧒 Genç (13-17)", "callback_data": "audience_13_17"}],
            [{"text": "👦 Genç Yetişkin (18-24)", "callback_data": "audience_18_24"}],
            [{"text": "👨 Yetişkin (25-34)", "callback_data": "audience_25_34"}],
            [{"text": "👪 Aile Kurmuş (35-44)", "callback_data": "audience_35_44"}],
            [{"text": "🧔 Orta Yaş (45-54)", "callback_data": "audience_45_54"}],
            [{"text": "👴 Olgun Yetişkin (55-64)", "callback_data": "audience_55_64"}],
            [{"text": "🧓 65 Yaş ve Üzeri", "callback_data": "audience_65_plus"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-08: Ses Seçim Sahnesi — FD-008_1 uyumlu toggle multi-select
    SceneDefinition(
        scene_id="SAHNE-08",
        scene_name="Ses Seçim Sahnesi",
        state=UserState.AUDIO_SELECTION,
        text=(
            "Teşekkürler! 🎙️\n\n"
            "Şimdi videonuz için <b>ses tercihlerinizi</b> belirleyelim.\n\n"
            "<b>🎙️ Dış Seslendirme</b> — Profesyonel seslendirme sanatçısı\n"
            "<b>🔊 Ortam Sesleri</b> — Doğal arka plan sesleri\n"
            "<b>🎵 Telifsiz Fon Müziği</b> — Arka plan müziği\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "<b>🔇 SESSİZ</b>\n"
            "<i>(Video içerisinde hiçbir ses kullanılmaz)</i>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📌 Birden Fazla Seçim Yapılabilir\n"
            "📌 Sessiz seçilirse diğer seçenekler devre dışı kalır"
        ),
        next_state=UserState.VOICE_LANGUAGE,  # FD-008_1: SAHNE-08 → SAHNE-09
        trigger_event=UserEvent.AUDIO_OPTION_SELECTED,
        buttons=[
            [{"text": "☐ 🎙️ Dış Seslendirme", "callback_data": "audio_toggle_voiceover"}],
            [{"text": "☐ 🔊 Ortam Sesleri", "callback_data": "audio_toggle_ambient"}],
            [{"text": "☐ 🎵 Telifsiz Fon Müziği", "callback_data": "audio_toggle_music"}],
            [{"text": "☐ 🔇 SESSİZ", "callback_data": "audio_toggle_silent"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-09: Seslendirme Dili Seçimi (08_HLK_FLOW_DIAGRAM.md uyumlu)
    SceneDefinition(
        scene_id="SAHNE-09",
        scene_name="Seslendirme Dili Seçimi",
        state=UserState.VOICE_LANGUAGE,
        text=(
            "Teşekkürler! 🎙️\n\n"
            "Şimdi videonuz için <b>seslendirme dilini</b> seçelim.\n\n"
            "Ürün tanıtım videonuz için seslendirme dilini "
            "aşağıdakilerden birini seçerek belirleyebilirsiniz.\n\n"
            "🌍 <b>Yeryüzündeki resmi bütün dillerde</b> seslendirme yapabilirim."
        ),
        next_state=UserState.VOICE_CHARACTER,
        trigger_event=UserEvent.VOICE_LANGUAGE_SELECTED,
        buttons=[
            [
                {"text": "🇹🇷 Türkçe", "callback_data": "voicelang_tr"},
                {"text": "EN English", "callback_data": "voicelang_en"},
            ],
            [
                {"text": "🇩🇪 Deutsch", "callback_data": "voicelang_de"},
                {"text": "🇫🇷 Français", "callback_data": "voicelang_fr"},
            ],
            [
                {"text": "🇪🇸 Español", "callback_data": "voicelang_es"},
                {"text": "🇷🇺 Русский", "callback_data": "voicelang_ru"},
            ],
            [
                {"text": "AR العربية", "callback_data": "voicelang_ar"},
                {"text": "🏳️ Kurdî", "callback_data": "voicelang_kr"},
            ],
            [{"text": "🌍 Farklı Bir Dil Seçeceğim", "callback_data": "voicelang_other"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-10: Ses Karakter Seçimi (08_HLK_FLOW_DIAGRAM.md uyumlu)
    SceneDefinition(
        scene_id="SAHNE-10",
        scene_name="Ses Karakter Seçimi",
        state=UserState.VOICE_CHARACTER,
        text=(
            "Teşekkürler! 🎭\n\n"
            "Şimdi <b>ses karakterini</b> seçelim.\n\n"
            "Ürün tanıtım videonuz için dış ses seçiminizi yapın.\n"
            "<i>Ses yaşı, tonlama, enerji, vurgu ve konuşma ritmi "
            "HLK tarafından belirlenir.</i>"
        ),
        next_state=UserState.EMPHASIS,
        trigger_event=UserEvent.VOICE_CHARACTER_SELECTED,
        buttons=[
            [{"text": "👩 Kadın Ses", "callback_data": "voicechar_female"}],
            [{"text": "👨 Erkek Ses", "callback_data": "voicechar_male"}],
            [{"text": "👶 Çocuk Ses", "callback_data": "voicechar_child"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-11: Vurgulanacaklar Seçimi (08_HLK_FLOW_DIAGRAM.md uyumlu)
    SceneDefinition(
        scene_id="SAHNE-11",
        scene_name="Özellikle Vurgulanacaklar Seçimi",
        state=UserState.EMPHASIS,
        text=(
            "Teşekkürler! ✨\n\n"
            "Videonuzda <b>özellikle vurgulanmasını</b> istediğiniz "
            "bir şey var mı?\n\n"
            "<i>Birden fazla seçim yapabilirsiniz.</i>"
        ),
        next_state=UserState.BRIEF_REVIEW,
        trigger_event=UserEvent.EMPHASIS_SELECTED,
        buttons=[
            [{"text": "☐ 🏷️ İndirim", "callback_data": "emphasis_discount"}],
            [{"text": "☐ 🚚 Ücretsiz Kargo", "callback_data": "emphasis_shipping"}],
            [{"text": "☐ 🎁 Hediye Paket", "callback_data": "emphasis_gift"}],
            [{"text": "☐ ✨ Yeni Sezon", "callback_data": "emphasis_newseason"}],
            [{"text": "☐ 🇹🇷 Yerli Üretim", "callback_data": "emphasis_local"}],
            [{"text": "☐ ✏️ Ben Eklemek istiyorum", "callback_data": "emphasis_custom"}],
            [{"text": "▶️ DEVAM", "callback_data": "emphasis_done"}],
        ],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-12: Brief Onay — REFERANS_Brief_Onay_Formu PNG render (MASTER-010)
    # PNG _deliver_brief_table() tarafından render edilip send_photo ile gönderilir.
    SceneDefinition(
        scene_id="SAHNE-12",
        scene_name="Brief Onay Ekranı",
        state=UserState.BRIEF_REVIEW,
        text="📋 Brief Onayı — REFERANS_Brief_Onay_Formu PNG olarak gönderilir.",
        next_state=UserState.BRIEF_COMPLETED,
        trigger_event=UserEvent.BRIEF_APPROVED,
        buttons=[],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # SAHNE-13: Brief Tamamlandı — FD-008_1 uyumlu (video + senaryo onay geçişi)
    # SAHNE-13'e geçiş _run_sahne13_flow() tarafından yönetilir
    SceneDefinition(
        scene_id="SAHNE-13",
        scene_name="Brief Tamamlandı",
        state=UserState.BRIEF_COMPLETED,
        text=(
            "✅ <b>Brief Tamamlandı!</b>\n\n"
            "Sabrınız için çok teşekkür ederiz. 🙏\n"
            "Ürün tanıtım videonuzun <b>senaryo hazırlıkları</b> başlamıştır.\n\n"
            "Hazırlanan senaryo <b>Senaryo Onay Formu</b> ile "
            "Telegram adresinize birkaç dakika içerisinde gönderilecektir.\n\n"
            "<i>Bol kazançlar dileriz!</i> 🚀"
        ),
        next_state=UserState.SCENARIO_APPROVAL,
        trigger_event=UserEvent.BRIEF_APPROVED,
        buttons=[],
        timeout_seconds=300,
        voice_enabled=False,
    ),

    # Senaryo Onay Formu — REFERANS_SENARYO_ONAY_FORMU.md uyumlu
    SceneDefinition(
        scene_id="scene_scenario_approval",
        scene_name="Senaryo Onay Formu",
        state=UserState.SCENARIO_APPROVAL,
        text=(
            "📝 <b>SENARYO ONAY FORMU</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Reklam senaryonuz hazırlanmıştır.\n"
            "Lütfen aşağıdaki butonlardan birini seçiniz.\n\n"
            "✅ <b>ONAY</b> — Senaryoyu onaylayıp fiyat teklifine geçin\n"
            "❌ <b>RET</b> — Senaryoyu reddedip oturumu sonlandırın"
        ),
        next_state=UserState.PRICING,
        trigger_event=UserEvent.SCENARIO_APPROVED,
        buttons=[
            [{"text": "✅ ONAY", "callback_data": "scenario_approve"}],
            [{"text": "❌ RET", "callback_data": "scenario_reject"}],
        ],
        timeout_seconds=600,
        voice_enabled=False,
    ),
]


def get_scene_for_state(state: UserState) -> Optional[SceneDefinition]:
    """Bir state için tanımlı sahne kaydını döndürür."""
    for scene in SCENE_REGISTRY:
        if scene.state == state:
            return scene
    return None


def get_next_scene(current_state: UserState) -> Optional[SceneDefinition]:
    """Mevcut state'den sonraki sahneyi belirler."""
    scene = get_scene_for_state(current_state)
    if scene and scene.next_state:
        return get_scene_for_state(scene.next_state)
    return None
