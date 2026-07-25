"""
HLK User Conversation State Machine
SE-007_1 — Agent State Classification System
SE-007_2 — Agent State Transition Rules
SE-007_3 — User Conversation State Architecture
SE-007_4 — User Conversation State Transition Rules
SE-007_5 — State Event Trigger Architecture
SE-007_6 — State Action Mapping Architecture

ANA YASA tek yetkili kaynaktır (Single Source of Truth).
Bu dosya, SE-007_3, SE-007_4, SE-007_5 ve 14_OLAY_KAYIT_MERKEZI.md referans
alınarak ANA YASA ile uyumlu hale getirilmiştir.

MASTER-003: ANA YASA Güncellendi + Kod Güncellendi + Runtime Doğrulandı = TAMAMLANDI
"""

import logging
from enum import Enum, auto
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# SE-007_3 — User Conversation State Architecture
# ANA YASA SE-007_3 resmi state listesi ile birebir uyumludur.
# ═══════════════════════════════════════════════════════════════════════════════

class UserState(str, Enum):
    """SE-007_3: Kullanıcı konuşma durumları (ANA YASA resmi listesi)."""

    # ── Oturum Başlangıcı ──
    START = "STATE_START"
    SCENE_1 = "STATE_SCENE_1"           # SAHNE-01: HLK Karşılama Videosu
    LANGUAGE_SELECTION = "STATE_LANGUAGE_SELECTION"
    SCENE_2 = "STATE_SCENE_2"           # SAHNE-02: Dile Özel AHU Lip-Sync Video

    # ── Ürün Linki ──
    WAIT_PRODUCT_LINK = "STATE_WAIT_PRODUCT_LINK"
    LINK_VALIDATION = "STATE_LINK_VALIDATION"
    LINK_VALIDATED = "STATE_LINK_VALIDATED"

    # ── Araştırma ve Brief ──
    BACKGROUND_RESEARCH_RUNNING = "STATE_BACKGROUND_RESEARCH_RUNNING"
    COLLECT_PRODUCT_MATERIALS = "STATE_COLLECT_PRODUCT_MATERIALS"

    # ── Video Yapılandırması (OR-004_2 uyumlu) ──
    PLATFORM_SELECTION = "STATE_PLATFORM_SELECTION"
    VIDEO_RESOLUTION_SELECTION = "STATE_VIDEO_RESOLUTION_SELECTION"
    VIDEO_DURATION_SELECTION = "STATE_VIDEO_DURATION_SELECTION"

    # ── FD-008_1: SAHNE-06 Tanıtım Tarzı + SAHNE-07 Hedef Kitle ──
    STYLE_SELECTION = "STATE_STYLE_SELECTION"             # SAHNE-06
    TARGET_AUDIENCE_SELECTION = "STATE_TARGET_AUDIENCE_SELECTION"  # SAHNE-07

    AUDIO_SELECTION = "STATE_AUDIO_SELECTION"

    # ── Brief Akışı Devamı (SAHNE-09 … SAHNE-12) ──
    VOICE_LANGUAGE = "STATE_VOICE_LANGUAGE"           # SAHNE-09
    VOICE_CHARACTER = "STATE_VOICE_CHARACTER"          # SAHNE-10
    EMPHASIS = "STATE_EMPHASIS"                        # SAHNE-11
    BRIEF_REVIEW = "STATE_BRIEF_REVIEW"                # SAHNE-12

    # ── Onay ve Fiyatlandırma ──
    BRIEF_COMPLETED = "STATE_BRIEF_COMPLETED"
    SCENARIO_APPROVAL = "STATE_SCENARIO_APPROVAL"
    PRICING = "STATE_PRICING"
    PAYMENT_VERIFICATION = "STATE_PAYMENT_VERIFICATION"

    # ── Üretim ve Kapanış ──
    VIDEO_PRODUCTION = "STATE_VIDEO_PRODUCTION"
    SESSION_COMPLETED = "STATE_SESSION_COMPLETED"
    SESSION_TIMEOUT = "STATE_SESSION_TIMEOUT"
    SESSION_CLOSED = "STATE_SESSION_CLOSED"

    # ── CEE: Constitution Enforcement Engine (AR-002_60 / 21_CEE) ──
    CEE_PRE_CHECK = "STATE_CEE_PRE_CHECK"
    CEE_POST_CHECK = "STATE_CEE_POST_CHECK"
    CEE_PASS = "STATE_CEE_PASS"
    CEE_FAIL = "STATE_CEE_FAIL"

    # ──────────────────────────────────────────────────────────────────────
    # Geriye dönük uyumluluk alias'ları
    # Bu isimler ANA YASA SE-007_3'te tanımlı DEĞİLDİR.
    # Yalnızca mevcut handler/scene_registry kodunu bozmamak için korunur.
    # Yeni geliştirmelerde ANA YASA isimleri (yukarıdakiler) kullanılmalıdır.
    # ──────────────────────────────────────────────────────────────────────
    ACTIVE_CONVERSATION = "STATE_ACTIVE_CONVERSATION"
    VIDEO_SETTINGS = "STATE_VIDEO_SETTINGS"


