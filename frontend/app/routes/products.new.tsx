import { useState } from "react";
import { useNavigate } from "react-router";

import { Page, btnCls, inputCls } from "../components/layout";
import { ErrorState } from "../components/states";
import { usePageMeta } from "../lib/meta";
import { productsApi } from "../lib/api/services";
import type { ApiError } from "../lib/api/client";

export default function NewProduct() {
  const navigate = useNavigate();

  usePageMeta({
    title: "Add a product — PriceBiz",
    description:
      "Add a new product to PriceBiz so the community can track its price.",
    ogTitle: "Add a product — PriceBiz",
    ogType: "website",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    ogDescription:
      "Add a new product to PriceBiz so the community can track its price.",
    twitterCard: "summary",
    twitterTitle: "Add a product — PriceBiz",
    twitterDescription:
      "Add a new product to PriceBiz so the community can track its price.",
    twitterImage: "/hero-trader.jpg",
  });

  const [f, setF] = useState({
    name: "",
    brand: "",
    category: "",
    variant_name: "",
    unit: "",
  });

  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<ApiError | null>(null);

  const field = (
    key: keyof typeof f,
    label: string,
    required = false,
    placeholder = "",
  ) => (
    <label className="text-sm font-medium">
      {label}

      {!required && (
        <span className="text-muted-foreground"> (optional)</span>
      )}

      <input
        required={required}
        placeholder={placeholder}
        value={f[key]}
        onChange={(event) =>
          setF({
            ...f,
            [key]: event.target.value,
          })
        }
        className={`${inputCls} mt-1`}
      />
    </label>
  );

  return (
    <Page title="Add a product" kicker="Products">
      <form
        className="grid max-w-2xl gap-4 rounded-[2rem] border bg-card p-6 md:grid-cols-2 md:p-8"
        onSubmit={async (event) => {
          event.preventDefault();

          setBusy(true);
          setErr(null);

          try {
            const p = await productsApi.create({
              ...f,
              brand: f.brand || undefined,
              category: f.category || undefined,
              unit: f.unit || undefined,
            });

            const params = new URLSearchParams();
            params.set("product", p._id);

            const firstVariantId = p.variants?.[0]?._id;

            if (firstVariantId) {
              params.set("variant", firstVariantId);
            }

            navigate(`/contribute?${params.toString()}`);
          } catch (error) {
            setErr(error as ApiError);
          } finally {
            setBusy(false);
          }
        }}
      >
        <div className="md:col-span-2">
          {field("name", "Product name", true, "e.g. Dangote Sugar")}
        </div>

        {field("brand", "Brand")}

        {field("category", "Category", false, "e.g. Groceries")}

        {field("variant_name", "Size / variant", true, "e.g. 1kg")}

        {field("unit", "Unit", false, "e.g. pack")}

        {err && (
          <div className="md:col-span-2">
            <ErrorState error={err} />
          </div>
        )}

        <div className="md:col-span-2">
          <button
            type="submit"
            disabled={busy}
            className={btnCls}
          >
            {busy ? "Saving…" : "Add product"}
          </button>
        </div>
      </form>
    </Page>
  );
}