# AUTONOM — Resume Versioning & Immutability (Stage 23)

## 1. Cryptographic Version Lifecycle

Job applications require strict auditability. When an applicant submits a resume to an employer, they must be able to view the exact, unalterable document snapshot that was transmitted.

AUTONOM implements an immutable versioning system governed by `ResumeVersionManager`:

```
+-------------------------------------------------------------+
|               Resume Draft (DocumentStatus.DRAFT)           |
|  - Freely editable sections, entries, and bullets           |
|  - Dynamic reordering and live template switching          |
+-------------------------------------------------------------+
                              |
                     Approve Resume Request
                              |
                              v
+-------------------------------------------------------------+
|           Version Approval & Snapshot Freezing              |
|  1. Status transitions to DocumentStatus.APPROVED           |
|  2. Canonical SHA-256 digest computed on serialized payload |
|  3. Immutable ResumeVersionRecord written to storage        |
|  4. Export artifacts bound to version record                |
+-------------------------------------------------------------+
                              |
                 Subsequent Edit Attempt
                              |
                              v
+-------------------------------------------------------------+
|                Draft Forking / Revisioning                  |
|  - Increments version counter (e.g. v1 -> v2)               |
|  - Creates fresh mutable draft copy                         |
|  - Historical version v1 remains permanently immutable     |
+-------------------------------------------------------------+
```

---

## 2. Immutability Guarantee

```python
class ResumeVersionRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"ver_{uuid4().hex[:8]}")
    resume_id: str
    version_number: int
    profile_snapshot_id: str
    job_ref: Optional[str] = None
    template_id: str
    template_version: str = "1.0.0"
    content_hash: str
    changelog: str
    created_at: datetime
    actor_id: str
    is_published: bool = True
    document_snapshot: dict[str, Any]
    export_artifact_ids: list[str] = Field(default_factory=list)
```

The `content_hash` is computed using standard SHA-256 over normalized JSON:
```python
def compute_content_hash(doc: ResumeDocument) -> str:
    raw = doc.model_dump_json(exclude={"content_hash", "updated_at"})
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

If any bit of the document snapshot changes, the checksum fails verification, guaranteeing uncorrupted audit history.
