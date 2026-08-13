/** Closed sex vocabulary — keep in sync with backend SexCode. */

export type SexOption = {
  code: string;
  labelEs: string;
};

export const SEX_OPTIONS: SexOption[] = [
  { code: "female", labelEs: "Mujer" },
  { code: "male", labelEs: "Hombre" },
  { code: "other", labelEs: "Otro" },
  { code: "prefer_not_to_say", labelEs: "Prefiero no decir" },
];