# ═══════════════════════════════════════════════════════════════════════════════
# SE-007_5 — State Event Trigger Architecture
# ANA YASA SE-007_5 ve 14_OLAY_KAYIT_MERKEZI.md ile uyumludur.
# ═══════════════════════════════════════════════════════════════════════════════

class UserEvent(str, Enum):
    """SE-007_5: State değişimini tetikleyen olaylar (ANA YASA resmi listesi)."""

    # ── Oturum Olayları (OLAY-001, OLAY-002) ──
    SESSION_STARTED = "EVENT_SESSION_STARTED"             # OLAY-001
    LANGUAGE_SELECTED = "EVENT_LANGUAGE_SELECTED"          # OLAY-002

    # ── Sahne Tamamlanma Olayları (SE-007_5) ──
    SCENE_1_COMPLETED = "EVENT_SCENE_1_COMPLETED"
    SCENE_2_COMPLETED = "EVENT_SCENE_2_COMPLETED"

    # ── Link Olayları (OLAY-003, OLAY-004, OLAY-005) ──
    PRODUCT_LINK_RECEIVED = "EVENT_PRODUCT_LINK_RECEIVED"       # OLAY-003
    LINK_VALIDATED = "EVENT_PRODUCT_LINK_VALIDATED"             # OLAY-004
    LINK_VALIDATION_FAILED = "EVENT_PRODUCT_LINK_REJECTED"      # OLAY-005

    # ── Araştırma Olayları (OLAY-006) ──
    PRODUCT_ANALYSIS_STARTED = "EVENT_PRODUCT_ANALYSIS_STARTED"  # OLAY-006

    # ── Materyal ve Brief Olayları (SE-007_5) ──
    MATERIAL_REQUEST_STARTED = "EVENT_MATERIAL_REQUEST_STARTED"
    MATERIAL_COLLECTION_COMPLETED = "EVENT_MATERIAL_COLLECTION_COMPLETED"

    # ── Video Yapılandırma Olayları (SE-007_5 / OR-004_2) ──
    PLATFORM_SELECTED = "EVENT_PLATFORM_SELECTED"
    RESOLUTION_SELECTED = "EVENT_RESOLUTION_SELECTED"
    DURATION_SELECTED = "EVENT_DURATION_SELECTED"
    STYLE_SELECTED = "EVENT_STYLE_SELECTED"              # SAHNE-06
    TARGET_AUDIENCE_SELECTED = "EVENT_TARGET_AUDIENCE_SELECTED"  # SAHNE-07
    AUDIO_OPTION_SELECTED = "EVENT_AUDIO_OPTION_SELECTED"

    # ── Brief Devamı Olayları (SAHNE-09 … SAHNE-12) ──
    VOICE_LANGUAGE_SELECTED = "EVENT_VOICE_LANGUAGE_SELECTED"
    VOICE_CHARACTER_SELECTED = "EVENT_VOICE_CHARACTER_SELECTED"
    EMPHASIS_SELECTED = "EVENT_EMPHASIS_SELECTED"

    # ── Brief ve Senaryo Olayları (OLAY-009, OLAY-011, OLAY-012) ──
    BRIEF_COMPLETED = "EVENT_BRIEF_COMPLETED"             # OLAY-009
    BRIEF_APPROVED = "EVENT_BRIEF_APPROVED"
    SCENARIO_APPROVED = "EVENT_SCENARIO_APPROVED"         # OLAY-011
    SCENARIO_REJECTED = "EVENT_SCENARIO_REJECTED"         # OLAY-012

    # ── Fiyatlandırma Olayları (OLAY-014, OLAY-015) ──
    PRICING_APPROVED = "EVENT_PRICE_APPROVED"             # OLAY-014
    PRICING_REJECTED = "EVENT_PRICE_REJECTED"             # OLAY-015

    # ── Ödeme Olayları (OLAY-029, OLAY-030) ──
    PAYMENT_DECLARED = "EVENT_PAYMENT_DECLARED"           # OLAY-029
    PAYMENT_APPROVED = "EVENT_PAYMENT_APPROVED"           # OLAY-030

    # ── Üretim Olayları (OLAY-023, OLAY-024, OLAY-031) ──
    VIDEO_PRODUCTION_STARTED = "EVENT_VIDEO_PRODUCTION_STARTED"    # OLAY-023
    VIDEO_PRODUCTION_COMPLETED = "EVENT_VIDEO_PRODUCTION_COMPLETED"  # OLAY-024
    VIDEO_PRODUCTION_FAILED = "EVENT_VIDEO_PRODUCTION_FAILED"      # Production başarısız
    PRODUCTION_PACKAGE_CREATED = "EVENT_PRODUCTION_PACKAGE_CREATED"  # OLAY-031

    # ── Oturum Kapanış Olayları (OLAY-028) ──
    SESSION_ENDED = "EVENT_SESSION_ENDED"
    TIMEOUT_REACHED = "EVENT_TIMEOUT_REACHED"
    SESSION_CLOSED = "EVENT_SESSION_CLOSED"                # OLAY-028

    # ── Hata / İstisna Olayları ──
    MAX_ATTEMPTS_REACHED = "EVENT_MAX_ATTEMPTS_REACHED"
    RETRY_LINK = "EVENT_RETRY_LINK"
    BRIEF_INCOMPLETE = "EVENT_BRIEF_INCOMPLETE"

    # ── EEC: Execution Event Collector (AR-002_61 / 22_EEC) ──
    TASK_STARTED = "EVENT_TASK_STARTED"
    TASK_CREATED = "EVENT_TASK_CREATED"
    EXECUTOR_ASSIGNED = "EVENT_EXECUTOR_ASSIGNED"
    MASTER_SCAN_STARTED = "EVENT_MASTER_SCAN_STARTED"
    MASTER_SCAN_COMPLETED = "EVENT_MASTER_SCAN_COMPLETED"
    FLOW_SCAN_STARTED = "EVENT_FLOW_SCAN_STARTED"
    FLOW_SCAN_COMPLETED = "EVENT_FLOW_SCAN_COMPLETED"
    STATE_SCAN_STARTED = "EVENT_STATE_SCAN_STARTED"
    STATE_SCAN_COMPLETED = "EVENT_STATE_SCAN_COMPLETED"
    ARCHITECTURE_SCAN_STARTED = "EVENT_ARCHITECTURE_SCAN_STARTED"
    ARCHITECTURE_SCAN_COMPLETED = "EVENT_ARCHITECTURE_SCAN_COMPLETED"
    OPERATIONAL_SCAN_STARTED = "EVENT_OPERATIONAL_SCAN_STARTED"
    OPERATIONAL_SCAN_COMPLETED = "EVENT_OPERATIONAL_SCAN_COMPLETED"
    FILE_OPENED = "EVENT_FILE_OPENED"
    FILE_READ = "EVENT_FILE_READ"
    FILE_UPDATED = "EVENT_FILE_UPDATED"
    FILE_CREATED = "EVENT_FILE_CREATED"
    CODE_ANALYSIS_STARTED = "EVENT_CODE_ANALYSIS_STARTED"
    CODE_ANALYSIS_COMPLETED = "EVENT_CODE_ANALYSIS_COMPLETED"
    CODE_IMPLEMENTATION_STARTED = "EVENT_CODE_IMPLEMENTATION_STARTED"
    CODE_IMPLEMENTATION_COMPLETED = "EVENT_CODE_IMPLEMENTATION_COMPLETED"
    CODE_COMPLETED = "EVENT_CODE_COMPLETED"
    CONSTITUTION_SCAN_STARTED = "EVENT_CONSTITUTION_SCAN_STARTED"
    CONSTITUTION_SCAN_COMPLETED = "EVENT_CONSTITUTION_SCAN_COMPLETED"
    RUNTIME_TEST_STARTED = "EVENT_RUNTIME_TEST_STARTED"
    RUNTIME_TEST_COMPLETED = "EVENT_RUNTIME_TEST_COMPLETED"
    SYNTAX_CHECK_STARTED = "EVENT_SYNTAX_CHECK_STARTED"
    SYNTAX_CHECK_COMPLETED = "EVENT_SYNTAX_CHECK_COMPLETED"

    # ──────────────────────────────────────────────────────────────────────
    # Geriye dönük uyumluluk alias'ları
    # Bu isimler ANA YASA SE-007_5 / OLAY Kayıt Merkezi'nde tanımlı DEĞİLDİR.
    # Yalnızca mevcut handler kodunu bozmamak için korunur.
    # Yeni geliştirmelerde yukarıdaki ANA YASA isimleri kullanılmalıdır.
    # ──────────────────────────────────────────────────────────────────────
    START_INITIATED = "EVENT_START_INITIATED"
    LINK_INVALID = "EVENT_LINK_INVALID"
    RESEARCH_STARTED = "EVENT_RESEARCH_STARTED"
    CONVERSATION_STARTED = "EVENT_CONVERSATION_STARTED"
    MATERIALS_COLLECTED = "EVENT_MATERIALS_COLLECTED"
    VIDEO_SETTINGS_DONE = "EVENT_VIDEO_SETTINGS_DONE"
    VIDEO_PRODUCTION_DONE = "EVENT_VIDEO_PRODUCTION_DONE"


