import { Link, useNavigate } from "react-router";
import { useCallback, useState } from "react";
import { Check, Circle } from "lucide-react";
import { GoogleSignInButton } from "./google-sign-in-button";

import { btnCls, inputCls } from "./layout";
import { ErrorState } from "./states";
import { useAuth } from "../lib/auth";
import type { ApiError } from "../lib/api/client";
import { PASSWORD_RULES, isPasswordValid } from "../lib/password";


export function AuthForm({
  mode,
}: {
  mode: "login" | "register";
}) {
  const { login, register, googleLogin } = useAuth();
  const navigate = useNavigate();

  const [f, setF] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
  });

  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<ApiError | null>(null);
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [passwordTouched, setPasswordTouched] = useState(false);
  const [googleError, setGoogleError] = useState("");

  const handleGoogleCredential = useCallback(
    async (credential: string) => {
      setGoogleError("");

      try {
        await googleLogin(credential);
        navigate("/profile", { replace: true });
      } catch (error) {
        setGoogleError(
          error instanceof Error
            ? error.message
            : "Google Sign-In failed. Please try again.",
        );
      }
    },
    [googleLogin, navigate],
  );

  const handleGoogleError = useCallback((message: string) => {
    setGoogleError(message);
  }, []);

  const reg = mode === "register";
  const passwordValid = isPasswordValid(f.password);

  const setField = (key: keyof typeof f, value: string) => {
    setF((prev) => ({ ...prev, [key]: value }));
  };

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr(null);

    if (reg && !passwordValid) {
      setPasswordTouched(true);
      return;
    }

    setBusy(true);

    try {
      if (reg) {
        await register({
          name: f.name,
          email: f.email,
          password: f.password,
          ...(f.phone ? { phone: f.phone } : {}),
        });
      } else {
        await login(f.email, f.password);
      }

      navigate("/profile", { replace: true });
    } catch (error) {
      setErr(error as ApiError);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-5 py-12 md:py-16">
      <div className="border border-border border-t-2 border-t-primary bg-card p-6 md:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          {reg ? "Create account" : "Account"}
        </p>

        <h1 className="mt-2 text-balance font-display text-[clamp(1.75rem,4vw,2.25rem)] font-bold leading-[1.15] tracking-[-0.025em]">
          {reg ? "Join PriceBiz" : "Welcome back"}
        </h1>

        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          {reg
            ? "Share prices and help your community."
            : "Log in to contribute and discuss."}
        </p>

        <form
          className="mt-7 space-y-5"
          onSubmit={handleSubmit}
        >
          {reg && (
            <div>
              <label
                htmlFor="auth-name"
                className="mb-1.5 block text-sm font-medium"
              >
                Full name
              </label>

              <input
                id="auth-name"
                required
                placeholder="e.g. Ada Okafor"
                autoComplete="name"
                value={f.name}
                onChange={(e) => setField("name", e.target.value)}
                className={inputCls}
              />
            </div>
          )}

          <div>
            <label
              htmlFor="auth-email"
              className="mb-1.5 block text-sm font-medium"
            >
              Email
            </label>

            <input
              id="auth-email"
              required
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              value={f.email}
              onChange={(e) => setField("email", e.target.value)}
              className={inputCls}
            />
          </div>

          {reg && (
            <div>
              <label
                htmlFor="auth-phone"
                className="mb-1.5 block text-sm font-medium"
              >
                Phone <span className="text-muted-foreground">(optional)</span>
              </label>

              <input
                id="auth-phone"
                type="tel"
                placeholder="+234 800 000 0000"
                autoComplete="tel"
                value={f.phone}
                onChange={(e) => setField("phone", e.target.value)}
                className={inputCls}
              />
            </div>
          )}

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="block text-sm font-medium"
            >
              Password
            </label>

            <div className="flex items-center border border-input bg-card transition-colors duration-150 ease-out focus-within:border-primary">
              <input
                id="password"
                name="password"
                required
                type={passwordVisible ? "text" : "password"}
                placeholder="Enter your password"
                autoComplete={
                  reg ? "new-password" : "current-password"
                }
                value={f.password}
                maxLength={128}
                onChange={(e) => {
                  setField("password", e.target.value);
                  setPasswordTouched(true);
                }}
                className="min-h-11 min-w-0 flex-1 bg-transparent px-3 py-2.5 text-base outline-none"
                aria-describedby={
                  reg ? "password-requirements" : undefined
                }
                aria-invalid={
                  reg && passwordTouched && !passwordValid
                    ? true
                    : undefined
                }
              />

              <button
                type="button"
                onClick={() =>
                  setPasswordVisible((visible) => !visible)
                }
                aria-label={
                  passwordVisible ? "Hide password" : "Show password"
                }
                aria-pressed={passwordVisible}
                className="inline-flex min-h-11 shrink-0 items-center px-3 text-sm font-medium text-primary transition-colors duration-150 ease-out hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                {passwordVisible ? "Hide" : "Show"}
              </button>
            </div>

            {reg && (
              <div
                id="password-requirements"
                className="space-y-2 pt-1"
              >
                <p className="text-sm font-medium">
                  Password requirements
                </p>

                <ul className="space-y-1.5" aria-live="polite">
                  {PASSWORD_RULES.map((rule) => {
                    const passed = rule.test(f.password);

                    return (
                      <li
                        key={rule.id}
                        className={`flex items-start gap-2 text-sm leading-6 ${
                          passed
                            ? "text-success"
                            : "text-muted-foreground"
                        }`}
                      >
                        {passed ? (
                          <Check
                            aria-hidden="true"
                            className="mt-1 h-4 w-4 shrink-0"
                          />
                        ) : (
                          <Circle
                            aria-hidden="true"
                            className="mt-1 h-4 w-4 shrink-0"
                          />
                        )}
                        <span>{rule.label}</span>
                      </li>
                    );
                  })}
                </ul>

                {passwordTouched &&
                  f.password.length > 0 &&
                  !passwordValid && (
                    <p className="text-sm text-destructive">
                      Meet all password requirements to create your account.
                    </p>
                  )}
              </div>
            )}
          </div>

          {err && <ErrorState error={err} />}

          <button
            type="submit"
            disabled={busy || (reg && !passwordValid)}
            className={`${btnCls} w-full`}
          >
            {busy
              ? "Please wait…"
              : reg
                ? "Create account"
                : "Log in"}
          </button>
        </form>

        <div className="mt-7 space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <span className="text-sm text-muted-foreground">
            or continue with
          </span>
          <div className="h-px flex-1 bg-border" />
        </div>

        <GoogleSignInButton
          onCredential={handleGoogleCredential}
          onError={handleGoogleError}
          disabled={busy}
        />

        {googleError && (
          <p role="alert" className="text-sm text-destructive">
            {googleError}
          </p>
        )}
      </div>

        <p className="mt-5 text-center text-sm text-muted-foreground">
          {reg ? (
            <>
              Already have an account?{" "}
              <Link
                to="/auth/login"
                className="text-primary underline underline-offset-4 transition-colors duration-150 ease-out hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                Log in
              </Link>
            </>
          ) : (
            <>
              New here?{" "}
              <Link
                to="/auth/register"
                className="text-primary underline underline-offset-4 transition-colors duration-150 ease-out hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                Create an account
              </Link>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
