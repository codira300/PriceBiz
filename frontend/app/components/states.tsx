import { AlertCircle, Inbox, Loader2, FlaskConical } from "lucide-react";
import type { ReactNode } from "react";
import type { ApiError } from "../lib/api/client";

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-muted-foreground">
      <Loader2 className="h-5 w-5 animate-spin text-primary" /> {label}
    </div>
  );
}

/**
 * Page-level skeleton that renders while data is loading.
 * Mirrors the shape of the content that will replace it so the
 * page doesn't jump around when data arrives.
 */
export function PageSkeleton({
  label = "Loading…",
  lines = 3,
}: {
  label?: string;
  lines?: number;
}) {
  return (
    <div className="space-y-4 py-16 text-muted-foreground">
      <div className="flex items-center justify-between gap-4">
        <div className="h-8 w-3/4 animate-pulse rounded-[2px] bg-primary/10" />
        <div className="h-8 w-1/4 animate-pulse rounded-[2px] bg-primary/10" />
      </div>

      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-6 w-full animate-pulse rounded-[2px] bg-primary/10"
        />
      ))}

      <div className="flex items-center justify-center gap-2">
        <Loader2 className="h-5 w-5 animate-spin text-primary" /> {label}
      </div>
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: ApiError; onRetry?: () => void }) {
  return (
    <div className="rounded-[3px] border border-destructive/30 bg-destructive/5 p-6 text-center" data-request-id={error.requestId}>
      <AlertCircle className="mx-auto h-6 w-6 text-destructive" />
      <p className="mt-2 font-medium">{error.message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 inline-flex min-h-11 items-center rounded-[3px] bg-foreground px-4 text-sm text-background transition-colors duration-150 ease-out hover:bg-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function Empty({ title, children, icon }: { title: string; children?: ReactNode; icon?: ReactNode }) {
  const Icon = icon ?? Inbox;

  return (
    <div className="rounded-[3px] border border-dashed border-border bg-card p-10 text-center">
      <Icon className="mx-auto h-8 w-8 text-muted-foreground" />
      <p className="mt-3 font-display text-lg font-semibold">{title}</p>
      <div className="mt-1 text-sm leading-6 text-muted-foreground">{children}</div>
    </div>
  );
}

export function SampleNotice({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <div className="mb-4 flex items-start gap-2 rounded-[3px] border border-accent-foreground/20 bg-accent px-3 py-2 text-sm text-accent-foreground">
      <FlaskConical className="mt-0.5 h-4 w-4 shrink-0" /> Showing sample data — the PriceBiz server couldn't be reached.
    </div>
  );
}
