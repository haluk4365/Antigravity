export const log = (...args: unknown[]) => console.log("[engine]", ...args);
export const warn = (...args: unknown[]) => console.warn("[engine:warn]", ...args);
export const err = (...args: unknown[]) => console.error("[engine:err]", ...args);
