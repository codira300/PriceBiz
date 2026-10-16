
import { Link, useSearchParams } from "react-router";
import { useState } from "react";
import { CheckCircle2 } from "lucide-react";

import { LocationSelect } from "../components/location-select";
import { Page, btnCls, inputCls } from "../components/layout";
import { ErrorState } from "../components/states";
import { useCachedAsync, asyncCache } from "../hooks/use-async";
import { pricesApi, productsApi } from "../lib/api/services";
import type { ApiError } from "../lib/api/client";
import { useAuth } from "../lib/auth";
import { usePageMeta } from "../lib/meta";
import { SELLER_TYPES, sellerLabel } from "../lib/format";
import type { SellerType } from "../lib/types";

export default function Contribute() {
  const [searchParams] = useSearchParams();

  const searchProduct = searchParams.get("product") ?? "";
  const searchVariant = searchParams.get("variant") ?? "";

  const { user } = useAuth();
  const all = useCachedAsync(
    "products:all",
    () => productsApi.search(""),
  );

  const [productId, setProductId] = useState(searchProduct);
  const [variantId, setVariantId] = useState(searchVariant);
  const [price, setPrice] = useState("");
  const [seller, setSeller] = useState<SellerType>("MARKET");
  const [sellerName, setSellerName] = useState("");
  const [loc, setLoc] = useState("");
  const [date, setDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<ApiError | null>(null);
  const [done, setDone] = useState(false);

  const product = all.data?.find((p) => p._id === productId);

  usePageMeta({
    title: "Add a price — PriceBiz",
    description:
      "Share what you paid for a product so your neighbours can negotiate fairly.",
  });

  if (done) {
    return (
      <Page title="Price observation submitted." kicker="Thank you">
        <CheckCircle2 className="h-10 w-10 text-success" />

        <p className="mt-3 text-muted-foreground">
          Your observation helps others understand typical prices.
        </p>

        <div className="mt-6 flex gap-3">
          <Link
            to={`/product/${encodeURIComponent(productId)}?variant=${encodeURIComponent(variantId)}`}
            className={btnCls}
          >
            View price range
          </Link>

          <button
            onClick={() => {
              setDone(false);
              setPrice("");
            }}
            className="rounded-full border px-6 py-3 text-sm"
          >
            Add another
          </button>
        </div>
      </Page>
    );
  }

  return (
    <Page title="Add a price you saw or paid" kicker="Contribute">
      {!user && (
        <p className="mb-6 rounded-xl bg-accent px-4 py-3 text-sm text-accent-foreground">
          You'll need to{" "}
          <Link to="/auth/login" className="underline">
            log in
          </Link>{" "}
          to submit an observation.
        </p>
      )}

      <form
        className="grid max-w-2xl gap-4 rounded-[2rem] border bg-card p-6 md:grid-cols-2 md:p-8"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          setErr(null);

          try {
            await pricesApi.contribute({
              product_id: productId,
              variant_id: variantId,
              price: Number(price),
              seller_type: seller,
              seller_name: sellerName || undefined,
              location_id: loc,
              observed_at: new Date(date).toISOString(),
            });

            // Invalidate caches so the new observation shows up immediately
            asyncCache.invalidate(`product:${productId}`);
            asyncCache.invalidate(
              `price-analysis:${productId}:${variantId ?? "any"}:${loc ?? "any"}`,
            );
            asyncCache.invalidate("products:all");

            setDone(true);
          } catch (e2) {
            setErr(e2 as ApiError);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label className="text-sm font-medium md:col-span-2">
          Product

          <select
            required
            value={productId}
            onChange={(e) => {
              const selectedId = e.target.value;
              setProductId(selectedId);
              setVariantId(
                all.data?.find((p) => p._id === selectedId)
                  ?.variants[0]?._id ?? "",
              );
            }}
            className={`${inputCls} mt-1`}
          >
            <option value="">Select product</option>

            {all.data?.map((p) => (
              <option key={p._id} value={p._id}>
                {p.name}
              </option>
            ))}
          </select>

          <span className="mt-1 block text-xs text-muted-foreground">
            Not listed?{" "}
            <Link
              to="/products/new"
              className="text-primary underline"
            >
              Add a product
            </Link>
          </span>
        </label>

        <label className="text-sm font-medium">
          Size / variant

          <select
            required
            value={variantId}
            onChange={(e) => setVariantId(e.target.value)}
            className={`${inputCls} mt-1`}
          >
            <option value="">Select</option>

            {product?.variants.map((v) => (
              <option key={v._id} value={v._id}>
                {v.name}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm font-medium">
          Price paid (₦)

          <input
            required
            type="number"
            min={1}
            inputMode="numeric"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            placeholder="e.g. 6000"
            className={`${inputCls} mt-1`}
          />
        </label>

        <label className="text-sm font-medium">
          Seller type

          <select
            value={seller}
            onChange={(e) =>
              setSeller(e.target.value as SellerType)
            }
            className={`${inputCls} mt-1`}
          >
            {SELLER_TYPES.map((t) => (
              <option key={t} value={t}>
                {sellerLabel(t)}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm font-medium">
          Seller name{" "}
          <span className="text-muted-foreground">(optional)</span>

          <input
            value={sellerName}
            onChange={(e) => setSellerName(e.target.value)}
            className={`${inputCls} mt-1`}
          />
        </label>

        <div className="text-sm font-medium">
          Location

          <div className="mt-1">
            <LocationSelect
              required
              value={loc}
              onChange={setLoc}
            />
          </div>
        </div>

        <label className="text-sm font-medium">
          Date observed

          <input
            type="date"
            required
            max={new Date().toISOString().slice(0, 10)}
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className={`${inputCls} mt-1`}
          />
        </label>

        {err && (
          <div className="md:col-span-2">
            <ErrorState error={err} />
          </div>
        )}

        <div className="md:col-span-2">
          <button disabled={busy} className={btnCls}>
            {busy ? "Submitting…" : "Submit observation"}
          </button>
        </div>
      </form>
    </Page>
  );
}