"""check_balances.py — KIE + ElevenLabs bakiye/kredi sorgusu."""

import os
import sys

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.kie_api import KieAIService


def main() -> None:
    load_dotenv()

    print("=" * 60)
    print("KIE AI")
    print("=" * 60)
    kie_key = os.environ.get("KIE_API_KEY")
    if kie_key:
        try:
            kie = KieAIService(kie_key)
            bal = kie.get_credit_balance()
            credits = bal.get("data") if isinstance(bal, dict) else "?"
            print(f"  Kredi bakiyesi: {credits}")
            print(f"  Tek 16 sn reklam ≈ 400-500 kredi (gerçek)")
            if isinstance(credits, (int, float)):
                ad_count = int(credits / 450)
                print(f"  Yapılabilecek 16 sn reklam: ~{ad_count} adet")
        except Exception as e:
            print(f"  HATA: {e}")
    else:
        print("  KIE_API_KEY .env'de yok")

    print()
    print("=" * 60)
    print("ELEVENLABS")
    print("=" * 60)
    el_key = os.environ.get("ELEVENLABS_API_KEY")
    if el_key:
        try:
            r = requests.get(
                "https://api.elevenlabs.io/v1/user/subscription",
                headers={"xi-api-key": el_key},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            tier = data.get("tier", "?")
            used = data.get("character_count", 0)
            limit = data.get("character_limit", 0)
            remaining = limit - used
            print(f"  Plan: {tier}")
            print(f"  Karakter kullanımı: {used:,} / {limit:,}")
            print(f"  Kalan: {remaining:,} karakter")
            # Reklam başına ortalama ses metni ~150 karakter (4 sahne)
            if limit > 0:
                ad_chars = 150
                remaining_ads = remaining // ad_chars
                print(f"  Tek reklam ≈ {ad_chars} karakter (4 voiceover)")
                print(f"  Yapılabilecek reklam: ~{remaining_ads} adet")
            # Sound effects ayrı sayılıyor olabilir
            next_renew = data.get("next_character_count_reset_unix")
            if next_renew:
                from datetime import datetime
                dt = datetime.fromtimestamp(next_renew)
                print(f"  Yenilenme: {dt.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"  HATA: {e}")
    else:
        print("  ELEVENLABS_API_KEY .env'de yok")

    print()


if __name__ == "__main__":
    main()
