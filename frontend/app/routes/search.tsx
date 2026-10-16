import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";
import { Search as SearchIcon, X as ClearIcon } from "lucide-react";
import { Page, btnCls, inputCls } from "../components/layout";
import {
  Empty,
  ErrorState,
  PageSkeleton,
  SampleNotice,
} from "../components/states";
import { usePageMeta } from "../lib/meta";
import { useCachedAsync } from "../hooks/use-async";
import { productsApi } from "../lib/api/services";

type SearchVariant = {
  _id: string;
  name: string;
  attributes?: Record<string, unknown>;
};

type SearchProduct = {
  _id?: string;
  name?: string;
  brand?: string | null;
  category?: string | null;
  observation_count?: number;
  variants?: SearchVariant[];
  product?: {
    _id: string;
    name: string;
    brand?: string | null;
    category?: string | null;
  };
  variant?: SearchVariant;
};

// Normalises a search hit, which may arrive nested under `product` or as a
// flat record, into a consistent shape for the UI.
function normalizeSearchResult(item: SearchProduct): SearchProduct {
  const product = item.product ?? item;

  const variants = item.product
    ? item.variant
      ? [item.variant]
      : []
    : Array.isArray(item.variants)
      ? item.variants
      : [];

  return {
    _id: product._id ?? item._id ?? "",
    name: product.name ?? item.name ?? "Unnamed product",
    brand: product.brand ?? item.brand ?? null,
    category: product.category ?? item.category ?? null,
    observation_count: item.observation_count ?? 0,
    variants: variants.filter((variant) => Boolean(variant._id)),
  };
}

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const q = searchParams.get("q") ?? "";
  const [text, setText] = useState(q);

  const res = useCachedAsync(
    `products:search:${q || "__empty__"}`,
    () =>
      q
        ? productsApi.search(q)
        : Promise.resolve({ data: [], sample: false }),
  );

  const products = Array.isArray(res.data)
    ? (res.data as SearchProduct[]).map(normalizeSearchResult)
    : [];

  usePageMeta({
    title: "Search products — PriceBiz",
    description:
      "Find a product and see its observed price range near you.",
    ogTitle: "Search products — PriceBiz",
    ogType: "website",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    ogDescription:
      "Find a product and see its observed price range near you.",
    twitterCard: "summary",
    twitterTitle: "Search products — PriceBiz",
    twitterDescription:
      "Find a product and see its observed price range near you.",
    twitterImage: "/hero-trader.jpg",
  });

  useEffect(() => {
    setText(q);
  }, [q]);

  function handleSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const trimmed = text.trim();

    if (trimmed) {
      navigate(`/search?q=${encodeURIComponent(trimmed)}`);
    } else {
      setSearchParams({});
    }
  }

  return (
    <Page
      title={q ? `Results for “${q}”` : "Search products"}
      kicker="Search"
    >
      <form onSubmit={handleSearch} className="mb-8 flex gap-2">
        <div className="relative flex-1">
          <SearchIcon className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Search for a product..."
            className={`${inputCls} pl-10 pr-10`}
          />

          {text && (
            <button
              type="button"
              onClick={() => {
                setText("");
                setSearchParams({});
              }}
              aria-label="Clear search"
              className="z-10 absolute right-3 top-1/2 -translate-y-1/2 rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              <ClearIcon className="h-4 w-4" />
            </button>
          )}
        </div>

        <button type="submit" className={btnCls}>
          Search
        </button>
      </form>

      <SampleNotice show={res.sample} />

      {!q ? (
        <Empty title="Type a product to begin">
          Try “sugar”, “nivea” or “rice”.
        </Empty>
      ) : res.loading ? (
        <PageSkeleton label="Searching…" />
      ) : res.error ? (
        <ErrorState error={res.error} onRetry={res.retry} />
      ) : !products.length ? (
        <Empty title="No products found">
          We couldn't find “{q}”.{" "}
          <Link
            to="/products/new"
            className="text-primary underline"
          >
            Add this product
          </Link>
        </Empty>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2">
          {products.map((p) => (
            <li
              key={p._id || `${p.name}-${p.brand ?? ""}`}
              className="rounded-3xl border bg-card p-5 card-hover"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-display text-lg font-semibold">
                    {p.name}
                  </h3>

                  <p className="text-sm text-muted-foreground">
                    {[p.brand, p.category]
                      .filter(Boolean)
                      .join(" · ")}
                  </p>
                </div>

                <span className="rounded-full bg-accent px-2.5 py-1 text-xs text-accent-foreground">
                  {p.observation_count} observations
                </span>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {p.variants.map((v) => (
                  <Link
                    key={v._id}
                    to={`/product/${p._id}?variant=${encodeURIComponent(v._id)}`}
                    className="rounded-full border px-3 py-1.5 text-sm hover:border-primary hover:text-primary"
                  >
                    {v.name} →
                  </Link>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </Page>
  );
}
