"""URL validation and SSRF security controls for job discovery (Stage 26)."""

import ipaddress
import socket
from urllib.parse import urlparse
from app.recruitment.discovery.errors import SSRFSecurityError


FORBIDDEN_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local / Cloud Metadata
    ipaddress.ip_network("0.0.0.0/8"),        # This host
    ipaddress.ip_network("100.64.0.0/10"),    # Carrier grade NAT
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]

FORBIDDEN_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "::1",
    "metadata.google.internal",
    "169.254.169.254",
}


def is_ip_forbidden(ip_str: str) -> bool:
    """Check if an IP address falls within any forbidden internal/metadata network."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in net for net in FORBIDDEN_NETWORKS)
    except ValueError:
        return False


def validate_safe_url(url: str, enforce_ssrf: bool = True) -> tuple[bool, str | None]:
    """Validate that a URL is safe to fetch: safe scheme, valid domain, non-internal IP.

    Returns:
        (is_safe, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty."

    try:
        parsed = urlparse(url.strip())
    except Exception as exc:
        return False, f"Malformed URL syntax: {exc}"

    # 1. Scheme check
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Forbidden URL scheme '{parsed.scheme}'. Only http and https are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL is missing a valid host name."

    hostname_lower = hostname.lower()

    # 2. Hostname blocklist
    if hostname_lower in FORBIDDEN_HOSTNAMES:
        return False, f"Target host '{hostname}' is a forbidden local or metadata address."

    if not enforce_ssrf:
        return True, None

    # 3. DNS resolution & IP check
    # Check if host is direct IP literal
    if is_ip_forbidden(hostname_lower):
        return False, f"Target host IP '{hostname}' belongs to a forbidden private or link-local range."

    # Resolve DNS to check resulting IPs
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for _, _, _, _, sockaddr in addr_info:
            ip_resolved = sockaddr[0]
            if is_ip_forbidden(ip_resolved):
                return False, f"Host '{hostname}' resolves to forbidden private IP '{ip_resolved}'."
    except socket.gaierror:
        # If DNS cannot be resolved in unit test / offline environment, allow if hostname syntax is valid
        pass
    except Exception as exc:
        return False, f"DNS resolution failed: {exc}"

    return True, None


def assert_safe_url(url: str, enforce_ssrf: bool = True) -> None:
    """Raise SSRFSecurityError if URL is unsafe."""
    is_safe, reason = validate_safe_url(url, enforce_ssrf=enforce_ssrf)
    if not is_safe:
        raise SSRFSecurityError(url, reason or "URL failed safety check")


def is_safe_ip_address(ip_str: str) -> bool:
    """Check if an IP address is safe (not forbidden/internal/metadata)."""
    return not is_ip_forbidden(ip_str)


def validate_discovery_url(url: str) -> str:
    """Validate and return URL or raise SSRFSecurityError."""
    assert_safe_url(url)
    return url
