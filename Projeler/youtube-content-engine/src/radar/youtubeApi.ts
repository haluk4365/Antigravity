const KEY = process.env.YOUTUBE_API_KEY;
if (!KEY) throw new Error("YOUTUBE_API_KEY missing");

const BASE = "https://www.googleapis.com/youtube/v3";

async function gv(path: string, params: Record<string, string | number>) {
  const qs = new URLSearchParams({ ...Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)])), key: KEY! });
  const r = await fetch(`${BASE}/${path}?${qs}`);
  if (!r.ok) {
    const body = await r.text();
    throw new Error(`YouTube API ${path} ${r.status}: ${body.slice(0, 300)}`);
  }
  return r.json() as Promise<any>;
}

export type VideoMeta = {
  videoId: string;
  channelTitle: string;
  title: string;
  publishedAt: string;
  viewCount: number;
  duration: string;
  thumbnailUrl: string;
  url: string;
  sourceType: "channel" | "topic" | "discovery";
};

export async function resolveUploadsPlaylist(handle: string): Promise<{ channelId: string; uploadsPlaylistId: string; channelTitle: string } | null> {
  const h = handle.startsWith("@") ? handle.slice(1) : handle;
  const data = await gv("channels", { part: "snippet,contentDetails", forHandle: h });
  const item = data.items?.[0];
  if (!item) return null;
  return {
    channelId: item.id,
    uploadsPlaylistId: item.contentDetails.relatedPlaylists.uploads,
    channelTitle: item.snippet.title,
  };
}

export async function fetchPlaylistVideoIds(playlistId: string, max = 50): Promise<string[]> {
  const ids: string[] = [];
  let pageToken: string | undefined;
  while (ids.length < max) {
    const data = await gv("playlistItems", {
      part: "contentDetails",
      playlistId,
      maxResults: Math.min(50, max - ids.length),
      ...(pageToken ? { pageToken } : {}),
    });
    for (const it of data.items || []) ids.push(it.contentDetails.videoId);
    if (!data.nextPageToken) break;
    pageToken = data.nextPageToken;
  }
  return ids;
}

export async function fetchVideosByIds(ids: string[]): Promise<any[]> {
  if (!ids.length) return [];
  const out: any[] = [];
  for (let i = 0; i < ids.length; i += 50) {
    const chunk = ids.slice(i, i + 50);
    const data = await gv("videos", { part: "snippet,statistics,contentDetails", id: chunk.join(",") });
    out.push(...(data.items || []));
  }
  return out;
}

export async function searchVideos(opts: {
  query?: string;
  publishedAfter?: string;
  order?: "viewCount" | "date" | "relevance";
  videoCategoryId?: string;
  relevanceLanguage?: string;
  max?: number;
}): Promise<string[]> {
  const params: Record<string, string | number> = {
    part: "id",
    type: "video",
    maxResults: opts.max ?? 25,
    order: opts.order ?? "viewCount",
  };
  if (opts.query) params.q = opts.query;
  if (opts.publishedAfter) params.publishedAfter = opts.publishedAfter;
  if (opts.videoCategoryId) params.videoCategoryId = opts.videoCategoryId;
  if (opts.relevanceLanguage) params.relevanceLanguage = opts.relevanceLanguage;
  const data = await gv("search", params);
  return (data.items || []).map((it: any) => it.id.videoId).filter(Boolean);
}

export function toVideoMeta(raw: any, sourceType: VideoMeta["sourceType"]): VideoMeta {
  return {
    videoId: raw.id,
    channelTitle: raw.snippet?.channelTitle ?? "",
    title: raw.snippet?.title ?? "",
    publishedAt: raw.snippet?.publishedAt ?? "",
    viewCount: Number(raw.statistics?.viewCount ?? 0),
    duration: raw.contentDetails?.duration ?? "",
    thumbnailUrl:
      raw.snippet?.thumbnails?.maxres?.url ||
      raw.snippet?.thumbnails?.high?.url ||
      raw.snippet?.thumbnails?.medium?.url ||
      raw.snippet?.thumbnails?.default?.url ||
      "",
    url: `https://www.youtube.com/watch?v=${raw.id}`,
    sourceType,
  };
}
