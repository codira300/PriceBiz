
export type SellerType =
  | "STORE"
  | "SHOP"
  | "MINI_FARM"
  | "MARKET"
  | "SUPERMARKET"
  | "WHOLESALER"
  | "ONLINE"
  | "OTHER";

// Product variants
export interface Variant {
  _id: string;
  product_id?: string;
  name: string;
  attributes?: Record<string, unknown>;
}

// Product returned by the backend
export interface Product {
  _id: string;
  name: string;
  brand?: string | null;
  category?: string | null;
  description?: string | null;
  details?: Record<string, unknown>;
  packaging?: Record<string, unknown>;
  creator_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

// GET /search/products returns an array of these objects
export interface ProductSearchResult {
  product: Product;
  variant: Variant;
  observation_count: number;
}

// GET /products/{product_id}
export interface ProductDetail {
  product: Product;
  variants: Variant[];
}

// Locations returned by GET /locations/
export interface LocationNode {
  _id: string;
  country: string;
  state?: string | null;
  lga?: string | null;
  area?: string | null;
  market?: string | null;
}

export interface AnalysisLocation {
  requested?: unknown;
  used?: unknown;
  path?: string[];
  broadened?: boolean;
}

export interface PriceSummary {
  type: string;
  minimum: number | null;
  maximum: number | null;
  currency: string;
  observation_count: number;
  normal_observation_count: number;
  outlier_count: number;
  other_observations: unknown[];
}

export interface SellerTypeStat {
  seller_type: SellerType;
  count: number;
  median_price: number;
  min_price: number;
  max_price: number;
}

export interface TrendPoint {
  date: string;
  median_price: number;
  count: number;
}

export interface Observation {
  _id: string;
  price: number;
  seller_type: SellerType;
  seller_name?: string | null;
  location_name?: string | null;
  observed_at: string;
  is_outlier?: boolean;
}

export interface PriceAnalysis {
  type: "PRICE_ANALYSIS" | "NO_DATA";
  product_id: string;
  variant_id?: string | null;
  location: AnalysisLocation | null;
  price_summary: PriceSummary | null;
  seller_types: Record<string, unknown> | SellerTypeStat[];
  trend: TrendPoint[];
  observations: Observation[];
}

export interface User {
  _id: string;
  name: string;
  email: string;
  phone?: string | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  user?: User;
}

export interface Post {
  _id: string;
  title?: string;
  body?: string;
  content?: string;
  author_id?: string;
  author_name?: string;
  product_id?: string | null;
  product_name?: string | null;
  location_id?: string | null;
  location_name?: string | null;
  created_at: string;
  comment_count?: number;
}

export interface Comment {
  _id: string;
  post_id?: string;
  author_id?: string;
  body?: string;
  content?: string;
  author_name?: string;
  created_at: string;
  parent_comment_id?: string | null;
}

export interface ApiErrorShape {
  code: string;
  message: string;
  request_id?: string;
  details?: unknown[];
}
