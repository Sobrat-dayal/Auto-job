"""Windows process and executable identity validation (Stage 17)."""

import ctypes
from ctypes import wintypes
import logging
import os
import psutil

logger = logging.getLogger("autonom.computer.windows.identity")

advapi32 = ctypes.windll.advapi32
kernel32 = ctypes.windll.kernel32


class ProcessIdentityValidator:
    """Validates Windows executable identity, integrity level, and authorization attributes."""

    @staticmethod
    def get_process_executable_path(pid: int) -> str:
        """Retrieves verified absolute executable path for a process."""
        try:
            p = psutil.Process(pid)
            return p.exe()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return ""

    @staticmethod
    def get_process_integrity_level(pid: int) -> str:
        """Determines the Windows token integrity level of a process (low, medium, high, system)."""
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        TOKEN_QUERY = 0x0008

        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_process:
            return "medium"

        h_token = wintypes.HANDLE()
        try:
            if not advapi32.OpenProcessToken(h_process, TOKEN_QUERY, ctypes.byref(h_token)):
                return "medium"

            # TokenIntegrityLevel is 25 in TOKEN_INFORMATION_CLASS enum
            TOKEN_INTEGRITY_LEVEL = 25
            length = wintypes.DWORD()
            advapi32.GetTokenInformation(h_token, TOKEN_INTEGRITY_LEVEL, None, 0, ctypes.byref(length))

            if length.value == 0:
                return "medium"

            buffer = ctypes.create_string_buffer(length.value)
            if not advapi32.GetTokenInformation(h_token, TOKEN_INTEGRITY_LEVEL, buffer, length.value, ctypes.byref(length)):
                return "medium"

            # TOKEN_MANDATORY_LABEL contains SID_AND_ATTRIBUTES
            # The subauthority rid determines the integrity level:
            # 0x1000: Low, 0x2000: Medium, 0x3000: High, 0x4000: System
            p_sid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p)).contents.value
            if p_sid:
                get_sid_subauthority_count = advapi32.GetSidSubAuthorityCount
                get_sid_subauthority_count.restype = ctypes.POINTER(ctypes.c_ubyte)
                count_p = get_sid_subauthority_count(p_sid)
                if count_p:
                    count = count_p.contents.value
                    get_sid_subauthority = advapi32.GetSidSubAuthority
                    get_sid_subauthority.restype = ctypes.POINTER(ctypes.c_ulong)
                    rid_p = get_sid_subauthority(p_sid, count - 1)
                    if rid_p:
                        rid = rid_p.contents.value
                        if rid < 0x2000:
                            return "low"
                        elif rid < 0x3000:
                            return "medium"
                        elif rid < 0x4000:
                            return "high"
                        else:
                            return "system"
        except Exception as e:
            logger.debug(f"Integrity check exception for PID {pid}: {e}")
        finally:
            if h_token.value:
                kernel32.CloseHandle(h_token)
            if h_process:
                kernel32.CloseHandle(h_process)

        return "medium"

    @staticmethod
    def is_elevated_process(pid: int) -> bool:
        """Returns True if the process runs with High or System integrity."""
        return ProcessIdentityValidator.get_process_integrity_level(pid) in ("high", "system")


process_identity_validator = ProcessIdentityValidator()
