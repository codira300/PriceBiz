import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";
import { Search as SearchIcon } from "lucide-react";
import { Page, btnCls, inputCls } from "../components/layout";
import {
  Empty,
  ErrorState,
  Loading,
  SampleNotice,
} from "../components/states";
import { useAsync } from "../hooks/use-async";
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

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const q = searchParams.get("q") ?? "";
  const [text, setText] = useState(q);

  const res = useAsync(
    () =>
      q
        ? productsApi.search(q)
        : Promise.resolve({ data: [], sample: false }),
    [q],
  );

  const products = ((res.data ?? []) as unknown as SearchProduct[]).map(
    (item) => {
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
    },
  );

  useEffect(() => {
    document.title = "Search products — PriceBiz";

    const description =
      "Find a product and see its observed price range near you.";

    const metadata = [
      { name: "description", content: description },
      { property: "og:title", content: "Search products — PriceBiz" },
      { property: "og:description", content: description },
    ];

    for (const { name, property, content } of metadata) {
      const selector = name
        ? `meta[name="${name}"]`
        : `meta[property="${property}"]`;

      let element = document.head.querySelector(selector);

      if (!element) {
        element = document.createElement("meta");

        if (name) {
          element.setAttribute("name", name);
        } else if (property) {
          element.setAttribute("property", property);
        }

        document.head.appendChild(element);
      }

      element.setAttribute("content", content);
    }
  }, []);

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
            className={`${inputCls} pl-10`}
          />
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
        <Loading label="Searching…" />
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
              className="rounded-3xl border bg-card p-5"
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
