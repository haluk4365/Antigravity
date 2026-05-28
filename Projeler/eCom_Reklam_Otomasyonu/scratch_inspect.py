import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\msist\.gemini\antigravity-ide\brain\78e42cb8-6a20-40f2-8f3f-ead199d671c0\.system_generated\logs\transcript.jsonl"

try:
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            content = data.get('content') or ""
            if data.get("type") == "USER_INPUT":
                print(f"USER: {content[:400]}")
            elif data.get("source") == "MODEL" and data.get("type") == "PLANNER_RESPONSE" and content.strip():
                print(f"AI: {content[:400]}\n")
except Exception as e:
    print(f"Error reading transcript: {e}")
