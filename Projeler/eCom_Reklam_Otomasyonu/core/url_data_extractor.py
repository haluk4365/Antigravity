from __future__ import annotations

"""
URL Data Extractor — Deterministik Ürün Veri Çıkarma
======================================================
E-ticaret URL'sinden tek seferde tam ürün verisi çıkarır.

Pipeline:
1. Short-link'leri expand eder ve normalize eder.
2. Direct requests ile HTML kazır ve JSON-LD/meta veriyi parse eder (0 kredi, hızlı).
3. Direct requests başarısız olursa Firecrawl ile scrape eder.
4. LLM (GPT-4.1 Mini) ile structured data extraction (konsept ve hedef kitle).
5. LLM Vision ile en iyi 1-3 ürün görseli seçimi.
"""

import re
import json
import html
import asyncio
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import requests

from logger import get_logger

log = get_logger("url_data_extractor")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM PROMPT — Ürün Verisi Çıkarma
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXTRACTION_PROMPT = """Sen bir e-ticaret ürün analiz uzmanısın. Aşağıdaki web sayfası verisinden şu bilgileri JSON formatında çıkar.

## Kurallar:
- Sayfada açıkça bulamadığın bilgileri makul şekilde çıkar (örn: marka adı domain'den anlaşılabilir)
- ad_concept alanı için ürüne uygun, kısa ve etkileyici bir Türkçe reklam konsepti üret
- target_audience alanı için ürünün doğal hedef kitlesini belirle
- Bütün Türkçe metinler (reklam konsepti, hedef kitle vb.) kusursuz, net ve gerçek Türkçe kelimelerle yazılmalıdır. Asla harf karmaşası, uydurma veya anlamsız kelimeler (gibberish) içermemelidir.
- Yanıtın SADECE JSON olmalı, başka hiçbir metin ekleme

## Çıkarılacak JSON formatı:
{{
    "brand_name": "Marka adı",
    "product_name": "Ürün adı (kısa ve net)",
    "product_description": "Ürünün 2-3 cümlelik açıklaması",
    "ad_concept": "Kısa, etkileyici Türkçe reklam konsepti (1-2 cümle, sinematik ve dinamik)",
    "target_audience": "Hedef kitle tanımı (1 cümle)",
    "product_category": "Ürün kategorisi (örn: Elektronik, Giyim, Kozmetik, Mobilya)"
}}

## Sayfa Verisi:
---
{page_content}
---"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM PROMPT — En İyi Görsel Seçimi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMAGE_SELECTION_PROMPT = """Aşağıdaki ürün görsellerini incele. Bu görseller bir AI video modeline (Seedance 2.0) REFERANS GÖRSEL olarak verilecek. Model bu görsellere bakarak video üretecek. Bu yüzden sadece ÜRÜNÜN FİZİKSEL görsellerini seç.

## Seçim Kriterleri (öncelik sırasına göre):
1. Ürünü en net ve yüksek kalitede gösteren
2. Reklam için en etkileyici açıya sahip
3. Arka planı temiz veya profesyonel
4. Ürünün tamamını gösteren (kırpılmamış)

## Kurallar:
- En az 1, en fazla 3 görsel seç
- Seçtiğin görseller BİRBİRİNDEN FARKLI (çeşitli açılar/pozlar) olmalıdır. Aynı veya çok benzer fotoğrafların kopyalarını birlikte seçme. Çeşitlilik sağla.
- Seçtiğin görsellerin indeks numaralarını JSON array olarak döndür
- SADECE JSON döndür: {{"selected_indices": [0, 2, 4]}}

## ASLA SEÇME (bu türler video referansı olarak UYGUN DEĞİLDİR):
- Üzerinde yazı/metin bulunan infografikler (örn: "Ne zaman uygulanır?", "Nasıl kullanılır?", özellik tabloları)
- Kullanım talimatı veya adım adım uygulama görselleri
- Boyut karşılaştırma, before/after kolaj görselleri
- İçerik listesi, sertifika veya uyarı görselleri
- Logo, ikon, banner veya web sitesi UI elementleri
- Düşük çözünürlüklü veya bulanık görseller
- Lifestyle görselleri (ürünün kendisi NET görünmüyorsa)

## SADECE SEÇ:
- Ürünün ambalajını/şişesini/kutusunu net gösteren fotoğraflar
- Ürünün kendisinin yakın çekim (close-up) fotoğrafları
- Ürünün profesyonel stüdyo çekimleri

## Görsel URL Listesi:
{image_list}"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM PROMPT — Lite (hızlı kategori)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LITE_EXTRACTION_PROMPT = """Aşağıdaki sayfa başlığı/meta bilgisinden ürün için kısa kategori çıkarımı yap.

