"""
E-posta Asistanı — main.py
Her gün saat 21:00'da Windows Görev Zamanlayıcısı tarafından çalıştırılır.
Gmail'deki okunmamış mailleri okur, Groq ile analiz eder:
  - Bankadan gelen (BANK): Bankadan_Gelenler etiketine taşır + gerekirse taslak yanıt oluşturur
  - Gereksiz  (A)        : Okundu işaretler + Gereksizler_AI etiketine taşır
  - Önemli    (B)        : Gmail'de taslak yanıt oluşturur (göndermez)
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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Proje kök dizinini belirle
BASE_DIR = Path(__file__).parent

# Loglama ayarları
log_file = BASE_DIR / "logs" / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# .env dosyasını yükle
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

import groq
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ── Sabitler ──────────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TRASH_LABEL  = os.getenv("GMAIL_TRASH_LABEL", "Gereksizler_AI")
BANK_LABEL   = os.getenv("GMAIL_BANK_LABEL",  "Bankadan_Gelenler")

# ── Banka Tespiti ────────────────────────────────────────────────────────────
# Bilinen Türk ve uluslararası bankalar + genel finans anahtar kelimeleri
BANK_KEYWORDS = [
    # Türk bankaları
    "ziraat", "halkbank", "vakifbank", "vakıfbank", "isbank", "iş bankası",
    "garanti", "akbank", "yapikrodi", "yapı kredi", "denizbank", "finansbank",
    "qnbfinansbank", "qnb", "teb", "türk ekonomi bankası", "hsbc", "ing",
    "odeabank", "sekerbank", "şekerbank", "alternatifbank", "burganbank",
    "fibabanka", "turkishbank", "anadolubank", "icbc",
    # Genel finans terimleri (gönderen domain veya konu için)
    "@ziraatbank", "@garantibbva", "@akbank", "@isbank", "@vakifbank",
    "@denizbank", "@teb.com", "@qnbfinansbank", "@hsbc", "@ingbank",
    "banka", "bank", "kredi", "ekstre", "hesap özeti", "borç", "taksit",
    "swift", "iban", "havale", "eft", "kart bloke", "bakiye",
]

import re

def is_bank_email(sender: str, subject: str) -> bool:
    """Gönderen veya konu banka/finans kurumuna işaret ediyorsa True döner."""
    text = (sender + " " + subject).lower()
    
    for kw in BANK_KEYWORDS:
        # E-posta domainleri ise doğrudan eşleşme ara
        if kw.startswith('@'):
            if kw in text:
                return True
        else:
            # Kelimeleri tam kelime (word boundary) olarak ara (örn. 'ing' duolingo içindeyken eşleşmesin)
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text):
                return True
    return False

CREDENTIALS_FILE = BASE_DIR / "credentials.json"   # Google Cloud'dan indirilecek
TOKEN_FILE       = BASE_DIR / "token.json"          # İlk oturumdan sonra otomatik oluşur

groq_client = groq.Groq(api_key=GROQ_API_KEY)

# ── Gmail Bağlantısı ──────────────────────────────────────────────────────────
def get_gmail_service():
    """Gmail API servisi döndürür. İlk çalıştırmada tarayıcı açılır."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                log.error(
                    "credentials.json bulunamadı!\n"
                    "Lütfen Google Cloud Console'dan indirip proje klasörüne koyun.\n"
                    "Adımlar için README.md dosyasını okuyun."
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


# ── Etiket Yönetimi ───────────────────────────────────────────────────────────
def get_or_create_label(service, label_name: str) -> str:
    """Etiket ID'sini döndürür, yoksa oluşturur."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for lbl in labels:
        if lbl["name"] == label_name:
            return lbl["id"]

    created = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
    ).execute()
    log.info(f"Etiket oluşturuldu: {label_name}")
    return created["id"]


# ── Mail İçeriği ──────────────────────────────────────────────────────────────
def decode_body(payload: dict) -> str:
    """E-posta gövdesini plain text olarak çıkarır."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                    break
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return body.strip()


def get_header(headers: list, name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


# ── OpenAI ile Sınıflandırma ─────────────────────────────────────────────────
CLASSIFY_PROMPT = """Sen bir e-posta sınıflandırma asistanısın.
Aşağıdaki e-postayı okuyarak yalnızca şu iki kategoriden birini seç:
  A — Gereksiz (spam, reklam, tanıtım, otomasyon, fatura bildirimi, haber bülteni, sistem bildirimi, sosyal medya bildirimi vb.)
  B — Önemli (gerçek bir kişiden gelen iş teklifi, soru, talep, randevu, şikayet veya yanıt gerektiren herhangi bir mesaj)

Yanıtın SADECE "A" veya "B" harfi olsun. Başka hiçbir şey yazma.

Gönderen: {sender}
Konu: {subject}
İçerik (ilk 800 karakter):
{body}
"""

def classify_email(sender: str, subject: str, body: str) -> str:
    """'A' veya 'B' döndürür."""
    prompt = CLASSIFY_PROMPT.format(
        sender=sender,
        subject=subject,
        body=body[:800]
    )
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1,
        temperature=0,
    )
    result = response.choices[0].message.content.strip().upper()
    return result if result in ("A", "B") else "A"


