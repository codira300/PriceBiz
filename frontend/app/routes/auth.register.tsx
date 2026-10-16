import { AuthForm } from "../components/auth-form";

import { usePageMeta } from "../lib/meta";

export default function RegisterPage() {
  usePageMeta({
    title: "Create an account — PriceBiz",
    description:
      "Join PriceBiz and help your community know the price before they buy.",
    ogTitle: "Create an account — PriceBiz",
    ogDescription: "Join PriceBiz.",
  });

  return <AuthForm mode="register" />;
}
