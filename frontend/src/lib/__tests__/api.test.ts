import { getHealth } from "@/lib/api";

describe("getHealth", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("returns health payload on success", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok", service: "ChicMatrix" }),
    }) as jest.Mock;

    const result = await getHealth("http://api.test");
    expect(result).toEqual({ status: "ok", service: "ChicMatrix" });
    expect(global.fetch).toHaveBeenCalledWith("http://api.test/health", {
      next: { revalidate: 30 },
    });
  });

  it("returns null when API fails", async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: false }) as jest.Mock;
    const result = await getHealth("http://api.test");
    expect(result).toBeNull();
  });
});
