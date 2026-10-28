import { Link, useParams } from "react-router";
import { useState } from "react";

import { btnCls, inputCls } from "../components/layout";
import { ErrorState, PageSkeleton, SampleNotice } from "../components/states";
import { useCachedAsync } from "../hooks/use-async";
import { usePageMeta } from "../lib/meta";
import { communityApi } from "../lib/api/services";
import { ApiError } from "../lib/api/client";
import { useAuth } from "../lib/auth";
import { timeAgo } from "../lib/format";

export default function PostPage() {
  const { id } = useParams();

  if (!id) {
    return (
      <ErrorState
        error={new ApiError({
          code: "INVALID_ROUTE",
          message: "Post ID is missing.",
        })}
      />
    );
  }

  return <PostContent id={id} />;
}

function PostContent({ id }: { id: string }) {
  const { user } = useAuth();

  const post = useCachedAsync(
    `community:post:${id}`,
    () => communityApi.get(id),
  );

  const p = post.data;

  usePageMeta({
    title: p?.title ? `${p.title} — PriceBiz` : "Post — PriceBiz",
    description:
      p?.body ??
      "Read and join the discussion about prices on PriceBiz.",
    ogTitle: p?.title ? `${p.title} — PriceBiz` : "Post — PriceBiz",
    ogType: "article",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    ogDescription:
      p?.body ??
      "Read and join the discussion about prices on PriceBiz.",
    twitterCard: "summary",
    twitterTitle: p?.title ? `${p.title} — PriceBiz` : "Post — PriceBiz",
    twitterDescription:
      p?.body ??
      "Read and join the discussion about prices on PriceBiz.",
    twitterImage: "/hero-trader.jpg",
  });

  const [text, setText] = useState("");
  const [err, setErr] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const trimmed = text.trim();
  const canSubmit = trimmed.length > 0 && !submitting;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;

    setErr(null);
    setSubmitting(true);

    try {
      await communityApi.comment(id, trimmed);
      setText("");
      post.retry();
    } catch (error) {
      setErr(
        error instanceof ApiError
          ? error
          : new ApiError({
              code: "UNKNOWN",
              message:
                error instanceof Error
                  ? error.message
                  : "Something went wrong. Please try again.",
            }),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-5 py-12 md:py-16">
      <Link
        to="/community"
        className="inline-flex min-h-11 items-center rounded-[3px] text-sm text-primary transition-colors duration-150 ease-out hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
      >
        ← Community
      </Link>

      {post.loading ? (
        <PageSkeleton />
      ) : post.error ? (
        <ErrorState error={post.error} onRetry={post.retry} />
      ) : p ? (
        <>
          <SampleNotice show={post.sample} />

          <article className="mt-4 border border-border bg-card p-6 md:p-8">
            <h1 className="text-balance font-display text-[clamp(1.75rem,4vw,2.5rem)] font-bold leading-[1.15] tracking-[-0.025em]">
              {p.title}
            </h1>

            <p className="mt-2 text-sm text-muted-foreground">
              {p.author_name || "PriceBiz member"} ·{" "}
              {p.location_name || "Location not set"} ·{" "}
              {timeAgo(p.created_at)}
            </p>

            <p className="mt-5 whitespace-pre-line text-base leading-7">
              {p.body}
            </p>
          </article>

          <h2 className="mt-8 font-display text-xl font-semibold">Replies</h2>

          <ul className="mt-3 space-y-3">
            {(p.comments ?? []).map((comment) => (
              <li
                key={comment._id}
                className="border border-border bg-card p-4"
              >
                <p className="text-sm leading-6">{comment.body}</p>

                <p className="mt-2 text-xs text-muted-foreground">
                  {comment.author_name || "PriceBiz member"} ·{" "}
                  {timeAgo(comment.created_at)}
                </p>
              </li>
            ))}

            {!p.comments?.length && (
              <li className="border border-dashed border-border px-4 py-6 text-sm text-muted-foreground">
                No replies yet. Add the first one.
              </li>
            )}
          </ul>

          {user ? (
            <form className="mt-5 space-y-3" onSubmit={handleSubmit}>
              <label
                htmlFor="post-reply"
                className="block text-sm font-medium"
              >
                Add a reply
              </label>

              <textarea
                id="post-reply"
                required
                rows={3}
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="What did you notice?"
                className={inputCls}
              />

              {err && (
                <div role="alert">
                  <ErrorState error={err} />
                </div>
              )}

              <button
                type="submit"
                className={btnCls}
                disabled={!canSubmit}
              >
                {submitting ? "Posting…" : "Reply"}
              </button>
            </form>
          ) : (
            <p className="mt-5 text-sm text-muted-foreground">
              <Link
                to="/auth/login"
                className="text-primary underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                Log in
              </Link>{" "}
              to reply.
            </p>
          )}
        </>
      ) : null}
    </div>
  );
}