import type { SellerType } from "./types";

const naira = new Intl.NumberFormat("en-NG", {
  style: "currency",
  currency: "NGN",
  maximumFractionDigits: 0,
});

export const formatNaira = (n: number | null | undefined) =>
  n == null || Number.isNaN(n) ? "—" : naira.format(n).replace("NGN", "₦").replace(/\s/g, "");

export const formatRange = (min: number, max: number) =>
  min === max ? formatNaira(min) : `${formatNaira(min)} – ${formatNaira(max)}`;

const SELLER_LABELS: Record<SellerType, string> = {
  STORE: "Store",
  SHOP: "Shop",
  MINI_FARM: "Mini Farm",
  MARKET: "Market",
  SUPERMARKET: "Supermarket",
  WHOLESALER: "Wholesaler",
  ONLINE: "Online",
  OTHER: "Other",
};
export const SELLER_TYPES = Object.keys(SELLER_LABELS) as SellerType[];
export const sellerLabel = (t: string) =>
  SELLER_LABELS[t as SellerType] ??
  t.toLowerCase().replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

export const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString("en-NG", { day: "numeric", month: "short", year: "numeric" });

export const timeAgo = (iso: string) => {
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 3600) return `${Math.max(1, Math.round(s / 60))}m ago`;
  if (s < 86400) return `${Math.round(s / 3600)}h ago`;
  return `${Math.round(s / 86400)}d ago`;
};
