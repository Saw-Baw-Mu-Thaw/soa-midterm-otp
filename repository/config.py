# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Microservice URLs
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_URL", "http://127.0.0.1:8000")
EMAIL_SERVICE_URL = os.getenv("EMAIL_URL", "http://127.0.0.1:8003")

# OTP Settings
OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "300")) 
MAX_OTP_ATTEMPTS = int(os.getenv("MAX_OTP_ATTEMPTS", "5"))