# AUTONOM Memory Consolidation & Procedural Extraction (Stage 15)

## 1. Deduplication

The Memory Engine prevents storage bloat through a two-stage deduplication pipeline:
1. **Normalized Content Hash**: SHA-256 hash computed over lowercased, whitespace-collapsed text. If an exact match is detected in the same scope, the existing record's `last_accessed_at` timestamp is updated and returned without creating duplicate database rows.
2. **Near-Duplicate Vector Scans**: Detects candidate records with cosine similarity $\ge 0.95$ within the same scope.

---

## 2. Contradiction Detection & Supersession

When a user updates a preference or an agent discovers conflicting information:
1. The `ConflictResolver` identifies overlapping topics with differing factual assertions.
2. A `MemoryConflictRecord` is persisted in `memory_conflicts` for review.
3. Upon resolution (manual or policy-driven), the older record is transitioned to `superseded` and its `superseded_by` pointer is linked to the newer authoritative memory.
4. Superseded records are omitted from future active search results by default, ensuring outdated facts are never presented as current truth.

---

## 3. Procedural Experience Extraction

When a multi-step workflow completes successfully with verified output artifacts:
1. The `MemoryConsolidator` inspects the DAG step execution graph.
2. It strips ephemeral variables and sanitizes parameters into parameterized step templates.
3. It registers a `ProceduralMemoryRecord` declaring capability bindings, required inputs, and required permissions.
4. Future planning agents retrieve this validated procedure to guide execution.
