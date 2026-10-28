import { Link, useParams, useSearchParams } from "react-router";
import { ChevronRight, Info, PlusCircle } from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { usePageMeta } from "../lib/meta";
import { LocationSelect } from "../components/location-select";
import { btnCls } from "../components/layout";
import {
  Empty,
  ErrorState,
  PageSkeleton,
  SampleNotice,
} from "../components/states";
import { useCachedAsync } from "../hooks/use-async";
import { pricesApi, productsApi } from "../lib/api/services";
import {
  formatDate,
  formatNaira,
  formatRange,
  sellerLabel,
} from "../lib/format";
import type {
  PriceAnalysis,
  PriceSummary,
  SellerTypeStat,
} from "../lib/types";

type SearchState = {
  variant?: string;
  loc?: string;
};

function getLocationName(value: unknown): string | undefined {
  if (
    typeof value === "object" &&
    value !== null &&
    "name" in value &&
    typeof value.name === "string"
  ) {
    return value.name;
  }

  return undefined;
}

// Positions a seller type's median price within the overall observed range,
// clamped to 0–100 so it can drive a progress bar. Falls back to the middle
// (50%) when the range is unavailable or degenerate.
function sellerBarPercent(
  seller: Pick<SellerTypeStat, "median_price">,
  summary: Pick<PriceSummary, "minimum" | "maximum">,
): number {
  const { minimum, maximum } = summary;

  if (minimum === null || maximum === null) {
    return 50;
  }

  const denominator = maximum * 1.2 - minimum * 0.8;
  if (denominator <= 0) {
    return 50;
  }

  return Math.min(
    100,
    Math.max(0, ((seller.median_price - minimum * 0.8) / denominator) * 100),
  );
}

