import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authApi } from "./api/services";
import { setAuthLostHandler, tokenStore } from "./api/client";
import type { AuthTokens, User } from "./types";

type Ctx = {
  user: User | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (b: { name: string; email: string; phone?: string | undefined; password: string }) => Promise<void>;
  logout: () => void;
};
const AuthCtx = createContext<Ctx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setAuthLostHandler(() => setUser(null));
    if (!tokenStore.access) return setReady(true);
    authApi.me().then(setUser).catch(() => setUser(null)).finally(() => setReady(true));
  }, []);

  
const accept = async (t: AuthTokens) => {
  tokenStore.set(t.access_token, t.refresh_token);

  const authenticatedUser = await authApi.me();
  setUser(authenticatedUser);
};


  return (
    <AuthCtx.Provider
      value={{
        user, ready,
        login: async (e, p) => accept(await authApi.login(e, p)),
        register: async (b) => accept(await authApi.register(b)),
        logout: () => { tokenStore.clear(); setUser(null); },
      }}
    >
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth() {
  const c = useContext(AuthCtx);
  if (!c) throw new Error("useAuth outside AuthProvider");
  return c;
}
