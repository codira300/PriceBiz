import { Link } from "react-router";
import { ArrowRight, ArrowUpRight, PlusCircle } from "lucide-react";

import { usePageMeta } from "../lib/meta";
import { ProductPicker } from "../components/product-picker";
import { useCachedAsync } from "../hooks/use-async";
import { communityApi } from "../lib/api/services";
import { timeAgo } from "../lib/format";

const POPULAR = [
  "Dangote Sugar",
  "Semovita",
  "Nivea",
  "Ofada Rice",
  "Peak Milk",
];

const SELLERS = [
  "Market",
  "Supermarket",
  "Wholesaler",
  "Shop",
  "Mini Farm",
  "Online",
];

const TRUST = [
  {
    title: "Observed, not official",
    description:
      "Every range comes from real price observations submitted by people, with outliers counted separately.",
  },
  {
    title: "Location-aware",
    description:
      "Country → state → LGA → area → market. We tell you when we widen the area.",
  },
  {
    title: "Seller breakdown",
    description:
      "See why a supermarket and a market stall differ for the same item.",
  },
];

export default function Home() {
  const posts = useCachedAsync(
    "community:feed",
    () => communityApi.list(),
  );

  usePageMeta({
    title: "PriceBiz — Know the price before you buy",
    description:
      "Search everyday products and see what people are paying in your area of Nigeria.",
    ogTitle: "PriceBiz — Know the price before you buy",
    ogType: "website",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    twitterCard: "summary_large_image",
    twitterTitle: "PriceBiz — Know the price before you buy",
    twitterDescription:
      "Search everyday products and see what people are paying in your area of Nigeria.",
    twitterImage: "/hero-trader.jpg",
  });

  return (
    <div className="bg-background">
      <section
        aria-labelledby="hero-title"
        className="border-b border-border bg-secondary/50"
      >
        <div className="mx-auto max-w-6xl px-5">
          <div className="grid gap-10 py-12 md:grid-cols-[1.1fr_0.9fr] md:items-center md:gap-14 md:py-16">
            <div className="animate-fade-in">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                Price intelligence for everyday goods
              </p>

              <h1
                id="hero-title"
                className="mt-4 max-w-xl text-balance font-display text-[clamp(2.5rem,6vw,4.5rem)] font-bold leading-[1.03] tracking-[-0.035em]"
              >
                Know the price before you buy.
              </h1>

              <p className="mt-5 max-w-md text-pretty text-base leading-7 text-muted-foreground sm:text-lg sm:leading-8">
                Search everyday products and see what people are paying in
                your area — from Ikorodu markets to Wuse supermarkets.
              </p>

              <div className="mt-7">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Popular searches
                </p>

                <ul className="mt-2 flex flex-wrap gap-x-5 gap-y-1">
                  {POPULAR.map((product) => (
                    <li key={product}>
                      <Link
                        to={`/search?q=${encodeURIComponent(product)}`}
                        className="inline-flex min-h-11 items-center border-b border-border text-sm font-medium text-foreground transition-colors duration-150 ease-out hover:border-primary hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                      >
                        {product}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <figure className="w-full border border-border bg-card">
              <div className="flex items-center justify-between gap-4 border-b border-border px-4 py-3">
                <span className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
                  Field note
                </span>
                <span className="text-xs text-muted-foreground">
                  Ikorodu, Lagos
                </span>
              </div>

              <div className="aspect-[4/5] overflow-hidden bg-secondary">
                <img
                  src="/hero-trader.jpg"
                  alt="Market trader holding a basket of tomatoes and peppers"
                  width={896}
                  height={1152}
                  className="h-full w-full object-cover object-top"
                />
              </div>

              <figcaption className="border-t border-border px-4 py-3 text-sm leading-6 text-muted-foreground">
                <span className="font-medium text-foreground">
                  Mama Bisi
                </span>{" "}
                logs her pepper prices every market day.
              </figcaption>
            </figure>
          </div>

          <div className="border-t border-border py-8 md:py-10">
            <ProductPicker />
          </div>
        </div>
      </section>

      <section
        aria-labelledby="how-it-works"
        className="mx-auto max-w-6xl px-5 py-14 md:py-20"
      >
        <div className="grid gap-10 md:grid-cols-[0.85fr_1.15fr] md:gap-14">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
              How the data works
            </p>

            <h2
              id="how-it-works"
              className="mt-3 max-w-sm text-balance font-display text-[clamp(1.75rem,3vw,2.5rem)] font-bold leading-[1.15] tracking-[-0.025em]"
            >
              Prices from every kind of seller
            </h2>

            <p className="mt-4 max-w-sm text-pretty text-base leading-7 text-muted-foreground">
              Markets, supermarkets, shops, wholesalers, farms and online
              sellers all tell a different part of the price story.
            </p>

            <ul className="mt-6 flex flex-wrap gap-2" aria-label="Seller types">
              {SELLERS.map((seller) => (
                <li
                  key={seller}
                  className="border border-border bg-card px-2.5 py-1 text-xs font-medium text-muted-foreground"
                >
                  {seller}
                </li>
              ))}
            </ul>
          </div>

          <ol className="divide-y divide-border border-y border-border">
            {TRUST.map(({ title, description }, index) => (
              <li
                key={title}
                className="grid grid-cols-[2.5rem_1fr] gap-4 py-5 sm:grid-cols-[3.5rem_1fr] sm:py-6"
              >
                <span
                  aria-hidden="true"
                  className="font-display text-sm font-semibold tabular-nums text-primary"
                >
                  {String(index + 1).padStart(2, "0")}
                </span>

                <div>
                  <h3 className="text-base font-semibold leading-6">
                    {title}
                  </h3>
                  <p className="mt-1 text-sm leading-6 text-muted-foreground">
                    {description}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section
        aria-labelledby="community-heading"
        className="border-t border-border bg-secondary/40"
      >
        <div className="mx-auto grid max-w-6xl gap-10 px-5 py-14 md:grid-cols-[1.15fr_0.85fr] md:gap-14 md:py-20">
          <div>
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                  Community
                </p>

                <h2
                  id="community-heading"
                  className="mt-3 font-display text-[clamp(1.75rem,3vw,2.5rem)] font-bold leading-[1.15] tracking-[-0.025em]"
                >
                  Recent price talk
                </h2>
              </div>

              <Link
                to="/community"
                className="inline-flex min-h-11 items-center gap-1.5 text-sm font-medium text-primary transition-colors duration-150 ease-out hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                View all
                <ArrowUpRight aria-hidden="true" className="h-4 w-4" />
              </Link>
            </div>

            {posts.loading ? (
              <div
                className="mt-6 border-t border-border"
                aria-label="Loading community activity"
              >
                {[0, 1, 2].map((item) => (
                  <div key={item} className="border-b border-border py-4">
                    <div className="h-4 w-2/3 animate-pulse rounded-[2px] bg-primary/10" />
                    <div className="mt-2 h-3 w-1/3 animate-pulse rounded-[2px] bg-primary/10" />
                  </div>
                ))}
              </div>
            ) : posts.error ? (
              <div className="mt-6 border border-border bg-card p-5">
                <p className="text-sm font-medium">
                  Community activity is unavailable right now.
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {posts.error.message}
                </p>
                <button
                  type="button"
                  onClick={posts.retry}
                  className="mt-4 inline-flex min-h-11 items-center bg-foreground px-4 text-sm font-medium text-background transition-colors duration-150 ease-out hover:bg-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                >
                  Try again
                </button>
              </div>
            ) : !posts.data?.length ? (
              <div className="mt-6 border-y border-border py-8">
                <p className="text-base font-medium">No conversations yet.</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Start one with a price you saw today.
                </p>
              </div>
            ) : (
              <ul className="mt-6 border-t border-border">
                {posts.data.slice(0, 3).map((post) => (
                  <li key={post._id} className="border-b border-border">
                    <Link
                      to={`/community/${post._id}`}
                      className="group flex items-start justify-between gap-4 py-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                    >
                      <span className="min-w-0">
                        <span className="block truncate font-medium transition-colors duration-150 ease-out group-hover:text-primary">
                          {post.title || "Untitled discussion"}
                        </span>
                        <span className="mt-1 block text-sm text-muted-foreground">
                          {post.location_name || "Location not set"} ·{" "}
                          {timeAgo(post.created_at)}
                        </span>
                      </span>

                      <ArrowUpRight
                        aria-hidden="true"
                        className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground transition-colors duration-150 ease-out group-hover:text-primary"
                      />
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <aside className="flex flex-col justify-between bg-foreground p-6 text-background md:p-8">
            <div>
              <PlusCircle
                aria-hidden="true"
                className="h-6 w-6 text-primary-glow"
              />

              <h2 className="mt-4 text-balance font-display text-2xl font-bold leading-tight text-background">
                Bought something today?
              </h2>

              <p className="mt-2 max-w-sm text-pretty text-sm leading-6 text-background/75">
                Share what you paid. Each observation helps your neighbours
                negotiate fairly.
              </p>
            </div>

            <Link
              to="/contribute"
              className="mt-8 inline-flex min-h-11 w-fit items-center gap-2 bg-primary px-5 text-sm font-semibold text-primary-foreground transition-colors duration-150 ease-out hover:bg-primary-glow hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
            >
              Add a price
              <ArrowRight aria-hidden="true" className="h-4 w-4" />
            </Link>
          </aside>
        </div>
      </section>
    </div>
  );
}
