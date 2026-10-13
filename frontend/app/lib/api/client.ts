
import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios";

import type { ApiErrorShape } from "../types";

const configuredApiBaseUrl = (
  import.meta as ImportMeta & {
    env: { VITE_API_BASE_URL?: string };
  }
).env.VITE_API_BASE_URL;

export const API_BASE_URL = (
  configuredApiBaseUrl?.trim() || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const ACCESS = "pricebiz.access";
const REFRESH = "pricebiz.refresh";

export const tokenStore = {
  get access(): string | null {
    if (typeof window === "undefined") return null;

    try {
      return localStorage.getItem(ACCESS);
    } catch {
      return null;
    }
  },

  get refresh(): string | null {
    if (typeof window === "undefined") return null;

    try {
      return localStorage.getItem(REFRESH);
    } catch {
      return null;
    }
  },

  set(access: string, refresh?: string): void {
    if (typeof window === "undefined") return;

    try {
      localStorage.setItem(ACCESS, access);

      if (refresh) {
        localStorage.setItem(REFRESH, refresh);
      }
    } catch {
      this.clear();
    }
  },

  clear(): void {
    if (typeof window === "undefined") return;

    try {
      localStorage.removeItem(ACCESS);
      localStorage.removeItem(REFRESH);
    } catch {
      return;
    }
  },
};

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = tokenStore.access;

  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  } else {
    config.headers.delete("Authorization");
  }

  return config;
});

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

type RefreshResponse = {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
};

let refreshing: Promise<string | null> | null = null;

let onAuthLost: () => void = () => {};

export const setAuthLostHandler = (fn: () => void): void => {
  onAuthLost = fn;
};

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = tokenStore.refresh;

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await axios.post<RefreshResponse>(
      `${API_BASE_URL}/auth/refresh`,
      { refresh_token: refreshToken },
      { timeout: 10000 },
    );

    const { access_token, refresh_token } = response.data;

    if (!access_token) {
      return null;
    }

    tokenStore.set(access_token, refresh_token);

    return access_token;
  } catch {
    return null;
  }
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | RetryableRequestConfig
      | undefined;

    const status = error.response?.status;
    const url = original?.url ?? "";
    const isAuthCall = /\/auth\/(login|register|refresh|logout|google)/.test(
      url,
    );

    if (
      status !== 401 ||
      !original ||
      original._retry ||
      isAuthCall
    ) {
      return Promise.reject(error);
    }

    original._retry = true;

    if (!tokenStore.refresh) {
      tokenStore.clear();
      onAuthLost();
      return Promise.reject(error);
    }

    refreshing ??= refreshAccessToken().finally(() => {
      refreshing = null;
    });

    const token = await refreshing;

    if (!token) {
      tokenStore.clear();
      onAuthLost();
      return Promise.reject(error);
    }

    original.headers.set("Authorization", `Bearer ${token}`);

    return api(original);
  },
);

export class ApiError extends Error {
  code: string;
  requestId?: string;
  status?: number;

  constructor(e: ApiErrorShape, status?: number) {
    super(e.message);

    this.name = "ApiError";
    this.code = e.code;
    this.requestId = e.request_id;
    this.status = status;
  }
}

export function toApiError(err: unknown): ApiError {
  if (err instanceof ApiError) {
    return err;
  }

  if (axios.isAxiosError(err)) {
    const responseData = err.response?.data as
      | {
          error?: ApiErrorShape;
          detail?: unknown;
        }
      | undefined;

    if (responseData?.error) {
      return new ApiError(
        responseData.error,
        err.response?.status,
      );
    }

    if (typeof responseData?.detail === "string") {
      return new ApiError(
        {
          code: "HTTP_ERROR",
          message: responseData.detail,
        },
        err.response?.status,
      );
    }

    if (!err.response) {
      return new ApiError({
        code: "NETWORK",
        message:
          "Can't reach PriceBiz right now. Check your connection.",
      });
    }

    return new ApiError(
      {
        code: "HTTP_ERROR",
        message: "Something went wrong. Please try again.",
      },
      err.response.status,
    );
  }

  return new ApiError({
    code: "UNKNOWN",
    message: "Something went wrong. Please try again.",
  });
}

export const isNetworkError = (err: unknown): boolean =>
  axios.isAxiosError(err) && !err.response;

export type Sourced<T> = {
  data: T;
  sample: boolean;
};

export async function withFallback<T>(
  call: () => Promise<T>,
  sample: () => T,
): Promise<Sourced<T>> {
  try {
    return {
      data: await call(),
      sample: false,
    };
  } catch (error) {
    if (isNetworkError(error)) {
      return {
        data: sample(),
        sample: true,
      };
    }

    throw toApiError(error);
  }
}
