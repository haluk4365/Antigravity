import { fetchVideosByIds, searchVideos, toVideoMeta, VideoMeta } from "./youtubeApi.js";
import { log, warn } from "../lib/logger.js";

export const TRACKED_TOPICS = ["claude code", "antigravity", "ai automation"];

export async function pullTopicVideos(): Promise<VideoMeta[]> {
  const since = new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString();
  const all: VideoMeta[] = [];
  for (const q of TRACKED_TOPICS) {
    try {
      const ids = await searchVideos({
        query: q,
        publishedAfter: since,
        order: "viewCount",
        relevanceLanguage: "en",
        max: 25,
      });
      const raw = await fetchVideosByIds(ids);
      const videos = raw.map((r) => toVideoMeta(r, "topic"));
      log(`topic "${q}": ${videos.length} videos`);
      all.push(...videos);
    } catch (e: any) {
      warn(`topic "${q}" error: ${e.message}`);
    }
  }
  return all;
}
