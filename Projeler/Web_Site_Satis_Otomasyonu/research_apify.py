import os
import json
from apify_client import ApifyClient

# Apify token .env / ortam degiskeninden okunur.
api_token = os.environ.get("APIFY_API_KEY_2") or os.environ.get("APIFY_API_KEY_1")

if not api_token:
    print("APIFY_API_KEY eksik! .env dosyanizi kontrol edin.")
    exit(1)

client = ApifyClient(api_token)

run_input = {
    "searchStringsArray": ["restaurant"],
    "locationQuery": "Kadikoy, Istanbul",
    "maxCrawledPlacesPerSearch": 2, # Just to test the schema quickly
    "language": "en",
    "searchMatching": "all",
    "website": "allPlaces",
    "skipClosedPlaces": False,
    "scrapePlaceDetailPage": True, # Get full details to see if website/phone are there
    "scrapeContacts": True, # To check if it returns email
    "scrapeSocialMediaProfiles": {
        "facebooks": False,
        "instagrams": True, # To see if IG has email
        "youtubes": False,
    },
    "maxImages": 1,
    "maxReviews": 2, # Just to see what format reviews come in
    "scrapeReviewsPersonalData": False
}

print("Starting Apify Actor (Google Maps Scraper)...")
run = client.actor("nwua9Gu5YrADL7ZDj").call(run_input=run_input)

print("\n--- DATASET SAMPLES ---")
sampled = 0
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(json.dumps(item, indent=2, ensure_ascii=False))
    sampled += 1
    if sampled >= 2: break

print(f"\nDone. Saved into {run['defaultDatasetId']}")
