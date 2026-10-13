import { useEffect } from "react";

import { AuthForm } from "../components/auth-form";

export default function LoginPage() {
  useEffect(() => {
    document.title = "Log in — PriceBiz";

    const metadata = [
      {
        name: "description",
        content:
          "Log in to PriceBiz to contribute prices and join discussions.",
      },
      {
        property: "og:title",
        content: "Log in — PriceBiz",
      },
      {
        property: "og:description",
        content: "Log in to PriceBiz.",
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

  return <AuthForm mode="login" />;
}