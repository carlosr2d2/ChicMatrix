export function parseApiError(raw: string): string {
  try {
    const parsed = JSON.parse(raw) as { detail?: string | { msg?: string }[] };
    if (typeof parsed.detail === "string") {
      return parsed.detail;
    }
    if (Array.isArray(parsed.detail) && parsed.detail.length > 0) {
      return parsed.detail.map((item) => item.msg ?? "Validation error").join(". ");
    }
  } catch {
    // plain text error
  }
  return raw || "Something went wrong. Please try again.";
}
