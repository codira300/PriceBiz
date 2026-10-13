// Sample data used ONLY when the FastAPI backend is unreachable (preview).
import type { LocationNode, Post, PriceAnalysis, Product, Comment, Observation, SellerType } from "../types";

export const SAMPLE_LOCATIONS: LocationNode[] = [
  { _id: "ng", name: "Nigeria", level: "COUNTRY" },
  { _id: "lagos", name: "Lagos", level: "STATE", parent_id: "ng" },
  { _id: "ikorodu", name: "Ikorodu", level: "LGA", parent_id: "lagos" },
  { _id: "ijede", name: "Ijede", level: "AREA", parent_id: "ikorodu" },
  { _id: "ikorodu-garage", name: "Ikorodu Garage Market", level: "MARKET", parent_id: "ikorodu" },
  { _id: "ikeja", name: "Ikeja", level: "LGA", parent_id: "lagos" },
  { _id: "computer-village", name: "Computer Village", level: "MARKET", parent_id: "ikeja" },
  { _id: "abuja", name: "FCT Abuja", level: "STATE", parent_id: "ng" },
  { _id: "wuse", name: "Wuse Market", level: "MARKET", parent_id: "abuja" },
];

export const SAMPLE_PRODUCTS: Product[] = [
  { _id: "p1", name: "Nivea Body Lotion", brand: "Nivea", category: "Personal care", observation_count: 24,
    variants: [{ _id: "v1", name: "400ml", unit: "bottle" }, { _id: "v2", name: "250ml", unit: "bottle" }] },
  { _id: "p2", name: "Dangote Sugar", brand: "Dangote", category: "Groceries", observation_count: 41,
    variants: [{ _id: "v3", name: "1kg", unit: "pack" }] },
  { _id: "p3", name: "Golden Penny Semovita", brand: "Golden Penny", category: "Groceries", observation_count: 18,
    variants: [{ _id: "v4", name: "2kg", unit: "bag" }, { _id: "v5", name: "5kg", unit: "bag" }] },
  { _id: "p4", name: "Local Rice (Ofada)", brand: null, category: "Groceries", observation_count: 33,
    variants: [{ _id: "v6", name: "1 paint bucket", unit: "bucket" }] },
  { _id: "p5", name: "Peak Milk Powder", brand: "Peak", category: "Groceries", observation_count: 0,
    variants: [{ _id: "v7", name: "400g refill", unit: "pack" }] },
];

const base: Record<string, number> = { p1: 6000, p2: 1650, p3: 3900, p4: 5200, p5: 4200 };

export function sampleAnalysis(productId: string, variantId?: string | null, locationId?: string | null): PriceAnalysis {
  const p = SAMPLE_PRODUCTS.find((x) => x._id === productId);
  const loc = SAMPLE_LOCATIONS.find((l) => l._id === (locationId || "ikorodu")) ?? SAMPLE_LOCATIONS[2]!;
  if (!p || !p.observation_count) {
    return { type: "NO_DATA", product_id: productId, variant_id: variantId ?? null,
      location: { requested: loc, used: loc, path: ["Nigeria", "Lagos", loc.name], broadened: false },
      price_summary: null, seller_types: [], trend: [], observations: [] };
  }
  const b = base[productId] ?? 5000;
  const broadened = loc.level === "MARKET" || loc.level === "AREA";
  const used = broadened ? SAMPLE_LOCATIONS.find((l) => l._id === loc.parent_id) ?? loc : loc;
  const T = <X,>(a: X[], i: number) => a[i % a.length]!;
  const types: SellerType[] = ["MARKET", "SUPERMARKET", "SHOP", "WHOLESALER", "MINI_FARM"];
  const mult = [0.95, 1.12, 1.03, 0.88, 0.97];
  const now = Date.now();
  const observations: Observation[] = Array.from({ length: 10 }, (_, i) => ({
    _id: `o${i}`,
    price: Math.round((b * T(mult, i) * (0.96 + ((i * 7) % 9) / 100)) / 50) * 50,
    seller_type: T(types, i),
    seller_name: T(["Mama Bisi Stores", "Justrite", "Corner Shop", "Alaba Bulk Ltd", "Ijede Farm"], i),
    location_name: used.name,
    observed_at: new Date(now - i * 2.3 * 86400000).toISOString(),
    is_outlier: i === 7,
  }));
  observations[7]!.price = Math.round(b * 1.6);
  return {
    type: "PRICE_ANALYSIS", product_id: productId, variant_id: variantId ?? p.variants[0]!._id,
    location: { requested: loc, used, path: ["Nigeria", "Lagos", used.name], broadened },
    price_summary: { min_price: Math.round(b * 0.9 / 50) * 50, max_price: Math.round(b * 1.08 / 50) * 50,
      median_price: b, total_observations: p.observation_count, normal_observations: p.observation_count - 2,
      outliers: 2, last_observed_at: observations[0]!.observed_at },
    seller_types: types.map((t, i) => ({ seller_type: t, count: 8 - i, median_price: Math.round(b * T(mult, i) / 50) * 50,
      min_price: Math.round(b * T(mult, i) * 0.94 / 50) * 50, max_price: Math.round(b * T(mult, i) * 1.06 / 50) * 50 })),
    trend: Array.from({ length: 8 }, (_, i) => ({
      date: new Date(now - (7 - i) * 7 * 86400000).toISOString().slice(0, 10),
      median_price: Math.round((b * (0.9 + i * 0.015 + (i % 3) * 0.01)) / 50) * 50,
      count: 2 + (i % 4),
    })),
    observations,
  };
}

const ago = (d: number) => new Date(Date.now() - d * 3600000).toISOString();
export const SAMPLE_POSTS: Post[] = [
  { _id: "c1", title: "Sugar price jumped at Ikorodu Garage this week", body: "Saw Dangote 1kg at ₦1,900 in two shops near the garage. Anyone else noticing this? Supermarkets still around ₦1,700.", author_name: "Tunde A.", product_name: "Dangote Sugar", location_name: "Ikorodu", created_at: ago(5), comment_count: 3 },
  { _id: "c2", title: "Where to buy Semovita in bulk in Abuja?", body: "Looking for wholesalers around Wuse that sell 5kg bags at a fair price.", author_name: "Ngozi E.", product_name: "Golden Penny Semovita", location_name: "FCT Abuja", created_at: ago(28), comment_count: 1 },
  { _id: "c3", title: "Tip: ask for the market price before saying your budget", body: "Sellers at Ijede open lower when you mention you've checked prices elsewhere.", author_name: "Kemi O.", location_name: "Ijede", created_at: ago(70), comment_count: 0 },
];
export const SAMPLE_COMMENTS: Comment[] = [
  { _id: "m1", body: "Same here, ₦1,850 at the junction shop.", author_name: "Ifeanyi", created_at: ago(3) },
  { _id: "m2", body: "Justrite still had it at ₦1,700 yesterday.", author_name: "Bola", created_at: ago(2) },
];
