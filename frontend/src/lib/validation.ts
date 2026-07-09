const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_PATTERN = /^\+[1-9]\d{6,14}$/;

export function validateEmail(email: string): string | null {
  if (!email.trim()) return "Email is required";
  if (!EMAIL_PATTERN.test(email)) return "Enter a valid email address";
  return null;
}

export function validatePassword(password: string, minLength = 8): string | null {
  if (!password) return "Password is required";
  if (password.length < minLength) return `Password must be at least ${minLength} characters`;
  return null;
}

export function validatePhone(phone: string): string | null {
  if (!phone.trim()) return "Phone number is required";
  if (!PHONE_PATTERN.test(phone)) return "Use E.164 format, e.g. +573001234567";
  return null;
}

export function validateOtp(otp: string): string | null {
  if (!otp.trim()) return "OTP code is required";
  if (!/^\d{6}$/.test(otp)) return "OTP must be 6 digits";
  return null;
}
