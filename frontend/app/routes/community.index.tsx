
import { Link } from "react-router";
import { useEffect, useState } from "react";
import { MessageCircle } from "lucide-react";

import { Page, btnCls, inputCls } from "../components/layout";
import {
  Empty,
  ErrorState,
  Loading,
  SampleNotice,
} from "../components/states";
import { useAsync } from "../hooks/use-async";
import { communityApi } from "../lib/api/services";
import { ApiError } from "../lib/api/client";
import { useAuth } from "../lib/auth";
import { timeAgo } from "../lib/format";

export default function Community() {
  const { user } = useAuth();
  const feed = useAsync(() => communityApi.list(), []);

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [err, setErr] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    document.title = "Community — PriceBiz";
  }, []);

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
            <Loading />
          ) : feed.error ? (
            <ErrorState error={feed.error} onRetry={feed.retry} />
          ) : !feed.data?.length ? (
            <Empty title="No discussions yet">
              Start the first one.
            </Empty>
          ) : (
            <ul className="space-y-4">
              {feed.data.map((post) => {
                const content = post.content ?? post.body ?? "";
                const separator = content.indexOf("\n\n");
                const displayedTitle =
                  post.title ||
                  (separator >= 0
                    ? content.slice(0, separator)
                    : content.split("\n")[0]) ||
                  "Discussion";
                const displayedBody =
                  post.body ||
                  (separator >= 0
                    ? content.slice(separator + 2)
                    : content);

                return (
                  <li key={post._id}>
                    <Link
                      to={`/community/${post._id}`}
                      className="block rounded-3xl border bg-card p-5 hover:border-primary"
                    >
                      <div className="flex flex-wrap gap-2 text-xs">
                        {post.product_name && (
                          <span className="rounded-full bg-accent px-2 py-0.5 text-accent-foreground">
                            {post.product_name}
                          </span>
                        )}

                        {post.location_name && (
                          <span className="rounded-full bg-muted px-2 py-0.5">
                            {post.location_name}
                          </span>
                        )}
                      </div>

                      <h3 className="mt-2 font-display text-lg font-semibold">
                        {displayedTitle}
                      </h3>

                      <p className="mt-1 line-clamp-2 whitespace-pre-line text-sm text-muted-foreground">
                        {displayedBody}
                      </p>

                      <p className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                        {post.author_name || "PriceBiz member"} ·{" "}
                        {timeAgo(post.created_at)}

                        <span className="flex items-center gap-1">
                          <MessageCircle className="h-3 w-3" />
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

        <aside className="h-fit rounded-3xl border bg-card p-6">
          <h2 className="font-display text-lg font-semibold">
            Start a discussion
          </h2>

          {!user ? (
            <p className="mt-2 text-sm text-muted-foreground">
              <Link to="/auth/login" className="text-primary underline">
                Log in
              </Link>{" "}
              to post.
            </p>
          ) : (
            <form className="mt-3 space-y-3" onSubmit={handleSubmit}>
              <input
                required
                maxLength={200}
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Title"
                aria-label="Discussion title"
                className={inputCls}
              />

              <textarea
                required
                maxLength={10000}
                value={body}
                onChange={(event) => setBody(event.target.value)}
                rows={4}
                placeholder="What did you notice?"
                aria-label="Discussion details"
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
