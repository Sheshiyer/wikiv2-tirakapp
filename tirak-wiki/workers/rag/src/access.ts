import type { Env } from './config';

/**
 * Production origins for the Tirak wiki. Exact matches only: no wildcard
 * subdomains and no blanket `*.vercel.app`. Extra origins (for example one
 * Vercel preview URL) go in the `ALLOWED_ORIGINS` var as a comma-separated list.
 */
export const PRODUCTION_ORIGINS = ['https://wiki.tirak.app'] as const;

/** Local dev origins, accepted only when ENVIRONMENT === 'development'. */
const LOCAL_DEV_HOSTS = new Set(['localhost', '127.0.0.1']);

export const MAX_PUBLIC_QUERY_CHARS = 1000;

/** Fallback limit when the CHAT_RATE_LIMITER binding is absent (per isolate, best effort). */
const FALLBACK_LIMIT = 10;
const FALLBACK_WINDOW_MS = 60_000;
const fallbackBuckets = new Map<string, { count: number; resetAt: number }>();

function parseOriginList(value: string | undefined): string[] {
  if (!value) {
    return [];
  }

  return value
    .split(',')
    .map((entry) => entry.trim().replace(/\/+$/, '').toLowerCase())
    .filter((entry) => entry.length > 0 && !entry.includes('*'));
}

export function getAllowedCorsOrigin(origin: string | null, env: Env): string | null {
  if (!origin) {
    return null;
  }

  let url: URL;
  try {
    url = new URL(origin);
  } catch {
    return null;
  }

  const normalized = url.origin.toLowerCase();
  const allowlist = new Set<string>([...PRODUCTION_ORIGINS, ...parseOriginList(env.ALLOWED_ORIGINS)]);

  if (allowlist.has(normalized)) {
    return origin;
  }

  if (
    env.ENVIRONMENT === 'development'
    && url.protocol === 'http:'
    && LOCAL_DEV_HOSTS.has(url.hostname.toLowerCase())
  ) {
    return origin;
  }

  return null;
}

/**
 * Returns true when the public chat request is within its rate limit.
 * Uses the Workers Rate Limiting binding when configured (see wrangler.jsonc),
 * otherwise a per-isolate in-memory window so local dev still works.
 */
export async function checkPublicChatRateLimit(request: Request, env: Env, appId: string): Promise<boolean> {
  const ip = request.headers.get('cf-connecting-ip') ?? 'unknown';
  const key = `chat:${appId}:${ip}`;

  if (env.CHAT_RATE_LIMITER) {
    const { success } = await env.CHAT_RATE_LIMITER.limit({ key });
    return success;
  }

  const now = Date.now();
  if (fallbackBuckets.size > 5000) {
    for (const [bucketKey, entry] of fallbackBuckets) {
      if (entry.resetAt <= now) {
        fallbackBuckets.delete(bucketKey);
      }
    }
  }

  const bucket = fallbackBuckets.get(key);
  if (!bucket || bucket.resetAt <= now) {
    fallbackBuckets.set(key, { count: 1, resetAt: now + FALLBACK_WINDOW_MS });
    return true;
  }

  bucket.count += 1;
  return bucket.count <= FALLBACK_LIMIT;
}