## Kurallar:
- SADECE JSON döndür, başka metin ekleme.
- category alanı ŞU listeden bir tanesi olsun (en yakın olanı seç): skincare, beauty, fashion, tech, food, supplement, accessory, home, fitness, kids, pet, jewelry, automotive, general.
- brand_name domain'den veya başlıktan tahmin edilebilir.
- product_name kısa ve net olsun.

## Çıktı formatı:
{{
    "brand_name": "Marka",
    "product_name": "Ürün adı",
    "category": "kategori_kodu"
}}

## Sayfa Bilgisi:
---
{page_brief}
---"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JSON-LD VE PLATFORM ÖZEL PARSERLAR (YARDIMCI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def find_json_object(text: str, start_marker: str) -> str | None:
    idx = text.find(start_marker)
    if idx == -1:
        return None
    sub = text[idx + len(start_marker):].strip()
    first_brace = sub.find("{")
    if first_brace == -1:
        return None
    sub = sub[first_brace:]
    
    brace_count = 0
    in_string = False
    escape_next = False
    json_chars = []
    
    for char in sub:
        json_chars.append(char)
        if escape_next:
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            continue
            
        if char == '"':
            in_string = not in_string
            continue
            
        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    break
                    
    if brace_count == 0:
        return "".join(json_chars)
    return None


def find_product_in_json(obj):
    if isinstance(obj, dict):
        type_val = obj.get("@type")
        if isinstance(type_val, str) and (type_val.lower() == "product" or type_val.endswith("/Product")):
            return obj
        if isinstance(type_val, list) and any(isinstance(t, str) and (t.lower() == "product" or t.endswith("/Product")) for t in type_val):
            return obj
        for val in obj.values():
            res = find_product_in_json(val)
            if res:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_product_in_json(item)
            if res:
                return res
    return None


def extract_from_json_ld(html_content: str) -> dict:
    blocks = []
    pattern = re.compile(
        r'<script\b[^>]*?type=["\']application/ld\+json["\'][^>]*?>(.*?)</script>',
        re.DOTALL | re.IGNORECASE
    )
    for match in pattern.finditer(html_content):
        content = match.group(1).strip()
        content = html.unescape(content)
        content = re.sub(r'^\s*//<!\[CDATA\[', '', content)
        content = re.sub(r'//\]\]>\s*$', '', content)
        content = re.sub(r'^\s*<!--', '', content)
        content = re.sub(r'-->\s*$', '', content)
        content = content.strip()
        try:
            parsed = json.loads(content)
            if parsed:
                blocks.append(parsed)
        except Exception:
            try:
                cleaned = "".join(ch for ch in content if ord(ch) >= 32 or ch in '\n\r\t')
                blocks.append(json.loads(cleaned))
            except Exception:
                pass
                
    for data in blocks:
        product_data = find_product_in_json(data)
        if product_data:
            result = {}
            result["product_name"] = product_data.get("name")
            
            brand_val = product_data.get("brand")
            if isinstance(brand_val, dict):
                result["brand_name"] = brand_val.get("name")
            elif isinstance(brand_val, str):
                result["brand_name"] = brand_val
                
            result["product_description"] = product_data.get("description")
            
            img_val = product_data.get("image")
            images = []
            if isinstance(img_val, list):
                for img in img_val:
                    if isinstance(img, str):
                        images.append(img)
                    elif isinstance(img, dict) and img.get("url"):
                        images.append(img.get("url"))
            elif isinstance(img_val, str):
                images.append(img_val)
            elif isinstance(img_val, dict) and img_val.get("url"):
                images.append(img_val.get("url"))
            result["image_urls"] = images
            
            offers = product_data.get("offers")
            if offers:
                if isinstance(offers, list):
                    offer = offers[0]
                else:
                    offer = offers
                price = offer.get("price")
                currency = offer.get("priceCurrency")
                if price is not None:
                    result["price"] = f"{price} {currency}" if currency else str(price)
                    result["raw_price"] = price
                    result["currency"] = currency
                    
            rating = product_data.get("aggregateRating")
            if rating:
                rating_val = rating.get("ratingValue")
                review_count = rating.get("reviewCount") or rating.get("ratingCount")
                if rating_val is not None:
                    result["rating"] = str(rating_val)
                if review_count is not None:
                    result["review_count"] = int(review_count)
                    
            category_val = product_data.get("category")
            if isinstance(category_val, str):
                result["product_category"] = category_val
                
            canonical = product_data.get("url")
            if canonical:
                result["canonical_url"] = canonical
                
            return {k: v for k, v in result.items() if v is not None}
            
    return {}


