import { describe, expect, it } from "vitest";

import { apiUrl } from "./api";

describe("apiUrl", () => {
  it("adds a leading slash to bare paths", () => {
    expect(apiUrl("api/health")).toMatch(/\/api\/health$/);
  });

  it("does not double up slashes", () => {
    expect(apiUrl("/api/health")).not.toMatch(/\/\/api/);
    expect(apiUrl("/api/health").endsWith("/api/health")).toBe(true);
  });
});
