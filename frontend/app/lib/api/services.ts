
import { api, withFallback, toApiError } from "./client";

import {
  SAMPLE_COMMENTS,
  SAMPLE_LOCATIONS,
  SAMPLE_POSTS,
  SAMPLE_PRODUCTS,
  sampleAnalysis,
} from "./sample";

import type {
  AuthTokens,
  Comment,
  LocationNode,
  Post,
  PriceAnalysis,
  Product,
  ProductDetail,
  ProductSearchResult,
  SellerType,
  User,
  Variant,
} from "../types";

const unwrap = <T,>(data: unknown, key = "results"): T => {
  if (Array.isArray(data)) {
    return data as T;
  }

  if (data && typeof data === "object") {
    const record = data as Record<string, unknown>;

    if (key in record) {
      return record[key] as T;
    }

    if ("items" in record) {
      return record.items as T;
    }
  }

  return data as T;
};

type ApiLocationRecord = {
  _id: string;
  country: string;
  state?: string | null;
  lga?: string | null;
  area?: string | null;
  market?: string | null;
};

const mapLocation = (location: ApiLocationRecord): LocationNode => {
  const level: LocationNode["level"] = location.market
    ? "MARKET"
    : location.area
      ? "AREA"
      : location.lga
        ? "LGA"
        : location.state
          ? "STATE"
          : "COUNTRY";

  const name =
    location.market ??
    location.area ??
    location.lga ??
    location.state ??
    location.country;

  return {
    _id: location._id,
    country: location.country,
    state: location.state ?? null,
    lga: location.lga ?? null,
    area: location.area ?? null,
    market: location.market ?? null,
    name,
    level,
  };
};

export const productsApi = {
  search: (q: string) =>
    withFallback(
      async () =>
        unwrap<ProductSearchResult[]>(
          (
            await api.get("/search/products", {
              params: { q },
            })
          ).data,
        ),
      () =>
        SAMPLE_PRODUCTS.filter((product) =>
          `${product.name} ${product.brand ?? ""} ${
            product.category ?? ""
          }`
            .toLowerCase()
            .includes(q.trim().toLowerCase()),
        ).map((product) => ({
          product,
          variant: {
            _id: "",
            name: "",
          },
          observation_count: 0,
        })),
    ),

  get: (id: string) =>
    withFallback(
      async () =>
        (await api.get<ProductDetail>(`/products/${id}`)).data,
      () => {
        const product = SAMPLE_PRODUCTS.find(
          (item) => item._id === id,
        );

        if (!product) {
          throw new Error(`Sample product not found: ${id}`);
        }

        return {
          product,
          variants: [],
        };
      },
    ),

  create: async (body: {
    name: string;
    brand?: string | null;
    category?: string | null;
    description?: string | null;
    details?: Record<string, unknown>;
    packaging?: Record<string, unknown>;
    variant_name?: string | null;
    variant_attributes?: Record<string, unknown>;
  }): Promise<Product> => {
    try {
      const response = await api.post<Product>("/products/", body);
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  createVariant: async (body: {
    product_id: string;
    name: string;
    attributes?: Record<string, unknown>;
  }): Promise<Variant> => {
    try {
      const response = await api.post<Variant>(
        "/product-variants/",
        body,
      );
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },
};

export const locationsApi = {
  list: () =>
    withFallback(
      async (): Promise<LocationNode[]> => {
        const response = await api.get("/locations/");
        const records = unwrap<ApiLocationRecord[]>(response.data);

        return records.map(mapLocation);
      },
      () => SAMPLE_LOCATIONS,
    ),

  create: async (body: {
    country: string;
    state?: string | null;
    lga?: string | null;
    area?: string | null;
    market?: string | null;
  }): Promise<LocationNode> => {
    try {
      const response = await api.post<ApiLocationRecord>(
        "/locations/",
        body,
      );

      return mapLocation(response.data);
    } catch (error) {
      throw toApiError(error);
    }
  },
};

export const pricesApi = {
  analysis: (
    productId: string,
    variantId?: string | null,
    locationId?: string | null,
  ) =>
    withFallback(
      async (): Promise<PriceAnalysis> => {
        if (!variantId) {
          throw new Error(
            "A variant must be selected before requesting price analysis.",
          );
        }

        const response = await api.get<PriceAnalysis>(
          `/price-analysis/variant/${variantId}`,
          {
            params: {
              location_id: locationId || undefined,
            },
          },
        );

        return response.data;
      },
      () => sampleAnalysis(productId, variantId, locationId),
    ),

  contribute: async (body: {
    product_id: string;
    variant_id: string;
    price: number;
    location_id: string;
    observed_at: string;
    source_id?: string | null;
    seller_type?: SellerType | null;
    evidence?: Record<string, unknown>;
  }) => {
    try {
      const response = await api.post(
        "/price-observations",
        body,
      );
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },
};

export const communityApi = {
  list: () =>
    withFallback(
      async () =>
        unwrap<Post[]>((await api.get("/posts/feed")).data),
      () => SAMPLE_POSTS,
    ),

  get: (id: string) =>
    withFallback(
      async () => (await api.get<Post>(`/posts/${id}`)).data,
      () => {
        const post = SAMPLE_POSTS.find(
          (item) => item._id === id,
        );

        if (!post) {
          throw new Error(`Sample post not found: ${id}`);
        }

        return {
          ...post,
          comments: SAMPLE_COMMENTS,
        } as Post & { comments: Comment[] };
      },
    ),

  create: async (body: {
    author_id: string;
    content: string;
    post_type?: string;
    product_id?: string | null;
    variant_id?: string | null;
    location_id?: string | null;
  }) => {
    try {
      const response = await api.post<Post>("/posts", body);
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  comments: (postId: string) =>
    withFallback(
      async () =>
        unwrap<Comment[]>(
          (await api.get(`/comments/post/${postId}`)).data,
        ),
      () => SAMPLE_COMMENTS,
    ),

  comment: async (body: {
    post_id: string;
    author_id: string;
    content: string;
    parent_comment_id?: string | null;
  }) => {
    try {
      const response = await api.post<Comment>("/comments", body);
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  react: async (body: {
    user_id: string;
    target_type: string;
    target_id: string;
    reaction: string;
  }) => {
    try {
      const response = await api.put("/reactions", body);
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  reactionCounts: (targetType: string, targetId: string) =>
    api
      .get("/reactions/counts", {
        params: {
          target_type: targetType,
          target_id: targetId,
        },
      })
      .then((response) => response.data),
};

export const authApi = {
  login: async (
    email: string,
    password: string,
  ): Promise<AuthTokens> => {
    try {
      const response = await api.post<AuthTokens>("/auth/login", {
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  register: async (body: {
    name: string;
    email: string;
    password: string;
  }): Promise<AuthTokens> => {
    try {
      const response = await api.post<AuthTokens>(
        "/auth/register",
        body,
      );
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  me: async (): Promise<User> => {
    try {
      const response = await api.get<{ user: User }>("/auth/me");
      return response.data.user;
    } catch (error) {
      throw toApiError(error);
    }
  },

  refresh: async (
    refreshToken: string,
  ): Promise<AuthTokens> => {
    try {
      const response = await api.post<AuthTokens>(
        "/auth/refresh",
        {
          refresh_token: refreshToken,
        },
      );
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  logout: async () => {
    try {
      const response = await api.post("/auth/logout");
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },
};
