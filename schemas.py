#schemas.py
from typing import Optional
from pydantic import BaseModel, Field

## Pydantic schemas for request or respond validation

class OTPGenerateRequest(BaseModel):
    transaction_id : int = Field(...,description="Transaction ID for OTP generation")

    class Config:
        json_shema_extra = {
            "example" : {
                "transaction_id": 1
            }
        }
class OTPGenerateRespone(BaseModel):
    success : bool
    message : str
    transaction_id : int
    otp_sent_to : str
    expires_in_seconds : int

    class Config:
        json_schema_extra = {
            "example" : {
                "success" : True,
                "message" : "OTP sent successfully",
                "transaction_id" : 1,
                "otp_sent_to" : "vestarex20@gmail.com",
                "expires_in_seconds" : 300

            }
        }

class OTPVerifyRequest(BaseModel):
    transaction_id : int = Field(...,description="Transaction ID")
    otp_code : str = Field(...,min_length = 6, max_length=6,description="6 digit OTP code")

    class Config:
        json_schema_extra = {
            "example" :  {
                "transaction_id" : 1,
                "otp_code" : "123456"
            } 
        }

class OTPVerifyResponse(BaseModel):
    success  : bool
    message : str
    transaction_id : int
    verified : bool
    remaining_attempts: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "OTP verified successfully",
                "transaction_id": 1,
                "verified": True
            }
        }

class OTPResendRequest(BaseModel):
    transaction_id : int = Field(...,description="Transaction ID for OTP resend")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": 1
            }
        }

class OTPResendRespond(BaseModel):
    success : bool
    message : str
    error_code : Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Transaction not found",
                "error_code": "TRANSACTION_NOT_FOUND"
            }
        }
class OTPResendRequest(BaseModel):
    transaction_id: int = Field(..., description="Transaction ID to resend OTP for")

    class Config:
        json_schema_extra = {
            "example": {"transaction_id": 1}
        }


