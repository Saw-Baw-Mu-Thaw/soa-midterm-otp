import requests
from otp_cache import OTPCache
from repository.config import EMAIL_SERVICE_URL, OTP_TTL_SECONDS, MAX_OTP_ATTEMPTS

cache = OTPCache(OTP_TTL_SECONDS, MAX_OTP_ATTEMPTS)

class OTPService:
    async def generate(self, transaction_id: int, email: str = "", name: str = "User") -> dict:
        if cache.get(transaction_id):
            remaining = cache.remaining_seconds(transaction_id) or 0
            return {"success": False, "message": f"Wait {remaining}s"}

        # Generate & store OTP
        cache.set(transaction_id, email)
        data = cache.get(transaction_id)
        code = data["code"]

        print(f"\nOTP FOR TXN {transaction_id}: {code} → {email}\n")

        # SEND REAL EMAIL
        try:
            requests.post(
                f"{EMAIL_SERVICE_URL}/send-otp",
                json={
                    "transaction_id": transaction_id,
                    "email": email or "test@example.com",
                    "otp_code": code,
                    "customer_name": name
                },
                timeout=8
            )
        except Exception as e:
            print(f"Email failed: {e}")

        masked = email[:1] + "***@" + email.split("@")[-1] if email and "@" in email else "terminal"

        return {
            "success": True,
            "message": "OTP generated & sent",
            "data": {
                "transaction_id": transaction_id,
                "otp_code": code,
                "otp_sent_to": masked,
                "expires_in_seconds": OTP_TTL_SECONDS
            }
        }

    def verify(self, transaction_id: int, code: str) -> dict:
        result = cache.verify(transaction_id, code)
        return {
            "success": result["success"],
            "verified": result["success"],
            "message": result["message"],
            "remaining_attempts": result.get("remaining_attempts")
        }

    async def resend(self, transaction_id: int) -> dict:
        cache.delete(transaction_id)
        return await self.generate(transaction_id)