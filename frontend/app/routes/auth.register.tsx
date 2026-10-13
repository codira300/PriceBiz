import { useEffect } from "react";

import { AuthForm } from "../components/auth-form";

export default function RegisterPage() {
  useEffect(() => {
    document.title = "Create an account — PriceBiz";

    const metadata = [
      {
        name: "description",
        content:
          "Join PriceBiz and help your community know the price before they buy.",
      },
      {
        property: "og:title",
        content: "Create an account — PriceBiz",
      },
      {
        property: "og:description",
        content: "Join PriceBiz.",
      },
    ];

    metadata.forEach(({ name, property, content }) => {
      const selector = name
        ? `meta[name="${name}"]`
        : `meta[property="${property}"]`;

      let element = document.head.querySelector(selector);

      if (!element) {
        element = document.createElement("meta");

        if (name) {
          element.setAttribute("name", name);
        } else if (property) {
          element.setAttribute("property", property);
        }

        document.head.appendChild(element);
      }

      element.setAttribute("content", content);
    });
  }, []);

  return <AuthForm mode="register" />;
}