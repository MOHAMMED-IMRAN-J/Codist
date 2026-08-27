import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

def get_fernet_key():
    # Derive a 32-byte url-safe base64-encoded key from the Django SECRET_KEY
    return base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())

def get_cipher():
    return Fernet(get_fernet_key())

def encrypt_message(text: str) -> str:
    if not text:
        return text
    cipher = get_cipher()
    return cipher.encrypt(text.encode('utf-8')).decode('utf-8')

def decrypt_message(encrypted_text: str) -> str:
    if not encrypted_text:
        return encrypted_text
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
    except Exception:
        return "Decryption failed."
