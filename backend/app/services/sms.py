import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SmsService:
    def send_sms(self, phone: str, message: str, otp_code: str | None = None) -> None:
        if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_phone_number:
            self._send_twilio(phone, message)
            return

        logger.info(
            "SMS OTP (Twilio not configured)",
            extra={"phone": phone, "sms_body": message, "otp_code": otp_code},
        )

    @staticmethod
    def _send_twilio(phone: str, message: str) -> None:
        from twilio.rest import Client

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        client.messages.create(
            body=message,
            from_=settings.twilio_phone_number,
            to=phone,
        )
        logger.info("SMS sent via Twilio", extra={"phone": phone})