export default function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const productId = id ?? "";

  const [searchParams, setSearchParams] = useSearchParams();

  const variant = searchParams.get("variant") ?? undefined;
  const loc = searchParams.get("loc") ?? undefined;

  usePageMeta({
    title: "Observed price range — PriceBiz",
    description:
      "Typical observed price range, seller breakdown and price trend for this product.",
    ogTitle: "Observed price range — PriceBiz",
    ogType: "product",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    ogDescription:
      "Typical observed price range, seller breakdown and price trend for this product.",
    twitterCard: "summary_large_image",
    twitterTitle: "Observed price range — PriceBiz",
    twitterDescription:
      "Typical observed price range, seller breakdown and price trend for this product.",
    twitterImage: "/hero-trader.jpg",
  });

  const product = useCachedAsync(
    `product:${productId}`,
    () => productsApi.get(productId),
  );

  const analysis = useCachedAsync(
    `price-analysis:${productId}:${variant ?? "any"}:${loc ?? "any"}`,
    () => pricesApi.analysis(productId, variant, loc),
  );

  const productData = product.data;

  const variantId =
    variant ?? analysis.data?.variant_id ?? productData?.variants?.[0]?._id;

  function setSearch(patch: SearchState) {
    const next = new URLSearchParams(searchParams);

    for (const [key, value] of Object.entries(patch)) {
      if (value === undefined || value === "") {
        next.delete(key);
      } else {
        next.set(key, value);
      }
    }

    setSearchParams(next);
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-12 md:py-16">
      <SampleNotice show={product.sample || analysis.sample} />

      <div className="mb-8 flex flex-col gap-6 border-b border-border pb-6 md:flex-row md:items-end md:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            {productData?.category ?? "Product"}
          </p>

          <h1 className="mt-2 text-balance font-display text-[clamp(2rem,4vw,3rem)] font-bold leading-[1.1] tracking-[-0.03em]">
            {productData?.name ?? (product.loading ? "Loading…" : "Product")}
          </h1>

          {productData?.brand && (
            <p className="mt-1 text-sm text-muted-foreground">
              {productData.brand}
            </p>
          )}

          {(productData?.variants?.length ?? 0) > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {productData?.variants?.map((v) => (
                <button
                  key={v._id}
                  type="button"
                  aria-pressed={variantId === v._id}
                  onClick={() => setSearch({ variant: v._id })}
                  className={`min-h-9 rounded-[3px] border px-3 text-sm transition-colors duration-150 ease-out focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring ${
                    variantId === v._id
                      ? "border-primary bg-accent text-accent-foreground"
                      : "border-border bg-card hover:border-primary"
                  }`}
                >
                  {v.name}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="w-full md:w-72">
          <LocationSelect
            label="Location"
            inputId="product-location"
            value={loc ?? ""}
            onChange={(value) =>
              setSearch({ loc: value || undefined })
            }
          />
        </div>
      </div>

      <div className="mt-8">
        {analysis.loading ? (
          <PageSkeleton label="Analysing prices…" />
        ) : analysis.error ? (
          <ErrorState
            error={analysis.error}
            onRetry={analysis.retry}
          />
        ) : analysis.data ? (
          <Analysis
            analysis={analysis.data}
            productId={productId}
            variantId={variantId}
          />
        ) : (
          <Empty title="Price analysis unavailable">
            <p>Price analysis could not be loaded. Please try again.</p>
            <div className="mt-5">
              <button
                type="button"
                className={btnCls}
                onClick={analysis.retry}
              >
                Try again
              </button>
            </div>
          </Empty>
        )}
      </div>
    </div>
  );
}

function Analysis({
  analysis,
  productId,
  variantId,
}: {
  analysis: PriceAnalysis;
  productId: string;
  variantId?: string;
}) {
  const location = analysis.location;
  const used = getLocationName(location?.used) ?? "your area";
  const requested =
    getLocationName(location?.requested) ?? "the selected location";
  const path = location?.path?.length ? location.path : [used];

  const sellerTypes: SellerTypeStat[] = Array.isArray(analysis.seller_types)
    ? (analysis.seller_types as SellerTypeStat[])
    : [];

  const trend = analysis.trend ?? [];
  const observations = analysis.observations ?? [];

  const contributeParams = new URLSearchParams({
    product: productId,
    ...(variantId ? { variant: variantId } : {}),
  });

  const contribute = (
    <Link
      to={`/contribute?${contributeParams.toString()}`}
      className={btnCls}
    >
      <PlusCircle className="h-4 w-4" />
      Help improve this estimate
    </Link>
  );

  if (analysis.type === "NO_DATA" || !analysis.price_summary) {
    return (
      <Empty title="Not enough price data yet">
        <p>
          PriceBiz doesn't have enough observations for this location.
        </p>
        <div className="mt-5">{contribute}</div>
      </Empty>
    );
  }

  const summary = analysis.price_summary;

  const priceRange =
    summary.minimum !== null && summary.maximum !== null
      ? formatRange(summary.minimum, summary.maximum)
      : "Price range unavailable";

  const statistics = [
    ["Total", summary.observation_count],
    ["Normal", summary.normal_observation_count],
    ["Outliers", summary.outlier_count],
  ] as const;

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <section className="border border-border bg-card p-6 md:p-8 lg:col-span-2">
        <nav
          aria-label="Price location"
          className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground"
        >
          {path.map((name, index) => (
            <span
              key={`${name}-${index}`}
              className="flex items-center gap-1"
            >
              {index > 0 && (
                <ChevronRight aria-hidden="true" className="h-3 w-3" />
              )}
              {name}
            </span>
          ))}
        </nav>

        <p className="mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-primary">
          Typical price range · near {used}
        </p>

        <p className="mt-2 break-words font-display text-[clamp(2.5rem,6vw,4rem)] font-bold leading-[1.05] tracking-[-0.03em]">
          {priceRange}
        </p>

        <p className="mt-3 max-w-lg text-sm leading-6 text-muted-foreground">
          Based on {summary.normal_observation_count} normal observations out of{" "}
          {summary.observation_count} total observations.
        </p>

        {location?.broadened && (
          <p className="mt-5 flex items-start gap-2 border-l-2 border-primary bg-accent px-4 py-3 text-sm leading-6 text-accent-foreground">
            <Info aria-hidden="true" className="mt-1 h-4 w-4 shrink-0" />
            Not enough observations for {requested}. Showing the broader{" "}
            {used} area.
          </p>
        )}

        <dl className="mt-6 grid grid-cols-3 gap-3">
          {statistics.map(([label, value]) => (
            <div
              key={label}
              className="flex flex-col-reverse border border-border bg-muted p-3 text-center"
            >
              <dt className="mt-1 text-xs leading-5 text-muted-foreground">
                {label} observations
              </dt>
              <dd className="font-display text-2xl font-bold tabular-nums">
                {value}
              </dd>
            </div>
          ))}
        </dl>

        <p className="mt-5 text-xs leading-5 text-muted-foreground">
          {summary.currency} observed price range, not an official price.
          Prices may vary by seller and location.
        </p>

        <div className="mt-6">{contribute}</div>
      </section>

      <section className="border border-border bg-card p-6">
        <h2 className="font-display text-xl font-semibold">
          By seller type
        </h2>

        <p className="mt-1 text-sm leading-6 text-muted-foreground">
          Why prices differ for the same item
        </p>

        {sellerTypes.length ? (
          <ul className="mt-5 space-y-4">
            {sellerTypes.map((seller) => {
              const pct = sellerBarPercent(seller, summary);

              return (
                <li key={seller.seller_type}>
                  <div className="flex justify-between gap-3 text-sm">
                    <span className="font-medium">
                      {sellerLabel(seller.seller_type)}{" "}
                      <span className="text-xs text-muted-foreground">
                        ({seller.count})
                      </span>
                    </span>

                    <span className="tabular-nums">
                      {formatNaira(seller.median_price)}
                    </span>
                  </div>

                  <div
                    className="mt-2 h-1.5 bg-muted"
                    role="img"
                    aria-label={`${sellerLabel(seller.seller_type)} median price is ${pct.toFixed(0)} percent across the observed range`}
                  >
                    <div
                      className="h-1.5 bg-primary"
                      style={{ width: `${Math.max(8, pct)}%` }}
                    />
                  </div>

                  <p className="mt-1 text-xs text-muted-foreground">
                    {formatRange(seller.min_price, seller.max_price)}
                  </p>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="mt-5 text-sm text-muted-foreground">
            No seller breakdown available yet.
          </p>
        )}
      </section>

      <section className="border border-border bg-card p-6 lg:col-span-2">
        <h2 className="font-display text-xl font-semibold">
          Observed price trend
        </h2>

        <p className="mt-1 text-sm leading-6 text-muted-foreground">
          This chart shows recorded prices over time. It does not predict
          future prices.
        </p>

        <div className="mt-5 h-64">
          {trend.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={trend}
                margin={{ left: 0, right: 8, top: 8 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--color-border)"
                />

                <XAxis
                  dataKey="date"
                  tickFormatter={(date) =>
                    formatDate(date).replace(/ \d{4}$/, "")
                  }
                  fontSize={12}
                  stroke="var(--color-muted-foreground)"
                />

                <YAxis
                  tickFormatter={(value) =>
                    `₦${(value / 1000).toFixed(1)}k`
                  }
                  fontSize={12}
                  width={48}
                  stroke="var(--color-muted-foreground)"
                />

                <Tooltip
                  formatter={(value) => [
                    formatNaira(Number(value)),
                    "Median observed",
                  ]}
                  labelFormatter={(date) => formatDate(String(date))}
                  contentStyle={{
                    borderRadius: 3,
                    border: "1px solid var(--color-border)",
                    boxShadow: "none",
                    backgroundColor: "var(--color-popover)",
                    fontSize: 12,
                  }}
                />

                <Line
                  type="monotone"
                  dataKey="median_price"
                  stroke="var(--color-primary)"
                  strokeWidth={2.5}
                  dot={{ r: 2.5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="py-20 text-center text-sm text-muted-foreground">
              No trend data yet.
            </p>
          )}
        </div>
      </section>

      <section className="border border-border bg-card p-6">
        <h2 className="font-display text-xl font-semibold">
          Recent observations
        </h2>

        {observations.length ? (
          <ul className="mt-4 divide-y divide-border">
            {observations.slice(0, 8).map((observation) => (
              <li
                key={observation._id}
                className="flex items-center justify-between gap-4 py-3 text-sm"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium">
                    {observation.seller_name ??
                      sellerLabel(observation.seller_type)}
                  </p>

                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {sellerLabel(observation.seller_type)} ·{" "}
                    {formatDate(observation.observed_at)}
                  </p>
                </div>

                <div className="shrink-0 text-right">
                  <p className="font-semibold tabular-nums">
                    {formatNaira(observation.price)}
                  </p>

                  {observation.is_outlier && (
                    <span className="text-xs uppercase tracking-wide text-destructive">
                      Outlier
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-sm text-muted-foreground">
            No price observations available yet.
          </p>
        )}
      </section>
    </div>
  );
}