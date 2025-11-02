#otp_service.py
import httpx
from repository.config import TRANSACTION_URL
from typing import Dict
import otp_cache
from repository.otp_repository import OTPRepository


class OTPService:
    def __init__(self):
        self.repository = OTPRepository()
        self.otp_cache = otp_cache.otp_cache
        self.transaction_url = TRANSACTION_URL.rstrip("/")

     #Generate OTP   
    async def generate_otp_with_transaction_data(self, transaction_id: int) -> dict:
             try:
                
                if self.otp_cache.get_otp(transaction_id):
                    remaining = self.otp_cache.get_remaining_time(transaction_id)
                    return {"success": False, "message": f"Wait {remaining}s"}
        
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{self.transaction_url}/transactions/{transaction_id}"
                    )
                    if resp.status_code != 200:
                        return {"success": False, "message": "Transaction not found"}
        
                    tx = resp.json()
                    email = tx.get("customer_email")
                    if not email:
                        email = "test@gmail.com"  # fallback
        
               
                code = self.otp_cache.generate_otp()
                info = self.otp_cache.store_otp(transaction_id, code, email)
        
                print(f"[OTP] Code {code} → {email}")
        
                return {
                    "success": True,
                    "message": "OTP sent!",
                    "data": {
                        "transaction_id": transaction_id,
                        "otp_sent_to": self._mask_email(email),
                        "expires_in_seconds": info["expires_in_seconds"]
                    }
                }
             except Exception as e:
                return {"success": False, "message": str(e)}
     
    #Verify OTP
    def verify_otp(self, transaction_id: int, otp_code: str) -> dict:
        try:
            verification_result = self.otp_cache.verify_otp(transaction_id, otp_code)

            if not verification_result["success"]:
                return {
                    "success": False,
                    "message": verification_result["message"],
                    "verified": False,
                    "remaining_attempts": verification_result.get("remaining_attempts"),
                }

            print(f"\nOTP Verified for Transaction {transaction_id}\n")
            return {
                "success": True,
                "message": "OTP verified successfully",
                "verified": True,
            }

        except Exception as e:
            print(f"[OTP Service] Error verifying OTP: {e}")
            return {"success": False, "message": f"Failed to verify OTP: {str(e)}", "verified": False}
    
    #Resend OTP
    async def resend_otp(self, transaction_id: int) -> dict:
        try:
            self.otp_cache.delete_otp(transaction_id)
            return await self.generate_otp_with_transaction_data(transaction_id)
        except Exception as e:
            print(f"[OTP Service] Error resending OTP: {e}")
            return {"success": False, "message": f"Failed to resend OTP: {str(e)}"}
    
    def check_otp_status(self, transaction_id: int) -> dict:
        try:
            otp_data = self.otp_cache.get_otp(transaction_id)
            
            if not otp_data:
                return {
                    'exists': False,
                    'verified': False,
                    'remaining_time': 0,
                    'attempts_used': 0
                }
            
            remaining_time = self.otp_cache.get_remaining_time(transaction_id)
            
            return {
                'exists': True,
                'verified': otp_data.get('verified', False),
                'remaining_time': remaining_time or 0,
                'attempts_used': otp_data.get('attempts', 0)
            }
            
        except Exception as e:
            print(f"[OTP Service] Error checking OTP status: {e}")
            return {
                'exists': False,
                'verified': False,
                'remaining_time': 0,
                'attempts_used': 0
            }
    
    def _mask_email(self, email: str) -> str:
        """Mask email address for privacy"""
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@')
        
        if len(local) <= 2:
            masked_local = local[0] + '*' * (len(local) - 1)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
