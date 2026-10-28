
import { Link } from "react-router";
import { useState } from "react";
import { MessageCircle } from "lucide-react";

import { Page, btnCls, inputCls } from "../components/layout";
import { Empty, ErrorState, PageSkeleton, SampleNotice } from "../components/states";
import { useCachedAsync } from "../hooks/use-async";
import { communityApi } from "../lib/api/services";
import { ApiError } from "../lib/api/client";
import { useAuth } from "../lib/auth";
import { usePageMeta } from "../lib/meta";
import { timeAgo } from "../lib/format";
import type { Post } from "../lib/types";

// Splits a stored post into a display title and body. Posts may carry an
// explicit title, or a single `content` string whose first paragraph is the
// title and the remainder is the body.
function splitPostContent(post: Post): { title: string; body: string } {
  const content = post.content ?? post.body ?? "";
  const separator = content.indexOf("\n\n");

  return {
    title:
      post.title ||
      (separator >= 0
        ? content.slice(0, separator)
        : content.split("\n")[0]) ||
      "Discussion",
    body:
      post.body ||
      (separator >= 0 ? content.slice(separator + 2) : content),
  };
}

export default function Community() {
  const { user } = useAuth();
  const feed = useCachedAsync(
    "community:feed",
    () => communityApi.list(),
  );

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [err, setErr] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);

  usePageMeta({
    title: "Community — PriceBiz",
    description:
      "Read and start discussions about prices, products and markets near you.",
    ogTitle: "Community — PriceBiz",
    ogType: "website",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    ogDescription:
      "Read and start discussions about prices, products and markets near you.",
    twitterCard: "summary_large_image",
    twitterTitle: "Community — PriceBiz",
    twitterDescription:
      "Read and start discussions about prices, products and markets near you.",
    twitterImage: "/hero-trader.jpg",
  });

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErr(null);

    const trimmedTitle = title.trim();
    const trimmedBody = body.trim();

    if (!user?._id) {
      setErr(
        new ApiError({
          code: "AUTH_REQUIRED",
          message: "Please log in again before posting.",
        }),
      );
      return;
    }

    if (!trimmedTitle || !trimmedBody) {
      setErr(
        new ApiError({
          code: "VALIDATION_ERROR",
          message: "Please enter both a title and discussion details.",
        }),
      );
      return;
    }

    setSubmitting(true);

    try {
      await communityApi.create({
        author_id: user._id,
        content: `${trimmedTitle}\n\n${trimmedBody}`,
        post_type: "GENERAL",
      });

      setTitle("");
      setBody("");
      await feed.retry();
    } catch (error) {
      setErr(
        error instanceof ApiError
          ? error
          : new ApiError({
              code: "UNKNOWN",
              message:
                error instanceof Error
                  ? error.message
                  : "Could not create the discussion. Please try again.",
            }),
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Page title="What people are saying" kicker="Community">
      <SampleNotice show={feed.sample} />

      <div className="grid gap-8 lg:grid-cols-[2fr_1fr]">
        <div>
          {feed.loading ? (
            <PageSkeleton />
          ) : feed.error ? (
            <ErrorState error={feed.error} onRetry={feed.retry} />
          ) : !feed.data?.length ? (
            <Empty title="No discussions yet">
              Start the first one.
            </Empty>
          ) : (
            <ul className="space-y-4">
              {feed.data.map((post) => {
                const { title: displayedTitle, body: displayedBody } =
                  splitPostContent(post);

                return (
                  <li key={post._id}>
                    <Link
                      to={`/community/${post._id}`}
                      className="block border border-border bg-card p-5 transition-colors duration-150 ease-out hover:border-primary/60 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                    >
                      <div className="flex flex-wrap gap-2 text-xs">
                        {post.product_name && (
                          <span className="border border-accent-foreground/15 bg-accent px-2 py-0.5 text-accent-foreground">
                            {post.product_name}
                          </span>
                        )}

                        {post.location_name && (
                          <span className="border border-border bg-muted px-2 py-0.5 text-muted-foreground">
                            {post.location_name}
                          </span>
                        )}
                      </div>

                      <h3 className="mt-3 text-balance font-display text-lg font-semibold leading-6">
                        {displayedTitle}
                      </h3>

                      <p className="mt-1 line-clamp-2 whitespace-pre-line text-sm leading-6 text-muted-foreground">
                        {displayedBody}
                      </p>

                      <p className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                        {post.author_name || "PriceBiz member"} ·{" "}
                        {timeAgo(post.created_at)}

                        <span className="flex items-center gap-1">
                          <MessageCircle aria-hidden="true" className="h-3.5 w-3.5" />
                          {post.comment_count ?? 0}
                        </span>
                      </p>
                    </Link>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        <aside className="h-fit border border-border bg-card p-6">
          <h2 className="font-display text-lg font-semibold">
            Start a discussion
          </h2>

          {!user ? (
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              <Link
                to="/auth/login"
                className="text-primary underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                Log in
              </Link>{" "}
              to post.
            </p>
          ) : (
            <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
              <div>
                <label
                  htmlFor="discussion-title"
                  className="mb-1.5 block text-sm font-medium"
                >
                  Title
                </label>

                <input
                  id="discussion-title"
                  required
                  maxLength={200}
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="e.g. Pepper prices in Ikorodu"
                  className={inputCls}
                />
              </div>

              <div>
                <label
                  htmlFor="discussion-body"
                  className="mb-1.5 block text-sm font-medium"
                >
                  Details
                </label>

                <textarea
                  id="discussion-body"
                  required
                  maxLength={10000}
                  value={body}
                  onChange={(event) => setBody(event.target.value)}
                  rows={4}
                  placeholder="What did you notice?"
                  className={inputCls}
                />
              </div>

              {err && (
                <div role="alert">
                  <ErrorState error={err} />
                </div>
              )}

              <button
                type="submit"
                className={btnCls}
                disabled={submitting}
              >
                {submitting ? "Posting…" : "Post"}
              </button>
            </form>
          )}
        </aside>
      </div>
    </Page>
  );
}
