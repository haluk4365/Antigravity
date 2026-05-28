import "./config.js";
import { pullChannelVideos, TRACKED_HANDLES } from "./radar/channels.js";
import { pullTopicVideos } from "./radar/topics.js";
import { pullDiscoveryVideos } from "./radar/discovery.js";
import { bucketize } from "./radar/buckets.js";
import { loadSeenIds, recordVideo, shouldSend } from "./notion/radarStore.js";
import { loadRecentHashes, recordIdea } from "./notion/ideaStore.js";
import { runIdeaEngine } from "./ideas/ideas.js";
import { buildHtml, buildSubject } from "./mail/template.js";
import { sendMail, sendFailureMail } from "./mail/send.js";
import { log, err } from "./lib/logger.js";

async function main() {
  log("start daily run", new Date().toISOString());

  const [channels, topics, seen, ideaHashes] = await Promise.all([
    pullChannelVideos(),
    pullTopicVideos(),
    loadSeenIds(),
    loadRecentHashes(30),
  ]);

  const trackedTitles = new Set(channels.map((v) => v.channelTitle));
  const discovery = await pullDiscoveryVideos(trackedTitles);

  const buckets = bucketize(channels, topics, discovery);

  // dedup against previously sent
  buckets.fresh = buckets.fresh.filter((v) => shouldSend(seen, v, "fresh"));
  buckets.matured = buckets.matured.filter((v) => shouldSend(seen, v, "matured"));
  buckets.discovery = buckets.discovery.filter((v) => shouldSend(seen, v, "discovery"));

  log(`buckets: fresh=${buckets.fresh.length} matured=${buckets.matured.length} discovery=${buckets.discovery.length}`);

  const ideas = await runIdeaEngine(ideaHashes);

  const html = buildHtml(buckets, ideas);
  const subject = buildSubject();

  await sendMail(subject, html);

  // record what we sent (after successful send)
  await Promise.all([
    ...buckets.fresh.map((v) => recordVideo(v, "fresh")),
    ...buckets.matured.map((v) => recordVideo(v, "matured")),
    ...buckets.discovery.map((v) => recordVideo(v, "discovery")),
    ...ideas.map((i) => recordIdea(i)),
  ]);

  log("done");
}

main().catch(async (e) => {
  err("fatal:", e);
  await sendFailureMail(e?.stack || String(e));
  process.exit(1);
});
