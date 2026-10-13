
import { useEffect } from "react";
import { Link } from "react-router";

import { Page, btnCls } from "../components/layout";
import { Loading } from "../components/states";
import { useAuth } from "../lib/auth";

export default function Profile() {
  const { user, ready, logout } = useAuth();

  useEffect(() => {
    document.title = "Your profile — PriceBiz";

    const description = "Your PriceBiz account.";

    let metaDescription = document.querySelector(
      'meta[name="description"]',
    );

    if (!metaDescription) {
      metaDescription = document.createElement("meta");
      metaDescription.setAttribute("name", "description");
      document.head.appendChild(metaDescription);
    }

    metaDescription.setAttribute("content", description);

    let ogTitle = document.querySelector('meta[property="og:title"]');

    if (!ogTitle) {
      ogTitle = document.createElement("meta");
      ogTitle.setAttribute("property", "og:title");
      document.head.appendChild(ogTitle);
    }

    ogTitle.setAttribute("content", "Your profile — PriceBiz");

    let ogDescription = document.querySelector(
      'meta[property="og:description"]',
    );

    if (!ogDescription) {
      ogDescription = document.createElement("meta");
      ogDescription.setAttribute("property", "og:description");
      document.head.appendChild(ogDescription);
    }

    ogDescription.setAttribute("content", description);
  }, []);

  if (!ready) {
    return <Loading />;
  }

  if (!user) {
    return (
      <Page title="You're not logged in" kicker="Account">
        <p className="mb-5 text-muted-foreground">
          Log in to view your account details.
        </p>
        <Link to="/auth/login" className={btnCls}>
          Log in
        </Link>
      </Page>
    );
  }

  const account = user as {
    _id?: string;
    id?: string;
    name?: string | null;
    email?: string | null;
    phone?: string | null;
  };

  const fields = [
    { label: "Full name", value: account.name },
    { label: "Email address", value: account.email },
    { label: "Phone number", value: account.phone },
  ];

  return (
    <Page
      title={account.name?.trim() || "Your profile"}
      kicker="Account"
    >
      <div className="max-w-xl overflow-hidden rounded-3xl border bg-card">
        <div className="border-b p-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-2xl font-bold text-primary">
            {(account.name?.trim() || account.email?.trim() || "U")
              .charAt(0)
              .toUpperCase()}
          </div>

          <h2 className="mt-4 text-xl font-semibold">
            {account.name?.trim() || "Name not provided"}
          </h2>

          <p className="mt-1 text-sm text-muted-foreground">
            {account.email || "Email not provided"}
          </p>
        </div>

        <dl className="divide-y">
          {fields.map((field) => (
            <div
              key={field.label}
              className="grid grid-cols-1 gap-1 px-6 py-4 sm:grid-cols-3 sm:gap-4"
            >
              <dt className="text-sm text-muted-foreground">
                {field.label}
              </dt>
              <dd className="break-all text-sm font-medium sm:col-span-2">
                {field.value?.trim() || "Not provided"}
              </dd>
            </div>
          ))}
        </dl>

        <div className="flex flex-wrap gap-3 border-t p-6">
          <Link to="/contribute" className={btnCls}>
            Add a price
          </Link>

          <button
            type="button"
            onClick={logout}
            className="rounded-full border px-6 py-3 text-sm"
          >
            Log out
          </button>
        </div>
      </div>
    </Page>
  );
}
