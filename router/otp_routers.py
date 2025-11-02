# router.py
from fastapi import APIRouter, HTTPException, status
from schemas import *
from otp_service import OTPService

router = APIRouter(prefix="/otp", tags=["OTP"])
service = OTPService()

@router.post("/generate", response_model=OTPGenerateResponse)
async def generate_otp(req: OTPGenerateRequest):
    result = await service.generate(req.transaction_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/verify", response_model=OTPVerifyResponse)
async def verify_otp(req: OTPVerifyRequest):
    result = service.verify(req.transaction_id, req.otp_code)

    if "not found" in result.get("message", "").lower():
        raise HTTPException(status_code=410, detail="OTP expired or invalid")
    if "max attempts" in result.get("message", "").lower():
        raise HTTPException(status_code=429, detail="Too many attempts")
    if not result["verified"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"],
            headers={"X-Remaining-Attempts": str(result.get("remaining_attempts", 0))}
        )
    return result

@router.post("/resend", response_model=OTPGenerateResponse)
async def resend_otp(req: OTPGenerateRequest):
    result = await service.resend(req.transaction_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result