"""
HLK i18n — Çoklu Dil Desteği (AR-002_30 uyumlu)
Kullanıcının SAHNE-01'de seçtiği dile göre tüm metinleri döndürür.

Kullanım:
    from config.i18n import t
    msg = t("scene_03.title", lang)  # "Video Formatı Seçimi"
"""
from typing import Optional

FALLBACK = "tr"

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-03: Video Format Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
S03 = {
    "title": {
        "tr": "Video Formatı Seçimi",
        "en": "Video Format Selection",
        "de": "Videoformat Auswahl",
        "fr": "Sélection du Format Vidéo",
        "es": "Selección de Formato de Video",
        "ar": "اختيار تنسيق الفيديو",
        "ru": "Выбор Формата Видео",
        "kr": "Hilbijartina Formatê Vîdyoyê",
    },
    "prompt": {
        "tr": "Harika seçim! 🎯\n\nSizin için en uygun reklam formatını seçelim.\n\nHer formatın kullanılabileceği platformlar:\n\n📱 <b>Dikey 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n🖥️ <b>Yatay 16:9</b> → YouTube, Facebook\n🔄 <b>Kare 1:1</b> → Instagram (Feed), Facebook\n\nBu üç seçenekten <b>yalnızca birini</b> seçebilirsiniz.\nSeçtiğiniz formata göre reklam stratejinizi hazırlayacağım.\n\nSize en uygun olan hangisi?",
        "en": "Great choice! 🎯\n\nLet's choose the best ad format for you.\n\nPlatforms available for each format:\n\n📱 <b>Vertical 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n🖥️ <b>Horizontal 16:9</b> → YouTube, Facebook\n🔄 <b>Square 1:1</b> → Instagram (Feed), Facebook\n\nYou can select <b>only one</b> of these three options.\nI'll prepare your ad strategy based on your chosen format.\n\nWhich one suits you best?",
        "de": "Tolle Wahl! 🎯\n\nLassen Sie uns das beste Anzeigenformat wählen.\n\nVerfügbare Plattformen pro Format:\n\n📱 <b>Hochformat 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n🖥️ <b>Querformat 16:9</b> → YouTube, Facebook\n🔄 <b>Quadrat 1:1</b> → Instagram (Feed), Facebook\n\nSie können <b>nur eine</b> dieser drei Optionen wählen.\n\nWelche passt am besten zu Ihnen?",
        "fr": "Excellent choix ! 🎯\n\nChoisissons le meilleur format publicitaire pour vous.\n\nPlateformes disponibles par format :\n\n📱 <b>Vertical 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n🖥️ <b>Horizontal 16:9</b> → YouTube, Facebook\n🔄 <b>Carré 1:1</b> → Instagram (Feed), Facebook\n\nVous ne pouvez sélectionner <b>qu'une seule</b> option.\n\nLaquelle vous convient le mieux ?",
        "es": "¡Gran elección! 🎯\n\nElijamos el mejor formato de anuncio para ti.\n\nPlataformas disponibles por formato:\n\n📱 <b>Vertical 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n🖥️ <b>Horizontal 16:9</b> → YouTube, Facebook\n🔄 <b>Cuadrado 1:1</b> → Instagram (Feed), Facebook\n\nSolo puedes seleccionar <b>una</b> de estas tres opciones.\n\n¿Cuál te conviene más?",
        "ar": "اختيار رائع! 🎯\n\nلنختر أفضل تنسيق إعلان لك.\n\nالمنصات المتاحة لكل تنسيق:\n\n📱 <b>عمودي 9:16</b> → تلغرام، تيك توك، انستغرام ريلز، يوتيوب شورتس\n🖥️ <b>أفقي 16:9</b> → يوتيوب، فيسبوك\n🔄 <b>مربع 1:1</b> → انستغرام (فيد)، فيسبوك\n\nيمكنك اختيار <b>خيار واحد فقط</b> من هذه الخيارات الثلاثة.\n\nأيها يناسبك أكثر؟",
        "ru": "Отличный выбор! 🎯\n\nДавайте выберем лучший формат рекламы для вас.\n\nДоступные платформы для каждого формата:\n\n📱 <b>Вертикальный 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n🖥️ <b>Горизонтальный 16:9</b> → YouTube, Facebook\n🔄 <b>Квадрат 1:1</b> → Instagram (Feed), Facebook\n\nВы можете выбрать <b>только один</b> из этих трёх вариантов.\n\nКакой вам подходит больше всего?",
        "kr": "Hilbijartineke bas! 🎯\n\nJi bo we formata reklame ya heri bas hilbijerin.\n\nPlatformen ji bo her formate:\n\n📱 <b>Vertical 9:16</b> → Telegram, TikTok, Instagram Reels, YouTube Shorts\n🖥️ <b>Horizontal 16:9</b> → YouTube, Facebook\n🔄 <b>Square 1:1</b> → Instagram (Feed), Facebook\n\nHu ji van hersē vebijarkan <b>tenē yekē</b> dikarin hilbijerin.\n\nKijan ji we re heri bas e?",
    },
    "vertical": {
        "tr": "Dikey 9:16",
        "en": "Vertical 9:16",
        "de": "Hochformat 9:16",
        "fr": "Vertical 9:16",
        "es": "Vertical 9:16",
        "ar": "عمودي 9:16",
        "ru": "Вертикальный 9:16",
        "kr": "Vertical 9:16",
    },
    "vertical_desc": {
        "tr": "TikTok, Reels, Shorts",
        "en": "TikTok, Reels, Shorts",
        "de": "TikTok, Reels, Shorts",
        "fr": "TikTok, Reels, Shorts",
        "es": "TikTok, Reels, Shorts",
        "ar": "تيك توك، ريلز، شورتس",
        "ru": "TikTok, Reels, Shorts",
        "kr": "TikTok, Reels, Shorts",
    },
    "horizontal": {
        "tr": "Yatay 16:9",
        "en": "Horizontal 16:9",
        "de": "Querformat 16:9",
        "fr": "Horizontal 16:9",
        "es": "Horizontal 16:9",
        "ar": "أفقي 16:9",
        "ru": "Горизонтальный 16:9",
        "kr": "Horizontal 16:9",
    },
    "horizontal_desc": {
        "tr": "YouTube, Web Sitesi",
        "en": "YouTube, Website",
        "de": "YouTube, Webseite",
        "fr": "YouTube, Site Web",
        "es": "YouTube, Sitio Web",
        "ar": "يوتيوب، موقع إلكتروني",
        "ru": "YouTube, Веб-сайт",
        "kr": "YouTube, Malper",
    },
    "square": {
        "tr": "Kare 1:1",
        "en": "Square 1:1",
        "de": "Quadrat 1:1",
        "fr": "Carré 1:1",
        "es": "Cuadrado 1:1",
        "ar": "مربع 1:1",
        "ru": "Квадрат 1:1",
        "kr": "Çargoşe 1:1",
    },
    "square_desc": {
        "tr": "Instagram, Facebook",
        "en": "Instagram, Facebook",
        "de": "Instagram, Facebook",
        "fr": "Instagram, Facebook",
        "es": "Instagram, Facebook",
        "ar": "انستغرام، فيسبوك",
        "ru": "Instagram, Facebook",
        "kr": "Instagram, Facebook",
    },
    "single_choice": {
        "tr": "Tek Seçim Yapılabilir",
        "en": "Single Choice Only",
        "de": "Nur eine Auswahl möglich",
        "fr": "Un seul choix possible",
        "es": "Solo una opción",
        "ar": "اختيار واحد فقط",
        "ru": "Только один выбор",
        "kr": "Tenê yek Hilbijartin",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-04: Video Çözünürlük Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
S04 = {
    "title": {
        "tr": "Video Çözünürlük Seçimi",
        "en": "Video Resolution Selection",
        "de": "Videoauflösung Auswahl",
        "fr": "Sélection de la Résolution Vidéo",
        "es": "Selección de Resolución de Video",
        "ar": "اختيار دقة الفيديو",
        "ru": "Выбор Разрешения Видео",
        "kr": "Hilbijartina Resolutiona Vîdyoyê",
    },
    "prompt": {
        "tr": "Teşekkürler! 📺\n\nŞimdi videonuzun <b>görüntü çözünürlüğünü</b> seçelim.\n\n<b>🟦 480p</b> — <i>Ekonomik seçenek, temel kullanım</i>\n<b>🟦 720p HD ⭐</b> — <i>Önerilen, kalite ve bütçe dengesi</i>\n<b>🟦 1080p Full HD</b> — <i>Daha yüksek kalite, daha yüksek üretim maliyeti</i>\n\nHangisini tercih edersiniz?",
        "en": "Thanks! 📺\n\nLet's choose your <b>video resolution</b>.\n\n<b>480p</b> — <i>Budget option, basic use</i>\n<b>720p HD ⭐</b> — <i>Recommended, quality-budget balance</i>\n<b>1080p Full HD</b> — <i>Higher quality, higher cost</i>\n\nWhich do you prefer?",
        "de": "Welche Auflösung möchten Sie für Ihr Produktvideo?",
        "fr": "Quelle résolution souhaitez-vous pour votre vidéo produit?",
        "es": "¿Qué resolución quieres para tu video de producto?",
        "ar": "ما الدقة التي تريدها لفيديو منتجك؟",
        "ru": "Какое разрешение вы хотите для видео вашего продукта?",
        "kr": "Kîjan resolutionê ji bo vîdyoya hilberîna xwe dixwazin?",
    },
    "480p": {"tr": "480p", "en": "480p", "de": "480p", "fr": "480p", "es": "480p", "ar": "480p", "ru": "480p", "kr": "480p"},
    "480p_desc": {
        "tr": "Ekonomik seçenek, temel kullanım",
        "en": "Budget option, basic use",
        "de": "Günstige Option, einfache Nutzung",
        "fr": "Option économique, usage basique",
        "es": "Opción económica, uso básico",
        "ar": "خيار اقتصادي، استخدام أساسي",
        "ru": "Эконом вариант, базовое использование",
        "kr": "Vebijêrka aborî, bikaranîna bingehîn",
    },
    "720p": {"tr": "720p HD ⭐", "en": "720p HD ⭐", "de": "720p HD ⭐", "fr": "720p HD ⭐", "es": "720p HD ⭐", "ar": "720p HD ⭐", "ru": "720p HD ⭐", "kr": "720p HD ⭐"},
    "720p_desc": {
        "tr": "Önerilen — Kalite ve bütçe dengesi",
        "en": "Recommended — Quality & budget balance",
        "de": "Empfohlen — Qualität & Budget Balance",
        "fr": "Recommandé — Équilibre qualité/budget",
        "es": "Recomendado — Equilibrio calidad/precio",
        "ar": "موصى به — توازن الجودة والميزانية",
        "ru": "Рекомендуется — Баланс качества и бюджета",
        "kr": "Pêşniyarkirî — Hevsengiya kalîte & budceyê",
    },
    "1080p": {"tr": "1080p Full HD", "en": "1080p Full HD", "de": "1080p Full HD", "fr": "1080p Full HD", "es": "1080p Full HD", "ar": "1080p Full HD", "ru": "1080p Full HD", "kr": "1080p Full HD"},
    "1080p_desc": {
        "tr": "Daha yüksek kalite, daha yüksek maliyet",
        "en": "Higher quality, higher cost",
        "de": "Höhere Qualität, höhere Kosten",
        "fr": "Qualité supérieure, coût plus élevé",
        "es": "Mayor calidad, mayor costo",
        "ar": "جودة أعلى، تكلفة أعلى",
        "ru": "Выше качество, выше стоимость",
        "kr": "Kalîteya bilindtir, lêçûna bilindtir",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-05: Video Süre Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
S05 = {
    "title": {
        "tr": "Video Süresi",
        "en": "Video Duration",
        "de": "Videodauer",
        "fr": "Durée de la Vidéo",
        "es": "Duración del Video",
        "ar": "مدة الفيديو",
        "ru": "Длительность Видео",
        "kr": "Dirêjahiya Vîdyoyê",
    },
    "prompt": {
        "tr": "Teşekkürler! ⏱️\n\nŞimdi reklam videonuzun <b>süresini</b> belirleyelim.\n\nLütfen istediğiniz video süresini <b>4 ile 30 saniye</b> arasında olacak şekilde aşağıya yazın.\n\n<i>Örnek: 15</i>",
        "en": "Thanks! ⏱️\n\nLet's set your <b>video duration</b>.\n\nPlease enter a duration between <b>4 and 30 seconds</b>.\n\n<i>Example: 15</i>",
        "de": "Legen wir die Dauer Ihres Werbevideos fest. Bitte geben Sie eine Dauer zwischen 4 und 30 Sekunden ein.",
        "fr": "Déterminons la durée de votre vidéo publicitaire. Veuillez entrer une durée entre 4 et 30 secondes.",
        "es": "Establezcamos la duración de tu video. Ingresa una duración entre 4 y 30 segundos.",
        "ar": "لنحدد مدة فيديو إعلانك. يرجى إدخال مدة بين 4 و 30 ثانية.",
        "ru": "Давайте установим длительность вашего рекламного видео. Введите значение от 4 до 30 секунд.",
        "kr": "Em dirêjahiya vîdyoya reklama we diyar bikin. Ji kerema xwe navbera 4 û 30 çirkeyan binivîsin.",
    },
    "hlk_decides": {
        "tr": "HLK'ya Bırak ⭐ (En uygun süreyi HLK belirler)",
        "en": "Let HLK Decide ⭐ (HLK determines optimal duration)",
        "de": "HLK entscheiden lassen ⭐ (HLK bestimmt optimale Dauer)",
        "fr": "Laisser HLK décider ⭐ (HLK détermine la durée optimale)",
        "es": "Dejar que HLK decida ⭐ (HLK determina duración óptima)",
        "ar": "دع HLK يقرر ⭐ (HLK يحدد المدة المثلى)",
        "ru": "Пусть HLK решит ⭐ (HLK определяет оптимальную длительность)",
        "kr": "Bihêle HLK Biryar Bide ⭐ (HLK dirêjahiya çêtirîn diyar dike)",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-06: Tanıtım Tarzı Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
S06 = {
    "title": {
        "tr": "Tanıtım Tarzı Seçimi",
        "en": "Ad Style Selection",
        "de": "Werbestil Auswahl",
        "fr": "Sélection du Style Publicitaire",
        "es": "Selección de Estilo de Anuncio",
        "ar": "اختيار نمط الإعلان",
        "ru": "Выбор Стиля Рекламы",
        "kr": "Hilbijartina Şêwaza Reklamê",
    },
    "prompt": {
        "tr": "Teşekkürler! 🎬\n\nŞimdi videonuzun <b>tanıtım tarzını</b> seçelim.\n\n<b>☐ UGC Tarzı ⭐</b> — <i>Ürün kullanıcısı gibi, influencer tarzı</i>\n<b>☐ Geleneksel & Modern</b> — <i>Klasik ve modernin buluşması</i>\n<b>☐ Sanatsal / Sinematik</b> — <i>Sinematik görsellik odaklı</i>\n<b>☐ Kendim Yazacağım</b> — <i>Kendi senaryonuzu gönderin</i>\n<b>☐ HLK'ya Bırak ⭐</b> — <i>Ürüne en uygun tarzı HLK belirlesin</i>\n\n📌 <b>Tek seçim</b> yapılabilir.",
        "en": "Thanks! 🎬\n\nLet's choose your <b>video style</b>.\n\n<b>UGC Style ⭐</b> — <i>Influencer-style, natural</i>\n<b>Traditional & Modern</b> — <i>Classic meets modern</i>\n<b>Cinematic</b> — <i>Cinematic visuals</i>\n<b>I'll Write My Own</b> — <i>Send your own script</i>\n<b>HLK Decides ⭐</b> — <i>HLK picks the best style</i>\n\n📌 <b>Single choice</b> only.",
        "de": "Welchen Stil möchten Sie für Ihr Produktvideo?",
        "fr": "Quel style souhaitez-vous pour votre vidéo produit?",
        "es": "¿Qué estilo quieres para tu video de producto?",
        "ar": "ما النمط الذي تريده لفيديو منتجك؟",
        "ru": "Какой стиль вы хотите для видео вашего продукта?",
        "kr": "Kîjan şêwazê ji bo vîdyoya hilberîna xwe dixwazin?",
    },
    "ugc": {
        "tr": "UGC Tarzı ⭐ (Kullanıcı gibi, influencer videosu)",
        "en": "UGC Style ⭐ (User-generated, influencer style)",
        "de": "UGC-Stil ⭐ (Nutzer-generiert, Influencer-Stil)",
        "fr": "Style UGC ⭐ (Style utilisateur, influenceur)",
        "es": "Estilo UGC ⭐ (Estilo usuario, influencer)",
        "ar": "نمط UGC ⭐ (نمط المستخدم، مؤثر)",
        "ru": "UGC Стиль ⭐ (Пользовательский, стиль блогера)",
        "kr": "Şêwaza UGC ⭐ (Bikarhêner, şêwaza influencer)",
    },
    "traditional": {
        "tr": "Geleneksel & Modern",
        "en": "Traditional & Modern",
        "de": "Traditionell & Modern",
        "fr": "Traditionnel & Moderne",
        "es": "Tradicional & Moderno",
        "ar": "تقليدي وعصري",
        "ru": "Традиционный & Современный",
        "kr": "Kevneşopî & Modern",
    },
    "cinematic": {
        "tr": "Sanatsal / Sinematik",
        "en": "Artistic / Cinematic",
        "de": "Künstlerisch / Kinoreif",
        "fr": "Artistique / Cinématique",
        "es": "Artístico / Cinematográfico",
        "ar": "فني / سينمائي",
        "ru": "Художественный / Кинематографичный",
        "kr": "Hunerî / Sînemayî",
    },
    "custom": {
        "tr": "Kendim Yazacağım",
        "en": "I'll Write My Own",
        "de": "Ich schreibe selbst",
        "fr": "Je vais écrire moi-même",
        "es": "Lo escribiré yo mismo",
        "ar": "سأكتب بنفسي",
        "ru": "Напишу сам",
        "kr": "Ez ê bi xwe binivîsim",
    },
    "hlk_decides": {
        "tr": "HLK'ya Bırak ⭐ (En uygun tarzı HLK belirler)",
        "en": "Let HLK Decide ⭐ (HLK determines best style)",
        "de": "HLK entscheiden lassen ⭐ (HLK bestimmt besten Stil)",
        "fr": "Laisser HLK décider ⭐ (HLK détermine le meilleur style)",
        "es": "Dejar que HLK decida ⭐ (HLK determina el mejor estilo)",
        "ar": "دع HLK يقرر ⭐ (HLK يحدد أفضل نمط)",
        "ru": "Пусть HLK решит ⭐ (HLK определяет лучший стиль)",
        "kr": "Bihêle HLK Biryar Bide ⭐",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-07: Hedef Kitle Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
S07 = {
    "title": {
        "tr": "Hedef Kitle Seçimi",
        "en": "Target Audience Selection",
        "de": "Zielgruppe Auswahl",
        "fr": "Sélection du Public Cible",
        "es": "Selección de Público Objetivo",
        "ar": "اختيار الجمهور المستهدف",
        "ru": "Выбор Целевой Аудитории",
        "kr": "Hilbijartina Armanca Temaşevanan",
    },
    "prompt": {
        "tr": "Teşekkürler! 👥\n\nŞimdi reklamınızın <b>hedef kitlesini</b> belirleyelim.\n\nÜrün tanıtım videonuzun hedef kitlesi aşağıdakilerden hangisidir?\n\n📌 <b>Tek seçim</b> yapılabilir.",
        "en": "Thanks! 👥\n\nLet's define your <b>target audience</b>.\n\nWho is your product video for?\n\n📌 <b>Single choice</b> only.",
        "de": "Wer ist die Zielgruppe für Ihr Produktvideo?",
        "fr": "Quel est le public cible de votre vidéo produit?",
        "es": "¿Cuál es el público objetivo de tu video?",
        "ar": "من هو الجمهور المستهدف لفيديو منتجك؟",
        "ru": "Кто является целевой аудиторией для видео вашего продукта?",
        "kr": "Armanca temaşevanên vîdyoya hilberîna we kî ye?",
    },
    "children": {"tr": "Çocuk (0-12)", "en": "Children (0-12)", "de": "Kinder (0-12)", "fr": "Enfants (0-12)", "es": "Niños (0-12)", "ar": "أطفال (0-12)", "ru": "Дети (0-12)", "kr": "Zarok (0-12)"},
    "teen": {"tr": "Genç (13-17)", "en": "Teens (13-17)", "de": "Jugendliche (13-17)", "fr": "Ados (13-17)", "es": "Adolescentes (13-17)", "ar": "مراهقون (13-17)", "ru": "Подростки (13-17)", "kr": "Ciwan (13-17)"},
    "young_adult": {"tr": "Genç Yetişkin (18-24)", "en": "Young Adult (18-24)", "de": "Junge Erwachsene (18-24)", "fr": "Jeune Adulte (18-24)", "es": "Adulto Joven (18-24)", "ar": "شباب (18-24)", "ru": "Молодые взрослые (18-24)", "kr": "Ciwanên Mezin (18-24)"},
    "adult": {"tr": "Yetişkin (25-34)", "en": "Adult (25-34)", "de": "Erwachsene (25-34)", "fr": "Adulte (25-34)", "es": "Adulto (25-34)", "ar": "بالغ (25-34)", "ru": "Взрослые (25-34)", "kr": "Mezin (25-34)"},
    "family": {"tr": "Aile Kurmuş (35-44)", "en": "Family (35-44)", "de": "Familie (35-44)", "fr": "Famille (35-44)", "es": "Familia (35-44)", "ar": "أسرة (35-44)", "ru": "Семейные (35-44)", "kr": "Malbat (35-44)"},
    "middle_age": {"tr": "Orta Yaş (45-54)", "en": "Middle Age (45-54)", "de": "Mittleres Alter (45-54)", "fr": "Âge Moyen (45-54)", "es": "Mediana Edad (45-54)", "ar": "متوسط العمر (45-54)", "ru": "Средний возраст (45-54)", "kr": "Temenê Navîn (45-54)"},
    "mature": {"tr": "Olgun (55-64)", "en": "Mature (55-64)", "de": "Reif (55-64)", "fr": "Mûr (55-64)", "es": "Maduro (55-64)", "ar": "ناضج (55-64)", "ru": "Зрелые (55-64)", "kr": "Gihiştî (55-64)"},
    "senior": {"tr": "65 Yaş ve Üzeri", "en": "65 and Above", "de": "65 und älter", "fr": "65 ans et plus", "es": "65 y más", "ar": "65 وما فوق", "ru": "65 и старше", "kr": "65 û Jor"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-08: Ses Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
S08 = {
    "title": {
        "tr": "Ses Tercihleri",
        "en": "Audio Preferences",
        "de": "Audio Einstellungen",
        "fr": "Préférences Audio",
        "es": "Preferencias de Audio",
        "ar": "تفضيلات الصوت",
        "ru": "Настройки Звука",
        "kr": "Vebijêrkên Deng",
    },
    "prompt": {
        "tr": "Teşekkürler! 🎙️\n\nŞimdi videonuz için <b>ses tercihlerinizi</b> belirleyelim.\n\n<b>🎙️ Dış Seslendirme</b> — <i>Profesyonel seslendirme</i>\n<b>🔊 Ortam Sesleri</b> — <i>Doğal arka plan sesleri</i>\n<b>🎵 Telifsiz Fon Müziği</b> — <i>Arka plan müziği</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 SESSİZ</b>\n<i>(Video içerisinde hiçbir ses kullanılmaz)</i>\n━━━━━━━━━━━━━━━━━━\n📌 Birden Fazla Seçim Yapılabilir\n📌 Sessiz seçilirse diğer seçenekler devre dışı kalır",
        "en": "Thanks! 🎙️\n\nLet's set your <b>audio preferences</b>.\n\n<b>🎙️ Voiceover</b> — <i>Professional narration</i>\n<b>🔊 Ambient Sounds</b> — <i>Natural background</i>\n<b>🎵 Background Music</b> — <i>Royalty-free music</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 SILENT</b>\n<i>(No audio in video)</i>\n━━━━━━━━━━━━━━━━━━\n📌 Multiple selections allowed\n📌 Silent disables all other options",
        "de": "Was sind Ihre Audio-Einstellungen für das Produktvideo?",
        "fr": "Quelles sont vos préférences audio pour la vidéo?",
        "es": "¿Cuáles son tus preferencias de audio para el video?",
        "ar": "ما هي تفضيلات الصوت لفيديو المنتج؟",
        "ru": "Каковы ваши настройки звука для видео продукта?",
        "kr": "Vebijêrkên deng ji bo vîdyoya hilberînê çi ne?",
    },
    "voiceover": {"tr": "Dış Seslendirme", "en": "Voiceover", "de": "Voiceover", "fr": "Voix Off", "es": "Voz en Off", "ar": "تعليق صوتي", "ru": "Озвучка", "kr": "Dengê Derveyî"},
    "ambient": {"tr": "Ortam Sesleri", "en": "Ambient Sounds", "de": "Umgebungsgeräusche", "fr": "Sons d'Ambiance", "es": "Sonidos Ambiente", "ar": "أصوات محيطة", "ru": "Фоновые звуки", "kr": "Dengên Derûdorê"},
    "music": {"tr": "Telifsiz Fon Müziği", "en": "Royalty-Free Music", "de": "Lizenzfreie Musik", "fr": "Musique Libre de Droits", "es": "Música Sin Royalties", "ar": "موسيقى بدون حقوق", "ru": "Бесплатная фоновая музыка", "kr": "Muzîka Bêheq"},
    "silent": {"tr": "Sessiz", "en": "Silent", "de": "Stumm", "fr": "Silencieux", "es": "Silencioso", "ar": "صامت", "ru": "Без звука", "kr": "Bêdeng"},
    "multi_choice": {
        "tr": "Birden Fazla Seçim Yapılabilir",
        "en": "Multiple Choices Allowed",
        "de": "Mehrfachauswahl möglich",
        "fr": "Choix multiples possibles",
        "es": "Se permiten múltiples opciones",
        "ar": "يسمح باختيارات متعددة",
        "ru": "Можно выбрать несколько",
        "kr": "Gelek Hilbijartin Mumkin e",
    },
    "continue": {"tr": "DEVAM", "en": "CONTINUE", "de": "WEITER", "fr": "CONTINUER", "es": "CONTINUAR", "ar": "متابعة", "ru": "ПРОДОЛЖИТЬ", "kr": "BIDOMÎNE"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-09: Seslendirme Dili
# ═══════════════════════════════════════════════════════════════════════════════
S09 = {
    "title": {
        "tr": "Seslendirme Dili Seçimi",
        "en": "Voice Language Selection",
        "de": "Sprachauswahl für Voiceover",
        "fr": "Sélection de la Langue de la Voix",
        "es": "Selección de Idioma de Voz",
        "ar": "اختيار لغة التعليق الصوتي",
        "ru": "Выбор Языка Озвучки",
        "kr": "Hilbijartina Zimanê Deng",
    },
    "prompt": {
        "tr": "Teşekkürler! 🎙️\n\nŞimdi videonuz için <b>seslendirme dilini</b> seçelim.\n\nÜrün tanıtım videonuz için seslendirme dilini aşağıdakilerden birini seçerek belirleyebilirsiniz.\n\n🌍 <b>Yeryüzündeki resmi bütün dillerde</b> seslendirme yapabilirim.",
        "en": "Thanks! 🎙️\n\nLet's choose your <b>voiceover language</b>.\n\nSelect from the options below.\n\n🌍 I can voice in <b>all official languages</b>.",
        "de": "Bitte wählen Sie die Voiceover-Sprache für Ihr Produktvideo.",
        "fr": "Veuillez sélectionner la langue de la voix off pour votre vidéo.",
        "es": "Selecciona el idioma de voz para tu video de producto.",
        "ar": "يرجى اختيار لغة التعليق الصوتي لفيديو منتجك.",
        "ru": "Пожалуйста, выберите язык озвучки для видео вашего продукта.",
        "kr": "Ji kerema xwe zimanê deng ji bo vîdyoya hilberîna xwe hilbijêrin.",
    },
    "other_lang": {"tr": "Farklı Bir Dil Seçeceğim", "en": "I'll Choose Another Language", "de": "Ich wähle eine andere Sprache", "fr": "Je vais choisir une autre langue", "es": "Elegiré otro idioma", "ar": "سأختار لغة أخرى", "ru": "Я выберу другой язык", "kr": "Ez ê zimanekî din hilbijêrim"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-10: Ses Karakter Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
S10 = {
    "title": {
        "tr": "Ses Karakteri Seçimi",
        "en": "Voice Character Selection",
        "de": "Stimmcharakter Auswahl",
        "fr": "Sélection du Personnage Vocal",
        "es": "Selección de Personaje de Voz",
        "ar": "اختيار شخصية الصوت",
        "ru": "Выбор Голосового Персонажа",
        "kr": "Hilbijartina Karakterê Deng",
    },
    "prompt": {
        "tr": "Teşekkürler! 🎭\n\nŞimdi <b>ses karakterini</b> seçelim.\n\nÜrün tanıtım videonuz için dış ses seçiminizi yapın.\n<i>Ses yaşı, tonlama, enerji, vurgu ve konuşma ritmi HLK tarafından belirlenir.</i>",
        "en": "Thanks! 🎭\n\nLet's choose your <b>voice character</b>.\n\nSelect the voice for your video.\n<i>Tone, energy, and rhythm are set by HLK.</i>",
        "de": "Wählen Sie Ihren Stimmcharakter. Ton, Energie und Rhythmus werden von HLK bestimmt.",
        "fr": "Sélectionnez votre personnage vocal. Le ton, l'énergie et le rythme sont déterminés par HLK.",
        "es": "Selecciona tu personaje de voz. El tono, energía y ritmo los determina HLK.",
        "ar": "اختر شخصية الصوت. النغمة والطاقة والإيقاع يحددها HLK.",
        "ru": "Выберите голосового персонажа. Тон, энергия и ритм определяются HLK.",
        "kr": "Karakterê dengê xwe hilbijêrin. Ton, enerjî û rîtm ji hêla HLK ve tê diyarkirin.",
    },
    "female": {"tr": "Kadın Ses", "en": "Female Voice", "de": "Weibliche Stimme", "fr": "Voix Féminine", "es": "Voz Femenina", "ar": "صوت أنثوي", "ru": "Женский голос", "kr": "Dengê Jin"},
    "male": {"tr": "Erkek Ses", "en": "Male Voice", "de": "Männliche Stimme", "fr": "Voix Masculine", "es": "Voz Masculina", "ar": "صوت ذكوري", "ru": "Мужской голос", "kr": "Dengê Mêr"},
    "child": {"tr": "Çocuk Ses", "en": "Child Voice", "de": "Kinderstimme", "fr": "Voix d'Enfant", "es": "Voz Infantil", "ar": "صوت طفل", "ru": "Детский голос", "kr": "Dengê Zarok"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-11: Vurgulanacaklar
# ═══════════════════════════════════════════════════════════════════════════════
S11 = {
    "title": {
        "tr": "Vurgulanacak Detaylar",
        "en": "Details to Highlight",
        "de": "Hervorzuhebende Details",
        "fr": "Détails à Souligner",
        "es": "Detalles a Destacar",
        "ar": "تفاصيل للتأكيد عليها",
        "ru": "Детали для выделения",
        "kr": "Detayên ku Dê Bên Diyarkirin",
    },
    "prompt": {
        "tr": "Teşekkürler! ✨\n\nVideonuzda <b>özellikle vurgulanmasını</b> istediğiniz bir şey var mı?\n\n<i>Birden fazla seçim yapabilirsiniz.</i>",
        "en": "Thanks! ✨\n\nAnything you'd like <b>especially highlighted</b> in your video?\n\n<i>Multiple selections allowed.</i>",
        "de": "Gibt es etwas, das wir in Ihrem Video besonders hervorheben sollen?",
        "fr": "Y a-t-il quelque chose que vous souhaitez particulièrement mettre en avant?",
        "es": "¿Hay algo que quieras que destaquemos especialmente en tu video?",
        "ar": "هل هناك شيء تريد منا تسليط الضوء عليه بشكل خاص في الفيديو؟",
        "ru": "Есть ли что-то, что вы хотите особенно выделить в видео?",
        "kr": "Tiştek heye ku hûn dixwazin em di vîdyoya we de bi taybetî diyar bikin?",
    },
    "discount": {"tr": "İndirim", "en": "Discount", "de": "Rabatt", "fr": "Réduction", "es": "Descuento", "ar": "خصم", "ru": "Скидка", "kr": "Daxistin"},
    "shipping": {"tr": "Ücretsiz Kargo", "en": "Free Shipping", "de": "Kostenloser Versand", "fr": "Livraison Gratuite", "es": "Envío Gratis", "ar": "شحن مجاني", "ru": "Бесплатная доставка", "kr": "Posteya Belaş"},
    "gift": {"tr": "Hediye Paketi", "en": "Gift Package", "de": "Geschenkpaket", "fr": "Coffret Cadeau", "es": "Paquete de Regalo", "ar": "حزمة هدايا", "ru": "Подарочный набор", "kr": "Pakêta Diyarî"},
    "new_season": {"tr": "Yeni Sezon", "en": "New Season", "de": "Neue Saison", "fr": "Nouvelle Saison", "es": "Nueva Temporada", "ar": "موسم جديد", "ru": "Новый сезон", "kr": "Sezona Nû"},
    "local": {"tr": "Yerli Üretim", "en": "Local Production", "de": "Lokale Produktion", "fr": "Production Locale", "es": "Producción Local", "ar": "إنتاج محلي", "ru": "Местное производство", "kr": "Hilberîna Herêmî"},
    "custom": {"tr": "Ben Eklemek İstiyorum", "en": "I Want to Add Something", "de": "Ich möchte etwas hinzufügen", "fr": "Je veux ajouter quelque chose", "es": "Quiero añadir algo", "ar": "أريد إضافة شيء", "ru": "Я хочу добавить", "kr": "Ez dixwazim tiştekî zêde bikim"},
    "custom_prompt": {
        "tr": "Lütfen eklemek istediğiniz detayı birkaç kelime ile belirtiniz.",
        "en": "Please describe the detail you'd like to add in a few words.",
        "de": "Bitte beschreiben Sie das Detail, das Sie hinzufügen möchten, in wenigen Worten.",
        "fr": "Veuillez décrire le détail que vous souhaitez ajouter en quelques mots.",
        "es": "Describe el detalle que quieres añadir en pocas palabras.",
        "ar": "يرجى وصف التفاصيل التي تريد إضافتها بكلمات قليلة.",
        "ru": "Опишите деталь, которую хотите добавить, в нескольких словах.",
        "kr": "Ji kerema xwe detayê ku dixwazin zêde bikin bi çend peyvan vebêjin.",
    },
    "done": {"tr": "DEVAM", "en": "CONTINUE", "de": "WEITER", "fr": "CONTINUER", "es": "CONTINUAR", "ar": "متابعة", "ru": "ПРОДОЛЖИТЬ", "kr": "BIDOMÎNE"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-12: Brief Onay
# ═══════════════════════════════════════════════════════════════════════════════
S12 = {
    "title": {
        "tr": "BRIEF ONAY FORMU",
        "en": "BRIEF APPROVAL FORM",
        "de": "BRIEF-BESTÄTIGUNGSFORMULAR",
        "fr": "FORMULAIRE D'APPROBATION DU BRIEF",
        "es": "FORMULARIO DE APROBACIÓN DEL BRIEF",
        "ar": "نموذج الموافقة على الموجز",
        "ru": "ФОРМА УТВЕРЖДЕНИЯ БРИФА",
        "kr": "FORMULA PEJIRANDINA KURTE",
    },
    "summary_title": {
        "tr": "BRIEF ÖZETİ",
        "en": "BRIEF SUMMARY",
        "de": "BRIEF-ZUSAMMENFASSUNG",
        "fr": "RÉSUMÉ DU BRIEF",
        "es": "RESUMEN DEL BRIEF",
        "ar": "ملخص الموجز",
        "ru": "КРАТКИЙ ОБЗОР",
        "kr": "KURTEYA KURT",
    },
    "summary_text": {
        "tr": "Şimdiye kadar verdiğiniz tüm bilgiler aşağıda özetlenmiştir.",
        "en": "All the information you've provided so far is summarized below.",
        "de": "Alle bisherigen Angaben sind unten zusammengefasst.",
        "fr": "Toutes les informations fournies sont résumées ci-dessous.",
        "es": "Toda la información proporcionada se resume a continuación.",
        "ar": "جميع المعلومات التي قدمتها ملخصة أدناه.",
        "ru": "Вся предоставленная информация кратко изложена ниже.",
        "kr": "Hemû agahiyên ku we daye li jêr têne kurt kirin.",
    },
    "approve": {"tr": "ONAYLA", "en": "APPROVE", "de": "BESTÄTIGEN", "fr": "APPROUVER", "es": "APROBAR", "ar": "موافقة", "ru": "УТВЕРДИТЬ", "kr": "PEJIRANDIN"},
    "edit": {"tr": "DÜZELT", "en": "EDIT", "de": "BEARBEITEN", "fr": "MODIFIER", "es": "EDITAR", "ar": "تعديل", "ru": "РЕДАКТИРОВАТЬ", "kr": "SERERASTKIRIN"},
    "edit_title": {
        "tr": "Brief Düzeltme Modu",
        "en": "Brief Edit Mode",
        "de": "Brief-Bearbeitungsmodus",
        "fr": "Mode Édition du Brief",
        "es": "Modo Edición del Brief",
        "ar": "وضع تعديل الموجز",
        "ru": "Режим Редактирования Брифа",
        "kr": "Moda Sererastkirina Kurte",
    },
    "edit_prompt": {
        "tr": "Değiştirmek istediğiniz alana tıklayın, ilgili adıma yönlendirileceksiniz. Düzenleme sonrası bu ekrana geri döneceksiniz.",
        "en": "Click the field you want to change, you'll be redirected to that step. You'll return here after editing.",
        "de": "Klicken Sie auf das zu ändernde Feld. Nach der Bearbeitung kehren Sie hierher zurück.",
        "fr": "Cliquez sur le champ à modifier. Vous reviendrez ici après l'édition.",
        "es": "Haz clic en el campo a cambiar. Volverás aquí después de editar.",
        "ar": "انقر على الحقل الذي تريد تغييره. ستعود إلى هنا بعد التعديل.",
        "ru": "Нажмите на поле для изменения. Вы вернетесь сюда после редактирования.",
        "kr": "Li ser qada ku dixwazin biguherînin bikirtînin. Piştî sererastkirinê hûn ê vegerin vir.",
    },
    "edit_done": {"tr": "DÜZENLEME TAMAM", "en": "EDITING DONE", "de": "BEARBEITUNG FERTIG", "fr": "ÉDITION TERMINÉE", "es": "EDICIÓN COMPLETA", "ar": "اكتمل التعديل", "ru": "РЕДАКТИРОВАНИЕ ЗАВЕРШЕНО", "kr": "SERERASTKIRIN QEDÎYA"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-13: Brief Tamamlandı
# ═══════════════════════════════════════════════════════════════════════════════
S13 = {
    "brief_completed": {
        "tr": "Brief Tamamlandı!",
        "en": "Brief Completed!",
        "de": "Brief Abgeschlossen!",
        "fr": "Brief Terminé!",
        "es": "¡Brief Completado!",
        "ar": "تم إكمال الموجز!",
        "ru": "Бриф Завершен!",
        "kr": "Kurte Qedîya!",
    },
    "thank_you": {
        "tr": "Sabrınız için çok teşekkür ederiz. Ürün tanıtım videonuzun senaryo hazırlıkları başlamıştır.",
        "en": "Thank you for your patience. The script preparations for your product video have begun.",
        "de": "Vielen Dank für Ihre Geduld. Die Drehbuchvorbereitungen haben begonnen.",
        "fr": "Merci de votre patience. Les préparatifs du script ont commencé.",
        "es": "Gracias por tu paciencia. Las preparaciones del guion han comenzado.",
        "ar": "شكرا لصبرك. بدأت تحضيرات السيناريو.",
        "ru": "Спасибо за терпение. Подготовка сценария началась.",
        "kr": "Spas ji bo bîhna we. Amadekariyên senaryoyê dest pê kirin.",
    },
    "scenario_coming": {
        "tr": "Hazırlanan senaryo Senaryo Onay Formu ile Telegram adresinize birkaç dakika içerisinde gönderilecektir.",
        "en": "The prepared script will be sent to your Telegram address within a few minutes with the Scenario Approval Form.",
        "de": "Das vorbereitete Skript wird in wenigen Minuten mit dem Szenario-Bestätigungsformular an Ihre Telegram-Adresse gesendet.",
        "fr": "Le script préparé sera envoyé à votre adresse Telegram dans quelques minutes avec le formulaire d'approbation.",
        "es": "El guion preparado se enviará a tu dirección de Telegram en unos minutos con el formulario de aprobación.",
        "ar": "سيتم إرسال السيناريو المعد إلى عنوان تلغرام الخاص بك في غضون دقائق مع نموذج الموافقة.",
        "ru": "Подготовленный сценарий будет отправлен на ваш Telegram в течение нескольких минут с формой утверждения.",
        "kr": "Senaryoya amadekirî dê di nav çend hûrdeman de bi Formula Pejirandinê re ji navnîşana weya Telegramê re were şandin.",
    },
    "good_luck": {
        "tr": "Bol kazançlar dileriz!",
        "en": "We wish you great profits!",
        "de": "Wir wünschen Ihnen viel Erfolg!",
        "fr": "Nous vous souhaitons beaucoup de succès!",
        "es": "¡Te deseamos mucho éxito!",
        "ar": "نتمنى لك أرباحًا وفيرة!",
        "ru": "Желаем вам больших прибылей!",
        "kr": "Em ji we re qezencên mezin dixwazin!",
    },
    "scenario_ready": {
        "tr": "<b>📝 Senaryonuz</b> hazırlandı, <i>form hazırlanıyor...</i>",
        "en": "<b>📝 Your script</b> is ready, <i>preparing the form...</i>",
        "de": "Skript ist fertig, Formular wird vorbereitet...",
        "fr": "Script prêt, préparation du formulaire...",
        "es": "Guion listo, preparando formulario...",
        "ar": "السيناريو جاهز، جاري تحضير النموذج...",
        "ru": "Сценарий готов, подготавливаем форму...",
        "kr": "Senaryo amade ye, form tê amadekirin...",
    },
    "approve": {"tr": "ONAY", "en": "APPROVE", "de": "BESTÄTIGEN", "fr": "APPROUVER", "es": "APROBAR", "ar": "موافقة", "ru": "УТВЕРДИТЬ", "kr": "PEJIRANDIN"},
    "reject": {"tr": "RET", "en": "REJECT", "de": "ABLEHNEN", "fr": "REFUSER", "es": "RECHAZAR", "ar": "رفض", "ru": "ОТКЛОНИТЬ", "kr": "REDKIRIN"},
    "reject_msg": {
        "tr": "Senaryoyu onaylamadığınızı görüyorum. Yeni bir reklam çalışması başlatmak için lütfen tekrar /start komutu ile giriş yapınız.",
        "en": "I see you didn't approve the script. To start a new ad project, please use the /start command again.",
        "de": "Sie haben das Skript nicht genehmigt. Für ein neues Projekt nutzen Sie bitte erneut /start.",
        "fr": "Vous n'avez pas approuvé le script. Pour un nouveau projet, utilisez à nouveau /start.",
        "es": "Veo que no aprobaste el guion. Para un nuevo proyecto, usa /start de nuevo.",
        "ar": "أرى أنك لم توافق على السيناريو. لبدء مشروع جديد، استخدم /start مرة أخرى.",
        "ru": "Вы не утвердили сценарий. Для нового проекта используйте /start снова.",
        "kr": "Ez dibînim ku we senaryo pejirand. Ji bo projeyek nû, ji kerema xwe dîsa /start bikar bînin.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# Ortak Butonlar / Genel
# ═══════════════════════════════════════════════════════════════════════════════
COMMON = {
    "continue_btn": {"tr": "DEVAM", "en": "CONTINUE", "de": "WEITER", "fr": "CONTINUER", "es": "CONTINUAR", "ar": "متابعة", "ru": "ПРОДОЛЖИТЬ", "kr": "BIDOMÎNE"},
    "yes": {"tr": "EVET", "en": "YES", "de": "JA", "fr": "OUI", "es": "SÍ", "ar": "نعم", "ru": "ДА", "kr": "ERÊ"},
    "no": {"tr": "HAYIR", "en": "NO", "de": "NEIN", "fr": "NON", "es": "NO", "ar": "لا", "ru": "НЕТ", "kr": "NA"},
    "done": {"tr": "Bitti", "en": "Done", "de": "Fertig", "fr": "Terminé", "es": "Hecho", "ar": "تم", "ru": "Готово", "kr": "Qedîya"},
    "screen_cleared": {"tr": "EKRAN SİLİNİR", "en": "SCREEN CLEARED", "de": "BILDSCHIRM GELÖSCHT", "fr": "ÉCRAN EFFACÉ", "es": "PANTALLA LIMPIADA", "ar": "تم مسح الشاشة", "ru": "ЭКРАН ОЧИЩЕН", "kr": "EKran Paqij Bû"},
    "saved": {"tr": "Seçiminiz kaydedildi.", "en": "Your selection has been saved.", "de": "Ihre Auswahl wurde gespeichert.", "fr": "Votre sélection a été enregistrée.", "es": "Tu selección ha sido guardada.", "ar": "تم حفظ اختيارك.", "ru": "Ваш выбор сохранен.", "kr": "Hilbijartina we hate tomar kirin."},
}

# ═══════════════════════════════════════════════════════════════════════════════
# Fiyat Teklif Formu
# ═══════════════════════════════════════════════════════════════════════════════
PRICING = {
    "title": {
        "tr": "HLK AI ASISTAN FİYAT TEKLİFİ",
        "en": "HLK AI ASSISTANT PRICE OFFER",
        "de": "HLK AI ASSISTENT PREISANGEBOT",
        "fr": "HLK AI ASSISTANT OFFRE DE PRIX",
        "es": "HLK AI ASISTENTE OFERTA DE PRECIO",
        "ar": "عرض سعر مساعد HLK AI",
        "ru": "HLK AI АССИСТЕНТ ЦЕНОВОЕ ПРЕДЛОЖЕНИЕ",
        "kr": "PÊŞNIYARA BIHAYÊ ASISTANÊ HLK AI",
    },
    "service_scope": {
        "tr": "Hizmet Kapsamı",
        "en": "Service Scope",
        "de": "Leistungsumfang",
        "fr": "Périmètre de Service",
        "es": "Alcance del Servicio",
        "ar": "نطاق الخدمة",
        "ru": "Объем Услуг",
        "kr": "Qada Xizmetê",
    },
    "kdv_dollar": {
        "tr": "KDV'li Dolar Tutarı",
        "en": "USD Amount (Inc. VAT)",
        "de": "USD-Betrag (inkl. MwSt.)",
        "fr": "Montant USD (TTC)",
        "es": "Importe USD (IVA incl.)",
        "ar": "المبلغ بالدولار (شامل الضريبة)",
        "ru": "Сумма в USD (с НДС)",
        "kr": "Mîqdara USD (VAT tê de)",
    },
    "tcmb_rate": {"tr": "TCMB Döviz Satış", "en": "TCMB Exchange Rate", "de": "TCMB Wechselkurs", "fr": "Taux de Change TCMB", "es": "Tipo de Cambio TCMB", "ar": "سعر صرف البنك المركزي", "ru": "Курс ЦБ", "kr": "Rêjeya Danûstandinê TCMB"},
    "sales_price": {
        "tr": "SATIŞ FİYATI",
        "en": "SALES PRICE",
        "de": "VERKAUFSPREIS",
        "fr": "PRIX DE VENTE",
        "es": "PRECIO DE VENTA",
        "ar": "سعر البيع",
        "ru": "ПРОДАЖНАЯ ЦЕНА",
        "kr": "BIHAYA FROTINÊ",
    },
    "footer_1": {
        "tr": "Ödeme alındıktan sonra üretim başlar.",
        "en": "Production begins after payment is received.",
        "de": "Die Produktion beginnt nach Zahlungseingang.",
        "fr": "La production commence après réception du paiement.",
        "es": "La producción comienza tras recibir el pago.",
        "ar": "يبدأ الإنتاج بعد استلام الدفع.",
        "ru": "Производство начинается после получения оплаты.",
        "kr": "Hilberîn piştî wergirtina drav dest pê dike.",
    },
    "footer_2": {
        "tr": "Onay sonrası ödeme ekranına yönlendirileceksiniz.",
        "en": "After approval, you will be directed to the payment screen.",
        "de": "Nach der Bestätigung werden Sie zum Zahlungsbildschirm weitergeleitet.",
        "fr": "Après approbation, vous serez dirigé vers l'écran de paiement.",
        "es": "Tras la aprobación, serás dirigido a la pantalla de pago.",
        "ar": "بعد الموافقة، ستتم إعادة توجيهك إلى شاشة الدفع.",
        "ru": "После утверждения вы будете перенаправлены на экран оплаты.",
        "kr": "Piştî pejirandinê, hûn ê ber bi ekrana dravdanê ve bêne birin.",
    },
    "approve_btn": {"tr": "Teklifi Onayla", "en": "Approve Offer", "de": "Angebot bestätigen", "fr": "Approuver l'offre", "es": "Aprobar Oferta", "ar": "الموافقة على العرض", "ru": "Утвердить предложение", "kr": "Pêşniyarê bipejirînin"},
    "reject_btn": {"tr": "Reddet", "en": "Reject", "de": "Ablehnen", "fr": "Refuser", "es": "Rechazar", "ar": "رفض", "ru": "Отклонить", "kr": "Redkirin"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# Ödeme Kartı / Banka Bilgileri
# ═══════════════════════════════════════════════════════════════════════════════
PAYMENT = {
    "card_title": {
        "tr": "HLK BANKA ÖDEME BİLGİLERİ KARTI",
        "en": "HLK BANK PAYMENT DETAILS CARD",
        "de": "HLK BANKZAHLUNGSDATEN-KARTE",
        "fr": "CARTE DE PAIEMENT BANCAIRE HLK",
        "es": "TARJETA DE PAGO BANCARIO HLK",
        "ar": "بطاقة معلومات الدفع المصرفي HLK",
        "ru": "БАНКОВСКАЯ ПЛАТЕЖНАЯ КАРТА HLK",
        "kr": "KARTA AGAHIYÊN DRAVDANA BANKÊ HLK",
    },
    "account_holder": {"tr": "HESAP SAHİBİ", "en": "ACCOUNT HOLDER", "de": "KONTOINHABER", "fr": "TITULAIRE DU COMPTE", "es": "TITULAR DE LA CUENTA", "ar": "صاحب الحساب", "ru": "ВЛАДЕЛЕЦ СЧЕТА", "kr": "XWEDÎ HESABÊ"},
    "payment_method": {"tr": "Ödeme Yöntemi", "en": "Payment Method", "de": "Zahlungsmethode", "fr": "Méthode de Paiement", "es": "Método de Pago", "ar": "طريقة الدفع", "ru": "Способ Оплаты", "kr": "Rêbaza Dravdanê"},
    "bank_transfer": {"tr": "Banka Havalesi / EFT", "en": "Bank Transfer / EFT", "de": "Banküberweisung / EFT", "fr": "Virement Bancaire", "es": "Transferencia Bancaria", "ar": "حوالة بنكية", "ru": "Банковский Перевод", "kr": "Transfera Bankê / EFT"},
    "warning_title": {"tr": "ÖNEMLİ UYARI", "en": "IMPORTANT NOTICE", "de": "WICHTIGER HINWEIS", "fr": "AVIS IMPORTANT", "es": "AVISO IMPORTANTE", "ar": "تنبيه هام", "ru": "ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ", "kr": "HIŞYARIYA GIRÎNG"},
    "warning_1": {
        "tr": "Ödemeniz alındıktan sonra üretim süreci başlar.",
        "en": "Production begins after your payment is received.",
        "de": "Die Produktion beginnt nach Zahlungseingang.",
        "fr": "La production commence après réception de votre paiement.",
        "es": "La producción comienza tras recibir su pago.",
        "ar": "يبدأ الإنتاج بعد استلام دفعتك.",
        "ru": "Производство начинается после получения оплаты.",
        "kr": "Hilberîn piştî wergirtina dravê we dest pê dike.",
    },
    "warning_2": {
        "tr": "Video belirtilen süre içerisinde adresinize dijital Mp4 formatında teslim edilir.",
        "en": "The video will be delivered to you digitally in Mp4 format within the specified time.",
        "de": "Das Video wird innerhalb der angegebenen Zeit digital im Mp4-Format geliefert.",
        "fr": "La vidéo vous sera livrée numériquement au format Mp4 dans le délai spécifié.",
        "es": "El video se entregará digitalmente en formato Mp4 dentro del plazo especificado.",
        "ar": "سيتم تسليم الفيديو رقميًا بصيغة Mp4 خلال الوقت المحدد.",
        "ru": "Видео будет доставлено в цифровом формате Mp4 в указанные сроки.",
        "kr": "Vîdyo dê di wextê diyarkirî de bi formata Mp4 ji we re were şandin.",
    },
    "warning_3": {
        "tr": "Onayınız sonrası süreç otomatik olarak başlar.",
        "en": "The process starts automatically after your approval.",
        "de": "Der Prozess startet automatisch nach Ihrer Bestätigung.",
        "fr": "Le processus démarre automatiquement après votre approbation.",
        "es": "El proceso comienza automáticamente tras su aprobación.",
        "ar": "تبدأ العملية تلقائيًا بعد موافقتك.",
        "ru": "Процесс начинается автоматически после вашего утверждения.",
        "kr": "Pêvajo piştî pejirandina we bixweber dest pê dike.",
    },
    "pay_done_btn": {"tr": "ÖDEME YAPTIM", "en": "I MADE THE PAYMENT", "de": "ZAHLUNG ERFOLGT", "fr": "PAIEMENT EFFECTUÉ", "es": "PAGO REALIZADO", "ar": "قمت بالدفع", "ru": "Я ОПЛАТИЛ", "kr": "MIN DRAV DA"},
    "pay_cancel_btn": {"tr": "ÖDEME İPTAL", "en": "CANCEL PAYMENT", "de": "ZAHLUNG ABBRECHEN", "fr": "ANNULER LE PAIEMENT", "es": "CANCELAR PAGO", "ar": "إلغاء الدفع", "ru": "ОТМЕНИТЬ ОПЛАТУ", "kr": "DRAVDANÊ BETAL BIKE"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# Yönetici Ödeme Bildirim Kartı
# ═══════════════════════════════════════════════════════════════════════════════
ADMIN_PAYMENT = {
    "title": {
        "tr": "YÖNETİCİ ÖDEME BİLDİRİMİ",
        "en": "ADMIN PAYMENT NOTIFICATION",
        "de": "ADMIN-ZAHLUNGSBENACHRICHTIGUNG",
        "fr": "NOTIFICATION DE PAIEMENT ADMIN",
        "es": "NOTIFICACIÓN DE PAGO ADMIN",
        "ar": "إشعار الدفع للمدير",
        "ru": "УВЕДОМЛЕНИЕ ОБ ОПЛАТЕ АДМИНУ",
        "kr": "AGAHIYA DRAVDANA RÊVEBER",
    },
    "verification": {"tr": "ÖDEME DOĞRULAMA", "en": "PAYMENT VERIFICATION", "de": "ZAHLUNGSVERIFIZIERUNG", "fr": "VÉRIFICATION DE PAIEMENT", "es": "VERIFICACIÓN DE PAGO", "ar": "التحقق من الدفع", "ru": "ПРОВЕРКА ОПЛАТЫ", "kr": "VERIFIKASYONA DRAVDANÊ"},
    "info_1": {
        "tr": "Kullanıcı ÖDEME YAPTIM bildirimi göndermiştir.",
        "en": "The user has sent an I MADE THE PAYMENT notification.",
        "de": "Der Benutzer hat eine ZAHLUNG-ERFOLGT-Benachrichtigung gesendet.",
        "fr": "L'utilisateur a envoyé une notification PAIEMENT EFFECTUÉ.",
        "es": "El usuario ha enviado una notificación de PAGO REALIZADO.",
        "ar": "أرسل المستخدم إشعار قمت بالدفع.",
        "ru": "Пользователь отправил уведомление Я ОПЛАТИЛ.",
        "kr": "Bikarhêner agahiya MIN DRAV DA şand.",
    },
    "info_2": {
        "tr": "Lütfen banka hesabınızı kontrol ediniz.",
        "en": "Please check your bank account.",
        "de": "Bitte überprüfen Sie Ihr Bankkonto.",
        "fr": "Veuillez vérifier votre compte bancaire.",
        "es": "Por favor, verifique su cuenta bancaria.",
        "ar": "يرجى التحقق من حسابك المصرفي.",
        "ru": "Пожалуйста, проверьте ваш банковский счет.",
        "kr": "Ji kerema xwe hesabê banka xwe kontrol bikin.",
    },
    "info_3": {
        "tr": "Ödeme hesabınıza ulaştıysa aşağıdaki butona basınız.",
        "en": "If the payment has reached your account, press the button below.",
        "de": "Wenn die Zahlung eingegangen ist, klicken Sie auf die Schaltfläche unten.",
        "fr": "Si le paiement est arrivé sur votre compte, appuyez sur le bouton ci-dessous.",
        "es": "Si el pago ha llegado a su cuenta, presione el botón de abajo.",
        "ar": "إذا وصل الدفع إلى حسابك، اضغط على الزر أدناه.",
        "ru": "Если оплата поступила на ваш счет, нажмите кнопку ниже.",
        "kr": "Heke drav gihîştiye hesabê we, bişkoka jêr pêl bikin.",
    },
    "user_info": {"tr": "KULLANICI BİLGİLERİ", "en": "USER INFORMATION", "de": "BENUTZERINFORMATIONEN", "fr": "INFORMATIONS UTILISATEUR", "es": "INFORMACIÓN DEL USUARIO", "ar": "معلومات المستخدم", "ru": "ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ", "kr": "AGAHIYÊN BIKARHÊNER"},
    "product_info": {"tr": "ÜRÜN BİLGİLERİ", "en": "PRODUCT INFORMATION", "de": "PRODUKTINFORMATIONEN", "fr": "INFORMATIONS PRODUIT", "es": "INFORMACIÓN DEL PRODUCTO", "ar": "معلومات المنتج", "ru": "ИНФОРМАЦИЯ О ПРОДУКТЕ", "kr": "AGAHIYÊN HILBERÎNÊ"},
    "payment_info": {"tr": "ÖDEME BİLGİLERİ", "en": "PAYMENT INFORMATION", "de": "ZAHLUNGSINFORMATIONEN", "fr": "INFORMATIONS DE PAIEMENT", "es": "INFORMACIÓN DE PAGO", "ar": "معلومات الدفع", "ru": "ИНФОРМАЦИЯ ОБ ОПЛАТЕ", "kr": "AGAHIYÊN DRAVDANÊ"},
    "auto_generated": {
        "tr": "Bu bildirim HLK tarafından otomatik oluşturulmuştur.",
        "en": "This notification was automatically generated by HLK.",
        "de": "Diese Benachrichtigung wurde automatisch von HLK generiert.",
        "fr": "Cette notification a été générée automatiquement par HLK.",
        "es": "Esta notificación fue generada automáticamente por HLK.",
        "ar": "تم إنشاء هذا الإشعار تلقائيًا بواسطة HLK.",
        "ru": "Это уведомление автоматически создано HLK.",
        "kr": "Ev agahî ji hêla HLK ve bixweber hate çêkirin.",
    },
    "approve_btn": {"tr": "Ödeme hesabıma geçti", "en": "Payment received in my account", "de": "Zahlung auf meinem Konto", "fr": "Paiement reçu sur mon compte", "es": "Pago recibido en mi cuenta", "ar": "تم استلام الدفع في حسابي", "ru": "Оплата поступила на мой счет", "kr": "Drav gihîşt hesabê min"},
    "ret_btn": {"tr": "RET — Odeme Ulasmadi", "en": "REJECT — Payment Not Received", "de": "ABLEHNEN — Zahlung nicht erhalten", "fr": "REFUSER — Paiement non recu", "es": "RECHAZAR — Pago no recibido", "ar": "رفض — لم يتم استلام الدفع", "ru": "ОТКЛОНИТЬ — Оплата не получена", "kr": "REDKIRIN — Drav Nehat"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# Final Mesaji (Odeme onayi sonrasi kullaniciya)
# ═══════════════════════════════════════════════════════════════════════════════
FINAL = {
    "payment_received": {"tr": "Odemenizi aldik.", "en": "We have received your payment.", "de": "Wir haben Ihre Zahlung erhalten.", "fr": "Nous avons recu votre paiement.", "es": "Hemos recibido su pago.", "ar": "لقد استلمنا دفعتك.", "ru": "Мы получили вашу оплату.", "kr": "Me drave we wergirt."},
    "production_started": {"tr": "Video uretiminiz baslatilmistir.", "en": "Your video production has been started.", "de": "Ihre Videoproduktion wurde gestartet.", "fr": "Votre production video a ete lancee.", "es": "Su produccion de video ha sido iniciada.", "ar": "تم بدء إنتاج الفيديو الخاص بك.", "ru": "Производство вашего видео запущено.", "kr": "Hilberina vidyoya we dest pe kir."},
    "duration_info": {"tr": "Bu surec yaklasik 10-15 dakika surmektedir.", "en": "This process takes approximately 10-15 minutes.", "de": "Dieser Prozess dauert etwa 10-15 Minuten.", "fr": "Ce processus prend environ 10-15 minutes.", "es": "Este proceso toma aproximadamente 10-15 minutos.", "ar": "تستغرق هذه العملية حوالي 10-15 دقيقة.", "ru": "Этот процесс занимает примерно 10-15 минут.", "kr": "Ev pevajo neziki 10-15 hurdeman dom dike."},
    "auto_delivery": {"tr": "Video tamamlandiginda otomatik olarak size gonderilecektir.", "en": "The video will be automatically sent to you when completed.", "de": "Das Video wird Ihnen nach Fertigstellung automatisch zugesandt.", "fr": "La video vous sera automatiquement envoyee une fois terminee.", "es": "El video se le enviara automaticamente cuando este completado.", "ar": "سيتم إرسال الفيديو إليك تلقائيا عند اكتماله.", "ru": "Видео будет автоматически отправлено вам после завершения.", "kr": "Dema vidyo qediya, de bixweber ji we re were sandin."},
    "timeout_warning": {"tr": "<b>HLK Reklam Asistani</b> ile acik bir Telegram oturumunuz kaldi, <b>2 dakika</b> icinde bu oturum kapatilacaktir.", "en": "You have an open Telegram session with <b>HLK Ad Assistant</b>, this session will be closed in <b>2 minutes</b>.", "de": "Sie haben eine offene Telegram-Sitzung mit <b>HLK Werbeassistent</b>, diese Sitzung wird in <b>2 Minuten</b> geschlossen.", "fr": "Vous avez une session Telegram ouverte avec <b>HLK Assistant Publicitaire</b>, cette session sera fermee dans <b>2 minutes</b>.", "es": "Tiene una sesion de Telegram abierta con <b>HLK Asistente de Anuncios</b>, esta sesion se cerrara en <b>2 minutos</b>.", "ar": "لديك جلسة تلغرام مفتوحة مع <b>مساعد HLK الإعلاني</b>، سيتم إغلاق هذه الجلسة خلال <b>دقيقتين</b>.", "ru": "У вас открыта сессия Telegram с <b>HLK Рекламным Ассистентом</b>, эта сессия будет закрыта через <b>2 минуты</b>.", "kr": "We runistina we ya Telegrame bi <b>HLK Alikare Reklame</b> re vekiri ye, ev runistin de di <b>2 hurdeman</b> de were girtin."},
    "timeout_closed": {"tr": "<b>HLK Reklam Asistani</b> ile acik olan Telegram oturumunuz <b>kapatilmistir.</b>", "en": "Your open Telegram session with <b>HLK Ad Assistant</b> has been <b>closed.</b>", "de": "Ihre offene Telegram-Sitzung mit <b>HLK Werbeassistent</b> wurde <b>geschlossen.</b>", "fr": "Votre session Telegram ouverte avec <b>HLK Assistant Publicitaire</b> a ete <b>fermee.</b>", "es": "Su sesion de Telegram abierta con <b>HLK Asistente de Anuncios</b> ha sido <b>cerrada.</b>", "ar": "تم <b>إغلاق</b> جلسة تلغرام المفتوحة مع <b>مساعد HLK الإعلاني</b>.", "ru": "Ваша открытая сессия Telegram с <b>HLK Рекламным Ассистентом</b> была <b>закрыта.</b>", "kr": "Runistina we ya vekiri ya Telegrame bi <b>HLK Alikare Reklame</b> re <b>hate girtin.</b>"},
    "payment_approved_toast": {"tr": "Odeme onaylandi — uretim basliyor!", "en": "Payment approved — production starting!", "de": "Zahlung bestatigt — Produktion startet!", "fr": "Paiement approuve — production en cours!", "es": "Pago aprobado — produccion iniciando!", "ar": "تمت الموافقة على الدفع — بدء الإنتاج!", "ru": "Оплата подтверждена — запуск производства!", "kr": "Drav hate pejirandin — hilberin dest pe dike!"},
    "new_session_start": {"tr": "Yeni bir reklam calismasi baslatmak icin lutfen tekrar <b>/start</b> komutu ile giris yapiniz.", "en": "To start a new ad project, please use the <b>/start</b> command again.", "de": "Um ein neues Werbeprojekt zu starten, verwenden Sie bitte erneut den Befehl <b>/start</b>.", "fr": "Pour demarrer un nouveau projet publicitaire, veuillez utiliser a nouveau la commande <b>/start</b>.", "es": "Para iniciar un nuevo proyecto publicitario, use el comando <b>/start</b> nuevamente.", "ar": "لبدء مشروع إعلاني جديد، يرجى استخدام أمر <b>/start</b> مرة أخرى.", "ru": "Чтобы начать новый рекламный проект, пожалуйста, снова используйте команду <b>/start</b>.", "kr": "Ji bo destpekirina projeyek reklame ya nu, ji kerema xwe disa fermana <b>/start</b> bikar binin."},
    "payment_cancelled": {"tr": "Odeme iptal edildi.", "en": "Payment cancelled.", "de": "Zahlung storniert.", "fr": "Paiement annule.", "es": "Pago cancelado.", "ar": "تم إلغاء الدفع.", "ru": "Оплата отменена.", "kr": "Drav hate betalkirin."},
}

# ═══════════════════════════════════════════════════════════════════════════════
# Urun Linki / Materyal (SAHNE-02 genisletme)
# ═══════════════════════════════════════════════════════════════════════════════
MATERIAL = {
    "title": {
        "tr": "Ek Materyal",
        "en": "Additional Materials",
        "de": "Zusätzliche Materialien",
        "fr": "Matériaux Supplémentaires",
        "es": "Materiales Adicionales",
        "ar": "مواد إضافية",
        "ru": "Дополнительные Материалы",
        "kr": "Materyalên Zêde",
    },
    "prompt_has": {
        "tr": "Harika! 🎉 <b>Ürün bilgilerini</b> aldım ve analiz ediyorum.\n\nÜrününüze ait <b>tamamlayıcı materyalleriniz</b> var mı?\n\n📷 <b>Fotoğraflar</b> — <i>farklı açılardan</i>\n🎬 <b>Videolar</b> — <i>ürün kullanımı</i>\n📄 <b>Katalog</b> veya broşür\n📋 <b>Teknik dökümanlar</b>\n\nVarsa şimdi yükleyebilirsiniz. Yoksa <b>YOK</b> butonuna basarak devam edebiliriz.",
        "en": "Great! 🎉 I've received your <b>product info</b> and I'm analyzing it.\n\nDo you have <b>additional materials</b> for your product?\n\n📷 <b>Photos</b> — <i>different angles</i>\n🎬 <b>Videos</b> — <i>product usage</i>\n📄 <b>Catalogs</b> or brochures\n📋 <b>Technical docs</b>\n\nUpload now or press <b>NO</b> to continue.",
        "de": "Haben Sie zusätzliche Materialien? (Fotos, Videos, Kataloge usw.)",
        "fr": "Avez-vous des matériaux supplémentaires? (Photos, vidéos, catalogues, etc.)",
        "es": "¿Tienes materiales adicionales? (Fotos, videos, catálogos, etc.)",
        "ar": "هل لديك مواد إضافية لمنتجك؟ (صور، فيديوهات، كتالوجات، إلخ)",
        "ru": "У вас есть дополнительные материалы? (Фото, видео, каталоги и т.д.)",
        "kr": "Materyalên zêde ji bo hilberîna we hene? (Wêne, vîdyo, katalog, hwd.)",
    },
    "var": {"tr": "VAR", "en": "YES", "de": "JA", "fr": "OUI", "es": "SÍ", "ar": "نعم", "ru": "ДА", "kr": "ERÊ"},
    "yok": {"tr": "YOK", "en": "NO", "de": "NEIN", "fr": "NON", "es": "NO", "ar": "لا", "ru": "НЕТ", "kr": "NA"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# Platform Seçimi
# ═══════════════════════════════════════════════════════════════════════════════
PLATFORM = {
    "title": {
        "tr": "Platform Seçimi",
        "en": "Platform Selection",
        "de": "Plattform Auswahl",
        "fr": "Sélection de Plateforme",
        "es": "Selección de Plataforma",
        "ar": "اختيار المنصة",
        "ru": "Выбор Платформы",
        "kr": "Hilbijartina Platformê",
    },
    "prompt": {
        "tr": "Teşekkürler! 🙏\n\nŞimdi reklamınızı hangi <b>platformda</b> yayınlamak istersiniz?\n\nSize en uygun platformu seçin, <b>reklam stratejinizi</b> ona göre hazırlayalım.",
        "en": "Thanks! 🙏\n\nWhich <b>platform</b> would you like to publish your ad on?\n\nChoose the best platform and I'll prepare your <b>ad strategy</b> accordingly.",
        "de": "Auf welcher Plattform soll Ihr Video veröffentlicht werden?",
        "fr": "Sur quelle plateforme votre vidéo sera-t-elle publiée?",
        "es": "¿En qué plataforma se publicará tu video?",
        "ar": "على أي منصة سيتم نشر الفيديو الخاص بك؟",
        "ru": "На какой платформе будет опубликовано ваше видео?",
        "kr": "Vîdyoya we dê li kîjan platformê were weşandin?",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# t() — Ana çeviri fonksiyonu
# ═══════════════════════════════════════════════════════════════════════════════

# Tüm kategorilerin kaydı
_SECTIONS = {
    "s03": S03, "s04": S04, "s05": S05, "s06": S06,
    "s07": S07, "s08": S08, "s09": S09, "s10": S10,
    "s11": S11, "s12": S12, "s13": S13,
    "common": COMMON, "pricing": PRICING, "payment": PAYMENT,
    "admin_payment": ADMIN_PAYMENT, "material": MATERIAL, "platform": PLATFORM, "final": FINAL,
}


def t(key: str, lang: Optional[str] = None) -> str:
    """Çeviri yapar. key formatı: "section.key" (örn: "s03.title")

    Args:
        key: Çeviri anahtarı (section.key)
        lang: Dil kodu. None ise veya bulunamazsa Türkçe (tr) kullanılır.

    Returns:
        Çevrilmiş metin
    """
    if not lang or lang not in ("tr", "en", "de", "fr", "es", "ar", "ru", "kr"):
        lang = FALLBACK

    parts = key.split(".", 1)
    if len(parts) != 2:
        return key

    section_key, field_key = parts
    section = _SECTIONS.get(section_key)
    if not section:
        return key

    field = section.get(field_key)
    if not field:
        return key

    return field.get(lang, field.get(FALLBACK, key))


def get_lang(user_data: dict) -> str:
    """user_data'dan aktif oturum dilini dondurur. Gecersiz dil varsa TR fallback."""
    lang = user_data.get("language", FALLBACK)
    if lang not in ("tr", "en", "de", "fr", "es", "ar", "ru", "kr"):
        lang = FALLBACK
    return lang
