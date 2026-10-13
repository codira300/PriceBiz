
export const PASSWORD_RULES = [
  {
    id: "length",
    label: "12–128 characters",
    test: (value: string) =>
      value.length >= 12 && value.length <= 128,
  },
  {
    id: "uppercase",
    label: "At least one uppercase letter",
    test: (value: string) => /[A-Z]/.test(value),
  },
  {
    id: "lowercase",
    label: "At least one lowercase letter",
    test: (value: string) => /[a-z]/.test(value),
  },
  {
    id: "number",
    label: "At least one number",
    test: (value: string) => /[0-9]/.test(value),
  },
  {
    id: "special",
    label: "At least one special character",
    test: (value: string) => /[^A-Za-z0-9\s]/.test(value),
  },
  {
    id: "whitespace",
    label: "No whitespace",
    test: (value: string) => !/\s/.test(value),
  },
] as const;

export function isPasswordValid(password: string): boolean {
  return PASSWORD_RULES.every((rule) => rule.test(password));
}
