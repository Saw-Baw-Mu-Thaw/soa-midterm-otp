#router/otp_routers.py
#Endpoints
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException,status
from pydantic import BaseModel, EmailStr, Field
from otp_service import OTPService
from schemas import (
    OTPGenerateRespone,
    OTPVerifyRequest,
    OTPVerifyResponse,
    OTPResendRequest,
    OTPGenerateRequest,         
)

router = APIRouter(
    prefix="/otp/otp",
    tags=["OTP Management"],
    
    
)

@router.post("/generate")
async def generate_otp(request: OTPGenerateRequest):
    otp_service = OTPService()
    result = await otp_service.generate_otp_with_transaction_data(request.transaction_id)

    if not result["success"]:
        raise HTTPException(status_code=429, detail=result["message"])

    
    return result["data"]

@router.post(
    "/verify",
    response_model=OTPVerifyResponse,
    responses={
        200: {"description" : "OTP verified"},
        400: {"description" : "Invalid OTP or too many attempts"},
        410: {"description" : "Expired OTP"},
    }
)
async def verify_otp(request: OTPVerifyRequest):
    otp_service = OTPService()
    result = otp_service.verify_otp(request.transaction_id, request.otp_code)

    if result.get("message") == "OTP has expired":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="OTP expired. Request a new one."
        )

    
    if "Maximum OTP attempts exceeded" in result.get("message", ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many wrong attempts."
        )

   
    if not result["verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"],  
            headers={"X-Remaining-Attempts": str(result.get("remaining_attempts", 0))}
        )

    return OTPVerifyResponse(
        success=True,
        message=result["message"],
        transaction_id=request.transaction_id,
        verified=True,
    )

@router.post(
    "/resend",
    response_model=OTPGenerateRespone,
    status_code=status.HTTP_200_OK,
)
async def resend_otp_endpoint(request: OTPResendRequest):
    otp_service = OTPService()
    result = await otp_service.resend_otp(request.transaction_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"],
        )

    return OTPGenerateRespone(
        success=True,
        message=result["message"],
        transaction_id=result["data"]["transaction_id"],
        otp_sent_to=result["data"]["otp_sent_to"],
        expires_in_seconds=result["data"]["expires_in_seconds"],
    )




