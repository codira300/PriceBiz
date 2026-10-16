import { AuthForm } from "../components/auth-form";

import { usePageMeta } from "../lib/meta";

export default function LoginPage() {
  usePageMeta({
    title: "Log in — PriceBiz",
    description:
      "Log in to PriceBiz to contribute prices and join discussions.",
    ogTitle: "Log in — PriceBiz",
    ogDescription: "Log in to PriceBiz.",
  });

  return <AuthForm mode="login" />;
}
