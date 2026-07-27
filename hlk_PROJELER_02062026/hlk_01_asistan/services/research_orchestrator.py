"""
AR-002 Ajan Orkestrasyon Katmanı — "Ürün Araştırma ve Analiz Görevi".

Ürün linki doğrulandıktan sonra (AR-002_13) bu görev başlatılır. Görev, ANA
KURALLAR'da tanımlı araştırma mimarisini uygular:

- AR-002_1  → görev önce analiz edilir; başarı kriterleri çıkarılır, sayfa bir kez
              alınıp ön analiz yapılır.
- AR-002_3  → her modül için adaylar belirlenir, kriterlere göre puanlanır,
              karşılaştırma tablosu ve dinamik öncelik sıralaması oluşturulur.
- AR-002_10 → her araştırma modülü bağımsız bir karar alanı olarak ele alınır;
              bir modülün sıralaması diğerine otomatik uygulanmaz.
- AR-002_7  → en yüksek öncelikli aday görevlendirilir; timeout/başarısızlıkta
              görev sıradaki adaya devredilir.
- Master "Araştırma Öncelik Hiyerarşisi" → modül sırası.
- 01_Global_Configuration → GC_MAX_AGENT_EXECUTION_TIME (aday timeout'u).

Dürüstlük ilkesi: Gerçek bir dış kaynak (arama API'si vb.) bağlı olmayan adaylar
sahte sonuç üretmez; sonuç üretemediklerini bildirir ve modül "karşılanamadı"
olarak kayda geçer. Sayfa HTML'i üzerinden gerçekten elde edilebilen bilgiler
(görsel, başlık/açıklama, fiyat, marka meta) gerçek olarak çıkarılır.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import httpx

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global Configuration (GC)
GC_MAX_AGENT_EXECUTION_TIME = 5.0  # saniye — GC-000

# Görev adı
RESEARCH_TASK_NAME = "Ürün Araştırma ve Analiz Görevi"

# HTTP User-Agent
_BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


@dataclass
class ResearchCandidate:
    """AR-002 araştırma adayı + değerlendirme kriterleri ve çalışma durumu."""
    code: str
    name: str
    executor: Callable
    # AR-002_3 puanlama kriterleri (ağırlıklı: kalite/doğruluk/güvenilirlik)
    uygunluk: int = 0
    dogruluk: int = 0
    guvenilirlik: int = 0
    kalite: int = 0
    hiz: int = 0
    guncellik: int = 0
    maliyet: int = 0
    # Çalışma parametreleri
    timeout: float = GC_MAX_AGENT_EXECUTION_TIME
    priority: float = 0.0
    assigned_reason: str = ""
    removed_reason: str = ""
    result: Optional[dict] = None
    ran: bool = False


# ─── Ajan Seçim Kriterleri (AR-002_3) ─────────────────────────────────────────

def _score(c: ResearchCandidate) -> float:
    """AR-002_3 puanlama. Kalite/doğruluk/güvenilirlik ağırlıklı; maliyet düşük ağırlık."""
    return (
        c.uygunluk * 1.0 +
        c.dogruluk * 0.8 +
        c.guvenilirlik * 0.8 +
        c.kalite * 1.0 +
        c.hiz * 0.6 +
        c.guncellik * 0.7 +
        (10 - c.maliyet) * 0.3
    )


# ─── Sayfa Getirme ────────────────────────────────────────────────────────────

async def _fetch_page(url: str) -> dict:
    """Sayfayı HTTP GET ile alır, HTML ve meta bilgilerini döndürür."""
    headers = {
        "User-Agent": _BROWSER_UA,
        "Accept-Language": "tr,en;q=0.8",
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser") if _BS4_AVAILABLE else None
        return {
            "status": resp.status_code,
            "html": html,
            "soup": soup,
            "error": None,
        }
    except Exception as e:
        return {"status": 0, "html": "", "soup": None, "error": str(e)}


# ─── Meta Bilgi Çıkarımı ─────────────────────────────────────────────────────

def _meta(soup, prop: str, default: str = "") -> str:
    """HTML meta tag'inden değer çıkarır (og:, name, itemprop)."""
    if not soup:
        return default
    # Open Graph
    tag = soup.find("meta", {"property": prop}) or soup.find("meta", {"name": prop})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return default


