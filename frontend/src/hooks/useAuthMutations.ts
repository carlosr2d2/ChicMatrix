"use client";

import { useMutation } from "@tanstack/react-query";

import { login, registerEmail, registerPhone, socialAuth, verifyEmail, verifyPhone } from "@/lib/auth";
import { getApiUrl } from "@/lib/config";

export function useRegisterEmailMutation() {
  const apiUrl = getApiUrl();
  return useMutation({
    mutationFn: (payload: Parameters<typeof registerEmail>[1]) => registerEmail(apiUrl, payload),
  });
}

export function useRegisterPhoneMutation() {
  const apiUrl = getApiUrl();
  return useMutation({
    mutationFn: (payload: Parameters<typeof registerPhone>[1]) => registerPhone(apiUrl, payload),
  });
}

export function useSocialAuthMutation() {
  const apiUrl = getApiUrl();
  return useMutation({
    mutationFn: (payload: Parameters<typeof socialAuth>[1]) => socialAuth(apiUrl, payload),
  });
}

export function useLoginMutation() {
  const apiUrl = getApiUrl();
  return useMutation({
    mutationFn: (payload: Parameters<typeof login>[1]) => login(apiUrl, payload),
  });
}

export function useVerifyEmailMutation() {
  const apiUrl = getApiUrl();
  return useMutation({
    mutationFn: (token: string) => verifyEmail(apiUrl, { token }),
  });
}

export function useVerifyPhoneMutation() {
  const apiUrl = getApiUrl();
  return useMutation({
    mutationFn: (payload: { phone: string; otp_code: string }) => verifyPhone(apiUrl, payload),
  });
}
