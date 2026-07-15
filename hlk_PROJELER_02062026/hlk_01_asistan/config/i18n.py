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
        "de": "Danke! 📺\n\nWählen wir Ihre <b>Videoauflösung</b>.\n\n<b>480p</b> — <i>Günstig, einfach</i>\n<b>720p HD ⭐</b> — <i>Empfohlen, Qualität-Budget</i>\n<b>1080p Full HD</b> — <i>Höhere Qualität, höhere Kosten</i>\n\nWas bevorzugen Sie?",
        "fr": "Merci ! 📺\n\nChoisissons votre <b>résolution vidéo</b>.\n\n<b>480p</b> — <i>Économique, basique</i>\n<b>720p HD ⭐</b> — <i>Recommandé, qualité-budget</i>\n<b>1080p Full HD</b> — <i>Qualité supérieure, coût plus élevé</i>\n\nQue préférez-vous ?",
        "es": "¡Gracias! 📺\n\nElijamos tu <b>resolución de video</b>.\n\n<b>480p</b> — <i>Económico, básico</i>\n<b>720p HD ⭐</b> — <i>Recomendado, calidad-precio</i>\n<b>1080p Full HD</b> — <i>Mayor calidad, mayor coste</i>\n\n¿Cuál prefieres?",
        "ar": "شكراً! 📺\n\nلنختر <b>دقة الفيديو</b>.\n\n<b>480p</b> — <i>خيار اقتصادي</i>\n<b>720p HD ⭐</b> — <i>موصى به، توازن الجودة</i>\n<b>1080p Full HD</b> — <i>جودة أعلى، تكلفة أعلى</i>\n\nماذا تفضل؟",
        "ru": "Спасибо! 📺\n\nВыберем <b>разрешение видео</b>.\n\n<b>480p</b> — <i>Эконом, базовый</i>\n<b>720p HD ⭐</b> — <i>Рекомендуется, баланс</i>\n<b>1080p Full HD</b> — <i>Выше качество, выше цена</i>\n\nЧто предпочитаете?",
        "kr": "Spas! 📺\n\nEm <b>resolutiona vîdyoyê</b> hilbijêrin.\n\n<b>480p</b> — <i>Aborî, bingehîn</i>\n<b>720p HD ⭐</b> — <i>Tête pêşniyar kirin</i>\n<b>1080p Full HD</b> — <i>Qalîteya bilind, lêçûn zêde</i>\n\nKîjan hûn dixwazin?",
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
        "es": "¡Gracias! ⏱️\n\nEstablezcamos la <b>duración de tu video</b>.\n\nIntroduce una duración entre <b>4 y 30 segundos</b>.\n\n<i>Ejemplo: 15</i>",
        "ar": "شكراً! ⏱️\n\nلنحدد <b>مدة الفيديو</b>.\n\nأدخل مدة بين <b>4 و 30 ثانية</b>.\n\n<i>مثال: 15</i>",
        "ru": "Спасибо! ⏱️\n\nУстановим <b>длительность видео</b>.\n\nВведите значение от <b>4 до 30 секунд</b>.\n\n<i>Пример: 15</i>",
        "kr": "Spas! ⏱️\n\nEm <b>dirêjahiya vîdyoyê</b> diyar bikin.\n\nJi kerema xwe di navbera <b>4 û 30 çirkeyan</b> de binivîsin.\n\n<i>Mînak: 15</i>",
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
        "de": "Danke! 🎬\n\nWählen wir Ihren <b>Videostil</b>.\n\n<b>UGC-Stil ⭐</b> — <i>Natürlich, influencer-artig</i>\n<b>Traditionell & Modern</b> — <i>Klassik trifft Moderne</i>\n<b>Kinoreif</b> — <i>Filmische Optik</i>\n<b>Eigenes Skript</b> — <i>Eigenen Text senden</i>\n<b>HLK wählt ⭐</b> — <i>Bester Stil automatisch</i>\n\n📌 <b>Einmalauswahl</b>.",
        "fr": "Merci ! 🎬\n\nChoisissons votre <b>style vidéo</b>.\n\n<b>Style UGC ⭐</b> — <i>Naturel, style influenceur</i>\n<b>Traditionnel & Moderne</b> — <i>Classique et moderne</i>\n<b>Cinématique</b> — <i>Visuel cinématographique</i>\n<b>Mon propre script</b> — <i>Envoyez votre texte</i>\n<b>HLK décide ⭐</b> — <i>Meilleur style automatique</i>\n\n📌 <b>Choix unique</b>.",
        "es": "¡Gracias! 🎬\n\nElijamos tu <b>estilo de video</b>.\n\n<b>Estilo UGC ⭐</b> — <i>Natural, tipo influencer</i>\n<b>Tradicional & Moderno</b> — <i>Clásico y moderno</i>\n<b>Cinematográfico</b> — <i>Visual cinematográfico</i>\n<b>Mi propio guión</b> — <i>Envía tu texto</i>\n<b>HLK decide ⭐</b> — <i>Mejor estilo automático</i>\n\n📌 <b>Elección única</b>.",
        "ar": "شكراً! 🎬\n\nلنختر <b>نمط الفيديو</b>.\n\n<b>نمط UGC ⭐</b> — <i>طبيعي، بأسلوب المؤثرين</i>\n<b>تقليدي وعصري</b> — <i>كلاسيكي يلتقي بالحديث</i>\n<b>سينمائي</b> — <i>مرئيات سينمائية</i>\n<b>سأكتب بنفسي</b> — <i>أرسل النص الخاص بك</i>\n<b>HLK يقرر ⭐</b> — <i>أفضل نمط تلقائياً</i>\n\n📌 <b>اختيار واحد</b>.",
        "ru": "Спасибо! 🎬\n\nВыберем <b>стиль видео</b>.\n\n<b>UGC Стиль ⭐</b> — <i>Естественный, как у блогера</i>\n<b>Традиционный & Современный</b> — <i>Классика и современность</i>\n<b>Кинематографичный</b> — <i>Кино-визуал</i>\n<b>Свой сценарий</b> — <i>Отправьте текст</i>\n<b>HLK решит ⭐</b> — <i>Лучший стиль автоматически</i>\n\n📌 <b>Один выбор</b>.",
        "kr": "Spas! 🎬\n\nEm <b>şêwazê vîdyoyê</b> hilbijêrin.\n\n<b>Şêwaza UGC ⭐</b> — <i>Xwezayî, mîna influencer</i>\n<b>Kevneşopî & Modern</b> — <i>Klasîk bi modern re</i>\n<b>Sînemayî</b> — <i>Dîmena sînemayî</i>\n<b>Ez ê bi xwe binivîsim</b> — <i>Nivîsa xwe bişîne</i>\n<b>HLK biryar dide ⭐</b> — <i>Baştirîn şêwaz otomatîk</i>\n\n📌 <b>Yek hilbijartin</b>.",
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
        "de": "Danke! 👥\n\nDefinieren wir Ihre <b>Zielgruppe</b>.\n\nFür wen ist Ihr Produktvideo?\n\n📌 <b>Einmalauswahl</b>.",
        "fr": "Merci ! 👥\n\nDéfinissons votre <b>public cible</b>.\n\nPour qui est votre vidéo ?\n\n📌 <b>Choix unique</b>.",
        "es": "¡Gracias! 👥\n\nDefinamos tu <b>público objetivo</b>.\n\n¿Para quién es tu video?\n\n📌 <b>Elección única</b>.",
        "ar": "شكراً! 👥\n\nلنحدد <b>جمهورك المستهدف</b>.\n\nلمن هذا الفيديو؟\n\n📌 <b>اختيار واحد</b>.",
        "ru": "Спасибо! 👥\n\nОпределим <b>целевую аудиторию</b>.\n\nДля кого ваше видео?\n\n📌 <b>Один выбор</b>.",
        "kr": "Spas! 👥\n\nEm <b>armanca temaşevanan</b> diyar bikin.\n\nVîdyoya we ji bo kê ye?\n\n📌 <b>Yek hilbijartin</b>.",
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
        "de": "Danke! 🎙️\n\nLegen wir Ihre <b>Audio-Einstellungen</b> fest.\n\n<b>🎙️ Voiceover</b> — <i>Professionelle Erzählung</i>\n<b>🔊 Umgebung</b> — <i>Natürlicher Hintergrund</i>\n<b>🎵 Musik</b> — <i>Lizenzfrei</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 STUMM</b>\n<i>(Kein Audio)</i>\n\n📌 Mehrfachauswahl",
        "fr": "Merci ! 🎙️\n\nDéfinissons vos <b>préférences audio</b>.\n\n<b>🎙️ Voix Off</b> — <i>Narration pro</i>\n<b>🔊 Ambiance</b> — <i>Sons naturels</i>\n<b>🎵 Musique</b> — <i>Libre de droits</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 SILENCIEUX</b>\n<i>(Aucun son)</i>\n\n📌 Choix multiples",
        "es": "¡Gracias! 🎙️\n\nDefinamos tus <b>preferencias de audio</b>.\n\n<b>🎙️ Voz en Off</b> — <i>Narración profesional</i>\n<b>🔊 Ambiente</b> — <i>Sonidos naturales</i>\n<b>🎵 Música</b> — <i>Libre de derechos</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 SILENCIOSO</b>\n<i>(Sin audio)</i>\n\n📌 Selección múltiple",
        "ar": "شكراً! 🎙️\n\nلنحدد <b>تفضيلات الصوت</b>.\n\n<b>🎙️ تعليق صوتي</b> — <i>رواية احترافية</i>\n<b>🔊 أصوات محيطة</b> — <i>طبيعية</i>\n<b>🎵 موسيقى</b> — <i>بدون حقوق</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 صامت</b>\n<i>(بدون صوت)</i>\n\n📌 اختيارات متعددة",
        "ru": "Спасибо! 🎙️\n\nНастроим <b>параметры звука</b>.\n\n<b>🎙️ Озвучка</b> — <i>Профессиональная</i>\n<b>🔊 Фон</b> — <i>Естественные звуки</i>\n<b>🎵 Музыка</b> — <i>Без роялти</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 БЕЗ ЗВУКА</b>\n<i>(Нет аудио)</i>\n\n📌 Множественный выбор",
        "kr": "Spas! 🎙️\n\nEm <b>vebijêrkên deng</b> diyar bikin.\n\n<b>🎙️ Dengê Derveyî</b> — <i>Profesyonel</i>\n<b>🔊 Dengên Derûdorê</b> — <i>Xwezayî</i>\n<b>🎵 Muzîk</b> — <i>Bê maf</i>\n━━━━━━━━━━━━━━━━━━\n<b>🔇 BÊDENG</b>\n<i>(Bê deng)</i>\n\n📌 Pirbijartin",
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
        "de": "Danke! 🎙️\n\nWählen wir Ihre <b>Voiceover-Sprache</b>.\n\n🌍 <b>Alle offiziellen Sprachen</b> verfügbar.",
        "fr": "Merci ! 🎙️\n\nChoisissons votre <b>langue de voix off</b>.\n\n🌍 <b>Toutes les langues officielles</b> disponibles.",
        "es": "¡Gracias! 🎙️\n\nElijamos tu <b>idioma de voz</b>.\n\n🌍 <b>Todos los idiomas oficiales</b> disponibles.",
        "ar": "شكراً! 🎙️\n\nلنختر <b>لغة التعليق الصوتي</b>.\n\n🌍 <b>جميع اللغات الرسمية</b> متاحة.",
        "ru": "Спасибо! 🎙️\n\nВыберем <b>язык озвучки</b>.\n\n🌍 <b>Все официальные языки</b> доступны.",
        "kr": "Spas! 🎙️\n\nEm <b>zimanê dengê derveyî</b> hilbijêrin.\n\n🌍 <b>Hemû zimanên fermî</b> berdest in.",
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
        "de": "Danke! ✨\n\nMöchten Sie etwas <b>besonders hervorheben</b>?\n\n<i>Mehrfachauswahl möglich.</i>",
        "fr": "Merci ! ✨\n\nSouhaitez-vous <b>mettre en avant</b> quelque chose ?\n\n<i>Choix multiples autorisés.</i>",
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
    # Brief field labels (BRIEF_FIELDS)
    "field_link": {"tr": "🔗 Ürün Linki", "en": "🔗 Product Link", "de": "🔗 Produktlink", "fr": "🔗 Lien Produit", "es": "🔗 Enlace del Producto", "ar": "🔗 رابط المنتج", "ru": "🔗 Ссылка на Продукт", "kr": "🔗 Girêdana Berhemê"},
    "field_material": {"tr": "📦 Ek Materyal", "en": "📦 Extra Materials", "de": "📦 Zusatzmaterial", "fr": "📦 Matériaux Supp.", "es": "📦 Material Extra", "ar": "📦 مواد إضافية", "ru": "📦 Доп. Материалы", "kr": "📦 Materyalên Zêde"},
    "field_platform": {"tr": "📱 Platform", "en": "📱 Platform", "de": "📱 Plattform", "fr": "📱 Plateforme", "es": "📱 Plataforma", "ar": "📱 المنصة", "ru": "📱 Платформа", "kr": "📱 Platform"},
    "field_format": {"tr": "📐 Video Formatı", "en": "📐 Video Format", "de": "📐 Videoformat", "fr": "📐 Format Vidéo", "es": "📐 Formato de Video", "ar": "📐 تنسيق الفيديو", "ru": "📐 Формат Видео", "kr": "📐 Formata Vîdyoyê"},
    "field_resolution": {"tr": "📺 Çözünürlük", "en": "📺 Resolution", "de": "📺 Auflösung", "fr": "📺 Résolution", "es": "📺 Resolución", "ar": "📺 الدقة", "ru": "📺 Разрешение", "kr": "📺 Resolution"},
    "field_duration": {"tr": "⏱️ Video Süresi", "en": "⏱️ Video Duration", "de": "⏱️ Videodauer", "fr": "⏱️ Durée Vidéo", "es": "⏱️ Duración del Video", "ar": "⏱️ مدة الفيديو", "ru": "⏱️ Длительность", "kr": "⏱️ Dirêjahiya Vîdyoyê"},
    "field_style": {"tr": "🎬 Tanıtım Tarzı", "en": "🎬 Ad Style", "de": "🎬 Werbestil", "fr": "🎬 Style Publicitaire", "es": "🎬 Estilo de Anuncio", "ar": "🎬 نمط الإعلان", "ru": "🎬 Стиль Рекламы", "kr": "🎬 Şêwaza Reklamê"},
    "field_audience": {"tr": "👥 Hedef Kitle", "en": "👥 Target Audience", "de": "👥 Zielgruppe", "fr": "👥 Public Cible", "es": "👥 Público Objetivo", "ar": "👥 الجمهور المستهدف", "ru": "👥 Целевая Аудитория", "kr": "👥 Temaşevanên Armanc"},
    "field_audio": {"tr": "🎙️ Ses Tercihleri", "en": "🎙️ Audio Preferences", "de": "🎙️ Audio-Einstellungen", "fr": "🎙️ Préférences Audio", "es": "🎙️ Preferencias de Audio", "ar": "🎙️ تفضيلات الصوت", "ru": "🎙️ Настройки Звука", "kr": "🎙️ Vebijêrkên Deng"},
    "field_voicelang": {"tr": "🗣️ Seslendirme Dili", "en": "🗣️ Voice Language", "de": "🗣️ Sprachausgabe", "fr": "🗣️ Langue de la Voix", "es": "🗣️ Idioma de Voz", "ar": "🗣️ لغة الصوت", "ru": "🗣️ Язык Озвучки", "kr": "🗣️ Zimanê Deng"},
    "field_voicechar": {"tr": "🎭 Ses Karakteri", "en": "🎭 Voice Character", "de": "🎭 Stimmcharakter", "fr": "🎭 Personnage Vocal", "es": "🎭 Personaje de Voz", "ar": "🎭 شخصية الصوت", "ru": "🎭 Персонаж Голоса", "kr": "🎭 Karakterê Deng"},
    "field_emphasis": {"tr": "✨ Vurgulanacaklar", "en": "✨ Highlights", "de": "✨ Hervorhebungen", "fr": "✨ Points Clés", "es": "✨ Destacados", "ar": "✨ نقاط بارزة", "ru": "✨ Акценты", "kr": "✨ Xalên Girîng"},
    # Brief field descriptions (aciklama_map)
    "desc_link": {"tr": "Analiz edilen ürün sayfası", "en": "Analyzed product page", "de": "Analysierte Produktseite", "fr": "Page produit analysée", "es": "Página de producto analizada", "ar": "صفحة المنتج المحللة", "ru": "Проанализированная страница", "kr": "Rûpela berhemê ya analîzkirî"},
    "desc_material": {"tr": "Kullanıcının yüklediği materyaller", "en": "User uploaded materials", "de": "Vom Benutzer hochgeladene Materialien", "fr": "Matériaux téléchargés", "es": "Materiales subidos por el usuario", "ar": "المواد التي حملها المستخدم", "ru": "Загруженные пользователем материалы", "kr": "Materyalên ku bikarhêner bar kirine"},
    "desc_platform": {"tr": "Yayınlanacak platform", "en": "Publishing platform", "de": "Veröffentlichungsplattform", "fr": "Plateforme de publication", "es": "Plataforma de publicación", "ar": "منصة النشر", "ru": "Платформа публикации", "kr": "Platforma weşandinê"},
    "desc_format": {"tr": "Seçilen video formatı", "en": "Selected video format", "de": "Gewähltes Videoformat", "fr": "Format vidéo sélectionné", "es": "Formato de video seleccionado", "ar": "تنسيق الفيديو المختار", "ru": "Выбранный формат видео", "kr": "Formata vîdyoyê ya hilbijartî"},
    "desc_resolution": {"tr": "Video çözünürlüğü", "en": "Video resolution", "de": "Videoauflösung", "fr": "Résolution vidéo", "es": "Resolución de video", "ar": "دقة الفيديو", "ru": "Разрешение видео", "kr": "Resolutiona vîdyoyê"},
    "desc_duration": {"tr": "Tercih edilen video süresi", "en": "Preferred video duration", "de": "Bevorzugte Videodauer", "fr": "Durée vidéo préférée", "es": "Duración de video preferida", "ar": "مدة الفيديو المفضلة", "ru": "Предпочтительная длительность", "kr": "Dirêjahiya vîdyoyê ya tercîhkirî"},
    "desc_style": {"tr": "Reklam tanıtım tarzı", "en": "Ad presentation style", "de": "Werbe-Präsentationsstil", "fr": "Style de présentation publicitaire", "es": "Estilo de presentación del anuncio", "ar": "أسلوب عرض الإعلان", "ru": "Стиль презентации рекламы", "kr": "Şêwaza pêşkêşkirina reklamê"},
    "desc_audience": {"tr": "Reklam hedef kitlesi", "en": "Ad target audience", "de": "Werbe-Zielgruppe", "fr": "Public cible de la publicité", "es": "Público objetivo del anuncio", "ar": "الجمهور المستهدف للإعلان", "ru": "Целевая аудитория рекламы", "kr": "Temaşevanên armanca reklamê"},
    "desc_audio": {"tr": "Ses tercihleri", "en": "Audio preferences", "de": "Audio-Einstellungen", "fr": "Préférences audio", "es": "Preferencias de audio", "ar": "تفضيلات الصوت", "ru": "Настройки звука", "kr": "Vebijêrkên deng"},
    "desc_voicelang": {"tr": "Seçilen seslendirme dili", "en": "Selected voice language", "de": "Gewählte Sprachausgabe", "fr": "Langue de voix sélectionnée", "es": "Idioma de voz seleccionado", "ar": "لغة الصوت المختارة", "ru": "Выбранный язык озвучки", "kr": "Zimanê dengê hilbijartî"},
    "desc_voicechar": {"tr": "Seslendirme karakteri", "en": "Voice character", "de": "Stimmcharakter", "fr": "Personnage vocal", "es": "Personaje de voz", "ar": "شخصية الصوت", "ru": "Персонаж голоса", "kr": "Karakterê deng"},
    "desc_emphasis": {"tr": "Öne çıkarılacak detaylar", "en": "Details to highlight", "de": "Hervorzuhebende Details", "fr": "Détails à mettre en avant", "es": "Detalles a destacar", "ar": "تفاصيل لإبرازها", "ru": "Детали для выделения", "kr": "Detayên ku werin diyar kirin"},
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
    "scenario_phase": {
        "tr": "senaryo aşamasına geçiliyor...",
        "en": "moving to scenario phase...",
        "de": "wechsel zur Szenariophase...",
        "fr": "passage à la phase scénario...",
        "es": "pasando a la fase de guion...",
        "ar": "الانتقال إلى مرحلة السيناريو...",
        "ru": "переход к этапу сценария...",
        "kr": "derbasî qonaxa sênaryoyê dibe...",
    },
    "scenario_ready": {
        "tr": "<b>📝 Senaryonuz</b> hazırlandı, <i>form hazırlanıyor...</i>",
        "en": "<b>📝 Your script</b> is ready, <i>preparing the form...</i>",
        "de": "<b>📝 Ihr Skript</b> ist fertig, <i>Formular wird vorbereitet...</i>",
        "fr": "<b>📝 Votre script</b> est prêt, <i>préparation du formulaire...</i>",
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
        "de": "Super! 🎉 Ich habe Ihre <b>Produktinformationen</b> erhalten.\n\nHaben Sie <b>zusätzliche Materialien</b>?\n\n📷 <b>Fotos</b> — <i>verschiedene Winkel</i>\n🎬 <b>Videos</b> — <i>Produktnutzung</i>\n📄 <b>Kataloge</b>\n📋 <b>Technische Unterlagen</b>\n\nJetzt hochladen oder <b>NEIN</b> drücken.",
        "fr": "Super ! 🎉 J'ai reçu vos <b>infos produit</b>.\n\nAvez-vous des <b>matériaux supplémentaires</b> ?\n\n📷 <b>Photos</b> — <i>différents angles</i>\n🎬 <b>Vidéos</b> — <i>utilisation</i>\n📄 <b>Catalogues</b>\n📋 <b>Docs techniques</b>\n\nTéléchargez ou appuyez sur <b>NON</b>.",
        "es": "¡Genial! 🎉 He recibido tu <b>información de producto</b>.\n\n¿Tienes <b>materiales adicionales</b>?\n\n📷 <b>Fotos</b> — <i>diferentes ángulos</i>\n🎬 <b>Videos</b> — <i>uso del producto</i>\n📄 <b>Catálogos</b>\n📋 <b>Documentos técnicos</b>\n\nSube ahora o pulsa <b>NO</b>.",
        "ar": "رائع! 🎉 استلمت <b>معلومات منتجك</b>.\n\nهل لديك <b>مواد إضافية</b>؟\n\n📷 <b>صور</b> — <i>زوايا مختلفة</i>\n🎬 <b>فيديوهات</b> — <i>استخدام المنتج</i>\n📄 <b>كتالوجات</b>\n📋 <b>مستندات تقنية</b>\n\nحمّل الآن أو اضغط <b>لا</b>.",
        "ru": "Отлично! 🎉 Я получил <b>информацию о продукте</b>.\n\nЕсть <b>дополнительные материалы</b>?\n\n📷 <b>Фото</b> — <i>разные ракурсы</i>\n🎬 <b>Видео</b> — <i>использование</i>\n📄 <b>Каталоги</b>\n📋 <b>Тех. документы</b>\n\nЗагрузите или нажмите <b>НЕТ</b>.",
        "kr": "Bellek! 🎉 Min <b>agahiyên hilberînê</b> wergirt.\n\n<b>Materyalên zêde</b> hene?\n\n📷 <b>Wêne</b> — <i>goşeyên cuda</i>\n🎬 <b>Vîdyo</b> — <i>bikaranîna hilberînê</i>\n📄 <b>Katalog</b>\n📋 <b>Belgeyên teknîkî</b>\n\nNiha bar bikin an <b>NA</b> bitikînin.",
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
        "de": "Danke! 🙏\n\nAuf welcher <b>Plattform</b> möchten Sie Ihre Anzeige veröffentlichen?\n\nIch bereite Ihre <b>Werbestrategie</b> vor.",
        "fr": "Merci ! 🙏\n\nSur quelle <b>plateforme</b> souhaitez-vous publier votre annonce ?\n\nJe préparerai votre <b>stratégie publicitaire</b>.",
        "es": "¡Gracias! 🙏\n\n¿En qué <b>plataforma</b> quieres publicar tu anuncio?\n\nPrepararé tu <b>estrategia publicitaria</b>.",
        "ar": "شكراً! 🙏\n\nعلى أي <b>منصة</b> تريد نشر إعلانك؟\n\nسأعد <b>استراتيجيتك الإعلانية</b>.",
        "ru": "Спасибо! 🙏\n\nНа какой <b>платформе</b> опубликовать ваше объявление?\n\nЯ подготовлю <b>рекламную стратегию</b>.",
        "kr": "Spas! 🙏\n\nHûn dixwazin li kîjan <b>platformê</b> reklama xwe biweşînin?\n\nEz ê <b>stratejiya reklamê</b> amade bikim.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Senaryo Onay Formu
# ═══════════════════════════════════════════════════════════════════════════════
SCENARIO = {
    "title": {
        "tr": "SENARYO ONAY FORMU",
        "en": "SCENARIO APPROVAL FORM",
        "de": "SZENARIO-GENEHMIGUNGSFORMULAR",
        "fr": "FORMULAIRE D'APPROBATION DU SCÉNARIO",
        "es": "FORMULARIO DE APROBACIÓN DE GUION",
        "ar": "نموذج الموافقة على السيناريو",
        "ru": "ФОРМА УТВЕРЖДЕНИЯ СЦЕНАРИЯ",
        "kr": "FORMA PESENDKIRINA SÊNARYOYÊ",
    },
    "step": {
        "tr": "✅1.Brief  ›  🔵2.Senaryo  ›  ⏳3.Fiyat Teklifi",
        "en": "✅1.Brief  ›  🔵2.Scenario  ›  ⏳3.Price Offer",
        "de": "✅1.Brief  ›  🔵2.Szenario  ›  ⏳3.Preisangebot",
        "fr": "✅1.Brief  ›  🔵2.Scénario  ›  ⏳3.Offre de Prix",
        "es": "✅1.Brief  ›  🔵2.Guion  ›  ⏳3.Oferta de Precio",
        "ar": "✅1.موجز  ›  🔵2.سيناريو  ›  ⏳3.عرض السعر",
        "ru": "✅1.Бриф  ›  🔵2.Сценарий  ›  ⏳3.Цена",
        "kr": "✅1.Kurte  ›  🔵2.Senaryo  ›  ⏳3.Teklîfa Bihayê",
    },
    "brand": {"tr": "MARKA", "en": "BRAND", "de": "MARKE", "fr": "MARQUE", "es": "MARCA", "ar": "العلامة", "ru": "БРЕНД", "kr": "MARKE"},
    "product": {"tr": "ÜRÜN", "en": "PRODUCT", "de": "PRODUKT", "fr": "PRODUIT", "es": "PRODUCTO", "ar": "المنتج", "ru": "ПРОДУКТ", "kr": "BERHEM"},
    "story_title": {
        "tr": "📖 Tanıtım Hikayesi",
        "en": "📖 Storyline",
        "de": "📖 Handlung",
        "fr": "📖 Scénario",
        "es": "📖 Historia",
        "ar": "📖 القصة",
        "ru": "📖 Сюжет",
        "kr": "📖 Çîrok",
    },
    "scene_plan": {
        "tr": "🎞️ Sahne Planı",
        "en": "🎞️ Scene Plan",
        "de": "🎞️ Szenenplan",
        "fr": "🎞️ Plan des Scènes",
        "es": "🎞️ Plan de Escenas",
        "ar": "🎞️ خطة المشاهد",
        "ru": "🎞️ План Сцен",
        "kr": "🎞️ Plana Dîmenan",
    },
    "scene_unit": {
        "tr": "sahne", "en": "scenes", "de": "Szenen", "fr": "scènes", "es": "escenas", "ar": "مشاهد", "ru": "сцен", "kr": "dîmen",
    },
    # Scene titles (dinamik sahneler)
    "scene_intro": {
        "tr": "Dikkat Çekici Giriş", "en": "Attention-Grabbing Opening", "de": "Aufmerksamkeitsstarker Einstieg",
        "fr": "Ouverture Captivante", "es": "Apertura Llamativa", "ar": "افتتاحية جاذبة", "ru": "Захватывающее Вступление", "kr": "Vekirina Balkêş",
    },
    "scene_product": {
        "tr": "Ürün Tanıtımı", "en": "Product Showcase", "de": "Produktvorstellung",
        "fr": "Présentation du Produit", "es": "Presentación del Producto", "ar": "عرض المنتج", "ru": "Презентация Продукта", "kr": "Danasîna Berhemê",
    },
    "scene_features": {
        "tr": "Özellikler ve Faydalar", "en": "Features & Benefits", "de": "Eigenschaften & Vorteile",
        "fr": "Caractéristiques & Avantages", "es": "Características y Beneficios", "ar": "الميزات والفوائد", "ru": "Особенности и Преимущества", "kr": "Taybetmendî & Feyde",
    },
    "scene_usage": {
        "tr": "Kullanım Gösterimi", "en": "Usage Demonstration", "de": "Anwendungsdemonstration",
        "fr": "Démonstration d'Utilisation", "es": "Demostración de Uso", "ar": "عرض الاستخدام", "ru": "Демонстрация Использования", "kr": "Nîşandana Bikaranînê",
    },
    "scene_cta": {
        "tr": "Kapanış — CTA", "en": "Closing — CTA", "de": "Abschluss — CTA",
        "fr": "Clôture — CTA", "es": "Cierre — CTA", "ar": "الختام — دعوة للإجراء", "ru": "Закрытие — CTA", "kr": "Dawî — CTA",
    },
    # Tone/audience/CTA by age group
    "tone_kids": {"tr": "eğlenceli ve renkli", "en": "fun and colorful", "de": "lustig und bunt", "fr": "amusant et coloré", "es": "divertido y colorido", "ar": "ممتع وملون", "ru": "весёлый и яркий", "kr": "kêfxweş û rengîn"},
    "aud_kids": {"tr": "çocukların", "en": "children's", "de": "der Kinder", "fr": "des enfants", "es": "de los niños", "ar": "الأطفال", "ru": "детей", "kr": "zarokan"},
    "cta_kids": {"tr": "ailesiyle birlikte keşfetmeye", "en": "to explore with their family", "de": "mit der Familie zu entdecken", "fr": "à explorer en famille", "es": "a explorar en familia", "ar": "للاستكشاف مع العائلة", "ru": "исследовать с семьёй", "kr": "bi malbata xwe re keşf bikin"},
    "tone_teen": {"tr": "dinamik ve enerjik", "en": "dynamic and energetic", "de": "dynamisch und energiegeladen", "fr": "dynamique et énergique", "es": "dinámico y enérgico", "ar": "ديناميكي وحيوي", "ru": "динамичный и энергичный", "kr": "dînamîk û enerjîk"},
    "aud_teen": {"tr": "gençlerin", "en": "teens'", "de": "der Jugendlichen", "fr": "des adolescents", "es": "de los adolescentes", "ar": "المراهقين", "ru": "подростков", "kr": "ciwanan"},
    "cta_teen": {"tr": "hemen keşfetmeye", "en": "to discover now", "de": "jetzt zu entdecken", "fr": "à découvrir maintenant", "es": "a descubrir ahora", "ar": "للاكتشاف الآن", "ru": "открыть сейчас", "kr": "niha keşf bikin"},
    "tone_young": {"tr": "modern ve trend", "en": "modern and trendy", "de": "modern und trendy", "fr": "moderne et tendance", "es": "moderno y de moda", "ar": "عصري ورائج", "ru": "современный и модный", "kr": "modern û trend"},
    "aud_young": {"tr": "genç yetişkinlerin", "en": "young adults'", "de": "junger Erwachsener", "fr": "des jeunes adultes", "es": "de los jóvenes adultos", "ar": "الشباب", "ru": "молодых взрослых", "kr": "ciwanên mezin"},
    "cta_young": {"tr": "şimdi satın almaya", "en": "to buy now", "de": "jetzt zu kaufen", "fr": "à acheter maintenant", "es": "a comprar ahora", "ar": "للشراء الآن", "ru": "купить сейчас", "kr": "niha bikire"},
    "tone_adult": {"tr": "profesyonel ve şık", "en": "professional and sleek", "de": "professionell und elegant", "fr": "professionnel et élégant", "es": "profesional y elegante", "ar": "احترافي وأنيق", "ru": "профессиональный и стильный", "kr": "profesyonel û şık"},
    "aud_adult": {"tr": "yetişkinlerin", "en": "adults'", "de": "der Erwachsenen", "fr": "des adultes", "es": "de los adultos", "ar": "البالغين", "ru": "взрослых", "kr": "mezinan"},
    "cta_adult": {"tr": "hemen sipariş vermeye", "en": "to order now", "de": "jetzt zu bestellen", "fr": "à commander maintenant", "es": "a pedir ahora", "ar": "للطلب الآن", "ru": "заказать сейчас", "kr": "niha siparîş bide"},
    "tone_family": {"tr": "güvenilir ve samimi", "en": "trustworthy and warm", "de": "vertrauenswürdig und herzlich", "fr": "fiable et chaleureux", "es": "confiable y cálido", "ar": "موثوق ودافئ", "ru": "надёжный и тёплый", "kr": "pêbawer û germ"},
    "aud_family": {"tr": "ailelerin", "en": "families'", "de": "der Familien", "fr": "des familles", "es": "de las familias", "ar": "العائلات", "ru": "семей", "kr": "malbatan"},
    "cta_family": {"tr": "ailesi için satın almaya", "en": "to buy for their family", "de": "für die Familie zu kaufen", "fr": "à acheter pour leur famille", "es": "a comprar para su familia", "ar": "للشراء لعائلاتهم", "ru": "купить для семьи", "kr": "ji bo malbata xwe bikire"},
    "tone_midage": {"tr": "kaliteli ve prestijli", "en": "quality and prestigious", "de": "hochwertig und prestigeträchtig", "fr": "de qualité et prestigieux", "es": "de calidad y prestigioso", "ar": "عالي الجودة ومرموق", "ru": "качественный и престижный", "kr": "qalîte û prestîj"},
    "aud_midage": {"tr": "seçkin kullanıcıların", "en": "discerning users'", "de": "anspruchsvoller Nutzer", "fr": "des utilisateurs exigeants", "es": "de los usuarios exigentes", "ar": "المستخدمين المميزين", "ru": "искушённых пользователей", "kr": "bikarhênerên bijare"},
    "cta_midage": {"tr": "kaliteyi deneyimlemeye", "en": "to experience quality", "de": "Qualität zu erleben", "fr": "à découvrir la qualité", "es": "a experimentar calidad", "ar": "لتجربة الجودة", "ru": "испытать качество", "kr": "qalîteyê biceribîne"},
    "tone_senior": {"tr": "sakin ve güven veren", "en": "calm and reassuring", "de": "ruhig und beruhigend", "fr": "calme et rassurant", "es": "tranquilo y tranquilizador", "ar": "هادئ ومطمئن", "ru": "спокойный и обнадёживающий", "kr": "aram û dilniya"},
    "aud_senior": {"tr": "olgun kullanıcıların", "en": "mature users'", "de": "reifer Nutzer", "fr": "des utilisateurs matures", "es": "de los usuarios maduros", "ar": "المستخدمين الناضجين", "ru": "зрелых пользователей", "kr": "bikarhênerên gihîştî"},
    "cta_senior": {"tr": "güvenle satın almaya", "en": "to buy with confidence", "de": "mit Vertrauen zu kaufen", "fr": "à acheter en toute confiance", "es": "a comprar con confianza", "ar": "للشراء بثقة", "ru": "купить с уверенностью", "kr": "bi pêbawerî bikire"},
    "tone_default": {"tr": "etkileyici", "en": "impressive", "de": "beeindruckend", "fr": "impressionnant", "es": "impresionante", "ar": "مؤثر", "ru": "впечатляющий", "kr": "bandor"},
    "aud_default": {"tr": "izleyicilerin", "en": "viewers'", "de": "der Zuschauer", "fr": "des spectateurs", "es": "de los espectadores", "ar": "المشاهدين", "ru": "зрителей", "kr": "temaşevanan"},
    "cta_default": {"tr": "satın almaya", "en": "to purchase", "de": "zu kaufen", "fr": "à acheter", "es": "a comprar", "ar": "للشراء", "ru": "купить", "kr": "bikire"},
    # Scene descriptions (with {brand}, {product_name}, {hitap}, {ton}, {cagri} placeholders)
    "desc_intro": {
        "tr": "{brand} {product_name} ürünü, {hitap} ilgisini çekecek {ton} bir sahnede gösterilir. İlk saniyelerde ürüne odaklanılır.",
        "en": "{brand} {product_name} is shown in a {ton} scene that captures {hitap} attention. The focus is on the product from the first seconds.",
        "de": "{brand} {product_name} wird in einer {ton} Szene gezeigt, die {hitap} Aufmerksamkeit erregt. Der Fokus liegt von Beginn an auf dem Produkt.",
        "fr": "{brand} {product_name} est présenté dans une scène {ton} qui capte l'attention {hitap}. L'accent est mis sur le produit dès les premières secondes.",
        "es": "{brand} {product_name} se muestra en una escena {ton} que capta la atención {hitap}. El enfoque está en el producto desde el primer segundo.",
        "ar": "يتم عرض {brand} {product_name} في مشهد {ton} يجذب انتباه {hitap}. التركيز على المنتج من الثواني الأولى.",
        "ru": "{brand} {product_name} показан в {ton} сцене, привлекающей внимание {hitap}. Фокус на продукте с первых секунд.",
        "kr": "{brand} {product_name} di dîmenek {ton} de tê nîşandan ku bala {hitap} dikişîne. Ji saniyeyên pêşîn ve bal li ser berhemê ye.",
    },
    "desc_product": {
        "tr": "Ürün yakın planda detaylı gösterilir. {brand} kalitesi ve {product_name}'in öne çıkan özellikleri, {hitap} beklentilerine uygun şekilde vurgulanır.",
        "en": "The product is shown in detailed close-up. {brand} quality and {product_name}'s key features are highlighted to match {hitap} expectations.",
        "de": "Das Produkt wird in Nahaufnahme gezeigt. {brand} Qualität und die Hauptmerkmale von {product_name} werden entsprechend {hitap} Erwartungen hervorgehoben.",
        "fr": "Le produit est montré en gros plan détaillé. La qualité {brand} et les caractéristiques de {product_name} sont mises en avant pour répondre aux attentes {hitap}.",
        "es": "El producto se muestra en primer plano detallado. La calidad {brand} y las características de {product_name} se destacan según las expectativas {hitap}.",
        "ar": "يتم عرض المنتج عن قرب بتفصيل. جودة {brand} وميزات {product_name} الرئيسية تُبرز لتتناسب مع توقعات {hitap}.",
        "ru": "Продукт показан крупным планом. Качество {brand} и особенности {product_name} подчёркнуты в соответствии с ожиданиями {hitap}.",
        "kr": "Berhem di nêzîk de bi hûrgilî tê nîşandan. Qalîteya {brand} û taybetmendiyên {product_name} li gorî hêviyên {hitap} têne diyar kirin.",
    },
    "desc_features": {
        "tr": "{product_name} ürününün {hitap} hayatına katacağı değer, görsel karşılaştırmalar ve ikonlarla {ton} bir dille sunulur.",
        "en": "The value {product_name} adds to {hitap} life is presented with visual comparisons and icons in a {ton} manner.",
        "de": "Der Mehrwert von {product_name} für {hitap} wird mit visuellen Vergleichen und Symbolen {ton} präsentiert.",
        "fr": "La valeur que {product_name} apporte à la vie {hitap} est présentée avec des comparaisons visuelles et des icônes de manière {ton}.",
        "es": "El valor que {product_name} aporta a la vida {hitap} se presenta con comparaciones visuales e iconos de manera {ton}.",
        "ar": "يتم تقديم القيمة التي يضيفها {product_name} لحياة {hitap} بمقارنات بصرية وأيقونات بأسلوب {ton}.",
        "ru": "Ценность {product_name} для {hitap} представлена с визуальными сравнениями и иконками в {ton} стиле.",
        "kr": "Nirxa ku {product_name} dide jiyana {hitap} bi berawirdiyên dîtbarî û îkonan bi awayekî {ton} tê pêşkêş kirin.",
    },
    "desc_usage": {
        "tr": "{product_name} ürününün gerçek kullanım anı, {hitap} günlük yaşamından bir kesitle gösterilir. Kullanım kolaylığı vurgulanır.",
        "en": "A real usage moment of {product_name} is shown with a glimpse into {hitap} daily life. Ease of use is emphasized.",
        "de": "Ein echter Anwendungsmoment von {product_name} wird mit einem Einblick in den Alltag {hitap} gezeigt. Die einfache Anwendung wird betont.",
        "fr": "Un moment d'utilisation réel de {product_name} est montré avec un aperçu de la vie quotidienne {hitap}. La facilité d'utilisation est soulignée.",
        "es": "Se muestra un momento de uso real de {product_name} con un vistazo a la vida diaria {hitap}. Se enfatiza la facilidad de uso.",
        "ar": "يتم عرض لحظة استخدام حقيقي لـ {product_name} مع لمحة من حياة {hitap} اليومية. يتم التأكيد على سهولة الاستخدام.",
        "ru": "Реальный момент использования {product_name} показан с кадрами из повседневной жизни {hitap}. Подчёркивается простота использования.",
        "kr": "Dema bikaranîna rast a {product_name} bi dîmenek ji jiyana rojane ya {hitap} tê nîşandan. Hêsaniya bikaranînê tê diyar kirin.",
    },
    "desc_cta": {
        "tr": "{brand} logosu ve ürün bilgisi ekranda belirir. {hitap} {cagri} yönlendiren, {ton} bir kapanış mesajı.",
        "en": "{brand} logo and product info appear. A {ton} closing message directing {hitap} {cagri}.",
        "de": "{brand} Logo und Produktinfo erscheinen. Eine {ton} Abschlussbotschaft, die {hitap} {cagri} lenkt.",
        "fr": "Le logo {brand} et les infos produit apparaissent. Un message de clôture {ton} dirigeant {hitap} {cagri}.",
        "es": "El logo {brand} y la información del producto aparecen. Un mensaje de cierre {ton} que dirige {hitap} {cagri}.",
        "ar": "يظهر شعار {brand} ومعلومات المنتج. رسالة ختامية {ton} توجه {hitap} {cagri}.",
        "ru": "Логотип {brand} и информация о продукте появляются. {ton} завершающее сообщение, направляющее {hitap} {cagri}.",
        "kr": "Logoya {brand} û agahiyên berhemê xuya dibin. Peyamek dawî ya {ton} ku {hitap} {cagri}.",
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
    "scenario": SCENARIO,
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
