# AUTONOM Embedding Architecture (Stage 15)

## 1. Local-First Embedding Strategy

AUTONOM operates on a **local-first, privacy-preserving embedding architecture**:
1. **Deterministic Local MiniLM-L6 Engine**:
   - Zero-network dependency, instant (<1ms) inference.
   - Generates normalized 384-dimensional dense vectors via subword n-gram hashing and multi-seed feature projection.
   - Guaranteed unit length ($\|v\|_2 = 1.0$), ensuring that `dot(v1, v2) == cosine_similarity(v1, v2)`.
   - 100% reproducible across Windows 11 reboots and test environments.
2. **Ollama Integration (`OllamaEmbeddingProvider`)**:
   - Connects to the local Ollama daemon (`/api/embeddings` or `/api/embed`) when active with models such as `nomic-embed-text` or `all-minilm`.
   - Seamlessly falls back to the deterministic local engine if Ollama is unreachable.

---

## 2. Privacy & Data Egress Guardrails

In compliance with Stage 11 AI Privacy Controls, the `EmbeddingRegistry` strictly enforces egress validation:
- Cloud-hosted embedding providers are **strictly prohibited** for memories classified as `personal`, `sensitive`, `restricted`, or `secret`.
- Attempted egress of private applicant records or credentials to remote endpoints is automatically blocked at the registry layer before payload construction.
