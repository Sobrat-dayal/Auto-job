# Multi-Agent Orchestration Security & Governance (Stage 12)

## 1. Overview

Autonomous multi-agent workflows possess significant power to execute actions, compile documents, and call external services. Stage 12 establishes rigorous security barriers to ensure complete user sovereignty, zero unauthorized execution, and memory safety.

---

## 2. Security Foundations

1. **Loopback Isolation**: The backend binds exclusively to `127.0.0.1`, rejecting external network connections.
2. **Correlation IDs**: Every workflow and step execution carries an explicit `correlation_id` tracked across ASGI requests, logs, and database records.
3. **Cryptographic Protection**: Sensitive candidate credentials, API keys, and private contact profiles remain encrypted via the Stage 01 DPAPI-backed Vault.

---

## 3. Human-in-the-Loop Authorization Gates

Steps marked with `requires_authorization = True` trigger the `WAITING_FOR_AUTHORIZATION` workflow state:
- Automated submission of job applications.
- Financial transactions or paid recruitment postings.
- Modifications to persistent operating system files or registry keys.
- Sending external communications to recruiters.

Execution halts until explicit approval is granted via the desktop UI.

---

## 4. Hardware Safety (RTX 4050 6GB Laptop GPU)

To safeguard consumer laptop hardware:
- A concurrency semaphore (`_llm_semaphore = asyncio.Semaphore(1)`) strictly restricts local GPU inference to **one model in VRAM at a time**.
- Thermal and VRAM exhaustion checks guard against thrashing or memory fragmentation.
- Timeout deadlines (`timeout_seconds`) prevent runaways or infinite loops from consuming resources.
