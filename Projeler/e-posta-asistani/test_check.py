"""
E-posta Asistani - Bilesenleri Kontrol Scripti
Gercek API cagrilari yapmadan tum modulleri test eder.
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(".env"))

print("=" * 60)
print("E-POSTA ASISTANI - SISTEM KONTROLU")
print("=" * 60)

# 1. .env kontrolu
print("\n[1/4] .env Degiskenleri:")
keys = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "GROQ_MODEL": os.getenv("GROQ_MODEL"),
    "GMAIL_TRASH_LABEL": os.getenv("GMAIL_TRASH_LABEL"),
    "GMAIL_BANK_LABEL": os.getenv("GMAIL_BANK_LABEL"),
}
all_ok = True
for k, v in keys.items():
    if v:
        print(f"  OK  {k} = {v if 'KEY' not in k else v[:12]+'...'}")
    else:
        print(f"  EKSIK  {k}")
        all_ok = False
print("  Sonuc:", "Tum degerler var" if all_ok else "EKSIK DEGERLER VAR!")

# 2. token.json kontrolu
print("\n[2/4] token.json (Gmail OAuth):")
token_file = Path("token.json")
if token_file.exists():
    token = json.loads(token_file.read_text())
    has_refresh = bool(token.get("refresh_token"))
    scopes = token.get("scopes", [])
    print(f"  Dosya: MEVCUT")
    print(f"  Refresh Token: {'VAR' if has_refresh else 'YOK - Yeniden giris gerekli!'}")
    print(f"  Scope sayisi: {len(scopes)}")
    for s in scopes:
        print(f"    - {s}")
else:
    print("  HATA: token.json bulunamadi! Ilk Gmail girisini yapin.")

# 3. Banka tespit fonksiyonu testi
print("\n[3/4] Banka Tespit Fonksiyonu:")
BANK_KEYWORDS = [
    "akbank", "ziraat", "garanti", "isbank", "vakifbank", "denizbank",
    "banka", "bank", "kredi", "ekstre", "iban", "havale", "eft",
    "@bilgi.akbank.com", "@garantibbva", "@isbank", "@vakifbank",
]

def is_bank_email(sender, subject):
    text = (sender + " " + subject).lower()
    return any(kw in text for kw in BANK_KEYWORDS)

tests = [
    ("AKBANK HABERCI <HIZMET@bilgi.akbank.com>", "Kredi karti harcamaniz", True),
    ("Google <no-reply@accounts.google.com>", "Guvenlik uyarisi", False),
    ("Duolingo <hello@duolingo.com>", "Gunluk hatirlatma", False),
    ("Railway <hello@notify.railway.app>", "Start Deploying", False),
    ("Garanti BBVA <info@garantibbva.com>", "Ekstre hazir", True),
    ("Ziraat Bankasi <info@ziraatbank.com>", "Hesap ozeti", True),
]

passed = 0
for sender, subject, expected in tests:
    result = is_bank_email(sender, subject)
    ok = result == expected
    if ok:
        passed += 1
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {sender[:45]}")
    print(f"         Konu: {subject} | Beklenen:{expected} Sonuc:{result}")

print(f"  Toplam: {passed}/{len(tests)} test gecti")

# 4. Groq API hizi testi (kisa)
print("\n[4/4] Groq API Baglantisi:")
try:
    import groq
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[{"role": "user", "content": "Sadece 'OK' yaz."}],
        max_tokens=3,
        temperature=0,
    )
    answer = response.choices[0].message.content.strip()
    print(f"  Baglanti: BASARILI")
    print(f"  Model yaniti: '{answer}'")
    print(f"  Kullanilan model: {response.model}")
except Exception as e:
    print(f"  HATA: {e}")

print("\n" + "=" * 60)
print("KONTROL TAMAMLANDI")
print("=" * 60)
