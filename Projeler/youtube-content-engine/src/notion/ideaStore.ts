import { Client } from "@notionhq/client";
import { createHash } from "node:crypto";
import { warn } from "../lib/logger.js";
import { NOTION_IDEA_DB_ID } from "../config.js";

const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DB_ID = NOTION_IDEA_DB_ID;

export type Idea = {
  problem: string;
  otomasyon: string;
  hedef_kitle: string;
  hook: string;
  skor: number;
  kaynak: string;
};

export function hashIdea(idea: Idea): string {
  const norm = idea.otomasyon.toLowerCase().replace(/\s+/g, " ").trim();
  return createHash("sha256").update(norm).digest("hex").slice(0, 24);
}

export async function loadRecentHashes(daysBack = 30): Promise<Set<string>> {
  const out = new Set<string>();
  const cutoff = new Date(Date.now() - daysBack * 24 * 60 * 60 * 1000).toISOString();
  let cursor: string | undefined;
  do {
    const resp: any = await notion.databases.query({
      database_id: DB_ID,
      page_size: 100,
      start_cursor: cursor,
      filter: {
        property: "firstSeenAt",
        date: { after: cutoff },
      },
    });
    for (const p of resp.results) {
      const h = p.properties?.ideaHash?.title?.[0]?.plain_text;
      if (h) out.add(h);
    }
    cursor = resp.has_more ? resp.next_cursor : undefined;
  } while (cursor);
  return out;
}

export async function recordIdea(idea: Idea) {
  const h = hashIdea(idea);
  const audMap: Record<string, string> = {
    "kobi": "KOBİ",
    "KOBİ": "KOBİ",
    "kobi̇": "KOBİ",
    "bireysel girişimci": "bireysel girişimci",
    "her ikisi": "her ikisi",
  };
  const aud = audMap[idea.hedef_kitle.toLowerCase().trim()] || "her ikisi";
  try {
    await notion.pages.create({
      parent: { database_id: DB_ID },
      properties: {
        ideaHash: { title: [{ text: { content: h } }] },
        ideaText: { rich_text: [{ text: { content: idea.otomasyon.slice(0, 1900) } }] },
        problem: { rich_text: [{ text: { content: idea.problem.slice(0, 1900) } }] },
        targetAudience: { select: { name: aud } },
        score: { number: idea.skor },
        source: { rich_text: [{ text: { content: idea.kaynak.slice(0, 1900) } }] },
        firstSeenAt: { date: { start: new Date().toISOString() } },
        sentInMailAt: { date: { start: new Date().toISOString() } },
      },
    });
  } catch (e: any) {
    warn(`notion idea write fail: ${e.message}`);
  }
}
