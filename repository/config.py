#repository/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Connection String of DATABASE named "ibanking_db"
DATABASE_URL = os.getenv("DATABASE_URL","mysql+pymysql://root:@localhost:3306/ibanking_db?charset=utf8mb4")


# Conneting into SMTP Server
SMTP_HOST = os.getenv("SMTP_HOST","smtp.gmail.com")

SMTP_PORT = int(os.getenv("SMTP_PORT",587))

SMTP_USER = os.getenv("SMTP_USER","webfinal2005@gmail.com")

SMTP_PASS = os.getenv("SMTP_PASS","quxcufvyaskpreah")

OTP_EXPIRE_MINUTES = 5
MAX_OTP_ATTEMPTS = 5
SENDER_NAME = "iBanking OTP Service"

#Microservice URL:

OTP_URL = os.getenv("OTP_URL", "http://127.0.0.1:8002/")


EMAIL_URL = os.getenv("EMAIL_URL", "http://127.0.0.1:8003/")


TRANSACTION_URL = os.getenv("TRANSACTION_URL", "http://127.0.0.1:8000/")

BANKING_URL = os.getenv("BANKING_URL", "http://127.0.0.1:8001/")

#OTP Config 
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", 5))
MAX_OTP_ATTEMPTS = int(os.getenv("MAX_OTP_ATTEMPTS", 5))