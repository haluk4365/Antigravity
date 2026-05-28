import os
import requests
import json

from dotenv import load_dotenv
load_dotenv()

token = os.environ.get("NOTION_SOCIAL_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

print("Checking Notion integration token details...")
res = requests.get("https://api.notion.com/v1/users/me", headers=headers)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    print(json.dumps(res.json(), indent=2))
else:
    print(res.text)