# ═══════════════════════════════════════════════════════════════════════════════
# SE-007_4 — User Conversation State Transition Rules
# ANA YASA SE-007_4 resmi geçiş kuralları ile uyumludur.
# ═══════════════════════════════════════════════════════════════════════════════

STATE_TRANSITIONS: dict[UserState, dict[UserEvent, UserState]] = {

    # ── Oturum Başlangıcı ve Sahne Geçişleri (SE-007_4 Normal Kullanıcı Akışı) ──
    UserState.START: {
        # ANA YASA yolu:
        UserEvent.SESSION_STARTED: UserState.SCENE_1,
        # Geriye dönük uyumluluk (eski kod):
        UserEvent.START_INITIATED: UserState.LANGUAGE_SELECTION,
    },

    UserState.SCENE_1: {
        UserEvent.SCENE_1_COMPLETED: UserState.LANGUAGE_SELECTION,
    },

    UserState.LANGUAGE_SELECTION: {
        # Geriye dönük uyumluluk (çalışan kod bu yolu kullanır).
        # SAHNE-02, handler içerisinde inline olarak yürütüldüğü için
        # StateEngine doğrudan WAIT_PRODUCT_LINK'e geçer.
        # ANA YASA SE-007_4 referansı: LANGUAGE_SELECTION → SCENE_2 → WAIT_PRODUCT_LINK
        UserEvent.LANGUAGE_SELECTED: UserState.WAIT_PRODUCT_LINK,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    UserState.SCENE_2: {
        # ANA YASA SE-007_4: SCENE_2 tamamlandığında ürün linki beklenir
        UserEvent.SCENE_2_COMPLETED: UserState.WAIT_PRODUCT_LINK,
    },

    # ── Ürün Linki (SE-007_4 Link Doğrulama Akışı) ──
    UserState.WAIT_PRODUCT_LINK: {
        UserEvent.PRODUCT_LINK_RECEIVED: UserState.LINK_VALIDATION,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
        UserEvent.MAX_ATTEMPTS_REACHED: UserState.SESSION_CLOSED,
    },

    UserState.LINK_VALIDATION: {
        UserEvent.LINK_VALIDATED: UserState.LINK_VALIDATED,
        UserEvent.LINK_VALIDATION_FAILED: UserState.WAIT_PRODUCT_LINK,
        # Geriye dönük uyumluluk:
        UserEvent.LINK_INVALID: UserState.WAIT_PRODUCT_LINK,
    },

    UserState.LINK_VALIDATED: {
        UserEvent.PRODUCT_ANALYSIS_STARTED: UserState.BACKGROUND_RESEARCH_RUNNING,
        # Geriye dönük uyumluluk:
        UserEvent.RESEARCH_STARTED: UserState.BACKGROUND_RESEARCH_RUNNING,
    },

    # ── Arka Plan Araştırması ve Materyal Toplama (SE-007_4) ──
    UserState.BACKGROUND_RESEARCH_RUNNING: {
        # ANA YASA yolu:
        UserEvent.MATERIAL_REQUEST_STARTED: UserState.COLLECT_PRODUCT_MATERIALS,
        # Geriye dönük uyumluluk (eski kod ACTIVE_CONVERSATION'a geçiyor):
        UserEvent.CONVERSATION_STARTED: UserState.ACTIVE_CONVERSATION,
    },

    # Geriye dönük uyumluluk: ACTIVE_CONVERSATION
    # ANA YASA'da bu state yoktur; COLLECT_PRODUCT_MATERIALS ile birleşmiştir.
    UserState.ACTIVE_CONVERSATION: {
        UserEvent.MATERIAL_COLLECTION_COMPLETED: UserState.COLLECT_PRODUCT_MATERIALS,
        # Geriye dönük uyumluluk:
        UserEvent.MATERIALS_COLLECTED: UserState.COLLECT_PRODUCT_MATERIALS,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    UserState.COLLECT_PRODUCT_MATERIALS: {
        # ANA YASA yolu:
        UserEvent.MATERIAL_COLLECTION_COMPLETED: UserState.PLATFORM_SELECTION,
        # Geriye dönük uyumluluk:
        UserEvent.PLATFORM_SELECTED: UserState.PLATFORM_SELECTION,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    # ── Video Yapılandırması (SE-007_4 + OR-004_2) ──
    UserState.PLATFORM_SELECTION: {
        # ANA YASA yolu:
        UserEvent.PLATFORM_SELECTED: UserState.VIDEO_RESOLUTION_SELECTION,
        # Geriye dönük uyumluluk (eski kod VIDEO_SETTINGS'e geçiyor):
        UserEvent.VIDEO_SETTINGS_DONE: UserState.VIDEO_SETTINGS,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    UserState.VIDEO_RESOLUTION_SELECTION: {
        UserEvent.RESOLUTION_SELECTED: UserState.VIDEO_DURATION_SELECTION,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    UserState.VIDEO_DURATION_SELECTION: {
        UserEvent.DURATION_SELECTED: UserState.STYLE_SELECTION,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    # ── FD-008_1: SAHNE-06 Tanıtım Tarzı + SAHNE-07 Hedef Kitle ──
    UserState.STYLE_SELECTION: {
        UserEvent.STYLE_SELECTED: UserState.TARGET_AUDIENCE_SELECTION,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },
    UserState.TARGET_AUDIENCE_SELECTION: {
        UserEvent.TARGET_AUDIENCE_SELECTED: UserState.AUDIO_SELECTION,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    UserState.AUDIO_SELECTION: {
        UserEvent.AUDIO_OPTION_SELECTED: UserState.VOICE_LANGUAGE,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    # ── Brief Devamı (SAHNE-09 … SAHNE-12) ──
    UserState.VOICE_LANGUAGE: {
        UserEvent.VOICE_LANGUAGE_SELECTED: UserState.VOICE_CHARACTER,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },
    UserState.VOICE_CHARACTER: {
        UserEvent.VOICE_CHARACTER_SELECTED: UserState.EMPHASIS,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },
    UserState.EMPHASIS: {
        UserEvent.EMPHASIS_SELECTED: UserState.BRIEF_REVIEW,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },
    UserState.BRIEF_REVIEW: {
        UserEvent.BRIEF_APPROVED: UserState.BRIEF_COMPLETED,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    # MASTER-003: ANA YASA FD-008_1 — SAHNE-03 → SAHNE-04 geçişi
    # Format seçiminden sonra çözünürlük seçimine geçilir.
    UserState.VIDEO_SETTINGS: {
        UserEvent.VIDEO_SETTINGS_DONE: UserState.VIDEO_RESOLUTION_SELECTION,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    # ── Brief ve Senaryo Onayı (SE-007_4 Senaryo Onay Akışı) ──
    UserState.BRIEF_COMPLETED: {
        # ANA YASA yolu:
        UserEvent.BRIEF_APPROVED: UserState.SCENARIO_APPROVAL,
        # Geriye dönük uyumluluk (eski kod doğrudan VIDEO_PRODUCTION'a):
        UserEvent.VIDEO_PRODUCTION_COMPLETED: UserState.VIDEO_PRODUCTION,
        UserEvent.VIDEO_PRODUCTION_DONE: UserState.VIDEO_PRODUCTION,
        UserEvent.BRIEF_INCOMPLETE: UserState.ACTIVE_CONVERSATION,
        # Ses seçimi ve timeout (log'da tanımsız geçiş hatası veriyordu):
        UserEvent.AUDIO_OPTION_SELECTED: UserState.VOICE_LANGUAGE,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },

    UserState.SCENARIO_APPROVAL: {
        UserEvent.SCENARIO_APPROVED: UserState.PRICING,
        UserEvent.SCENARIO_REJECTED: UserState.SESSION_CLOSED,
    },

    # ── Fiyatlandırma (SE-007_4 Fiyat Teklifi Akışı) ──
    UserState.PRICING: {
        UserEvent.PRICING_APPROVED: UserState.PAYMENT_VERIFICATION,
        UserEvent.PRICING_REJECTED: UserState.SESSION_CLOSED,
    },

    # ── Ödeme Doğrulama (SE-007_4 Ödeme Doğrulama Akışı) ──
    UserState.PAYMENT_VERIFICATION: {
        UserEvent.PAYMENT_APPROVED: UserState.VIDEO_PRODUCTION,
        UserEvent.PAYMENT_DECLARED: UserState.PAYMENT_VERIFICATION,  # Kendi üzerinde kalır
        UserEvent.SESSION_CLOSED: UserState.SESSION_CLOSED,
    },

    # ── Video Üretimi (SE-007_4) ──
    UserState.VIDEO_PRODUCTION: {
        UserEvent.VIDEO_PRODUCTION_COMPLETED: UserState.SESSION_COMPLETED,
        UserEvent.VIDEO_PRODUCTION_FAILED: UserState.SESSION_CLOSED,   # OLAY-025 uyumlu
        UserEvent.SESSION_ENDED: UserState.SESSION_COMPLETED,
        # Geriye dönük uyumluluk:
        UserEvent.VIDEO_PRODUCTION_DONE: UserState.SESSION_COMPLETED,
    },

    # ── Oturum Kapanışı (SE-007_4 Timeout Sonrası Akış) ──
    UserState.SESSION_TIMEOUT: {
        UserEvent.SESSION_CLOSED: UserState.SESSION_CLOSED,
    },

    # ── CEE: Constitution Enforcement Engine (AR-002_60 / 21_CEE) ──
    UserState.CEE_PRE_CHECK: {
        UserEvent.SESSION_STARTED: UserState.CEE_POST_CHECK,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },
    UserState.CEE_POST_CHECK: {
        UserEvent.SESSION_STARTED: UserState.CEE_PASS,
        UserEvent.SESSION_ENDED: UserState.CEE_FAIL,
        UserEvent.TIMEOUT_REACHED: UserState.SESSION_TIMEOUT,
    },
    UserState.CEE_PASS: {
        UserEvent.SESSION_ENDED: UserState.SESSION_COMPLETED,
    },
    UserState.CEE_FAIL: {
        UserEvent.SESSION_STARTED: UserState.CEE_PRE_CHECK,
        UserEvent.SESSION_ENDED: UserState.SESSION_CLOSED,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# SE-007_6 — State Action Mapping Architecture
# ═══════════════════════════════════════════════════════════════════════════════

STATE_ACTION_MAP: dict[UserState, list[str]] = {
    # ── Oturum Başlangıcı ──
    UserState.START: [
        "Session Initialization",
    ],
    UserState.SCENE_1: [
        "SAHNE-01 Karşılama Videosu", "Scene Lock (AR-002_44)",
    ],
    UserState.LANGUAGE_SELECTION: [
        "Language Selection UI",
    ],
    UserState.SCENE_2: [
        "SAHNE-02 Dil Karşılama Videosu", "AHU Lip-Sync",
    ],

    # ── Ürün Linki ──
    UserState.WAIT_PRODUCT_LINK: [
        "Link Input Handler",
    ],
    UserState.LINK_VALIDATION: [
        "Link Validation Orchestrator", "Karar Mekanizması (GK-001_10)",
    ],
    UserState.LINK_VALIDATED: [
        "Ürün Referans Paketi Oluşturma (AR-002_13)",
    ],

    # ── Araştırma ──
    UserState.BACKGROUND_RESEARCH_RUNNING: [
        "Product Research Module", "Brand Research Module",
        "Image Research Module", "Research-Conversation Parallel (AR-002_35)",
    ],

    # ── Materyal Toplama ──
    UserState.ACTIVE_CONVERSATION: [
        "Active Conversation Screen", "Conversation Scene Engine",
        "Daktilo Efekti (TEXT_ONLY_MODE)",
    ],
    UserState.COLLECT_PRODUCT_MATERIALS: [
        "Material Upload Module", "Material Validation Module",
        "Tamamlayıcı Materyal Toplama (OR-003_3/4)",
    ],

    # ── Video Yapılandırması ──
    UserState.PLATFORM_SELECTION: [
        "Platform Selection UI",
    ],
    UserState.VIDEO_RESOLUTION_SELECTION: [
        "Resolution Selection UI",
    ],
    UserState.VIDEO_DURATION_SELECTION: [
        "Duration Selection UI", "Video Süresi Doğrulama (OR-003_8)",
    ],

    # ── FD-008_1: SAHNE-06 Tanıtım Tarzı + SAHNE-07 Hedef Kitle ──
    UserState.STYLE_SELECTION: [
        "Tanıtım Tarzı Seçimi (SAHNE-06)", "Style Selection UI",
    ],
    UserState.TARGET_AUDIENCE_SELECTION: [
        "Hedef Kitle Seçimi (SAHNE-07)", "Target Audience Selection UI",
    ],

    UserState.AUDIO_SELECTION: [
        "Audio Selection UI", "Ses Yapılandırması (OR-004_4)",
    ],

    # ── Brief Devamı (SAHNE-09 … SAHNE-12, FD-008_1 uyumlu) ──
    UserState.VOICE_LANGUAGE: [
        "Seslendirme Dili Seçimi (SAHNE-09)", "Voice Language Selection UI",
    ],
    UserState.VOICE_CHARACTER: [
        "Ses Karakter Seçimi (SAHNE-10)", "Voice Character Selection UI",
    ],
    UserState.EMPHASIS: [
        "Vurgulanacaklar Seçimi (SAHNE-11)", "Emphasis Selection UI",
    ],
    UserState.BRIEF_REVIEW: [
        "Brief Onay Ekranı (SAHNE-12)", "Brief Review UI",
        "Brief Onay (OR-004_5)",
    ],

    UserState.VIDEO_SETTINGS: [
        "Video Settings UI",
    ],

    # ── Onay ve Fiyatlandırma ──
    UserState.BRIEF_COMPLETED: [
        "Brief Summary", "Brief Onay (OR-004_5)",
    ],
    UserState.SCENARIO_APPROVAL: [
        "Senaryo Onay Formu", "Scenario Approval (OR-004_6)",
    ],
    UserState.PRICING: [
        "Yönetici Fiyatlandırma Formu", "Kullanıcı Fiyat Teklif Formu",
        "Pricing (OR-004_7)",
    ],
    UserState.PAYMENT_VERIFICATION: [
        "Yönetici Ödeme Onay Formu", "Payment Verification (OR-004_10)",
    ],

    # ── Üretim ve Kapanış ──
    UserState.VIDEO_PRODUCTION: [
        "PID Generator (AR-002_57)", "Production Package Engine (AR-002_58)",
        "Prompt Builder", "Video Generation Module", "Render Manager",
        "Quality Control (QR-004_4)",
    ],
    UserState.SESSION_COMPLETED: [
        "Session Summary", "Delivery (WF-010)", "Digital Asset Archive",
    ],
    UserState.SESSION_TIMEOUT: [
        "Timeout Notification",
    ],
    UserState.SESSION_CLOSED: [
        "Session Cleanup (OR-004_9)",
    ],

    # ── CEE: Constitution Enforcement Engine (AR-002_60) ──
    UserState.CEE_PRE_CHECK: [
        "Anayasa Maddelerini Topla",
        "Constitutional Task Package (CTP) Oluştur",
        "Executor'a CTP İlet",
    ],
    UserState.CEE_POST_CHECK: [
        "Kod-Anayasa Karşılaştırması (CDE Matrisi)",
        "Flow Diagram Uyumluluk Kontrolü",
        "State Engine Uyumluluk Kontrolü",
        "Operational Rules Uyumluluk Kontrolü",
        "Mimari Bütünlük Kontrolü",
        "Runtime Davranış Doğrulaması",
        "PASS/FAIL Kararı (CEE-004)",
    ],
    UserState.CEE_PASS: [
        "Görev Tamamlandı (MASTER-003)",
        "Sonuç Kalıcı Hale Gelir",
    ],
    UserState.CEE_FAIL: [
        "Enforcement Report Üret",
        "Eksikleri Executor'a Geri Gönder (CEE-002)",
        "Eskalasyon Kontrolü (CEE-005)",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# StateEngine — SE-007_3/4/5/6 uyumlu
# ═══════════════════════════════════════════════════════════════════════════════

class StateEngine:
    """SE-007_3/4/5/6: Kullanıcı Durum Makinesi (User Conversation State Machine)."""

    def __init__(self, user_data: dict):
        self.user_data = user_data
        self._ensure_state()

    def _ensure_state(self):
        if "user_state" not in self.user_data:
            self.user_data["user_state"] = UserState.START.value
        if "state_history" not in self.user_data:
            self.user_data["state_history"] = []
        if "event_history" not in self.user_data:
            self.user_data["event_history"] = []

    @property
    def current(self) -> UserState:
        self._ensure_state()
        return UserState(self.user_data["user_state"])

    @current.setter
    def current(self, state: UserState):
        self._ensure_state()
        self.user_data["user_state"] = state.value

    def get_event_history(self) -> list:
        return self.user_data.get("event_history", [])

    def fire(self, event: UserEvent) -> Optional[UserState]:
        """SE-007_5: Bir event tetikler, geçiş varsa uygular."""
        self._ensure_state()
        current_state = self.current

        transitions = STATE_TRANSITIONS.get(current_state, {})
        next_state = transitions.get(event)

        if next_state is None:
            logger.warning(
                f"⛔ Geçiş engellendi: {current_state.value} ---[{event.value}]--> ? "
                f"(tanımlı geçiş yok)"
            )
            self.user_data["event_history"].append({
                "event": event.value, "from": current_state.value,
                "to": None, "status": "blocked",
            })
            return None

        old_state = self.current
        self.current = next_state

        self.user_data["state_history"].append({
            "from": old_state.value, "to": next_state.value, "event": event.value,
        })
        self.user_data["event_history"].append({
            "event": event.value, "from": old_state.value,
            "to": next_state.value, "status": "applied",
        })

        logger.info(f"🔄 STATE: {old_state.value} --[{event.value}]--> {next_state.value}")

        modules = STATE_ACTION_MAP.get(next_state, [])
        if modules:
            logger.info(f"⚙️  [{next_state.value}] aktif modüller: {', '.join(modules)}")

        return next_state

    def can_transition(self, event: UserEvent) -> bool:
        """Belirtilen event'in geçerli state'de geçiş yapıp yapamayacağını kontrol eder."""
        transitions = STATE_TRANSITIONS.get(self.current, {})
        return event in transitions

    def get_allowed_events(self) -> list[UserEvent]:
        """Mevcut state'de tetiklenebilecek event'leri döndürür."""
        transitions = STATE_TRANSITIONS.get(self.current, {})
        return list(transitions.keys())

    def get_active_modules(self) -> list[str]:
        """SE-007_6: Mevcut state için aktif modülleri döndürür."""
        return STATE_ACTION_MAP.get(self.current, [])

    def reset(self):
        """Oturumu baştan başlatır."""
        self.user_data["user_state"] = UserState.START.value
        self.user_data["state_history"] = []
        self.user_data["event_history"] = []
        logger.info("🔄 STATE: Oturum sıfırlandı")
