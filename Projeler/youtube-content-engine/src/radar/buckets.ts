import { VideoMeta } from "./youtubeApi.js";

export type BucketName = "fresh" | "matured" | "discovery";

export type Buckets = {
  fresh: VideoMeta[];
  matured: VideoMeta[];
  discovery: VideoMeta[];
  priority: VideoMeta | null;
};

const HOUR = 60 * 60 * 1000;
const DAY = 24 * HOUR;

function hoursSince(iso: string): number {
  return (Date.now() - new Date(iso).getTime()) / HOUR;
}

export function bucketize(channels: VideoMeta[], topics: VideoMeta[], discovery: VideoMeta[]): Buckets {
  const all = [...channels, ...topics];
  const seen = new Set<string>();
  const dedup = (arr: VideoMeta[]) =>
    arr.filter((v) => {
      if (seen.has(v.videoId)) return false;
      seen.add(v.videoId);
      return true;
    });

  const fresh = dedup(
    all
      .filter((v) => hoursSince(v.publishedAt) <= 48)
      .sort((a, b) => b.viewCount / Math.max(1, hoursSince(b.publishedAt)) - a.viewCount / Math.max(1, hoursSince(a.publishedAt)))
  ).slice(0, 5);

  const matured = dedup(
    all
      .filter((v) => {
        const age = hoursSince(v.publishedAt) / 24;
        return age > 7 && age < 21 && v.viewCount > 5000;
      })
      .sort((a, b) => b.viewCount - a.viewCount)
  ).slice(0, 5);

  const disc = dedup(discovery.sort((a, b) => b.viewCount - a.viewCount)).slice(0, 3);

  // priority = highest velocity across all
  const priority =
    [...fresh, ...matured, ...disc].sort(
      (a, b) => b.viewCount / Math.max(1, hoursSince(b.publishedAt)) - a.viewCount / Math.max(1, hoursSince(a.publishedAt))
    )[0] ?? null;

  return { fresh, matured, discovery: disc, priority };
}

export function velocity(v: VideoMeta): number {
  const h = (Date.now() - new Date(v.publishedAt).getTime()) / HOUR;
  return v.viewCount / Math.max(1, h);
}
