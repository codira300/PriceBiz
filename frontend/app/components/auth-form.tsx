import { Link, useNavigate } from "react-router";
import { useCallback, useState } from "react";
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
    <div className="mx-auto max-w-md px-5 py-16">
      <div className="rounded-[2rem] border bg-card p-8 shadow-float">
        <h1 className="font-display text-3xl font-bold">
          {reg ? "Join PriceBiz" : "Welcome back"}
        </h1>

        <p className="mt-1 text-sm text-muted-foreground">
          {reg
            ? "Share prices and help your community."
            : "Log in to contribute and discuss."}
        </p>

        <form
          className="mt-6 space-y-4"
          onSubmit={handleSubmit}
        >
          {reg && (
            <input
              required
              placeholder="Full name"
              autoComplete="name"
              value={f.name}
              onChange={(e) => setField("name", e.target.value)}
              className={inputCls}
            />
          )}

          <input
            required
            type="email"
            placeholder="Email"
            autoComplete="email"
            value={f.email}
            onChange={(e) => setField("email", e.target.value)}
            className={inputCls}
          />

          {reg && (
            <input
              type="tel"
              placeholder="Phone (optional)"
              autoComplete="tel"
              value={f.phone}
              onChange={(e) => setField("phone", e.target.value)}
              className={inputCls}
            />
          )}

          <div className="space-y-3">
            <label
              htmlFor="password"
              className="block text-sm font-medium"
            >
              Password
            </label>

            <div className="flex items-center rounded-xl border border-input bg-card focus-within:ring-2 focus-within:ring-primary/20">
              <input
                id="password"
                name="password"
                required
                type={passwordVisible ? "text" : "password"}
                placeholder="Password"
                autoComplete={
                  reg ? "new-password" : "current-password"
                }
                value={f.password}
                maxLength={128}
                onChange={(e) => {
                  setField("password", e.target.value);
                  setPasswordTouched(true);
                }}
                className="min-w-0 flex-1 rounded-xl bg-transparent px-4 py-3 text-sm outline-none"
                aria-describedby={
                  reg ? "password-requirements" : undefined
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
                className="shrink-0 px-4 py-3 text-sm font-medium text-primary"
              >
                {passwordVisible ? "Hide" : "Show"}
              </button>
            </div>

            {reg && (
              <div
                id="password-requirements"
                className="space-y-2"
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
                        className={`text-sm ${
                          passed
                            ? "text-green-700"
                            : "text-muted-foreground"
                        }`}
                      >
                        <span aria-hidden="true">
                          {passed ? "✓" : "○"}
                        </span>{" "}
                        {rule.label}
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

        <div className="mt-6 space-y-4">
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
                className="text-primary"
              >
                Log in
              </Link>
            </>
          ) : (
            <>
              New here?{" "}
              <Link
                to="/auth/register"
                className="text-primary"
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
