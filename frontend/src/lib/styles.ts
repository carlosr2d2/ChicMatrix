/** Closed style vocabulary v1 — keep in sync with backend StyleCode. */

export type StyleOption = {
  code: string;
  labelEs: string;
};

export const STYLE_OPTIONS: StyleOption[] = [
  { code: "formal", labelEs: "Formales" },
  { code: "sport", labelEs: "Deporte" },
  { code: "biker", labelEs: "Motociclistas" },
  { code: "rocker", labelEs: "Rockeros" },
  { code: "casual", labelEs: "Casual" },
  { code: "minimal", labelEs: "Minimal" },
  { code: "streetwear", labelEs: "Streetwear" },
];

export const STYLE_LABELS: Record<string, string> = Object.fromEntries(
  STYLE_OPTIONS.map((option) => [option.code, option.labelEs]),
);

export function styleLabel(code: string): string {
  return STYLE_LABELS[code] ?? code;
}
