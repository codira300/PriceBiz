import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { ArrowRight, Search } from "lucide-react";

import { productsApi } from "../lib/api/services";
import type { Product } from "../lib/types";
import { LocationSelect } from "./location-select";
import { btnCls, inputCls } from "./layout";

/**
 * Floating hero card: pick product + variant + location,
 * then jump to price intelligence.
 */
export function ProductPicker() {
  const navigate = useNavigate();

  const [q, setQ] = useState("");
  const [results, setResults] = useState<Product[]>([]);
  const [product, setProduct] = useState<Product | null>(null);
  const [variant, setVariant] = useState("");
  const [loc, setLoc] = useState("");

  useEffect(() => {
    if (product && q === product.name) {
      return;
    }

    if (q.trim().length < 2) {
      setResults([]);
      return;
    }

    const timer = setTimeout(() => {
      productsApi
        .search(q)
        .then((response) => setResults(response.data))
        .catch(() => setResults([]));
    }, 250);

    return () => clearTimeout(timer);
  }, [q, product]);

  const go = () => {
    if (product) {
      const params = new URLSearchParams();

      if (variant) {
        params.set("variant", variant);
      }

      if (loc) {
        params.set("loc", loc);
      }

      const queryString = params.toString();

      navigate(
        `/product/${encodeURIComponent(product._id)}${
          queryString ? `?${queryString}` : ""
        }`,
      );
    } else if (q.trim()) {
      navigate(`/search?q=${encodeURIComponent(q.trim())}`);
    }
  };

  return (
    <div className="rounded-[2.5rem] border bg-card p-6 shadow-float md:p-10">
      <p className="text-center text-xs font-semibold uppercase tracking-widest text-primary">
        Start here — check a price
      </p>

      <h2 className="mt-2 text-center font-display text-2xl font-bold md:text-3xl">
        What are you buying?
      </h2>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          go();
        }}
        className="mx-auto mt-6 grid max-w-3xl gap-3 md:grid-cols-[1.4fr_1fr]"
      >
        <div className="relative">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          />

          <input
            value={q}
            onChange={(event) => {
              setQ(event.target.value);
              setProduct(null);
              setVariant("");
            }}
            placeholder="Search for a product..."
            className={`${inputCls} pl-10`}
            aria-label="Search for a product"
          />

          {results.length > 0 && !product && (
            <ul className="absolute z-20 mt-2 w-full overflow-hidden rounded-xl border bg-popover shadow-float">
              {results.slice(0, 6).map((p) => (
                <li key={p._id}>
                  <button
                    type="button"
                    onClick={() => {
                      setProduct(p);
                      setQ(p.name);
                      setVariant(p.variants[0]?._id ?? "");
                      setResults([]);
                    }}
                    className="flex w-full items-center justify-between px-4 py-2.5 text-left text-sm hover:bg-muted"
                  >
                    <span>
                      {p.name}
                      {p.brand && (
                        <span className="text-muted-foreground">
                          {" "}
                          · {p.brand}
                        </span>
                      )}
                    </span>

                    <span className="text-xs text-muted-foreground">
                      {p.observation_count ?? 0} obs.
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <LocationSelect value={loc} onChange={setLoc} />

        {product && product.variants.length > 1 && (
          <div className="flex flex-wrap gap-2 md:col-span-2">
            {product.variants.map((v) => (
              <button
                type="button"
                key={v._id}
                onClick={() => setVariant(v._id)}
                className={`rounded-full border px-3 py-1 text-xs ${
                  variant === v._id
                    ? "border-primary bg-accent text-accent-foreground"
                    : ""
                }`}
              >
                {v.name}
              </button>
            ))}
          </div>
        )}

        <div className="text-center md:col-span-2">
          <button
            type="submit"
            className={btnCls}
            disabled={!q.trim()}
          >
            {product ? "See observed prices" : "Search"}
            <ArrowRight className="h-4 w-4" />
          </button>

          <p className="mt-3 text-xs text-muted-foreground">
            Prices come from community observations and may vary by seller
            and location.
          </p>
        </div>
      </form>
    </div>
  );
}