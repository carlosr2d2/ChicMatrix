export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  role: string;
  permissions: string[];
};

export type PhoneOtpLoginResponse = {
  message: string;
  otp_code?: string | null;
};

export type LoginRequest =
  | { method: "email"; email: string; password: string }
  | { method: "phone"; phone: string; otp_code?: string }
  | { method: "social"; provider: "google" | "apple"; id_token: string };

export type RegisterEmailRequest = {
  email: string;
  password: string;
  name?: string;
  consent_accepted: boolean;
};

export type RegisterEmailResponse = {
  user_id: string;
  email: string;
  verified: boolean;
  message: string;
  verification_token?: string | null;
};

export type RegisterPhoneRequest = {
  phone: string;
  name?: string;
  consent_accepted: boolean;
};

export type RegisterPhoneResponse = {
  user_id: string;
  phone: string;
  verified: boolean;
  message: string;
  otp_code?: string | null;
};

export type VerifyEmailRequest = {
  token: string;
};

export type VerifyEmailResponse = {
  user_id: string;
  email: string | null;
  verified: boolean;
  message: string;
};

export type VerifyPhoneRequest = {
  phone: string;
  otp_code: string;
};

export type VerifyPhoneResponse = {
  user_id: string;
  phone: string | null;
  verified: boolean;
  message: string;
};

export type SocialAuthRequest = {
  provider: "google" | "apple";
  id_token: string;
  name?: string;
  phone?: string;
  consent_accepted: boolean;
};

export type SocialAuthResponse = {
  user_id: string;
  email: string | null;
  phone: string | null;
  verified: boolean;
  social_provider: string;
  linked_existing_account: boolean;
  message: string;
};

import { parseApiError } from "@/lib/errors";

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
  return response.json() as Promise<T>;
}

export async function registerEmail(
  apiUrl: string,
  payload: RegisterEmailRequest,
): Promise<RegisterEmailResponse> {
  const response = await fetch(`${apiUrl}/register/email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<RegisterEmailResponse>(response);
}

export async function registerPhone(
  apiUrl: string,
  payload: RegisterPhoneRequest,
): Promise<RegisterPhoneResponse> {
  const response = await fetch(`${apiUrl}/register/phone`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<RegisterPhoneResponse>(response);
}

export async function verifyEmail(
  apiUrl: string,
  payload: VerifyEmailRequest,
): Promise<VerifyEmailResponse> {
  const response = await fetch(`${apiUrl}/verify/email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<VerifyEmailResponse>(response);
}

export async function verifyPhone(
  apiUrl: string,
  payload: VerifyPhoneRequest,
): Promise<VerifyPhoneResponse> {
  const response = await fetch(`${apiUrl}/verify/phone`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<VerifyPhoneResponse>(response);
}

export async function socialAuth(
  apiUrl: string,
  payload: SocialAuthRequest,
): Promise<SocialAuthResponse> {
  const response = await fetch(`${apiUrl}/auth/social`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<SocialAuthResponse>(response);
}

export async function login(
  apiUrl: string,
  payload: LoginRequest,
): Promise<TokenResponse | PhoneOtpLoginResponse> {
  const response = await fetch(`${apiUrl}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonResponse<TokenResponse | PhoneOtpLoginResponse>(response);
}

export async function refreshTokens(
  apiUrl: string,
  refreshToken: string,
): Promise<TokenResponse> {
  const response = await fetch(`${apiUrl}/login/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  return parseJsonResponse<TokenResponse>(response);
}

export async function logout(apiUrl: string, refreshToken: string): Promise<void> {
  const response = await fetch(`${apiUrl}/login/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(parseApiError(detail));
  }
}

export function isTokenResponse(
  payload: TokenResponse | PhoneOtpLoginResponse,
): payload is TokenResponse {
  return "access_token" in payload;
}