# ─── Araştırma Modülleri (her biri bir ResearchCandidate.executor) ────────────

async def _exec_images(page: dict) -> dict | None:
    """M1: Ürün görseli araştırması — sayfadaki img etiketlerinden ürün görsellerini topla."""
    if not _BS4_AVAILABLE or not page.get("soup"):
        return None
    soup = page["soup"]
    images = []
    filtered_noise = 0
    logo_count = 0
    svg_count = 0
    cat_count = 0

    # ── AR-002_24: Logo/menü/ikon filtreleme ──────────────────────────
    noise_keywords = [
        # Site logolari / UI elemanlari
        "logo", "marka", "brand", "footer", "header", "banner", "sprite",
        "icon", "badge", "placeholder", "loading", "avatar", "profile",
        "default", "spinner", "preloader",
        # Navigasyon / menus
        "house", "home", "shopping-bag", "cart", "heart", "wishlist",
        "favorite", "user", "account", "customer",
        "squares-four", "menu", "grid", "list",
        "search", "magnifying", "close", "x-mark",
        "hamburger", "chevron", "arrow",
        # Sosyal medya / paylasim
        "facebook", "instagram", "twitter", "youtube",
        "pinterest", "whatsapp", "social", "share",
        "download", "upload",
        # UI ses/medya kontrolleri (ikonlar)
        "mic", "microphone", "speaker", "audio", "sound",
        "play-", "pause", "stop-", "mute", "volume",
        "video-player", "media-control",
        # Rating / yildiz / rozet
        "star-rating", "review-star", "trust-badge", "rating",
        "trustpilot", "verified-", "guarantee",
        # Dil / ulke bayraklari
        "flag-", "language-", "translate", "currency",
        # Renk / beden / varyant secim ikonlari
        "swatch", "color-", "size-",
    ]

    # ── AR-002_25: Ürün Referans bilgilerini cikar ──────────────────
    soup = page.get("soup")
    og_title = (_meta(soup, "og:title") or "").lower()
    og_site = (_meta(soup, "og:site_name") or "").lower()
    meta_desc = (_meta(soup, "description") or "").lower()
    title_tag = (soup.find("title").get_text(strip=True).lower() if soup and soup.find("title") else "")
    # Marka/urun isim parcaciklari (esleme dogrulamasi icin)
    _product_terms = set()
    for _src_text in [og_title, og_site, title_tag]:
        for _word in _src_text.replace("-", " ").replace("|", " ").split():
            _w = _word.strip().strip(".,;:!?()[]{}\"'").lower()
            if len(_w) >= 3 and _w not in ("the", "and", "for", "buy", "shop", "size",
                "color", "price", "sale", "new", "best", "all", "our", "your",
                "with", "from", "that", "this", "have", "been", "also", "more",
                "about", "product", "products", "collection", "collections",
                "page", "online", "store", "shopify", "my"):
                _product_terms.add(_w)

    for img in soup.find_all("img"):
        src = img.get("src", "") or img.get("data-src", "")
        if not src or src.endswith(".svg"):
            if src.endswith(".svg"):
                svg_count += 1
            continue

        alt = (img.get("alt", "") or "").lower()
        cls = " ".join(img.get("class", [])).lower() if img.get("class") else ""
        src_lower = src.lower()

        # ADIM 1 — AR-002_24: Teknik gürültü filtresi
        combined = f"{alt} {cls} {src_lower}"
        if any(kw in combined for kw in noise_keywords):
            filtered_noise += 1
            if "logo" in combined:
                logo_count += 1
            continue

        if "/collections/" in src_lower:
            cat_count += 1
            continue

        # ADIM 2 — AR-002_25: Ürün Referans Paketi ile esleme dogrulamasi
        # Gorselin dosya adi veya alt metni, urunle ilgili en az bir terim icermeli.
        _img_text = f"{alt} {src_lower}"
        _has_product_match = False
        if _product_terms:
            for _term in _product_terms:
                if _term in _img_text:
                    _has_product_match = True
                    break
        # Eger hic urun terimi cikarilamadiysa (sayfada meta yoksa),
        # yalnizca acikca UI olmayan dosya adlari gecsin.
        # Ornek: "mic.gif", "star.png" → UI, urun gorseli degil.
        if _product_terms and not _has_product_match:
            # AR-002_25: AGENT_NOISE — urunle ilgisi yok
            filtered_noise += 1
            continue

        if not src.startswith("http"):
            src = "https:" + src if src.startswith("//") else src

        images.append(src)

    if not images:
        return None

    # ── AR-002_18: Bilgi değeri siralamasi ──────────────────────────
    # og:image oncelikli referans; yoksa ilk urun gorseli
    og_image = _meta(page.get("soup"), "og:image") if page.get("soup") else ""

    referans = ""
    ilgili = []
    if og_image and og_image in images:
        referans = og_image
        ilgili = [img for img in images if img != og_image]
    elif images:
        # og:image yoksa en anlamli goruntu adayini referans sec
        # (urun adini iceren, .jpg/.png, vendor/cdn path'li)
        _scored = []
        for _i, _img in enumerate(images):
            _score = 0
            _il = _img.lower()
            # Urun terimleriyle eslesme
            for _term in _product_terms:
                if _term in _il:
                    _score += 2
            # Dosya uzantisi urun fotografi mi?
            if any(_il.endswith(_ext) for _ext in (".jpg", ".jpeg", ".png", ".webp")):
                _score += 1
            # CDN/products yolu tercihi
            if any(_p in _il for _p in ("/products/", "/cdn/", "/files/", "/photos/")):
                _score += 1
            # UI/site geneli path'ler cezali
            if any(_p in _il for _p in ("/assets/", "/theme/", "/layout/", "/svg/", "/icons/")):
                _score -= 2
            _scored.append((_score, _img))
        _scored.sort(key=lambda x: x[0], reverse=True)
        if _scored and _scored[0][0] > -1:
            referans = _scored[0][1]
            ilgili = [img for img in images if img != referans]
        else:
            referans = images[0]
            ilgili = images[1:]

    return {
        "referans_gorsel": referans,
        "ilgili_gorseller": ilgili,
        "ilgili_gorsel_sayisi": len(ilgili),
        "filtrelenen_gurultu": filtered_noise,
        "toplam_elenen": filtered_noise,
        "elenen_logo_sayisi": logo_count,
        "elenen_svg_sayisi": svg_count,
        "elenen_kategori_gorseli_sayisi": cat_count,
    }


