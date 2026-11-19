# Job Discovery Security and SSRF Defense (Stage 26)

## Server-Side Request Forgery (SSRF) Prevention
Because AUTONOM accepts user-supplied URLs and crawls web career pages, strict SSRF defenses protect local services and cloud instances:

### 1. Scheme Enforcement
Only `http` and `https` protocols are permitted. `file://`, `ftp://`, `gopher://`, `data:`, and internal URI schemes are rejected before socket allocation.

### 2. Forbidden Hostnames and Subnets
Target hostnames and DNS-resolved IP addresses are validated against forbidden CIDR ranges:
- **Loopback**: `127.0.0.0/8`, `::1/128`, `localhost`
- **RFC 1918 Private**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- **Link-Local & Cloud Metadata**: `169.254.0.0/16`, `fe80::/10`, `metadata.google.internal`
- **Shared / NAT**: `100.64.0.0/10`

### 3. Redirect Re-Verification
HTTP redirects are NOT followed blindly (`follow_redirects=False`). On every HTTP 301, 302, 307, or 308 redirect, the `Location` target URL is extracted and independently subjected to SSRF validation before establishing a new connection.

## Content Sanitization & Prompt Injection Containment
External job postings represent untrusted user content that is later processed by LLM specialist agents.
1. **HTML Sanitization**: All `<script>`, `<style>`, `<iframe>`, `on*` event handlers, and `javascript:` URLs are stripped.
2. **Prompt Injection Disarming**: Phrases attempting to escape context (e.g. `ignore all previous instructions`, `system prompt override`, `bypass recruitment policy`) are detected and replaced with `[POTENTIAL_INJECTION_DEFUSED]`.