# ── OpenAI ile Taslak Yanıt ───────────────────────────────────────────────────
DRAFT_PROMPT = """Sen profesyonel bir e-posta yazarısın.
Aşağıdaki e-postaya Türkçe, nazik ve iş dünyasına uygun kısa bir yanıt taslağı yaz.
Yanıtı sadece e-posta metni olarak ver; selamlama ve imzayı dahil et.
İmzada "Saygılarımla" kullan.

Gönderen: {sender}
Konu: {subject}
Mesaj:
{body}
"""

def generate_draft_reply(sender: str, subject: str, body: str) -> str:
    prompt = DRAFT_PROMPT.format(sender=sender, subject=subject, body=body[:1500])
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


# ── Gmail Aksiyonları ─────────────────────────────────────────────────────────
def mark_read_and_label(service, msg_id: str, label_id: str):
    """Mesajı okundu işaretler ve etikete taşır."""
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={
            "removeLabelIds": ["UNREAD", "INBOX"],
            "addLabelIds": [label_id],
        }
    ).execute()


def create_draft_reply(service, original_msg: dict, reply_text: str):
    """Gmail'de taslak yanıt oluşturur (göndermez)."""
    headers = original_msg["payload"]["headers"]
    sender      = get_header(headers, "From")
    subject     = get_header(headers, "Subject")
    message_id  = get_header(headers, "Message-ID")
    thread_id   = original_msg["threadId"]

    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"

    mime_msg = MIMEMultipart()
    mime_msg["To"]          = sender
    mime_msg["Subject"]     = reply_subject
    mime_msg["In-Reply-To"] = message_id
    mime_msg["References"]  = message_id
    mime_msg.attach(MIMEText(reply_text, "plain", "utf-8"))

    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
    draft_body = {"message": {"raw": raw, "threadId": thread_id}}

    service.users().drafts().create(userId="me", body=draft_body).execute()


# ── Ana Çalışma Akışı ────────────────────────────────────────────────────────
def run():
    log.info("=" * 60)
    log.info(f"E-posta Asistanı başlatıldı — {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    log.info("=" * 60)

    service = get_gmail_service()
    trash_label_id = get_or_create_label(service, TRASH_LABEL)
    bank_label_id  = get_or_create_label(service, BANK_LABEL)

    # Son 24 saatin okunmamış mesajlarını getir
    results = service.users().messages().list(
        userId="me",
        q="is:unread newer_than:1d",
        maxResults=50
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        log.info("Okunmamış mesaj bulunamadı. İşlem tamamlandı.")
        return

    log.info(f"{len(messages)} adet okunmamış mesaj bulundu.")

    kategori_banka = 0
    kategori_a     = 0
    kategori_b     = 0

    for msg_ref in messages:
        try:
            msg = service.users().messages().get(
                userId="me", id=msg_ref["id"], format="full"
            ).execute()

            headers  = msg["payload"]["headers"]
            sender   = get_header(headers, "From")
            subject  = get_header(headers, "Subject")
            body     = decode_body(msg["payload"])

            log.info(f"  📧 [{sender}] {subject}")

            # ── 1. Önce banka kontrolü (AI'dan önce, kural tabanlı) ──────────
            if is_bank_email(sender, subject):
                log.info(f"     → Kategori: BANKA")
                # Bankadan gelen etikete taşı (gelen kutusundan çıkar)
                mark_read_and_label(service, msg["id"], bank_label_id)
                log.info(f"     🏦 '{BANK_LABEL}' etiketine taşındı.")

                # AI ile yanıt gerekip gerekmediğini kontrol et
                kategori = classify_email(sender, subject, body)
                if kategori == "B":
                    reply_text = generate_draft_reply(sender, subject, body)
                    create_draft_reply(service, msg, reply_text)
                    log.info(f"     ✉️  Bankadan gelen için taslak yanıt oluşturuldu (Gönderilmedi).")

                kategori_banka += 1
                continue  # Diğer kategorilere düşmesin

            # ── 2. Normal sınıflandırma ──────────────────────────────────────
            kategori = classify_email(sender, subject, body)
            log.info(f"     → Kategori: {kategori}")

            if kategori == "A":
                mark_read_and_label(service, msg["id"], trash_label_id)
                log.info(f"     ✅ Okundu + '{TRASH_LABEL}' etiketine taşındı.")
                kategori_a += 1
            else:
                reply_text = generate_draft_reply(sender, subject, body)
                create_draft_reply(service, msg, reply_text)
                log.info(f"     ✉️  Taslak yanıt oluşturuldu (Gönderilmedi).")
                kategori_b += 1

        except Exception as e:
            log.error(f"     ❌ Hata: {e}")

    log.info("-" * 60)
    log.info(
        f"Tamamlandı — 🏦 Banka: {kategori_banka} | "
        f"🗑  Gereksiz: {kategori_a} | ✉️  Taslak Yanıt: {kategori_b}"
    )
    log.info("=" * 60)


if __name__ == "__main__":
    run()