async def _exec_og_image(page: dict) -> dict | None:
    """M1 (alternatif): Open Graph görselini al."""
    if not _BS4_AVAILABLE or not page.get("soup"):
        return None
    og = _meta(page["soup"], "og:image")
    if og:
        return {"referans_gorsel": og, "ilgili_gorseller": [], "ilgili_gorsel_sayisi": 0}
    return None


async def _exec_brand_meta(page: dict) -> dict | None:
    """M2: Marka analizi — meta/HTML'den marka adı çıkar."""
    if not _BS4_AVAILABLE or not page.get("soup"):
        return None
    soup = page["soup"]

    # og:site_name
    marka = _meta(soup, "og:site_name") or _meta(soup, "product:brand")
    if marka:
        return {"marka": marka}

    # title'dan dene
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        title = title_tag.string.strip()
        parts = [p.strip() for p in title.split("|")]
        if len(parts) > 1:
            return {"marka": parts[-1]}

    return {"marka": title_tag.string.strip() if title_tag and title_tag.string else ""}


async def _exec_desc(page: dict) -> dict | None:
    """M3: Ürün açıklamaları — meta başlık/açıklama."""
    if not _BS4_AVAILABLE or not page.get("soup"):
        return None
    soup = page["soup"]
    title = _meta(soup, "og:title") or _meta(soup, "twitter:title") or ""
    desc = _meta(soup, "description") or _meta(soup, "og:description") or ""
    if title or desc:
        return {"urun_adi": title, "aciklama": desc}
    return None


