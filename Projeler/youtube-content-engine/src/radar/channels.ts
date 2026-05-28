import { fetchPlaylistVideoIds, fetchVideosByIds, resolveUploadsPlaylist, toVideoMeta, VideoMeta } from "./youtubeApi.js";
import { log, warn } from "../lib/logger.js";

export const TRACKED_HANDLES = ["@nateherk", "@Itssssss_Jack", "@nicksaraev", "@RoboNuggets"];

export async function pullChannelVideos(): Promise<VideoMeta[]> {
  const all: VideoMeta[] = [];
  for (const handle of TRACKED_HANDLES) {
    try {
      const meta = await resolveUploadsPlaylist(handle);
      if (!meta) {
        warn(`channel resolve failed: ${handle}`);
        continue;
      }
      const ids = await fetchPlaylistVideoIds(meta.uploadsPlaylistId, 50);
      const raw = await fetchVideosByIds(ids);
      const videos = raw.map((r) => toVideoMeta(r, "channel"));
      log(`channel ${handle}: ${videos.length} videos`);
      all.push(...videos);
    } catch (e: any) {
      warn(`channel ${handle} error: ${e.message}`);
    }
  }
  return all;
}
