
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { authApi } from "./api/services";
import { setAuthLostHandler, tokenStore } from "./api/client";
import type { AuthTokens, User } from "./types";
import { isPasswordValid } from "./password";

type Ctx = {
  user: User | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (b: {
    name: string;
    email: string;
    phone?: string;
    password: string;
  }) => Promise<void>;
  googleLogin: (credential: string) => Promise<void>;
  logout: () => void;
};

const AuthCtx = createContext<Ctx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setAuthLostHandler(() => setUser(null));

    if (!tokenStore.access) {
      setReady(true);
      return;
    }

    authApi
      .me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setReady(true));
  }, []);

  const accept = async (tokens: AuthTokens) => {
    tokenStore.set(tokens.access_token, tokens.refresh_token);

    try {
      const authenticatedUser = await authApi.me();
      setUser(authenticatedUser);
    } catch (error) {
      tokenStore.clear();
      setUser(null);
      throw error;
    }
  };

  const login = async (email: string, password: string) => {
    await accept(await authApi.login(email, password));
  };

  const register = async (b: {
    name: string;
    email: string;
    phone?: string;
    password: string;
  }) => {
    if (!isPasswordValid(b.password)) {
      throw new Error("Password does not meet the required criteria.");
    }

    await accept(await authApi.register(b));
  };

  const googleLogin = async (credential: string) => {
    await accept(await authApi.google(credential));
  };

  const logout = () => {
    tokenStore.clear();
    setUser(null);
  };

  return (
    <AuthCtx.Provider
      value={{
        user,
        ready,
        login,
        register,
        googleLogin,
        logout,
      }}
    >
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthCtx);

  if (!context) {
    throw new Error("useAuth outside AuthProvider");
  }

  return context;
}
