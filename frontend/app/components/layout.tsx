import { Link, NavLink, useNavigate } from "react-router";
import type { ReactNode } from "react";

import { useAuth } from "../lib/auth";

export function Logo() {
  return (
    <Link
      to="/"
      className="flex items-center gap-2 font-display text-lg font-bold"
    >
      <span className="relative inline-flex h-7 w-10">
        <span className="absolute left-0 h-7 w-7 rounded-full bg-primary" />
        <span className="absolute right-0 h-7 w-7 rounded-full bg-primary-glow/90 mix-blend-multiply" />
      </span>
      PriceBiz
    </Link>
  );
}

export function SiteLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/auth/login", { replace: true });
  };
  
  const nav =
    "text-sm font-medium hover:text-primary [&.active]:text-primary";

  const profileLabel =
    user?.name?.trim().split(/\s+/)[0] ||
    user?.email?.trim() ||
    "Profile";

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b bg-background/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5">
          <Logo />

          <nav className="hidden items-center gap-6 md:flex">
            <NavLink to="/search" className={nav}>
              Search
            </NavLink>
            <NavLink to="/contribute" className={nav}>
              Contribute
            </NavLink>
            <NavLink to="/community" className={nav}>
              Community
            </NavLink>
          </nav>

          <div className="flex items-center gap-2">
            {user ? (
              <>
                <Link
                  to="/profile"
                  className="rounded-full border px-3 py-1.5 text-sm"
                >
                  {profileLabel}
                </Link>
                <button
                    type="button"
                    onClick={handleLogout}
                    className="text-sm text-muted-foreground hover:text-foreground"
                >
                    Log out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/auth/login"
                  className="text-sm font-medium"
                >
                  Log in
                </Link>
                <Link
                  to="/auth/register"
                  className="rounded-full bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground"
                >
                  Join
                </Link>
              </>
            )}
          </div>
        </div>

        <nav className="flex justify-center gap-6 border-t py-2 md:hidden">
          <NavLink to="/search" className={nav}>
            Search
          </NavLink>
          <NavLink to="/contribute" className={nav}>
            Contribute
          </NavLink>
          <NavLink to="/community" className={nav}>
            Community
          </NavLink>
        </nav>
      </header>

      <main className="flex-1">{children}</main>

      <footer className="border-t py-8 text-center text-xs text-muted-foreground">
        PriceBiz shows observed price ranges from community contributions.
        Prices may vary by seller and location.
      </footer>
    </div>
  );
}

export function Page({
  title,
  kicker,
  children,
}: {
  title: string;
  kicker?: string;
  children: ReactNode;
}) {
  return (
    <div className="mx-auto max-w-6xl px-5 py-10 animate-fade-in">
      {kicker && (
        <p className="text-xs font-semibold uppercase tracking-wider text-primary mb-1">
          {kicker}
        </p>
      )}

      <h1 className="mt-0 font-display text-3xl font-bold tracking-tight md:text-4xl">
        {title}
      </h1>

      <div className="mt-8">{children}</div>
    </div>
  );
}

export const inputCls =
  "w-full rounded-xl border border-input bg-card px-4 py-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-colors";

export const btnCls =
  "inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-all hover:brightness-110 active:scale-95 disabled:opacity-60 disabled:pointer-events-none btn-pressed";