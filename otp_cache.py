#otp-cache.py
from datetime import datetime, timedelta
import random
import string
import threading
import time
from typing import Dict, Optional


class OTPCache:

    def __init__(self, ttl_seconds: int = 300, max_attempts: int = 5):
        self._cache: Dict[int, dict] = {}  
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds
        self._max_attempts = max_attempts
        self._cleanup_thread = None
        self._running = False
        self._start_cleanup_thread()
    
    # Start background thread for expired OTP clean up
    def _start_cleanup_thread(self):
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._running = True
            self._cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
            self._cleanup_thread.start()

    # Background task to remove expired OTP
    def _cleanup_expired(self):
        while self._running:
            try:
                time.sleep(30)  # Check every 30 sec
                current_time = datetime.now() 

                with self._lock:
                    expired_keys = [
                        tid for tid, data in self._cache.items()
                        if current_time > data['expired_at']
                    ]
                    
                    for tid in expired_keys:
                        del self._cache[tid]
                        print(f"[OTP Cache] Cleaned up expired OTP for transaction {tid}")
            
            except Exception as e:
                print(f"[OTP Cache] Cleanup Error: {e}")
    
    # Create Random 6 digit OTP
    def generate_otp(self) -> str:
        return ''.join(random.choices(string.digits, k=6))
    
    # Store OTP with expiration time
    def store_otp(self, transaction_id: int, otp_code: str, email: str) -> dict:
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=self._ttl_seconds)

            self._cache[transaction_id] = {
                'otp_code': otp_code,
                'email': email,
                'created_at': datetime.now(),
                'expired_at': expires_at,
                'attempts': 0,
                'verified': False
            }
            
            return {
                'expired_at': expires_at,
                'expires_in_seconds': self._ttl_seconds
            }
        
    # Retrieve OTP when exists and not expired yet
    def get_otp(self, transaction_id: int) -> Optional[dict]:
        with self._lock:
            if transaction_id not in self._cache:
                return None
            
            otp_data = self._cache[transaction_id]

            if datetime.now() > otp_data['expired_at']:
                del self._cache[transaction_id]
                return None
            
            return otp_data.copy()
        
    def verify_otp(self, transaction_id: int, otp_code: str) -> dict:
        with self._lock:
            if transaction_id not in self._cache:
                return {
                    'success': False,
                    'verified': False,
                    'message': 'OTP not found or expired'
                }
            
            otp_data = self._cache[transaction_id]

            # Check if expired
            if datetime.now() > otp_data['expired_at']:
                del self._cache[transaction_id]
                return {
                    'success': False,
                    'verified': False,
                    'message': 'OTP has expired'
                }
            
            # Check if verified already
            if otp_data['verified']:
                return {
                    'success': False,
                    'verified': False,
                    'message': 'OTP already used'
                }
            
            # Checking Attempts Count
            if otp_data['attempts'] >= self._max_attempts:
                del self._cache[transaction_id]
                return {
                    'success': False,
                    'verified': False,
                    'message': 'Maximum OTP attempts exceeded'
                }
            
            otp_data['attempts'] += 1

            # Verify OTP
            if otp_data['otp_code'] == otp_code:
                otp_data['verified'] = True
                otp_data['verified_at'] = datetime.now()
                return {
                    'success': True,
                    'verified': True,
                    'message': 'OTP verified successfully'
                }
            else:
                remaining = self._max_attempts - otp_data['attempts']
                return {
                    'success': False,
                    'verified': False,
                    'message': 'Invalid OTP code',
                    'remaining_attempts': remaining
                }
    
    def delete_otp(self, transaction_id: int) -> bool:
        with self._lock:
            if transaction_id in self._cache:
                del self._cache[transaction_id]
                return True
            return False
    
    def is_verified(self, transaction_id: int) -> bool:
        with self._lock:
            if transaction_id not in self._cache:
                return False
            return self._cache[transaction_id].get('verified', False)
        
    def get_remaining_time(self, transaction_id: int) -> Optional[int]:
        otp_data = self.get_otp(transaction_id)

        if not otp_data:
            return None
        
        remaining = (otp_data['expired_at'] - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def stop(self):
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)


# Global OTP cache instance 
otp_cache = OTPCache(ttl_seconds=300, max_attempts=5)