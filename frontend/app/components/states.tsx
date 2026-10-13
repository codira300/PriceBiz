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

export function ErrorState({ error, onRetry }: { error: ApiError; onRetry?: () => void }) {
  return (
    <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-6 text-center" data-request-id={error.requestId}>
      <AlertCircle className="mx-auto h-6 w-6 text-destructive" />
      <p className="mt-2 font-medium">{error.message}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-4 rounded-full bg-foreground px-4 py-2 text-sm text-background">
          Try again
        </button>
      )}
    </div>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="rounded-2xl border border-dashed bg-card p-10 text-center">
      <Inbox className="mx-auto h-7 w-7 text-muted-foreground" />
      <p className="mt-3 font-display text-lg font-semibold">{title}</p>
      <div className="mt-1 text-sm text-muted-foreground">{children}</div>
    </div>
  );
}

export function SampleNotice({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <div className="mb-4 flex items-center gap-2 rounded-full bg-accent px-4 py-2 text-xs text-accent-foreground">
      <FlaskConical className="h-3.5 w-3.5" /> Showing sample data — the PriceBiz server couldn't be reached.
    </div>
  );
}