def extract_trendyol_state(html_content: str) -> dict:
    json_str = find_json_object(html_content, "window.__PRODUCT_DETAIL_APP_INITIAL_STATE__")
    if json_str:
        try:
            state = json.loads(json_str)
            product = state.get("product", {})
            
            name = product.get("name") or product.get("nameWithProductCode")
            brand = product.get("brand", {}).get("name") if isinstance(product.get("brand"), dict) else None
            
            images = []
            raw_images = product.get("images", [])
            for img in raw_images:
                if isinstance(img, str):
                    img_url = img
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                    elif img_url.startswith("/"):
                        img_url = "https://cdn.dsmcdn.com" + img_url
                    images.append(img_url)
                elif isinstance(img, dict) and img.get("url"):
                    img_url = img.get("url")
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                    images.append(img_url)
            
            price_val = None
            price_info = product.get("price", {})
            if price_info:
                price_val = price_info.get("discountedPrice") or price_info.get("sellingPrice") or price_info.get("originalPrice")
            
            desc = product.get("description", "")
            if desc:
                desc = re.sub(r'<[^>]+>', ' ', desc).strip()
            
            category = product.get("category", {}).get("name") if isinstance(product.get("category"), dict) else None
            
            rating = None
            review_count = None
            rating_info = product.get("ratingScore", {})
            if rating_info:
                rating = rating_info.get("averageRating")
                review_count = rating_info.get("totalCommentCount")
                
            return {
                "product_name": name,
                "brand_name": brand,
                "image_urls": images,
                "price": f"{price_val} TL" if price_val else None,
                "raw_price": price_val,
                "currency": "TRY",
                "product_description": desc,
                "product_category": category,
                "rating": str(rating) if rating else None,
                "review_count": int(review_count) if review_count else None,
            }
        except Exception as e:
            log.warning(f"Error parsing Trendyol state: {e}")
    return {}


