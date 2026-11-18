"""Origin and URL validation for secure browser automation."""

import ipaddress
import logging
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

BLOCKED_SCHEMES = {
    "file",
    "ftp",
    "gopher",
    "javascript",
    "chrome",
    "edge",
    "about:config",
    "vbscript",
    "jar",
    "view-source",
}

CLOUD_METADATA_IPS = {
    "169.254.169.254",  # AWS, Azure, OpenStack, GCP
    "169.254.169.123",
    "100.100.100.200",  # Alibaba Cloud
}

CLOUD_METADATA_HOSTS = {
    "metadata.google.internal",
    "metadata.internal",
    "instance-data",
}

PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


@dataclass
class OriginSecurityResult:
    is_allowed: bool
    url: str
    normalized_url: str
    scheme: str
    host: str
    port: int | None
    is_loopback: bool
    is_private_ip: bool
    is_metadata_endpoint: bool
    risk_level: str  # low, medium, high, critical
    rejection_reason: str | None = None


class OriginValidator:
    """Validates URLs and origins against strict security policies."""

    def __init__(
        self,
        allow_loopback: bool = False,
        allow_private_ips: bool = False,
        allowed_domains: set[str] | None = None,
        blocked_domains: set[str] | None = None,
        test_mode: bool = False,
    ) -> None:
        self.allow_loopback = allow_loopback or test_mode
        self.allow_private_ips = allow_private_ips or test_mode
        self.allowed_domains = allowed_domains or set()
        self.blocked_domains = blocked_domains or set()
        self.test_mode = test_mode

    def validate_url(self, raw_url: str) -> OriginSecurityResult:
        """Evaluates whether a target URL is permitted for navigation or requests."""
        raw_url = raw_url.strip()
        if not raw_url:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url="",
                scheme="",
                host="",
                port=None,
                is_loopback=False,
                is_private_ip=False,
                is_metadata_endpoint=False,
                risk_level="critical",
                rejection_reason="Empty URL provided.",
            )

        # Handle about:blank specifically
        if raw_url.lower() == "about:blank":
            return OriginSecurityResult(
                is_allowed=True,
                url=raw_url,
                normalized_url="about:blank",
                scheme="about",
                host="blank",
                port=None,
                is_loopback=False,
                is_private_ip=False,
                is_metadata_endpoint=False,
                risk_level="low",
                rejection_reason=None,
            )

        # Allow data: URLs only in test mode if non-executable
        if raw_url.lower().startswith("data:"):
            if not self.test_mode:
                return OriginSecurityResult(
                    is_allowed=False,
                    url=raw_url[:50] + "...",
                    normalized_url="",
                    scheme="data",
                    host="",
                    port=None,
                    is_loopback=False,
                    is_private_ip=False,
                    is_metadata_endpoint=False,
                    risk_level="high",
                    rejection_reason="Data URLs are disabled in production for security.",
                )
            return OriginSecurityResult(
                is_allowed=True,
                url=raw_url[:50] + "...",
                normalized_url=raw_url,
                scheme="data",
                host="",
                port=None,
                is_loopback=False,
                is_private_ip=False,
                is_metadata_endpoint=False,
                risk_level="low",
                rejection_reason=None,
            )

        try:
            parsed = urlparse(raw_url)
        except Exception as exc:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url="",
                scheme="",
                host="",
                port=None,
                is_loopback=False,
                is_private_ip=False,
                is_metadata_endpoint=False,
                risk_level="critical",
                rejection_reason=f"Malformed URL: {exc}",
            )

        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
        port = parsed.port

        if scheme in BLOCKED_SCHEMES:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url=parsed.geturl(),
                scheme=scheme,
                host=host,
                port=port,
                is_loopback=False,
                is_private_ip=False,
                is_metadata_endpoint=False,
                risk_level="critical",
                rejection_reason=f"Blocked scheme: '{scheme}' is prohibited.",
            )

        if scheme not in ("http", "https"):
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url=parsed.geturl(),
                scheme=scheme,
                host=host,
                port=port,
                is_loopback=False,
                is_private_ip=False,
                is_metadata_endpoint=False,
                risk_level="high",
                rejection_reason=f"Unsupported scheme: '{scheme}'. Only HTTP and HTTPS are permitted.",
            )

        if not host:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url=parsed.geturl(),
                scheme=scheme,
                host="",
                port=port,
                is_loopback=False,
                is_private_ip=False,
                is_metadata_endpoint=False,
                risk_level="high",
                rejection_reason="No hostname found in URL.",
            )

        # Check metadata hostnames
        if host in CLOUD_METADATA_HOSTS:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url=parsed.geturl(),
                scheme=scheme,
                host=host,
                port=port,
                is_loopback=False,
                is_private_ip=True,
                is_metadata_endpoint=True,
                risk_level="critical",
                rejection_reason="Cloud instance metadata service access is strictly blocked.",
            )

        # Check explicit blocked domains
        for blocked in self.blocked_domains:
            if host == blocked or host.endswith(f".{blocked}"):
                return OriginSecurityResult(
                    is_allowed=False,
                    url=raw_url,
                    normalized_url=parsed.geturl(),
                    scheme=scheme,
                    host=host,
                    port=port,
                    is_loopback=False,
                    is_private_ip=False,
                    is_metadata_endpoint=False,
                    risk_level="high",
                    rejection_reason=f"Domain '{host}' is in the blocked domains list.",
                )

        # Check IP address or resolve host to check IP
        is_loopback = host in ("localhost", "127.0.0.1", "::1", "0.0.0.0")
        is_private_ip = False
        is_metadata = host in CLOUD_METADATA_IPS

        if is_metadata:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url=parsed.geturl(),
                scheme=scheme,
                host=host,
                port=port,
                is_loopback=is_loopback,
                is_private_ip=True,
                is_metadata_endpoint=True,
                risk_level="critical",
                rejection_reason="Access to cloud metadata IP is prohibited.",
            )

        # Try parsing as IP
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_loopback:
                is_loopback = True
            if ip.is_private or ip.is_reserved or ip.is_link_local:
                is_private_ip = True
            for net in PRIVATE_NETWORKS:
                if ip in net:
                    is_private_ip = True
                    break
        except ValueError:
            # It's a hostname, check if localhost
            if host == "localhost" or host.endswith(".localhost"):
                is_loopback = True

        if is_loopback and not self.allow_loopback:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url=parsed.geturl(),
                scheme=scheme,
                host=host,
                port=port,
                is_loopback=True,
                is_private_ip=is_private_ip,
                is_metadata_endpoint=False,
                risk_level="high",
                rejection_reason="Loopback navigation is blocked for safety. Enable test mode or whitelist localhost to override.",
            )

        if is_private_ip and not is_loopback and not self.allow_private_ips:
            return OriginSecurityResult(
                is_allowed=False,
                url=raw_url,
                normalized_url=parsed.geturl(),
                scheme=scheme,
                host=host,
                port=port,
                is_loopback=False,
                is_private_ip=True,
                is_metadata_endpoint=False,
                risk_level="high",
                rejection_reason="Access to private or RFC1918 internal networks is blocked.",
            )

        # If allowed domains list is provided and not empty, enforce it
        if self.allowed_domains:
            matched = any(host == d or host.endswith(f".{d}") for d in self.allowed_domains)
            if not matched and not (is_loopback and self.allow_loopback):
                return OriginSecurityResult(
                    is_allowed=False,
                    url=raw_url,
                    normalized_url=parsed.geturl(),
                    scheme=scheme,
                    host=host,
                    port=port,
                    is_loopback=is_loopback,
                    is_private_ip=is_private_ip,
                    is_metadata_endpoint=False,
                    risk_level="medium",
                    rejection_reason=f"Domain '{host}' is not in the allowed domains list.",
                )

        risk_level = "low"
        if scheme == "http":
            risk_level = "medium"  # Unencrypted HTTP

        return OriginSecurityResult(
            is_allowed=True,
            url=raw_url,
            normalized_url=parsed.geturl(),
            scheme=scheme,
            host=host,
            port=port,
            is_loopback=is_loopback,
            is_private_ip=is_private_ip,
            is_metadata_endpoint=False,
            risk_level=risk_level,
            rejection_reason=None,
        )
