// Startup env validator. Imported once at boot; fails fast with a clear
// message instead of crashing deep inside a vendor SDK at first use.

const REQUIRED = [
  "NOTION_API_KEY",
  "NOTION_RADAR_DB_ID",
  "NOTION_IDEA_DB_ID",
  "ANTHROPIC_API_KEY",
  "YOUTUBE_API_KEY",
  "RESEND_API_KEY",
] as const;

type RequiredKey = (typeof REQUIRED)[number];

const missing: string[] = [];
const resolved = {} as Record<RequiredKey, string>;

for (const key of REQUIRED) {
  const v = process.env[key];
  if (!v || v.trim() === "") {
    missing.push(key);
  } else {
    resolved[key] = v;
  }
}

if (missing.length > 0) {
  // eslint-disable-next-line no-console
  console.error(`[CONFIG] Missing required env vars: ${missing.join(", ")}`);
  process.exit(1);
}

export const config = resolved;
export const NOTION_RADAR_DB_ID = resolved.NOTION_RADAR_DB_ID;
export const NOTION_IDEA_DB_ID = resolved.NOTION_IDEA_DB_ID;
