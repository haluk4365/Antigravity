import { Client } from "@notionhq/client";
import { VideoMeta } from "../radar/youtubeApi.js";
import { BucketName } from "../radar/buckets.js";
import { warn } from "../lib/logger.js";
import { NOTION_RADAR_DB_ID } from "../config.js";

const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DB_ID = NOTION_RADAR_DB_ID;

export async function loadSeenIds(): Promise<Map<string, BucketName>> {
  const out = new Map<string, BucketName>();
  let cursor: string | undefined;
  do {
    const resp: any = await notion.databases.query({
      database_id: DB_ID,
      page_size: 100,
      start_cursor: cursor,
    });
    for (const p of resp.results) {
      const id = p.properties?.videoId?.title?.[0]?.plain_text;
      const bucket = p.properties?.lastBucket?.select?.name as BucketName | undefined;
      if (id) out.set(id, bucket ?? "fresh");
    }
    cursor = resp.has_more ? resp.next_cursor : undefined;
  } while (cursor);
  return out;
}

export async function recordVideo(v: VideoMeta, bucket: BucketName) {
  try {
    await notion.pages.create({
      parent: { database_id: DB_ID },
      properties: {
        videoId: { title: [{ text: { content: v.videoId } }] },
        channelTitle: { rich_text: [{ text: { content: v.channelTitle.slice(0, 1900) } }] },
        videoLabel: { rich_text: [{ text: { content: v.title.slice(0, 1900) } }] },
        url: { url: v.url },
        publishedAt: { date: { start: v.publishedAt } },
        viewCount: { number: v.viewCount },
        sourceType: { select: { name: v.sourceType } },
        firstSeenAt: { date: { start: new Date().toISOString() } },
        lastBucket: { select: { name: bucket } },
      },
    });
  } catch (e: any) {
    warn(`notion radar write fail ${v.videoId}: ${e.message}`);
  }
}

export function shouldSend(seen: Map<string, BucketName>, v: VideoMeta, bucket: BucketName): boolean {
  const prev = seen.get(v.videoId);
  if (!prev) return true;
  return prev !== bucket;
}
