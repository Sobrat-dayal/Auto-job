# Recruitment Monitoring Security & Privacy Safeguards (Stage 30)

## 1. Safety Boundaries Enforced
Stage 30 adheres strictly to AUTONOM's core security guidelines:
1. **Zero Automated Submissions**:
   - No HTTP POST requests are ever dispatched to external application submission forms.
   - Applications are never submitted without explicit user oversight and confirmation (reserved for Stage 31+).
2. **Zero Recruiter Outreach**:
   - No unsolicited emails, direct messages, or connection requests are sent.
3. **Zero CAPTCHA Bypass or Anti-Bot Evasion**:
   - No browser fingerprint spoofing, proxy cycling, or anti-bot challenge solvers.
   - Respects all robots.txt, terms of service, and official API guidelines.
4. **Emergency Stop Precedence**:
   - Both `is_emergency_stop_active` and `is_automation_paused` block all background runs instantaneously with `EmergencyStopActiveError`.
5. **Local Authentication**:
   - All REST API endpoints enforce Bearer API token validation.
6. **Notification Privacy Protection**:
   - Hides sensitive salary and employer data from desktop toasts in public or screen-sharing environments.