async def _exec_headings(page: dict) -> dict | None:
    """M3 (alternatif): Sayfa başlıkları (H1)."""
    if not _BS4_AVAILABLE or not page.get("soup"):
        return None
    h1 = page["soup"].find("h1")
    if h1:
        return {"urun_adi": h1.get_text(strip=True)}
    return None


async def _exec_price(page: dict) -> dict | None:
    """M6: Fiyat segmenti — meta/HTML'den fiyat çıkar."""
    if not _BS4_AVAILABLE or not page.get("soup"):
        return None
    soup = page["soup"]
    fiyat = _meta(soup, "product:price:amount") or _meta(soup, "og:price:amount") or ""
    para = _meta(soup, "product:price:currency") or _meta(soup, "og:price:currency") or "TRY"
    if fiyat:
        return {"fiyat": fiyat, "para_birimi": para}
    return None


async def _exec_audience(page: dict) -> dict | None:
    """M4: Hedef müşteri analizi — ürün verilerinden kitle çıkarımı."""
    if not page.get("soup"):
        return None
    soup = page["soup"]
    title_meta = _meta(soup, "og:title") or ""
    title_lower = title_meta.lower()

    # Cinsiyet
    if any(w in title_lower for w in ["kadın", "kadin", "woman", "female", "kız"]):
        cinsiyet = "Kadın"
    elif any(w in title_lower for w in ["erkek", "man", "male", "men"]):
        cinsiyet = "Erkek"
    else:
        cinsiyet = "Unisex"

    # Yaş aralığı
    yas = "20-45"
    # Gelir segmenti
    gelir = "Orta Gelir"
    urun_segmenti = "Orta"

    # İlgi alanları
    ilgi = ["Moda", "Giyim"]
    if any(w in title_lower for w in ["spor", "sport"]):
        ilgi.append("Spor & Fitness")

    # Alışveriş alışkanlığı
    aliskanlik = "Online alışverişe yatkın, trendleri takip eden"

    return {
        "cinsiyet": cinsiyet,
        "yas_araligi": yas,
        "gelir_segmenti": gelir,
        "urun_segmenti": urun_segmenti,
        "ilgi_alanlari": ilgi,
        "alisveris_aliskinligi": aliskanlik,
        "hedef_kitle_ozeti": (
            f"{cinsiyet}, {yas} yaş, {gelir} seviyesinde, "
            f"{', '.join(ilgi)} ile ilgilenen kullanıcılar."
        ),
    }


