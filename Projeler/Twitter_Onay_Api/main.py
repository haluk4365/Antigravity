"""Twitter / Instagram Draft Onay API.

Mail'deki "Onayla" butonları buraya gelir.

Endpoint'ler:
  - /approve         → Twitter draft'ı Typefully'ye schedule eder
  - /approve-carousel → Instagram_Carousel_Cron carousel'ını Approved işaretler
                        ve kullanıcıya post-ready sayfa gösterir (slide URL'leri + caption)
"""

import os
import html
import hmac
import json
import base64
import hashlib
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

APP_SECRET = os.environ["APPROVAL_SECRET"]
TYPEFULLY_API_KEY = os.environ["TYPEFULLY_API_KEY"]
TYPEFULLY_SOCIAL_SET_ID = os.environ["TYPEFULLY_SOCIAL_SET_ID"]
NOTION_TOKEN = os.environ["NOTION_SOCIAL_TOKEN"]

TYPEFULLY_BASE = f"https://api.typefully.com/v2/social-sets/{TYPEFULLY_SOCIAL_SET_ID}"
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

app = FastAPI()


def _verify_token(token: str) -> dict:
    try:
        payload_b64, sig = token.split(".", 1)
        expected = hmac.new(
            APP_SECRET.encode(), payload_b64.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise HTTPException(401, "Geçersiz imza")
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Token okunamadı")


def _schedule_typefully(draft_id: str) -> dict:
    r = requests.patch(
        f"{TYPEFULLY_BASE}/drafts/{draft_id}",
        headers={
            "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"publish_at": "next-free-slot"},
        timeout=20,
    )
    if r.status_code not in (200, 201):
        raise HTTPException(502, f"Typefully hata: {r.status_code} {r.text[:200]}")
    return r.json()


def _update_notion(row_id: str, scheduled_at: str | None) -> None:
    props = {"Status": {"select": {"name": "Approved"}}}
    if scheduled_at:
        props["Scheduled At"] = {"date": {"start": scheduled_at}}
    r = requests.patch(
        f"{NOTION_API}/pages/{row_id}",
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        json={"properties": props},
        timeout=20,
    )
    if r.status_code not in (200, 201):
        raise HTTPException(502, f"Notion hata: {r.status_code} {r.text[:200]}")


def _success_html(scheduled_at: str | None, title: str) -> str:
    when = "kuyruktaki bir sonraki slota"
    if scheduled_at:
        try:
            dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
            from zoneinfo import ZoneInfo
            tr = dt.astimezone(ZoneInfo("Europe/Istanbul"))
            when = tr.strftime("%d.%m.%Y %H:%M") + " (TR)"
        except Exception:
            pass
    return f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;background:#f6f8fa;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;">
<div style="background:#fff;border-radius:16px;padding:48px;max-width:480px;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.06);">
<div style="font-size:48px;margin-bottom:16px;">✅</div>
<h1 style="font-size:22px;color:#111;margin:0 0 12px;">Onaylandı, sıraya alındı.</h1>
<p style="font-size:15px;color:#666;line-height:1.5;margin:0 0 8px;">{title[:140]}</p>
<p style="font-size:14px;color:#888;margin:0;">Yayın saati: <b>{when}</b></p>
</div></body></html>"""


@app.get("/")
def root():
    return {"status": "ok", "service": "twitter-onay-api"}


@app.get("/approve", response_class=HTMLResponse)
def approve(t: str):
    payload = _verify_token(t)
    draft_id = payload.get("d")
    row_id = payload.get("r")
    title = payload.get("title", "")
    if not draft_id or not row_id:
        raise HTTPException(400, "Eksik token")

    result = _schedule_typefully(str(draft_id))
    scheduled_at = result.get("publish_at") or result.get("scheduled_at")

    _update_notion(row_id, scheduled_at)
    return HTMLResponse(_success_html(scheduled_at, title))


# ════════════════════════════════════════════════════════════════════
# Instagram Carousel onay akışı
# ════════════════════════════════════════════════════════════════════

def _fetch_notion_page(row_id: str) -> dict:
    r = requests.get(
        f"{NOTION_API}/pages/{row_id}",
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
        },
        timeout=15,
    )
    if r.status_code not in (200, 201):
        raise HTTPException(502, f"Notion fetch hata: {r.status_code} {r.text[:200]}")
    return r.json()


def _rich_text(prop: dict) -> str:
    return "".join(t.get("plain_text", "") for t in (prop or {}).get("rich_text", []))


def _mark_carousel_approved(row_id: str) -> None:
    payload = {
        "properties": {
            "Carousel Status": {"select": {"name": "Approved"}},
            "Carousel Approved At": {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
        }
    }
    r = requests.patch(
        f"{NOTION_API}/pages/{row_id}",
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )
    if r.status_code not in (200, 201):
        raise HTTPException(502, f"Notion update hata: {r.status_code} {r.text[:200]}")


def _carousel_post_ready_html(title: str, slides: list[dict], caption: str) -> str:
    title_safe = html.escape(title or "Carousel")
    caption_safe = html.escape(caption or "").replace("\n", "<br>")
    caption_for_copy = json.dumps(caption or "")  # JS string literal

    slide_cards = []
    for s in slides:
        idx = s.get("index", "?")
        url = s.get("url", "")
        if not url:
            continue
        slide_cards.append(f"""
<div style="margin-bottom:16px;text-align:center;">
  <img src="{html.escape(url)}" style="max-width:280px;width:100%;border-radius:10px;box-shadow:0 4px 14px rgba(0,0,0,0.08);"/>
  <div style="margin-top:6px;">
    <a href="{html.escape(url)}" download style="font-size:13px;color:#6366f1;text-decoration:none;">⬇ Slide {idx} indir</a>
  </div>
</div>""")
    slides_html = "".join(slide_cards)

    return f"""<!DOCTYPE html>
<html><body style="font-family:-apple-system,sans-serif;background:#f3f4f6;margin:0;padding:24px;">
<div style="max-width:520px;margin:0 auto;background:#fff;border-radius:14px;padding:32px;box-shadow:0 4px 24px rgba(0,0,0,0.06);">
  <div style="text-align:center;font-size:48px;margin-bottom:12px;">✅</div>
  <h1 style="font-size:22px;color:#111;margin:0 0 8px;text-align:center;">Onaylandı — Instagram'a Hazır</h1>
  <p style="font-size:14px;color:#666;text-align:center;margin:0 0 24px;">{title_safe}</p>

  <h3 style="font-size:14px;color:#374151;text-transform:uppercase;letter-spacing:0.5px;margin:24px 0 12px;">Slide'lar</h3>
  {slides_html}

  <h3 style="font-size:14px;color:#374151;text-transform:uppercase;letter-spacing:0.5px;margin:24px 0 8px;">Caption</h3>
  <div id="cap" style="background:#f9fafb;border-left:3px solid #6366f1;padding:14px;border-radius:6px;font-size:13px;color:#374151;line-height:1.55;margin-bottom:12px;">{caption_safe}</div>
  <button onclick="navigator.clipboard.writeText({caption_for_copy}); this.innerText='✓ Kopyalandı';" style="background:#111827;color:#fff;border:0;padding:10px 18px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">📋 Caption'ı kopyala</button>

  <div style="margin-top:24px;padding:14px;background:#fef3c7;border-radius:8px;font-size:13px;color:#78350f;">
    <b>Manuel post adımı:</b> Instagram uygulamasını aç → "+" → Carousel → slide'ları sırayla seç → caption'ı yapıştır.
  </div>
</div>
</body></html>"""


@app.get("/approve-carousel", response_class=HTMLResponse)
def approve_carousel(t: str):
    payload = _verify_token(t)
    if payload.get("t") != "carousel":
        raise HTTPException(400, "Token tipi uyumsuz (carousel beklendi)")
    row_id = payload.get("r")
    title = payload.get("title", "")
    if not row_id:
        raise HTTPException(400, "Eksik row_id")

    page = _fetch_notion_page(row_id)
    props = page.get("properties", {})

    slides_raw = _rich_text(props.get("Carousel Slides", {}))
    try:
        slides = json.loads(slides_raw) if slides_raw else []
    except Exception:
        slides = []
    caption = _rich_text(props.get("Instagram Caption", {}))

    if not slides:
        raise HTTPException(404, "Slide bulunamadı (Carousel Slides boş)")

    _mark_carousel_approved(row_id)
    return HTMLResponse(_carousel_post_ready_html(title, slides, caption))
