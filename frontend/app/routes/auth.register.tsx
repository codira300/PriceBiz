import { AuthForm } from "../components/auth-form";

import { usePageMeta } from "../lib/meta";

export default function RegisterPage() {
  usePageMeta({
    title: "Create an account — PriceBiz",
    description:
      "Join PriceBiz and help your community know the price before they buy.",
    ogTitle: "Create an account — PriceBiz",
    ogType: "website",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    ogDescription: "Join PriceBiz.",
    twitterCard: "summary",
    twitterTitle: "Create an account — PriceBiz",
    twitterDescription: "Join PriceBiz.",
    twitterImage: "/hero-trader.jpg",
  });

  return <AuthForm mode="register" />;
}
