import { useEffect } from "react";
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

import { LocationSelect } from "../components/location-select";
import { btnCls } from "../components/layout";
import {
  Empty,
  ErrorState,
  Loading,
  SampleNotice,
} from "../components/states";
import { useAsync } from "../hooks/use-async";
import { pricesApi, productsApi } from "../lib/api/services";
import {
  formatDate,
  formatNaira,
  formatRange,
  sellerLabel,
} from "../lib/format";
import type { PriceAnalysis, SellerTypeStat } from "../lib/types";

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

export default function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const productId = id ?? "";

  const [searchParams, setSearchParams] = useSearchParams();

  const variant = searchParams.get("variant") ?? undefined;
  const loc = searchParams.get("loc") ?? undefined;

  useEffect(() => {
    document.title = "Observed price range — PriceBiz";

    const description =
      "Typical observed price range, seller breakdown and price trend for this product.";

    const updateMeta = (
      selector: string,
      attribute: string,
      value: string,
    ) => {
      let element = document.querySelector<HTMLMetaElement>(selector);

      if (!element) {
        element = document.createElement("meta");
        const match = selector.match(/["']([^"']+)["']/);

        if (!match) {
          return;
        }

        element.setAttribute(
          selector.includes("property=") ? "property" : "name",
          match[1],
        );

        document.head.appendChild(element);
      }

      element.setAttribute(attribute, value);
    };

    updateMeta('meta[name="description"]', "content", description);
    updateMeta('meta[property="og:title"]', "content", document.title);
    updateMeta(
      'meta[property="og:description"]',
      "content",
      description,
    );
  }, []);

  const product = useAsync(
    () => productsApi.get(productId),
    [productId],
  );

  const analysis = useAsync(
    () => pricesApi.analysis(productId, variant, loc),
    [productId, variant, loc],
  );

  const p = product.data;

  const variantId =
    variant ?? analysis.data?.variant_id ?? p?.variants?.[0]?._id;

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
    <div className="mx-auto max-w-6xl px-5 py-10">
      <SampleNotice show={product.sample || analysis.sample} />

      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-primary">
            {p?.category ?? "Product"}
          </p>

          <h1 className="mt-1 font-display text-4xl font-bold">
            {p?.name ?? (product.loading ? "Loading…" : "Product")}
          </h1>

          {p?.brand && (
            <p className="text-muted-foreground">{p.brand}</p>
          )}

          {(p?.variants?.length ?? 0) > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {p?.variants?.map((v) => (
                <button
                  key={v._id}
                  type="button"
                  onClick={() => setSearch({ variant: v._id })}
                  className={`rounded-full border px-3 py-1.5 text-sm ${
                    variantId === v._id
                      ? "border-primary bg-accent text-accent-foreground"
                      : "bg-card"
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
            value={loc ?? ""}
            onChange={(value) =>
              setSearch({ loc: value || undefined })
            }
          />
        </div>
      </div>

      <div className="mt-8">
        {analysis.loading ? (
          <Loading label="Analysing prices…" />
        ) : analysis.error ? (
          <ErrorState
            error={analysis.error}
            onRetry={analysis.retry}
          />
        ) : analysis.data ? (
          <Analysis
            a={analysis.data}
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
  a,
  productId,
  variantId,
}: {
  a: PriceAnalysis;
  productId: string;
  variantId?: string;
}) {
  const location = a.location;
  const used = getLocationName(location?.used) ?? "your area";
  const requested =
    getLocationName(location?.requested) ?? "the selected location";
  const path = location?.path?.length ? location.path : [used];

  const sellerTypes: SellerTypeStat[] = Array.isArray(a.seller_types)
    ? (a.seller_types as SellerTypeStat[])
    : [];

  const trend = a.trend ?? [];
  const observations = a.observations ?? [];

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

  if (a.type === "NO_DATA" || !a.price_summary) {
    return (
      <Empty title="Not enough price data yet">
        <p>
          PriceBiz doesn't have enough observations for this location.
        </p>
        <div className="mt-5">{contribute}</div>
      </Empty>
    );
  }

  const s = a.price_summary;

  const priceRange =
    s.minimum !== null && s.maximum !== null
      ? formatRange(s.minimum, s.maximum)
      : "Price range unavailable";

  const statistics = [
    ["Total", s.observation_count],
    ["Normal", s.normal_observation_count],
    ["Outliers", s.outlier_count],
  ] as const;

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <section className="relative overflow-hidden rounded-[2rem] border bg-card p-8 lg:col-span-2">
        <div className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-sun opacity-20" />

        <nav className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
          {path.map((name, index) => (
            <span
              key={`${name}-${index}`}
              className="flex items-center gap-1"
            >
              {index > 0 && <ChevronRight className="h-3 w-3" />}
              {name}
            </span>
          ))}
        </nav>

        <p className="mt-4 text-sm font-semibold uppercase tracking-widest text-primary">
          Typical price range · near {used}
        </p>

        <p className="mt-2 font-display text-5xl font-bold tracking-tight md:text-6xl">
          {priceRange}
        </p>

        <p className="mt-3 text-muted-foreground">
          Based on {s.normal_observation_count} normal observations out of{" "}
          {s.observation_count} total observations.
        </p>

        {location?.broadened && (
          <p className="mt-4 flex items-start gap-2 rounded-xl bg-accent px-4 py-3 text-sm text-accent-foreground">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            Not enough observations for {requested}. Showing the broader{" "}
            {used} area.
          </p>
        )}

        <div className="mt-6 grid grid-cols-3 gap-3 text-center">
          {statistics.map(([label, value]) => (
            <div key={label} className="rounded-2xl bg-muted p-3">
              <p className="font-display text-2xl font-bold">{value}</p>
              <p className="text-xs text-muted-foreground">
                {label} observations
              </p>
            </div>
          ))}
        </div>

        <p className="mt-5 text-xs text-muted-foreground">
          {s.currency} observed price range, not an official price. Prices
          may vary by seller and location.
        </p>

        <div className="mt-6">{contribute}</div>
      </section>

      <section className="rounded-[2rem] border bg-card p-6">
        <h2 className="font-display text-xl font-semibold">
          By seller type
        </h2>

        <p className="text-xs text-muted-foreground">
          Why prices differ for the same item
        </p>

        {sellerTypes.length ? (
          <ul className="mt-4 space-y-3">
            {sellerTypes.map((seller) => {
              const denominator =
                s.minimum !== null && s.maximum !== null
                  ? s.maximum * 1.2 - s.minimum * 0.8
                  : 0;

              const pct =
                denominator > 0 && s.minimum !== null
                  ? Math.min(
                      100,
                      Math.max(
                        0,
                        ((seller.median_price - s.minimum * 0.8) /
                          denominator) *
                          100,
                      ),
                    )
                  : 50;

              return (
                <li key={seller.seller_type}>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">
                      {sellerLabel(seller.seller_type)}{" "}
                      <span className="text-xs text-muted-foreground">
                        ({seller.count})
                      </span>
                    </span>

                    <span>{formatNaira(seller.median_price)}</span>
                  </div>

                  <div className="mt-1 h-2 rounded-full bg-muted">
                    <div
                      className="h-2 rounded-full bg-primary"
                      style={{ width: `${Math.max(8, pct)}%` }}
                    />
                  </div>

                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {formatRange(seller.min_price, seller.max_price)}
                  </p>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="mt-4 text-sm text-muted-foreground">
            No seller breakdown available yet.
          </p>
        )}
      </section>

      <section className="rounded-[2rem] border bg-card p-6 lg:col-span-2">
        <h2 className="font-display text-xl font-semibold">
          Observed price trend
        </h2>

        <p className="text-xs text-muted-foreground">
          This chart shows recorded prices over time. It does not predict
          future prices.
        </p>

        <div className="mt-4 h-64">
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
                  fontSize={11}
                  stroke="var(--color-muted-foreground)"
                />

                <YAxis
                  tickFormatter={(value) =>
                    `₦${(value / 1000).toFixed(1)}k`
                  }
                  fontSize={11}
                  width={48}
                  stroke="var(--color-muted-foreground)"
                />

                <Tooltip
                  formatter={(value) => [
                    formatNaira(Number(value)),
                    "Median observed",
                  ]}
                  labelFormatter={(date) => formatDate(String(date))}
                />

                <Line
                  type="monotone"
                  dataKey="median_price"
                  stroke="var(--color-primary)"
                  strokeWidth={3}
                  dot={{ r: 3 }}
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

      <section className="rounded-[2rem] border bg-card p-6">
        <h2 className="font-display text-xl font-semibold">
          Recent observations
        </h2>

        {observations.length ? (
          <ul className="mt-3 divide-y">
            {observations.slice(0, 8).map((observation) => (
              <li
                key={observation._id}
                className="flex items-center justify-between py-2.5 text-sm"
              >
                <div>
                  <p className="font-medium">
                    {observation.seller_name ??
                      sellerLabel(observation.seller_type)}
                  </p>

                  <p className="text-xs text-muted-foreground">
                    {sellerLabel(observation.seller_type)} ·{" "}
                    {formatDate(observation.observed_at)}
                  </p>
                </div>

                <div className="text-right">
                  <p className="font-semibold">
                    {formatNaira(observation.price)}
                  </p>

                  {observation.is_outlier && (
                    <span className="text-[10px] uppercase tracking-wide text-destructive">
                      Outlier
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-muted-foreground">
            No price observations available yet.
          </p>
        )}
      </section>
    </div>
  );
}