def extract_amazon_details(html_content: str) -> dict:
    res = {}
    title_m = re.search(r'<span[^>]*?id=["\']productTitle["\'][^>]*?>(.*?)</span>', html_content, re.DOTALL | re.IGNORECASE)
    if title_m:
        res["product_name"] = html.unescape(title_m.group(1).strip())
    
    brand_m = re.search(r'<a[^>]*?id=["\']bylineInfo["\'][^>]*?>(.*?)</a>', html_content, re.DOTALL | re.IGNORECASE)
    if brand_m:
        brand_text = html.unescape(brand_m.group(1).strip())
        brand_text = re.sub(r'^(Brand:\s*|Marka:\s*|Visit the\s*|\bStore\b)', '', brand_text, flags=re.IGNORECASE).strip()
        res["brand_name"] = brand_text
        
    price_m = re.search(r'<span class="a-price-whole">(.*?)<span class="a-price-decimal">', html_content, re.DOTALL | re.IGNORECASE)
    if price_m:
        whole = re.sub(r'<[^>]+>', '', price_m.group(1)).strip()
        frac_m = re.search(r'<span class="a-price-fraction">(.*?)</span>', html_content, re.DOTALL | re.IGNORECASE)
        frac = frac_m.group(1).strip() if frac_m else "00"
        res["price"] = f"{whole}.{frac}"
    else:
        price_alt = re.search(r'<span class="a-offscreen">(.*?)</span>', html_content, re.IGNORECASE)
        if price_alt:
            res["price"] = html.unescape(price_alt.group(1).strip())
            
    desc_m = re.search(r'<div[^>]*?id=["\']productDescription["\'][^>]*?>(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
    if desc_m:
        res["product_description"] = re.sub(r'<[^>]+>', ' ', desc_m.group(1)).strip()
        
    gallery_str = find_json_object(html_content, "colorImages")
    images = []
    if gallery_str:
        try:
            gallery_data = json.loads(gallery_str)
            # Sometimes gallery_data is a dict mapping color to list of image dicts,
            # or it is a list of image dicts directly, or a dict containing 'initial' key
            if isinstance(gallery_data, dict):
                # If there's an 'initial' key, or other keys, extract images from list
                for val in gallery_data.values():
                    if isinstance(val, list):
                        for img in val:
                            if isinstance(img, dict):
                                img_url = img.get("hiRes") or img.get("large") or img.get("main", {}).get("url")
                                if img_url and img_url not in images:
                                    images.append(img_url)
                    elif isinstance(val, dict):
                        img_url = val.get("hiRes") or val.get("large") or val.get("url")
                        if img_url and img_url not in images:
                            images.append(img_url)
            elif isinstance(gallery_data, list):
                for img in gallery_data:
                    if isinstance(img, dict):
                        img_url = img.get("hiRes") or img.get("large") or img.get("main", {}).get("url")
                        if img_url and img_url not in images:
                            images.append(img_url)
        except Exception as e:
            log.warning(f"Error parsing Amazon colorImages JSON: {e}")
    if not images:
        landing_img = re.search(r'<img[^>]*?id=["\']landingImage["\'][^>]*?data-a-dynamic-image=["\'](.*?)["\']', html_content, re.IGNORECASE)
        if landing_img:
            try:
                img_dict = json.loads(html.unescape(landing_img.group(1)))
                images = list(img_dict.keys())
            except Exception:
                pass
    res["image_urls"] = images
    
    rating_m = re.search(r'<span class="a-icon-alt">(.*?)</span>', html_content, re.IGNORECASE)
    if rating_m:
        res["rating"] = rating_m.group(1).strip()
    reviews_m = re.search(r'<span id="acrCustomerReviewText"[^>]*>(.*?)</span>', html_content, re.IGNORECASE)
    if reviews_m:
        res["review_count"] = reviews_m.group(1).strip()
        
    return {k: v for k, v in res.items() if v}


def extract_generic_metadata(html_content: str) -> dict:
    res = {}
    title_m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if not title_m:
        title_m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']', html_content, re.IGNORECASE)
    if not title_m:
        title_m = re.search(r'<meta[^>]+name=["\']twitter:title["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if not title_m:
        title_m = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if title_m:
        res["product_name"] = html.unescape(title_m.group(1).strip())
        
    if not res.get("product_name"):
        h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        if h1_m:
            res["product_name"] = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip()

    brand_m = re.search(r'<meta[^>]+property=["\']og:brand["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if not brand_m:
        brand_m = re.search(r'<meta[^>]+name=["\']brand["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if not brand_m:
        brand_m = re.search(r'<meta[^>]+name=["\']shopify-vendor["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if brand_m:
        res["brand_name"] = html.unescape(brand_m.group(1).strip())
        
    price_m = re.search(r'<meta[^>]+property=["\']product:price:amount["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    curr_m = re.search(r'<meta[^>]+property=["\']product:price:currency["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if not price_m:
        price_m = re.search(r'<meta[^>]+property=["\']og:price:amount["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
        curr_m = re.search(r'<meta[^>]+property=["\']og:price:currency["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if price_m:
        price_val = price_m.group(1).strip()
        curr_val = curr_m.group(1).strip() if curr_m else ""
        res["price"] = f"{price_val} {curr_val}".strip()
        res["raw_price"] = price_val
        res["currency"] = curr_val

    images = []
    og_img_matches = re.finditer(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    for m in og_img_matches:
        img = html.unescape(m.group(1).strip())
        if img and img not in images:
            images.append(img)
    tw_img_m = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if tw_img_m:
        img = html.unescape(tw_img_m.group(1).strip())
        if img and img not in images:
            images.append(img)
    
    if not images:
        img_tags = re.findall(r'<img[^>]+src=["\'](https?://.*?)["\']', html_content, re.IGNORECASE)
        for img_url in img_tags:
            if not any(pattern in img_url.lower() for pattern in ["logo", "icon", "favicon", "sprite"]):
                if img_url not in images:
                    images.append(img_url)
    res["image_urls"] = images

    desc_m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if not desc_m:
        desc_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if desc_m:
        res["product_description"] = html.unescape(desc_m.group(1).strip())

    canonical_m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if canonical_m:
        res["canonical_url"] = html.unescape(canonical_m.group(1).strip())
        
    return {k: v for k, v in res.items() if v}


def parse_all_from_html(html_content: str, url: str) -> dict:
    # 1. Try JSON-LD first
    data = extract_from_json_ld(html_content)
    
    # 2. Try platform-specific parsing
    platform_data = {}
    if "trendyol.com" in url:
        platform_data = extract_trendyol_state(html_content)
    elif "amazon." in url:
        platform_data = extract_amazon_details(html_content)
        
    # Merge platform data
    for k, v in platform_data.items():
        if v and not data.get(k):
            data[k] = v
            
    # 3. Fallback to generic metadata
    generic_data = extract_generic_metadata(html_content)
    for k, v in generic_data.items():
        if not data.get(k):
            data[k] = v
        elif k == "image_urls" and not data["image_urls"]:
            data["image_urls"] = v
            
    # 4. Cleanups and Fallbacks
    if not data.get("brand_name"):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        domain = domain.replace("www.", "").split(".")[0].lower()
        if domain not in {"trendyol", "hepsiburada", "amazon", "temu", "etsy"}:
            data["brand_name"] = domain.capitalize()
            
    if not data.get("canonical_url"):
        data["canonical_url"] = url
        
    return data


class URLDataExtractor:
    """
    URL → Structured Data pipeline.

    Scrapes URL directly or falls back to Firecrawl, prioritizes JSON-LD extraction,
    normalizes URLs, expands short-links, and processes product details deterministically.
    """

    def __init__(
        self,
        openai_service,
        firecrawl_service,
    ):
        self.openai = openai_service
        self.firecrawl = firecrawl_service

    async def extract(self, url: str) -> dict:
        """
        URL'den tam ürün verisi çıkarır.
        """
        import asyncio

        log.info(f"URL veri çıkarma başlatılıyor: {url}")

        # 1. Expand and Normalize URL
        expanded_url = await self.expand_url_async(url)
        normalized_url = self.normalize_url(expanded_url)

        log.info(f"Orijinal: {url} -> Genişletilmiş: {expanded_url} -> Normalize: {normalized_url}")

        # 2. Try direct HTML scrape first (fast, 0 credits, priorities JSON-LD)
        html_content, source = await asyncio.to_thread(self._scrape_direct_html, normalized_url)

        # If direct html scrape failed or returned insufficient content, fall back to Firecrawl
        if not html_content or len(html_content) < 1000:
            log.info("Direct scraper yetersiz veya başarısız, Firecrawl fallback devreye giriyor...")
            fc_markdown, fc_image_urls, fc_metadata, fc_html, fc_source = await asyncio.to_thread(
                self._scrape_url_firecrawl, normalized_url
            )
            html_content = fc_html or ""
            parsed_data = self.parse_all_from_html(html_content, normalized_url) if html_content else {}
            
            if fc_markdown:
                parsed_data["page_content"] = fc_markdown
            if fc_image_urls:
                if "image_urls" not in parsed_data or not parsed_data["image_urls"]:
                    parsed_data["image_urls"] = fc_image_urls
            if fc_metadata:
                if "product_name" not in parsed_data or not parsed_data["product_name"]:
                    parsed_data["product_name"] = fc_metadata.get("title")
                if "product_description" not in parsed_data or not parsed_data["product_description"]:
                    parsed_data["product_description"] = fc_metadata.get("description")
            source = fc_source
        else:
            parsed_data = self.parse_all_from_html(html_content, normalized_url)
            text_content = re.sub(r"<style.*?</style>", "", html_content, flags=re.IGNORECASE | re.DOTALL)
            text_content = re.sub(r"<script.*?</script>", "", text_content, flags=re.IGNORECASE | re.DOTALL)
            text_content = re.sub(r"<[^>]+>", " ", text_content)
            text_content = re.sub(r"\s+", " ", text_content).strip()
            parsed_data["page_content"] = text_content[:5000]

        # Minimum required verification
        if not parsed_data.get("product_name") and not parsed_data.get("brand_name"):
            raise ValueError(
                f"URL'den hiçbir veri çıkarılamadı: {normalized_url}\n"
                "Lütfen farklı bir ürün linki deneyin."
            )

        # 3. LLM structured data extraction (generates Türkçe ad_concept and target_audience)
        extracted = await asyncio.to_thread(
            self._extract_structured_data, parsed_data.get("page_content", ""), parsed_data
        )

        result = {
            "brand_name": extracted.get("brand_name") or parsed_data.get("brand_name") or "",
            "product_name": extracted.get("product_name") or parsed_data.get("product_name") or "",
            "product_description": extracted.get("product_description") or parsed_data.get("product_description") or "",
            "ad_concept": extracted.get("ad_concept") or "Ürünü keşfet, farkı hisset.",
            "target_audience": extracted.get("target_audience") or "Genel tüketici",
            "product_category": extracted.get("product_category") or parsed_data.get("product_category") or "Genel",
            "canonical_url": parsed_data.get("canonical_url") or normalized_url,
            "price": parsed_data.get("price"),
            "rating": parsed_data.get("rating"),
            "review_count": parsed_data.get("review_count"),
            "raw_price": parsed_data.get("raw_price"),
            "currency": parsed_data.get("currency"),
        }

        # 4. Image selection
        image_urls = parsed_data.get("image_urls", [])
        best_images = await asyncio.to_thread(
            self._select_best_images, image_urls
        )

        result["best_image_urls"] = best_images
        result["all_image_urls"] = image_urls
        result["page_content"] = parsed_data.get("page_content", "")[:2000]
        result["extraction_source"] = source

        log.info(
            f"URL veri çıkarma tamamlandı: "
            f"marka='{result.get('brand_name')}', "
            f"ürün='{result.get('product_name')}', "
            f"fiyat='{result.get('price')}', "
            f"rating='{result.get('rating')}', "
            f"{len(best_images)} referans görsel, "
            f"kaynak={source}"
        )

        return result

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # INTERNAL METHODS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _scrape_direct_html(self, url: str) -> tuple[str | None, str]:
        try:
            log.info(f"Direct HTML scraping başlatılıyor: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                html_text = res.text
                if len(html_text) > 1000 and "body" in html_text.lower():
                    log.info(f"Direct HTML scraper başarılı: {len(html_text)} char")
                    return html_text, "direct_requests"
            log.warning(f"Direct HTML scraper yetersiz yanıt: status={res.status_code}, len={len(res.text) if res else 0}")
        except Exception as e:
            log.warning(f"Direct HTML scraper hatası: {e}")
        return None, "none"

    def _scrape_url_firecrawl(self, url: str) -> tuple[str, list[str], dict, str, str]:
        try:
            result = self.firecrawl.scrape(url)
            if result["success"]:
                markdown = result.get("markdown", "")
                html_content = result.get("html", "")
                metadata = result.get("metadata", {})
                image_urls = self.firecrawl.extract_images_from_markdown(markdown)

                og_image = metadata.get("ogImage")
                if og_image and og_image not in image_urls:
                    image_urls.insert(0, og_image)

                log.info(f"Firecrawl başarılı: {len(markdown)} char, {len(html_content)} html, {len(image_urls)} görsel")
                return markdown, image_urls, metadata, html_content, "firecrawl"

            log.warning(f"Firecrawl başarısız: {result.get('error')}")
        except Exception:
            log.warning("Firecrawl hatası", exc_info=True)
        return "", [], {}, "", "none"

    def _scrape_url(self, url: str) -> tuple[str, list[str], dict, str]:
        """Eski 1:1 Firecrawl API wrapper — geriye dönük uyumluluk için."""
        res = self._scrape_url_firecrawl(url)
        return res[0], res[1], res[2], res[4]

    def _extract_structured_data(self, page_content: str, metadata: dict) -> dict:
        enriched_content = ""
        if metadata:
            if metadata.get("product_name"):
                enriched_content += f"Ürün Adı: {metadata['product_name']}\n"
            if metadata.get("brand_name"):
                enriched_content += f"Marka: {metadata['brand_name']}\n"
            if metadata.get("price"):
                enriched_content += f"Fiyat: {metadata['price']}\n"
            if metadata.get("product_description"):
                enriched_content += f"Ürün Açıklaması: {metadata['product_description']}\n"
            if metadata.get("product_category"):
                enriched_content += f"Kategori: {metadata['product_category']}\n"
            if metadata.get("canonical_url"):
                enriched_content += f"Kaynak URL: {metadata['canonical_url']}\n"
            enriched_content += "---\n"

        TOTAL_BUDGET = 6000
        remaining_budget = max(500, TOTAL_BUDGET - len(enriched_content))
        enriched_content += page_content[:remaining_budget]

        prompt = EXTRACTION_PROMPT.format(page_content=enriched_content)

        try:
            messages = [
                {"role": "system", "content": "Sen bir JSON çıktı üreten asistansın. Her zaman geçerli JSON döndür."},
                {"role": "user", "content": prompt},
            ]

            result = self.openai.chat_json(messages, max_tokens=1000)

            required_fields = ["brand_name", "product_name", "ad_concept"]
            for field in required_fields:
                if not result.get(field):
                    log.warning(f"LLM çıkarma: '{field}' alanı boş, fallback uygulanıyor")
                    if field == "brand_name" and metadata.get("brand_name"):
                        result[field] = metadata["brand_name"]
                    elif field == "product_name" and metadata.get("product_name"):
                        result[field] = metadata["product_name"]

            log.info(
                f"LLM structured extraction tamamlandı: "
                f"marka='{result.get('brand_name')}', "
                f"ürün='{result.get('product_name')}'"
            )
            return result

        except Exception:
            log.error("LLM structured extraction hatası", exc_info=True)
            return {
                "brand_name": metadata.get("brand_name", "Bilinmeyen Marka"),
                "product_name": metadata.get("product_name", "Bilinmeyen Ürün"),
                "product_description": metadata.get("product_description", ""),
                "ad_concept": "Ürünü keşfet, farkı hisset.",
                "target_audience": "Genel tüketici",
                "product_category": metadata.get("product_category", "Genel"),
            }

    def _select_best_images(self, image_urls: list[str]) -> list[str]:
        if not image_urls:
            log.warning("Görsel URL'si bulunamadı — boş liste dönüyor")
            return []

        valid_urls = []
        seen_base_urls = set()
        
        for url in image_urls:
            if not self.openai._validate_image_url(url):
                continue
                
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.netloc}{parsed.path}"
            
            if base_url not in seen_base_urls:
                seen_base_urls.add(base_url)
                valid_urls.append(url)

        if not valid_urls:
            log.warning("Geçerli görsel URL'si bulunamadı (format filtresi sonrası)")
            return []

        if len(valid_urls) <= 3:
            log.info(f"3 veya daha az görsel var ({len(valid_urls)}) — hepsi seçildi")
            return valid_urls

        candidates = valid_urls[:10]

        try:
            image_list = "\n".join(
                f"[{i}] {url}" for i, url in enumerate(candidates)
            )
            prompt = IMAGE_SELECTION_PROMPT.format(image_list=image_list)

            content_list = [{"type": "text", "text": prompt}]
            for url in candidates:
                content_list.append({
                    "type": "image_url",
                    "image_url": {"url": url, "detail": "low"},
                })

            messages = [
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": content_list}
            ]

            response = self.openai.client.chat.completions.create(
                model=self.openai.model,
                messages=messages,
                max_completion_tokens=200,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                log.warning("Vision API boş yanıt döndürdü — ilk 3 görsel kullanılıyor")
                return candidates[:3]

            import json
            result = json.loads(content)
            selected_indices = result.get("selected_indices", [0])

            selected_urls = []
            for idx in selected_indices:
                if isinstance(idx, int) and 0 <= idx < len(candidates):
                    selected_urls.append(candidates[idx])

            if not selected_urls:
                log.warning("Vision geçersiz indeksler döndürdü — ilk görsel kullanılıyor")
                return [candidates[0]]

            log.info(f"Vision {len(candidates)} görsel arasından "
                     f"{len(selected_urls)} tanesini seçti: "
                     f"indeksler={selected_indices}")
            return selected_urls

        except Exception:
            log.warning("Vision görsel seçim hatası — ilk 3 görsel kullanılıyor",
                        exc_info=True)
            return candidates[:3]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ⚡ LITE EXTRACT — sadece kategori (5-10s)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def extract_lite(self, url: str) -> dict:
        """Hızlı kategori çıkarımı — sadece title/meta okur, görsel seçmez.
        """
        import asyncio

        log.info(f"⚡ Lite extract başlıyor: {url}")

        expanded_url = await self.expand_url_async(url)
        normalized_url = self.normalize_url(expanded_url)

        html_content, source = await asyncio.to_thread(self._scrape_direct_html, normalized_url)
        
        parsed_data = {}
        if html_content:
            parsed_data = self.parse_all_from_html(html_content, normalized_url)

        if parsed_data.get("product_name") and parsed_data.get("product_category"):
            log.info(f"⚡ Lite extract direct parse başarılı: category={parsed_data.get('product_category')}")
            return {
                "brand_name": parsed_data.get("brand_name") or "",
                "product_name": parsed_data.get("product_name") or "",
                "category": parsed_data.get("product_category").strip().lower(),
            }

        log.info("⚡ Lite extract: Direct parsing yetersiz veya boş, Firecrawl devreye giriyor...")
        try:
            result = await asyncio.to_thread(self.firecrawl.scrape, normalized_url)
        except Exception:
            log.warning("Lite extract: Firecrawl hatası", exc_info=True)
            return {"brand_name": "", "product_name": "", "category": "general"}

        if not result.get("success"):
            log.warning(f"Lite extract: Firecrawl başarısız — {result.get('error')}")
            return {"brand_name": "", "product_name": "", "category": "general"}

        metadata = result.get("metadata", {}) or {}
        markdown = result.get("markdown", "") or ""
        fc_html = result.get("html", "") or ""

        if fc_html:
            parsed_data = self.parse_all_from_html(fc_html, normalized_url)
            if parsed_data.get("product_name") and parsed_data.get("product_category"):
                return {
                    "brand_name": parsed_data.get("brand_name") or "",
                    "product_name": parsed_data.get("product_name") or "",
                    "category": parsed_data.get("product_category").strip().lower(),
                }

        page_brief_parts = []
        if metadata.get("title"):
            page_brief_parts.append(f"Başlık: {metadata['title']}")
        if metadata.get("description"):
            page_brief_parts.append(f"Meta Açıklama: {metadata['description']}")
        if metadata.get("ogTitle"):
            page_brief_parts.append(f"OG Başlık: {metadata['ogTitle']}")
        if metadata.get("ogDescription"):
            page_brief_parts.append(f"OG Açıklama: {metadata['ogDescription']}")
        if metadata.get("sourceURL"):
            page_brief_parts.append(f"URL: {metadata['sourceURL']}")
        if markdown:
            page_brief_parts.append(f"İçerik (kısaltılmış): {markdown[:800]}")

        page_brief = "\n".join(page_brief_parts) if page_brief_parts else normalized_url
        prompt = LITE_EXTRACTION_PROMPT.format(page_brief=page_brief)

        try:
            messages = [
                {"role": "system", "content": "Sen bir JSON çıktı üreten asistansın. Sadece geçerli JSON döndür."},
                {"role": "user", "content": prompt},
            ]
            data = await asyncio.to_thread(
                self.openai.chat_json, messages, max_tokens=200
            )
            category = (data.get("category") or "general").strip().lower()
            log.info(
                f"⚡ Lite extract tamam: brand='{data.get('brand_name')}', "
                f"product='{data.get('product_name')}', category='{category}'"
            )
            return {
                "brand_name": data.get("brand_name", "") or "",
                "product_name": data.get("product_name", "") or "",
                "category": category,
            }
        except Exception:
            log.warning("Lite extract LLM hatası — general fallback", exc_info=True)
            return {"brand_name": "", "product_name": "", "category": "general"}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # YARDIMCI METODLAR
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def expand_url_async(self, url: str) -> str:
        """Asynchronously expands a short URL to its final destination."""
        import asyncio
        import requests
        
        def _expand():
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                }
                try:
                    res = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
                    if res.status_code < 400 and res.url:
                        return res.url
                except Exception:
                    pass
                
                res = requests.get(url, headers=headers, allow_redirects=True, timeout=10, stream=True)
                return res.url
            except Exception as e:
                log.warning(f"Failed to expand URL {url}: {e}")
                return url

        return await asyncio.to_thread(_expand)

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalizes marketplace tracking URLs."""
        from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
        import re
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path
            
            query_params = parse_qsl(parsed.query)
            
            blacklist_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id',
                'adjust_t', 'adjust_tracker', 'adjust_campaign', 'adjust_adgroup', 'adjust_creative',
                'gclid', 'fbclid', 'click_id', 'clickid', 'aff_id', 'aff_sub', 'affiliate',
                'ref', 'referrer', 'ref_', 'sprefix', 'sr', 'qid', 'pf_rd_r', 'pf_rd_p',
                'tag',
                'campaignid', 'adgroupid', 'feedid', 'creative', 'device', 'network',
                'gref', 'linkCode', 'camp', 'creativeASIN', 'boutiqueId', 'merchantId'
            }
            
            new_params = []
            
            if 'trendyol.com' in domain:
                pass
            elif 'amazon.' in domain:
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', path, re.IGNORECASE)
                if not asin_match:
                    asin_match = re.search(r'/gp/product/([A-Z0-9]{10})', path, re.IGNORECASE)
                if asin_match:
                    path = f"/dp/{asin_match.group(1)}"
            elif 'hepsiburada.com' in domain:
                new_params = [(k, v) for k, v in query_params if k.lower() == 'magaza']
            elif 'temu.com' in domain:
                pass
            elif 'etsy.com' in domain:
                pass
            else:
                new_params = [(k, v) for k, v in query_params if k.lower() not in blacklist_params]
                
            new_query = urlencode(new_params)
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            return normalized
        except Exception as e:
            log.warning(f"Error normalizing URL {url}: {e}")
            return url

    def parse_all_from_html(self, html_content: str, url: str) -> dict:
        return parse_all_from_html(html_content, url)

    @staticmethod
    def is_valid_product_url(url: str) -> tuple[bool, str]:
        """Ürün satış sayfası URL'i için pre-validation.
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse((url or "").strip())
            if parsed.scheme not in ("http", "https"):
                return False, "Lütfen http veya https ile başlayan bir link gönder."
            if not parsed.netloc or "." not in parsed.netloc:
                return False, "Geçersiz site adresi - linkte alan adı eksik."
            blacklist = {
                "t.me", "telegram.me",
                "x.com", "twitter.com", "www.x.com", "www.twitter.com",
                "facebook.com", "www.facebook.com", "fb.com",
                "instagram.com", "www.instagram.com",
                "tiktok.com", "www.tiktok.com",
                "youtube.com", "www.youtube.com", "youtu.be",
                "linkedin.com", "www.linkedin.com",
            }
            if parsed.netloc.lower() in blacklist:
                return False, (
                    "Lütfen bir ürün satış sayfasının linkini gönder, "
                    "sosyal medya linki değil."
                )
            return True, ""
        except Exception:
            return False, "Link okunamadı, tekrar dener misin?"

    @staticmethod
    def extract_url_from_text(text: str) -> str | None:
        """
        Metin içinden URL çıkarır.
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        match = re.search(url_pattern, text)
        if match:
            url = match.group(0).rstrip(".,;:!?)")
            return url
            
        domain_pattern = r'\b(www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/[^\s<>"{}|\\^`\[\]]*)?'
        match = re.search(domain_pattern, text)
        if match:
            url = match.group(0).rstrip(".,;:!?)")
            return "https://" + url
            
        return None