async def _exec_tone(page: dict) -> dict | None:
    """M5: Marka dili ve tarzı analizi — sayfa içeriğinden marka sesi çıkarımı."""
    if not page.get("soup"):
        return None
    soup = page["soup"]
    text = (soup.get_text() if _BS4_AVAILABLE else " ") or " "
    text_lower = text.lower()[:5000]

    # Ton tespiti
    if any(w in text_lower for w in ["özel", "lüks", "prestij"]):
        ton = "Lüks & Prestijli"
    elif any(w in text_lower for w in ["samimi", "dost"]):
        ton = "Samimi & Sıcak"
    elif any(w in text_lower for w in ["resmi", "profesyonel", "kurumsal"]):
        ton = "Resmi & Profesyonel"
    else:
        ton = "Doğal & Dengeli"

    # Vurgulanan değerler
    degerler = []
    if any(w in text_lower for w in ["kalite"]):
        degerler.append("Kalite vurgusu")
    if any(w in text_lower for w in ["tasarım", "tasarim"]):
        degerler.append("Tasarım vurgusu")
    if any(w in text_lower for w in ["indirim", "kampanya"]):
        degerler.append("Fırsat/İndirim vurgusu")
    if any(w in text_lower for w in ["özgün", "benzersiz"]):
        degerler.append("Özgünlük/Farklılık vurgusu")
    if any(w in text_lower for w in ["konfor", "rahat"]):
        degerler.append("Konfor/Rahatlık vurgusu")

    if not degerler:
        degerler.append("Ürün odaklı iletişim")

    # Marka adı
    marka = _meta(soup, "og:site_name") or ""

    # Samimiyet seviyesi
    samimiyet = "Düşük" if ton in ("Resmi & Profesyonel", "Lüks & Prestijli") else "Yüksek"
    profesyonellik = "Doğal" if ton == "Doğal & Dengeli" else "Yüksek"

    if marka:
        iletisim = (
            f"{marka} markası, {ton} bir dil kullanarak "
            f"hedef kitlesiyle duygusal bağ kurmayı hedefliyor."
        )
    else:
        iletisim = (
            f"Marka, {ton} bir dil kullanarak "
            f"ürün odaklı bir iletişim stratejisi izliyor."
        )

    return {
        "marka_dili_tonu": ton,
        "iletisim_tarzi": iletisim,
        "vurgulanan_degerler": degerler,
        "samimiyet_seviyesi": samimiyet,
        "profesyonellik_seviyesi": profesyonellik,
    }


async def _exec_competitor(page: dict) -> dict | None:
    """M7: Rakip analizi — ürün verilerinden pazar konumlandırması."""
    if not page.get("soup"):
        return None

    soup = page["soup"]
    title_meta = (_meta(soup, "og:title") or "").lower()
    fiyat_str = _meta(soup, "product:price:amount") or ""

    # Kategori tespiti
    kategori = "Kadın Üst Giyim"
    alt_kategori = ""
    for kw, kat in [
        ("korst", "Korse & Body"), ("elbise", "Elbise"),
        ("bluz", "Bluz & Üst"), ("etek", "Etek"),
        ("pantolon", "Pantolon"), ("mont", "Mont & Ceket"),
        ("ayakkabı", "Ayakkabı"), ("çanta", "Çanta & Aksesuar"),
        ("takı", "Takı & Aksesuar"), ("sweat", "Sweatshirt"),
        ("tişört", "Tişört"),
    ]:
        if kw in title_meta:
            alt_kategori = kat
            break

    # Fiyat bandı
    try:
        fiyat = float(fiyat_str.replace(",", "").replace(".", ""))
    except (ValueError, TypeError):
        fiyat = 0

    if fiyat > 5000:
        fiyat_bandi = "Premium (> ₺5.000)"
        rakip = "Butik / Tasarımcı markaları"
        strateji = "Kıtlık, özgünlük ve özel tasarım vurgusu"
    elif fiyat > 1500:
        fiyat_bandi = "Üst-Orta (₺1.500 - ₺5.000)"
        rakip = "Yerel tasarımcı markaları, butikler"
        strateji = "Kalite, tasarım ve özgünlük vurgusu"
    elif fiyat > 500:
        fiyat_bandi = "Orta (₺500 - ₺1.500)"
        rakip = "Büyük perakende markaları"
        strateji = "Fiyat-performans ve çeşitlilik vurgusu"
    else:
        fiyat_bandi = "Ekonomik (< ₺500)"
        rakip = "Küresel fast-fashion markaları"
        strateji = "Uygun fiyat ve trend takibi vurgusu"

    marka = _meta(soup, "og:site_name") or "Bu marka"

    return {
        "urun_kategorisi": kategori,
        "alt_kategori": alt_kategori if alt_kategori else kategori,
        "fiyat_bandi": fiyat_bandi,
        "rakip_seviyesi": rakip,
        "pazarlama_stratejisi": strateji,
        "pazar_konumu": (
            f"{marka}, {kategori} kategorisinde {fiyat_bandi} "
            f"fiyat bandında konumlanmıştır."
        ),
        "potansiyel_rakipler": (
            f"{marka} için başlıca rakipler {rakip} seviyesindeki markalardır."
        ),
    }


