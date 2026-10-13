import { useCallback, useEffect, useRef, useState } from "react";
import { toApiError, type ApiError, type Sourced } from "../lib/api/client";

export function useAsync<T>(fn: () => Promise<Sourced<T>>, deps: unknown[]) {
  const [state, setState] = useState<{ data: T | null; sample: boolean; loading: boolean; error: ApiError | null }>({
    data: null, sample: false, loading: true, error: null,
  });
  const ref = useRef(fn);
  ref.current = fn;
  const run = useCallback(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    ref.current()
      .then((r) => alive && setState({ data: r.data, sample: r.sample, loading: false, error: null }))
      .catch((e) => alive && setState({ data: null, sample: false, loading: false, error: toApiError(e) }));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(() => run(), [run]);
  return { ...state, retry: run };
}
