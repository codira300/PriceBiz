import { Link, NavLink, useNavigate } from "react-router";
import type { ReactNode } from "react";

import { useAuth } from "../lib/auth";

export function Logo() {
  return (
    <Link
      to="/"
      className="flex items-center gap-2 rounded-[3px] font-display text-lg font-bold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
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
    "inline-flex min-h-11 items-center rounded-[3px] text-sm font-medium transition-colors duration-150 ease-out hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring [&.active]:text-primary";

  const profileLabel =
    user?.name?.trim().split(/\s+/)[0] ||
    user?.email?.trim() ||
    "Profile";

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b bg-background/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5">
          <Logo />

          <nav
            aria-label="Primary"
            className="hidden items-center gap-6 md:flex"
          >
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
                  className="inline-flex min-h-10 items-center rounded-[3px] border border-border px-3 text-sm transition-colors duration-150 ease-out hover:border-primary hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                >
                  {profileLabel}
                </Link>
                <button
                    type="button"
                    onClick={handleLogout}
                    className="inline-flex min-h-10 items-center px-1 text-sm text-muted-foreground transition-colors duration-150 ease-out hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                >
                    Log out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/auth/login"
                  className="inline-flex min-h-10 items-center rounded-[3px] px-1 text-sm font-medium transition-colors duration-150 ease-out hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                >
                  Log in
                </Link>
                <Link
                  to="/auth/register"
                  className="inline-flex min-h-10 items-center rounded-[3px] bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors duration-150 ease-out hover:bg-primary-glow hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                >
                  Join
                </Link>
              </>
            )}
          </div>
        </div>

        <nav
          aria-label="Mobile primary"
          className="flex justify-center gap-6 border-t py-1 md:hidden"
        >
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
    <div className="mx-auto max-w-6xl animate-fade-in px-5 py-12 md:py-16">
      {kicker && (
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          {kicker}
        </p>
      )}

      <h1 className="mt-0 text-balance font-display text-[clamp(2rem,4vw,3rem)] font-bold leading-[1.1] tracking-[-0.03em]">
        {title}
      </h1>

      <div className="mt-8 md:mt-10">{children}</div>
    </div>
  );
}

export const inputCls =
  "min-h-11 w-full rounded-[3px] border border-input bg-card px-4 py-2.5 text-base text-foreground outline-none transition-colors duration-150 ease-out placeholder:text-muted-foreground focus:border-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

export const btnCls =
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-[3px] border border-primary bg-primary px-5 text-sm font-semibold text-primary-foreground transition-colors duration-150 ease-out hover:border-primary-glow hover:bg-primary-glow hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:pointer-events-none disabled:opacity-60";