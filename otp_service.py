# otp_service.py
from otp_cache import OTPCache
from repository.config import OTP_TTL_SECONDS, MAX_OTP_ATTEMPTS

cache = OTPCache(OTP_TTL_SECONDS, MAX_OTP_ATTEMPTS)

class OTPService:
    async def generate(self, transaction_id: int) -> dict:
        if cache.get(transaction_id):
            remaining = cache.remaining_seconds(transaction_id) or 0
            return {"success": False, "message": f"Wait {remaining}s"}
    
        expires_in = cache.set(transaction_id, "user@example.com")
        stored_code = cache.get(transaction_id)["code"]  
        print(f"\nOTP FOR TXN {transaction_id}: {stored_code}\n")
    
        return {
            "success": True,
            "message": "OTP generated",
            "data": {
                "transaction_id": transaction_id,
                "expires_in_seconds": expires_in
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