import { useEffect } from "react";

export function usePageMeta({
  title,
  description,
  ogTitle,
  ogDescription,
  ogType,
  ogImage,
  ogUrl,
  ogSiteName,
  twitterCard,
  twitterTitle,
  twitterDescription,
  twitterImage,
}: {
  title?: string;
  description?: string;
  ogTitle?: string;
  ogDescription?: string;
  ogType?: string;
  ogImage?: string;
  ogUrl?: string;
  ogSiteName?: string;
  twitterCard?: string;
  twitterTitle?: string;
  twitterDescription?: string;
  twitterImage?: string;
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

    // Standard HTML meta
    if (description !== undefined) {
      upsertMeta(
        'meta[name="description"]',
        "name",
        "description",
        description,
      );
    }

    // Open Graph
    if (ogTitle !== undefined) {
      upsertMeta('meta[property="og:title"]', "property", "og:title", ogTitle);
    }

    if (ogType !== undefined) {
      upsertMeta('meta[property="og:type"]', "property", "og:type", ogType);
    }

    if (ogImage !== undefined) {
      upsertMeta(
        'meta[property="og:image"]',
        "property",
        "og:image",
        ogImage,
      );
    }

    if (ogUrl !== undefined) {
      upsertMeta('meta[property="og:url"]', "property", "og:url", ogUrl);
    }

    if (ogSiteName !== undefined) {
      upsertMeta(
        'meta[property="og:site_name"]',
        "property",
        "og:site_name",
        ogSiteName,
      );
    }

    if (ogDescription !== undefined) {
      upsertMeta(
        'meta[property="og:description"]',
        "property",
        "og:description",
        ogDescription,
      );
    }

    // Twitter Cards
    if (twitterCard !== undefined) {
      upsertMeta(
        'meta[name="twitter:card"]',
        "name",
        "twitter:card",
        twitterCard,
      );
    }

    if (twitterTitle !== undefined) {
      upsertMeta(
        'meta[name="twitter:title"]',
        "name",
        "twitter:title",
        twitterTitle,
      );
    }

    if (twitterDescription !== undefined) {
      upsertMeta(
        'meta[name="twitter:description"]',
        "name",
        "twitter:description",
        twitterDescription,
      );
    }

    if (twitterImage !== undefined) {
      upsertMeta(
        'meta[name="twitter:image"]',
        "name",
        "twitter:image",
        twitterImage,
      );
    }
  }, [
    title,
    description,
    ogTitle,
    ogType,
    ogImage,
    ogUrl,
    ogSiteName,
    ogDescription,
    twitterCard,
    twitterTitle,
    twitterDescription,
    twitterImage,
  ]);
}
