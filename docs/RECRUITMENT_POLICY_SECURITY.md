# AUTONOM Recruitment Policy Security

## Stage 25 of 50 — Security Safeguards & Integrity

---

### Security Boundaries

1. **Authentication & Role-Based Access Control**:
   - Every recruitment policy endpoint requires an authenticated session (`AuthDep`).
   - Unauthorized attempts return `401 Unauthorized` or `403 Forbidden`.
2. **Immutable Audit Hashes**:
   - Strategy edits compute a SHA-256 digest of the complete serialized strategy configuration:
     `snapshot_hash = hashlib.sha256(canonical_json(strategy)).hexdigest()`
   - Decisions log the active strategy hash at the exact time of decision execution, preventing retroactive dispute of historical automated decisions.
3. **Emergency Stop Hardware Invariant**:
   - If the Stage 14 Emergency Stop signal is received, the Policy Engine immediately evaluates all pending or incoming opportunities to `PROHIBITED_BY_POLICY` at Precedence Level 1.
4. **Zero-Hallucination Qualification Invariant**:
   - Profile claims cannot be synthesized or inferred by LLMs to satisfy job eligibility. Any claim missing verified provenance in the Stage 21 profile database returns `insufficient_evidence` or `ineligible`.
