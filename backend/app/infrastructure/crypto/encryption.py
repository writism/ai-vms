import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _derive_key(raw_key: str) -> bytes:
    return hashlib.sha256(raw_key.encode()).digest()


def encrypt(plaintext: str, raw_key: str) -> str:
    """AES-256-GCM 암호화. 반환: base64(nonce + ciphertext)"""
    key = _derive_key(raw_key)
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt(token: str, raw_key: str) -> str:
    """AES-256-GCM 복호화."""
    key = _derive_key(raw_key)
    raw = base64.b64decode(token)
    nonce, ct = raw[:12], raw[12:]
    return AESGCM(key).decrypt(nonce, ct, None).decode()


def is_encrypted(value: str) -> bool:
    """암호화 토큰 여부 추정 (base64 + 길이 기반)."""
    try:
        decoded = base64.b64decode(value)
        return len(decoded) > 12
    except Exception:
        return False
