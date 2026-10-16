import { Link } from "react-router";
import { ArrowRight, MessagesSquare, PlusCircle } from "lucide-react";

import { usePageMeta } from "../lib/meta";
import { ProductPicker } from "../components/product-picker";
import { useCachedAsync } from "../hooks/use-async";
import { communityApi } from "../lib/api/services";
import { timeAgo } from "../lib/format";
import { PageSkeleton } from "../components/states";

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

export default function Home() {
  const posts = useCachedAsync(
    "community:feed",
    () => communityApi.list(),
  );

  usePageMeta({
    title: "PriceBiz — Know the price before you buy",
    description:
      "Search everyday products and see what people are paying in your area of Nigeria.",
  });

  return (
    <>
      <section className="relative overflow-hidden bg-secondary/60">
        <div className="pointer-events-none absolute -right-40 -top-40 h-[42rem] w-[42rem] rounded-full border border-primary/40" />

        <div className="mx-auto grid max-w-6xl items-end gap-8 px-5 pt-14 md:grid-cols-[1.1fr_1fr] md:pt-20">
          <div className="pb-40 md:pb-48">
            <h1 className="font-display text-5xl font-bold leading-[1.02] tracking-tight md:text-7xl">
              PriceBiz
              <span className="block font-medium">know the price</span>
              <span className="block font-medium">before you buy.</span>
            </h1>

            <p className="mt-6 max-w-md text-lg text-muted-foreground">
              Search everyday products and see what people are paying in your
              area — from Ikorodu markets to Wuse supermarkets.
            </p>

            <div className="mt-6 flex flex-wrap gap-2">
              {POPULAR.map((product) => (
                <Link
                  key={product}
                  to={`/search?q=${encodeURIComponent(product)}`}
                  className="rounded-full border bg-card px-3 py-1 text-xs hover:border-primary"
                >
                  {product}
                </Link>
              ))}
            </div>
          </div>

          <div className="relative mx-auto h-[26rem] w-full max-w-md md:h-[34rem]">
            <div className="absolute bottom-0 left-1/2 h-[24rem] w-[20rem] -translate-x-1/2 overflow-hidden rounded-t-full bg-sun md:h-[32rem] md:w-[26rem]">
              <img
                src="/hero-trader.jpg"
                alt="Market trader holding a basket of tomatoes and peppers"
                width={896}
                height={1152}
                className="h-full w-full object-cover object-top"
              />
            </div>

            <div className="absolute -left-24 top-24 hidden text-left text-sm md:block">
              <p className="font-semibold">Mama Bisi (Ikorodu)</p>
              <p className="text-muted-foreground">
                Logs her pepper prices
                <br />
                every market day.
              </p>
            </div>
          </div>
        </div>
      </section>

      <div className="relative z-10 mx-auto -mt-32 max-w-4xl px-5">
        <ProductPicker />
      </div>

      <section className="mx-auto grid max-w-6xl gap-6 px-5 py-20 md:grid-cols-[1fr_2fr]">
        <h2 className="font-display text-4xl font-bold leading-tight">
          Prices from <span className="text-primary">every kind</span> of seller
        </h2>

        <div className="grid gap-4 sm:grid-cols-3">
          {[
            [
              "Observed, not official",
              "Every range comes from real price observations, with outliers counted separately.",
            ],
            [
              "Location-aware",
              "Country → State → LGA → Area → Market. We tell you when we widen the area.",
            ],
            [
              "Seller breakdown",
              "See why a supermarket and a market stall differ for the same item.",
            ],
          ].map(([title, description]) => (
            <div key={title} className="rounded-3xl border bg-card p-6">
              <h3 className="font-display text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {description}
              </p>
            </div>
          ))}

          <div className="flex flex-wrap gap-2 sm:col-span-3">
            {SELLERS.map((seller) => (
              <span
                key={seller}
                className="rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground"
              >
                {seller}
              </span>
            ))}
          </div>
        </div>
      </section>

      <hr className="section-divider" />

      <section className="mx-auto grid max-w-6xl gap-6 px-5 pb-20 md:grid-cols-2">
        <div className="rounded-3xl border bg-card p-6">
          <div className="flex items-center justify-between">
            <h3 className="flex items-center gap-2 font-display text-xl font-semibold">
              <MessagesSquare className="h-5 w-5 text-primary" />
              Community activity
            </h3>

            <Link to="/community" className="text-sm text-primary">
              View all
            </Link>
          </div>

          <ul className="mt-4 divide-y">
            {posts.data?.slice(0, 3).map((post) => (
              <li key={post._id} className="py-3">
                <Link
                  to={`/community/${post._id}`}
                  className="font-medium hover:text-primary"
                >
                  {post.title}
                </Link>

                <p className="text-xs text-muted-foreground">
                  {post.location_name} · {timeAgo(post.created_at)}
                </p>
              </li>
            ))}

            {posts.loading && (
              <li className="py-3">
                <PageSkeleton label="Loading community activity…" />
              </li>
            )}
          </ul>
        </div>

        <div className="flex flex-col justify-between rounded-3xl bg-foreground p-8 text-background">
          <div>
            <PlusCircle className="h-7 w-7 text-primary-glow" />

            <h3 className="mt-3 font-display text-2xl font-bold">
              Bought something today?
            </h3>

            <p className="mt-2 text-sm opacity-80">
              Share what you paid. Each observation helps your neighbours
              negotiate fairly.
            </p>
          </div>

          <Link
            to="/contribute"
            className="mt-6 inline-flex w-fit items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground"
          >
            Add a price
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </>
  );
}