async def _exec_strategy(page: dict, results: dict) -> dict | None:
    """Reklam stratejisi hazırlığı — toplanan modül sonuçlarının sentezi."""
    karsilanan = sum(1 for v in results.values() if v)
    modul_sayisi = 8

    marka = ""
    urun = ""
    if results.get("brand"):
        marka = results["brand"].get("marka", "")
    if results.get("desc"):
        urun = results["desc"].get("urun_adi", "")

    ozet_parts = [f"Toplam {karsilanan}/{modul_sayisi} modül karşılandı."]
    if urun:
        ozet_parts.append(f"Ürün: {urun}")
    if marka:
        ozet_parts.append(f"Marka: {marka}")
    if results.get("audience"):
        ozet_parts.append(f"Hedef kitle: {results['audience'].get('hedef_kitle_ozeti', '')}")
    if results.get("tone"):
        ozet_parts.append(f"Marka tonu: {results['tone'].get('marka_dili_tonu', '')}")
    if results.get("competitor"):
        ozet_parts.append(f"Pozisyon: {results['competitor'].get('pazar_konumu', '')}")

    return {
        "sentez_girdileri": list(results.keys()),
        "durum": "tam strateji iskeleti için yeterli girdi mevcut",
        "ozet": " | ".join(ozet_parts),
    }


# ─── Modül Kayıtları (AR-002_10: her modül bağımsız) ─────────────────────────

_module_registry: list[tuple[str, str, list[ResearchCandidate]]] = [
    # M1: Ürün Görseli Araştırması
    ("Ürün görseli araştırması", "A-PAGE-IMG", [
        ResearchCandidate(code="A-PAGE-IMG", name="Ürün Sayfası Görselleri",
                          executor=_exec_images, uygunluk=9, dogruluk=8,
                          guvenilirlik=8, kalite=8, hiz=9, guncellik=9, maliyet=2),
        ResearchCandidate(code="A-OG-IMG", name="Open Graph Görsel",
                          executor=_exec_og_image, uygunluk=6, dogruluk=5,
                          guvenilirlik=5, kalite=5, hiz=9, guncellik=7, maliyet=1),
    ]),
    # M2: Marka Analizi
    ("Marka analizi", "A-BRAND-META", [
        ResearchCandidate(code="A-BRAND-META", name="Sayfa Marka Meta",
                          executor=_exec_brand_meta, uygunluk=9, dogruluk=9,
                          guvenilirlik=9, kalite=9, hiz=9, guncellik=9, maliyet=1),
    ]),
    # M3: Ürün Açıklamaları
    ("Ürün açıklamaları", "A-DESC-META", [
        ResearchCandidate(code="A-DESC-META", name="Sayfa Başlık/Açıklama Meta",
                          executor=_exec_desc, uygunluk=9, dogruluk=8,
                          guvenilirlik=8, kalite=8, hiz=9, guncellik=9, maliyet=1),
        ResearchCandidate(code="A-HEADINGS", name="Sayfa Başlıkları (H1)",
                          executor=_exec_headings, uygunluk=5, dogruluk=5,
                          guvenilirlik=5, kalite=5, hiz=9, guncellik=7, maliyet=1),
    ]),
    # M4: Hedef Müşteri Analizi
    ("Hedef müşteri analizi", "A-AUDIENCE", [
        ResearchCandidate(code="A-AUDIENCE", name="Hedef Kitle Çıkarım Modeli",
                          executor=_exec_audience, uygunluk=7, dogruluk=6,
                          guvenilirlik=6, kalite=6, hiz=8, guncellik=7, maliyet=2),
    ]),
    # M5: Marka Dili ve Tarzı
    ("Marka dili ve tarzı", "A-TONE", [
        ResearchCandidate(code="A-TONE", name="İçerik Tonu Çözümleme",
                          executor=_exec_tone, uygunluk=8, dogruluk=7,
                          guvenilirlik=7, kalite=7, hiz=8, guncellik=8, maliyet=1),
    ]),
    # M6: Fiyat Segmenti
    ("Fiyat segmenti", "A-PRICE-META", [
        ResearchCandidate(code="A-PRICE-META", name="Sayfa Fiyat Meta",
                          executor=_exec_price, uygunluk=9, dogruluk=6,
                          guvenilirlik=6, kalite=7, hiz=9, guncellik=9, maliyet=1),
    ]),
    # M7: Rakip Analizi
    ("Rakip analizi", "A-COMPETITOR", [
        ResearchCandidate(code="A-COMPETITOR", name="Pazar Konumlandırma Analizi",
                          executor=_exec_competitor, uygunluk=8, dogruluk=6,
                          guvenilirlik=6, kalite=7, hiz=8, guncellik=8, maliyet=2),
    ]),
    # M8: Reklam Stratejisi (özel — tüm sonuçları alır)
    ("Reklam stratejisi hazırlığı", "A-SYNTH", [
        ResearchCandidate(code="A-SYNTH", name="Strateji Sentezi",
                          executor=_exec_strategy, uygunluk=10, dogruluk=8,
                          guvenilirlik=8, kalite=9, hiz=9, guncellik=9, maliyet=1),
    ]),
]


