"""
bildirim_gonder.py
──────────────────
E-posta Asistanı çalıştıktan sonra
Gmail OAuth ile KENDİ hesabına bildirim maili gönderir.
İçerik: Görev tamamlandı + Aylık maliyet raporu
"""

import os
import sys
import io
import base64
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
]

TOKEN_FILE       = BASE_DIR / "token.json"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"

# ── Log özeti oku ────────────────────────────────────────────────────────────
def get_son_log_ozeti() -> str:
    """Son çalışmanın log dosyasından özet satırları çeker."""
    log_dir = BASE_DIR / "logs"
    log_files = sorted(log_dir.glob("run_*.log"), reverse=True)
    if not log_files:
        return "Log dosyası bulunamadı."

    son_log = log_files[0]
    try:
        lines = son_log.read_text(encoding="utf-8", errors="replace").splitlines()
        # Son 15 satırı al
        ozet_satirlar = [l for l in lines if any(k in l for k in [
            "Tamamlandı", "bulundu", "Gereksiz", "Banka", "Taslak", "Hata", "başlatıldı"
        ])]
        return "\n".join(ozet_satirlar[-10:]) if ozet_satirlar else "\n".join(lines[-10:])
    except Exception as e:
        return f"Log okunamadı: {e}"


# ── Gmail servisi ─────────────────────────────────────────────────────────────
def get_gmail_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        else:
            log.error("Token geçersiz veya yok. Lütfen önce main.py'yi çalıştırın.")
            sys.exit(1)

    return build("gmail", "v1", credentials=creds)


# ── Profil (kendi e-posta adresi) ────────────────────────────────────────────
def get_email_address(service) -> str:
    profile = service.users().getProfile(userId="me").execute()
    return profile.get("emailAddress", "me")


# ── Mail oluştur ──────────────────────────────────────────────────────────────
def olustur_bildirim_maili(alici: str, log_ozeti: str) -> MIMEMultipart:
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")

    html_govde = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }}
    .kart {{ background: #ffffff; border-radius: 12px; padding: 30px; max-width: 600px;
             margin: auto; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
    .baslik {{ font-size: 22px; font-weight: bold; color: #1a1a2e; margin-bottom: 6px; }}
    .tarih  {{ font-size: 13px; color: #888; margin-bottom: 24px; }}
    .rozet  {{ display: inline-block; background: #22c55e; color: #fff;
               border-radius: 20px; padding: 4px 14px; font-size: 13px;
               font-weight: bold; margin-bottom: 20px; }}
    .bolum  {{ margin-top: 24px; }}
    .bolum-baslik {{ font-size: 14px; font-weight: bold; color: #555;
                    border-bottom: 1px solid #eee; padding-bottom: 6px;
                    margin-bottom: 12px; text-transform: uppercase;
                    letter-spacing: 0.5px; }}
    .log-kutu {{ background: #1e1e2e; color: #a6e3a1; font-family: monospace;
                font-size: 12px; padding: 14px; border-radius: 8px;
                white-space: pre-wrap; line-height: 1.6; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ text-align: left; background: #f8f9fa; padding: 8px 12px;
          font-size: 12px; color: #666; border-bottom: 2px solid #eee; }}
    td {{ padding: 8px 12px; font-size: 13px; border-bottom: 1px solid #f0f0f0; }}
    .maliyet {{ font-weight: bold; color: #e11d48; }}
    .ucretsiz {{ font-weight: bold; color: #22c55e; }}
    .toplam-satir td {{ background: #fff7ed; font-weight: bold; }}
    .footer {{ margin-top: 28px; font-size: 11px; color: #aaa; text-align: center; }}
  </style>
</head>
<body>
  <div class="kart">
    <div class="baslik">🤖 E-posta Asistanı</div>
    <div class="tarih">Çalışma Zamanı: {tarih}</div>
    <div class="rozet">✅ GÖREV TAMAMLANDI</div>

    <div class="bolum">
      <div class="bolum-baslik">📋 Çalışma Özeti</div>
      <div class="log-kutu">{log_ozeti}</div>
    </div>

    <div class="bolum">
      <div class="bolum-baslik">💰 Aylık Maliyet Raporu</div>
      <table>
        <thead>
          <tr>
            <th>Servis</th>
            <th>Kullanım</th>
            <th>Maliyet</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>🤖 Groq API (llama-3.3-70b)</td>
            <td>~30 çalışma × 50 mail × 2 istek</td>
            <td class="ucretsiz">ÜCRETSİZ</td>
          </tr>
          <tr>
            <td>📧 Gmail API</td>
            <td>Okuma + Etiketleme + Taslak</td>
            <td class="ucretsiz">ÜCRETSİZ</td>
          </tr>
          <tr>
            <td>🚂 Railway (Hosting)</td>
            <td>7/24 çalışma (Hobby Plan)</td>
            <td class="maliyet">~$5 / ay</td>
          </tr>
          <tr>
            <td>☁️ Google Cloud OAuth</td>
            <td>Gmail API kimlik doğrulama</td>
            <td class="ucretsiz">ÜCRETSİZ</td>
          </tr>
          <tr class="toplam-satir">
            <td colspan="2"><strong>TOPLAM AYLIK MALİYET</strong></td>
            <td class="maliyet">~$5 / ay (~170 ₺)</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="bolum">
      <div class="bolum-baslik">📊 Verimlilik Özeti</div>
      <table>
        <tr>
          <td>📅 Çalışma Sıklığı</td>
          <td>Her gün 21:00</td>
        </tr>
        <tr>
          <td>⏱️ Ortalama Süre</td>
          <td>~60 saniye</td>
        </tr>
        <tr>
          <td>🤖 AI Model</td>
          <td>Groq — llama-3.3-70b-versatile</td>
        </tr>
        <tr>
          <td>🏷️ Etiketler</td>
          <td>Gereksizler_AI · Bankadan_Gelenler</td>
        </tr>
        <tr>
          <td>💸 İşlem başı maliyet</td>
          <td>$0.00 (Groq ücretsiz)</td>
        </tr>
      </table>
    </div>

    <div class="footer">
      Antigravity Otomasyon Sistemi · bildirim_gonder.py · {tarih}
    </div>
  </div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✅ E-posta Asistanı — Görev Tamamlandı | {tarih}"
    msg["To"]      = alici
    msg["From"]    = alici
    msg.attach(MIMEText(html_govde, "html", "utf-8"))
    return msg


# ── Gönder ────────────────────────────────────────────────────────────────────
def gonder():
    log.info("Bildirim e-postası hazırlanıyor...")
    service = get_gmail_service()
    alici   = get_email_address(service)
    log_ozeti = get_son_log_ozeti()

    msg = olustur_bildirim_maili(alici, log_ozeti)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    log.info(f"✅ Bildirim e-postası gönderildi → {alici}")


if __name__ == "__main__":
    gonder()
