import {
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { useNavigate } from "react-router";
import { ArrowRight, Search } from "lucide-react";

import { productsApi } from "../lib/api/services";
import { cn } from "../lib/utils";
import { LocationSelect } from "./location-select";

type PickerVariant = {
  _id: string;
  name: string;
};

type PickerProduct = {
  _id: string;
  name: string;
  brand: string | null;
  observationCount: number;
  variants: PickerVariant[];
};

type SearchHit = {
  _id?: string;
  name?: string;
  brand?: string | null;
  observation_count?: number;
  variants?: PickerVariant[];
  product?: {
    _id: string;
    name: string;
    brand?: string | null;
  };
  variant?: PickerVariant;
};

/**
 * Normalises a search hit, which may arrive nested under `product` or as a
 * flat record, into a consistent shape for the picker.
 */
function normalizeHit(hit: SearchHit): PickerProduct | null {
  const product = hit.product ?? hit;

  if (!product._id || !product.name) {
    return null;
  }

  const variants = hit.product
    ? hit.variant
      ? [hit.variant]
      : []
    : Array.isArray(hit.variants)
      ? hit.variants
      : [];

  return {
    _id: product._id,
    name: product.name,
    brand: product.brand ?? null,
    observationCount: hit.observation_count ?? 0,
    variants: variants.filter((variant) => Boolean(variant._id)),
  };
}

const fieldCls =
  "min-h-11 w-full rounded-[3px] border border-input bg-background px-3 py-2.5 text-base text-foreground outline-none transition-colors duration-150 ease-out placeholder:text-muted-foreground focus:border-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

/**
 * Hero search: pick product + variant + location, then jump to price
 * intelligence.
 */
export function ProductPicker() {
  const navigate = useNavigate();

  const [q, setQ] = useState("");
  const [results, setResults] = useState<PickerProduct[]>([]);
  const [product, setProduct] = useState<PickerProduct | null>(null);
  const [variant, setVariant] = useState("");
  const [loc, setLoc] = useState("");
  const [activeIndex, setActiveIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);

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
        .then((response) => {
          const hits = Array.isArray(response.data)
            ? (response.data as SearchHit[])
            : [];

          setResults(
            hits
              .map(normalizeHit)
              .filter((item): item is PickerProduct => item !== null),
          );
        })
        .catch(() => setResults([]));
    }, 250);

    return () => clearTimeout(timer);
  }, [q, product]);

  useEffect(() => {
    setActiveIndex(-1);
  }, [results]);

  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setResults([]);
        setActiveIndex(-1);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);

  const suggestions = results.slice(0, 6);
  const showSuggestions = suggestions.length > 0 && !product;

  const chooseProduct = (item: PickerProduct) => {
    setProduct(item);
    setQ(item.name);
    setVariant(item.variants[0]?._id ?? "");
    setResults([]);
    setActiveIndex(-1);
  };

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

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (!showSuggestions) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((current) =>
        Math.min(current + 1, suggestions.length - 1),
      );
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((current) => Math.max(current - 1, 0));
    } else if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();

      const item = suggestions[activeIndex];

      if (item) {
        chooseProduct(item);
      }
    } else if (event.key === "Escape") {
      setResults([]);
      setActiveIndex(-1);
    }
  }

  return (
    <div ref={containerRef} className="border border-border bg-card p-5 md:p-7">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between sm:gap-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
            Start here
          </p>

          <h2 className="mt-2 font-display text-2xl font-bold leading-tight tracking-[-0.02em] md:text-3xl">
            What are you buying?
          </h2>
        </div>

        <p className="text-sm leading-6 text-muted-foreground">
          Check a product price near you.
        </p>
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          go();
        }}
        className="mt-6"
      >
        <div className="grid gap-4 md:grid-cols-[1.4fr_1fr_auto] md:items-end">
          <div>
            <label
              htmlFor="home-product-search"
              className="mb-1.5 block text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground"
            >
              Product
            </label>

            <div className="relative">
              <Search
                aria-hidden="true"
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
              />

              <input
                id="home-product-search"
                value={q}
                onChange={(event) => {
                  setQ(event.target.value);
                  setProduct(null);
                  setVariant("");
                }}
                onKeyDown={handleKeyDown}
                placeholder="e.g. Dangote Sugar"
                className={cn(fieldCls, "pl-9")}
                role="combobox"
                aria-label="Search for a product"
                aria-autocomplete="list"
                aria-haspopup="listbox"
                aria-expanded={showSuggestions}
                aria-controls={
                  showSuggestions ? "home-product-suggestions" : undefined
                }
                aria-activedescendant={
                  activeIndex >= 0
                    ? `home-product-option-${activeIndex}`
                    : undefined
                }
                autoComplete="off"
              />

              {showSuggestions && (
                <ul
                  id="home-product-suggestions"
                  role="listbox"
                  aria-label="Product suggestions"
                  className="absolute z-30 mt-1 max-h-72 w-full overflow-y-auto border border-border bg-popover py-1"
                >
                  {suggestions.map((item, index) => (
                    <li key={item._id}>
                      <button
                        id={`home-product-option-${index}`}
                        type="button"
                        role="option"
                        aria-selected={activeIndex === index}
                        onMouseEnter={() => setActiveIndex(index)}
                        onMouseDown={(event) => event.preventDefault()}
                        onClick={() => chooseProduct(item)}
                        className={cn(
                          "flex min-h-11 w-full items-center justify-between gap-4 px-3 py-2.5 text-left text-sm transition-colors duration-150 ease-out",
                          activeIndex === index
                            ? "bg-accent text-accent-foreground"
                            : "hover:bg-muted",
                        )}
                      >
                        <span className="min-w-0 truncate">
                          {item.name}
                          {item.brand && (
                            <span className="text-muted-foreground">
                              {" "}
                              · {item.brand}
                            </span>
                          )}
                        </span>

                        <span className="shrink-0 text-xs text-muted-foreground">
                          {item.observationCount} obs.
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <LocationSelect
            value={loc}
            onChange={setLoc}
            label="Location"
            inputId="home-location"
            inputClassName="min-h-11 rounded-[3px] py-2.5 text-base focus:border-primary"
          />

          <button
            type="submit"
            disabled={!q.trim()}
            className="inline-flex min-h-11 items-center justify-center gap-2 border border-primary bg-primary px-5 text-sm font-semibold text-primary-foreground transition-colors duration-150 ease-out hover:border-primary-glow hover:bg-primary-glow hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:cursor-not-allowed disabled:opacity-50"
          >
            {product ? "See prices" : "Search"}
            <ArrowRight aria-hidden="true" className="h-4 w-4" />
          </button>
        </div>

        {product && product.variants.length > 1 && (
          <fieldset className="mt-4">
            <legend className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
              Size / variant
            </legend>

            <div className="mt-2 flex flex-wrap gap-2">
              {product.variants.map((item) => (
                <button
                  key={item._id}
                  type="button"
                  aria-pressed={variant === item._id}
                  onClick={() => setVariant(item._id)}
                  className={cn(
                    "min-h-9 rounded-[3px] border px-3 text-sm transition-colors duration-150 ease-out focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
                    variant === item._id
                      ? "border-primary bg-accent text-accent-foreground"
                      : "border-border bg-background hover:border-primary",
                  )}
                >
                  {item.name || "Default"}
                </button>
              ))}
            </div>
          </fieldset>
        )}

        <p className="mt-4 text-sm leading-6 text-muted-foreground">
          Prices come from community observations and may vary by seller and
          location.
        </p>
      </form>
    </div>
  );
}
