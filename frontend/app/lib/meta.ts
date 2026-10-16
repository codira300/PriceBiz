import { useEffect } from "react";

export function usePageMeta({
  title,
  description,
  ogTitle,
  ogDescription,
}: {
  title?: string;
  description?: string;
  ogTitle?: string;
  ogDescription?: string;
}) {
  useEffect(() => {
    if (title !== undefined) {
      document.title = title;
    }

    const upsertMeta = (
      selector: string,
      attribute: "name" | "property",
      key: string,
      value: string,
    ) => {
      let element = document.head.querySelector<HTMLMetaElement>(selector);

      if (!element) {
        element = document.createElement("meta");
        element.setAttribute(attribute, key);
        document.head.appendChild(element);
      }

      element.setAttribute("content", value);
    };

    if (description !== undefined) {
      upsertMeta(
        'meta[name="description"]',
        "name",
        "description",
        description,
      );
    }

    if (ogTitle !== undefined) {
      upsertMeta('meta[property="og:title"]', "property", "og:title", ogTitle);
    }

    if (ogDescription !== undefined) {
      upsertMeta(
        'meta[property="og:description"]',
        "property",
        "og:description",
        ogDescription,
      );
    }
  }, [title, description, ogTitle, ogDescription]);
}
