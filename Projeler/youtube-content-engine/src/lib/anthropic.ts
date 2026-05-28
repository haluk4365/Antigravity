import Anthropic from "@anthropic-ai/sdk";

const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) throw new Error("ANTHROPIC_API_KEY missing");

export const anthropic = new Anthropic({ apiKey });
export const MODEL = "claude-sonnet-4-5";
