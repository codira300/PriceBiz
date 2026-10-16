import { AuthForm } from "../components/auth-form";

import { usePageMeta } from "../lib/meta";

export default function LoginPage() {
  usePageMeta({
    title: "Log in — PriceBiz",
    description:
      "Log in to PriceBiz to contribute prices and join discussions.",
    ogTitle: "Log in — PriceBiz",
    ogType: "website",
    ogImage: "/hero-trader.jpg",
    ogUrl: window.location.href,
    ogSiteName: "PriceBiz",
    ogDescription: "Log in to PriceBiz.",
    twitterCard: "summary",
    twitterTitle: "Log in — PriceBiz",
    twitterDescription: "Log in to PriceBiz.",
    twitterImage: "/hero-trader.jpg",
  });

  return <AuthForm mode="login" />;
}
