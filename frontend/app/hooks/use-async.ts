import { useCallback, useEffect, useRef, useState } from "react";

import { toApiError, type ApiError, type Sourced } from "../lib/api/client";

/**
 * In-memory client-side cache shared across all `useAsync` / `useCachedAsync`
 * instances. Keys are strings; values are timestamped entries so callers can
 * read "stale-while-revalidating" data immediately and refresh in the
 * background. No external dependencies.
 */

type CacheEntry<T> = {
  data: T;
  fetchedAt: number;
};

const cache = new Map<string, CacheEntry<unknown>>();

const DEFAULT_STALE_MS = 5 * 60 * 1000; // 5 minutes

export const asyncCache = {
  /** Read a cached value if it exists and is not stale. Returns undefined otherwise. */
  get<T>(key: string, staleMs: number = DEFAULT_STALE_MS): T | undefined {
    const entry = cache.get(key) as CacheEntry<T> | undefined;
    if (!entry) return undefined;
    if (Date.now() - entry.fetchedAt > staleMs) return undefined;
    return entry.data;
  },

  /** Write a value to the cache. */
  set<T>(key: string, data: T): void {
    cache.set(key, { data, fetchedAt: Date.now() });
  },

  /** Remove a specific key so the next fetch goes to the network. */
  invalidate(key: string): void {
    cache.delete(key);
  },

  /** Remove all cached values. */
  clear(): void {
    cache.clear();
  },
};

/**
 * `useAsync` with a client-side read-through cache.
 *
 * Mirrors the exact return shape of `useAsync`:
 *   { data, sample, loading, error, retry }
 *
 * On first render it reads from the cache. If a fresh entry exists it is
 * returned immediately (no loading flash). Otherwise the fetch function runs,
 * and its result is written to the cache before being returned.
 *
 * `retry` invalidates the cached key and refetches.
 *
 * @param cacheKey   Unique key for this query (e.g. "locations:list")
 * @param fn         Fetch function returning Promise<Sourced<T>>
 * @param staleMs    How long cached data is considered fresh (default 5 min)
 */
export function useCachedAsync<T>(
  cacheKey: string,
  fn: () => Promise<Sourced<T>>,
  options: { staleMs?: number } = {}
) {
  const { staleMs = DEFAULT_STALE_MS } = options;

  const [state, setState] = useState<{
    data: T | null;
    sample: boolean;
    loading: boolean;
    error: ApiError | null;
  }>({ data: null, sample: false, loading: true, error: null });

  const fnRef = useRef(fn);
  fnRef.current = fn;

  // Seed from cache on mount so fresh data renders immediately.
  useEffect(() => {
    const cached = asyncCache.get<T>(cacheKey, staleMs);
    if (cached !== undefined) {
      setState({ data: cached, sample: false, loading: false, error: null });
    }
  }, [cacheKey, staleMs]);

  const run = useCallback(() => {
    let alive = true;

    const cached = asyncCache.get<T>(cacheKey, staleMs);
    if (cached !== undefined && alive) {
      setState({ data: cached, sample: false, loading: false, error: null });
      return () => { alive = false; };
    }

    setState((s) => ({ ...s, loading: true, error: null }));

    fnRef.current()
      .then((r) => {
        if (!alive) return;
        asyncCache.set(cacheKey, r.data);
        setState({
          data: r.data,
          sample: r.sample,
          loading: false,
          error: null,
        });
      })
      .catch((e) => {
        if (!alive) return;
        setState({
          data: null,
          sample: false,
          loading: false,
          error: toApiError(e),
        });
      });

    return () => { alive = false; };
  }, [cacheKey, staleMs]);

  useEffect(() => {
    run();
  }, [run]);

  const retry = useCallback(() => {
    asyncCache.invalidate(cacheKey);
    run();
  }, [cacheKey, run]);

  return { ...state, retry };
}
