import { matchRoutes } from "react-router";
import { describe, expect, it } from "vitest";

import { router } from "../routes/__root";

describe("App routing", () => {
  it("matches the home page instead of falling back to not found", () => {
    const matches = matchRoutes(router.routes, "/");

    expect(matches).not.toBeNull();
    expect(matches?.some((match) => match.route.index)).toBe(true);
  });
});