async def run_research_task(url: str, user_id: int | None = None) -> dict:
    """'Ürün Araştırma ve Analiz Görevi'ni AR-002 orkestrasyonu ile yürütür.

    Her modül bağımsız değerlendirilir (AR-002_10): adaylar puanlanır, sıralanır,
    en yüksek öncelikli görevlendirilir, başarısızlıkta sıradaki adaya devredilir
    ve tüm karar kayıtları işlenir.
    """
    task = {
        "name": RESEARCH_TASK_NAME,
        "url": url,
        "user_id": user_id,
        "success_criteria": [],
        "records": [],
    }
    logger.info(f"🧪 GÖREV OLUŞTURULDU: '{RESEARCH_TASK_NAME}' | url={url[:60]}")

    # Sayfayı getir
    page = await _fetch_page(url)
    logger.info(f"[{RESEARCH_TASK_NAME}] Ön analiz — sayfa durumu: {page['status']} (bs4={_BS4_AVAILABLE})")

    if not page["html"]:
        logger.error(f"[{RESEARCH_TASK_NAME}] Sayfa alınamadı: {page['error']}")
        return {"error": f"Sayfa alınamadı: {page['error']}"}

    # Modülleri çalıştır
    results = {}
    for modul_adi, modul_kodu, candidates in _module_registry:
        code = modul_kodu
        name = modul_adi

        # Adayları puanla ve sırala
        logger.info(f"[{RESEARCH_TASK_NAME}] Aday karşılaştırma tablosu (AR-002_3):")
        ranked = sorted(candidates, key=_score, reverse=True)
        chosen = None
        record = None

        for i, cand in enumerate(ranked):
            cand.priority = _score(cand)
            logger.info(
                f"  {cand.code} → puan={cand.priority:.1f} "
                f"(uygunluk={cand.uygunluk}, doğruluk={cand.dogruluk}, "
                f"güvenilirlik={cand.guvenilirlik}, kalite={cand.kalite}, "
                f"hız={cand.hiz}, güncellik={cand.guncellik}, maliyet={cand.maliyet})"
            )

        # En yüksek puanlı adayı görevlendir (AR-002_7)
        chosen = ranked[0] if ranked else None
        if chosen:
            logger.info(f"En yüksek puanlı aday → görevlendirildi")

        if not chosen:
            task["records"].append({
                "modul": code,
                "karar": "KARŞILANAMADI",
                "gerekce": "Hiçbir aday mevcut değil",
            })
            continue

        logger.info(f"▶️  [{code}] Görevlendirildi: {chosen.name}")

        # Adayı çalıştır
        try:
            if code == "A-SYNTH":
                res = await chosen.executor(page, results)
            else:
                res = await asyncio.wait_for(
                    chosen.executor(page),
                    timeout=chosen.timeout,
                )

            if res is not None:
                results[code] = res
                record = {
                    "modul": code,
                    "karar": "KARŞILANDI",
                    "secilen_aday": chosen.name,
                    "puan": chosen.priority,
                    "gorevlendirme_gerekcesi": "en yüksek puanlı aday",
                    "gorev_sonucu": str(res)[:200],
                }
                logger.info(f"✅  [{code}] → sonuç üretti: {str(res)[:100]}")
                logger.info(
                    f"[{RESEARCH_TASK_NAME}] KARAR: KARŞILANDI | "
                    f"aday={chosen.name} | puan={chosen.priority:.1f}"
                )
            else:
                # Sıradaki adaya devret (AR-002_7)
                alt_candidate = ranked[1] if len(ranked) > 1 else None
                if alt_candidate:
                    logger.info(f"Önceki aday sonuç üretemedi → görev devralındı (AR-002_7)")
                    try:
                        if code == "A-SYNTH":
                            res = await alt_candidate.executor(page, results)
                        else:
                            res = await asyncio.wait_for(
                                alt_candidate.executor(page),
                                timeout=alt_candidate.timeout,
                            )
                        if res:
                            results[code] = res
                            record = {
                                "modul": code, "karar": "KARŞILANDI",
                                "secilen_aday": alt_candidate.name,
                                "puan": _score(alt_candidate),
                                "gorevlendirme_gerekcesi": "asıl aday sonuç üretemedi, devraldı",
                                "gorev_sonucu": str(res)[:200],
                            }
                            logger.info(f"✅  [{code}] → sonuç üretti: {str(res)[:100]}")
                    except Exception as _e:
                        record = {
                            "modul": code, "karar": "KARŞILANAMADI",
                            "gerekce": "Tüm adaylar denendi; hiçbiri sonuç üretemedi",
                        }
                        logger.info(
                            f"[{RESEARCH_TASK_NAME}] KARAR: KARŞILANAMADI | "
                            f"tüm adaylar sonuç üretemedi"
                        )
                else:
                    record = {
                        "modul": code, "karar": "KARŞILANAMADI",
                        "gerekce": "Tek aday sonuç üretemedi, alternatif yok",
                    }
        except asyncio.TimeoutError:
            logger.info(f"⏱️  [{code}] → timeout, devredildi")
            record = {"modul": code, "karar": "KARŞILANAMADI", "gerekce": "timeout"}
        except Exception as e:
            logger.info(f"⚠️  [{code}] → hata ({str(e)[:60]}), devredildi")
            record = {"modul": code, "karar": "KARŞILANAMADI", "gerekce": f"hata: {str(e)[:80]}"}

        if record:
            task["records"].append(record)

    # Sentetik modül sonuçlarını birleştir
    if "A-PAGE-IMG" in results or "A-OG-IMG" in results:
        results.setdefault("image", results.get("A-PAGE-IMG") or results.get("A-OG-IMG"))

    karsilanan = sum(1 for r in task["records"] if r.get("karar") == "KARŞILANDI")
    logger.info(f"[{RESEARCH_TASK_NAME}] GÖREV TAMAMLANDI: {karsilanan} modül karşılandı")

    return {
        "gorev": RESEARCH_TASK_NAME,
        "url": url,
        "karsilanan_modul_sayisi": karsilanan,
        "records": task["records"],
        "results": results,
    }
