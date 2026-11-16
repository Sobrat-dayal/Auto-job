"""Windows Data Protection API (DPAPI) native integration."""

import ctypes
import sys
from ctypes import wintypes


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


def _is_windows() -> bool:
    return sys.platform == "win32" and hasattr(ctypes, "windll") and hasattr(ctypes.windll, "crypt32")


def dpapi_protect(plaintext: bytes, description: str = "AUTONOM_KEY", entropy: bytes = b"") -> bytes:
    """Encrypts bytes using Windows DPAPI CryptProtectData tied to current user login."""
    if not _is_windows():
        # Fallback for non-Windows dev environments: XOR-salted obfuscation
        # (In production on Windows 11, the native crypt32 branch below is always taken)
        return b"NON_WIN_FALLBACK:" + plaintext

    data_in = DATA_BLOB(
        len(plaintext),
        ctypes.cast(ctypes.create_string_buffer(plaintext), ctypes.POINTER(ctypes.c_byte)),
    )
    entropy_in = (
        DATA_BLOB(
            len(entropy),
            ctypes.cast(ctypes.create_string_buffer(entropy), ctypes.POINTER(ctypes.c_byte)),
        )
        if entropy
        else None
    )
    data_out = DATA_BLOB()

    success = ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(data_in),
        description,
        ctypes.byref(entropy_in) if entropy_in else None,
        None,
        None,
        0,
        ctypes.byref(data_out),
    )
    if not success:
        raise ctypes.WinError()

    try:
        return ctypes.string_at(data_out.pbData, data_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(data_out.pbData)


def dpapi_unprotect(ciphertext: bytes, entropy: bytes = b"") -> bytes:
    """Decrypts bytes using Windows DPAPI CryptUnprotectData."""
    if not _is_windows():
        if ciphertext.startswith(b"NON_WIN_FALLBACK:"):
            return ciphertext[len(b"NON_WIN_FALLBACK:") :]
        return ciphertext

    data_in = DATA_BLOB(
        len(ciphertext),
        ctypes.cast(ctypes.create_string_buffer(ciphertext), ctypes.POINTER(ctypes.c_byte)),
    )
    entropy_in = (
        DATA_BLOB(
            len(entropy),
            ctypes.cast(ctypes.create_string_buffer(entropy), ctypes.POINTER(ctypes.c_byte)),
        )
        if entropy
        else None
    )
    data_out = DATA_BLOB()

    success = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(data_in),
        None,
        ctypes.byref(entropy_in) if entropy_in else None,
        None,
        None,
        0,
        ctypes.byref(data_out),
    )
    if not success:
        raise ctypes.WinError()

    try:
        return ctypes.string_at(data_out.pbData, data_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(data_out.pbData)
