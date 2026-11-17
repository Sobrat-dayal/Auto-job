# AUTONOM Vector Storage (Stage 15)

## 1. Storage Architecture

AUTONOM balances reliability and speed using a dual-tier vector storage approach tailored for desktop Windows x64 deployments:

1. **Persistent SQLite Storage (`memory_embeddings`)**:
   - Stores raw float vectors in `vector_json` alongside model ID, dimension, and checksum.
   - Tied via foreign key to `memory_records.id`.
   - Survives backend restarts and application reloads.
2. **In-Memory Normalized Cosine Index (`VectorStore`)**:
   - Warmed up on backend launch via `ServiceContainer.initialize()`.
   - Executes vector similarity search in microseconds using vectorized dot-product arithmetic.
   - Enforces strict dimension validation (e.g. 384 dimensions) and scope isolation filtering.
   - Excludes soft-deleted or superseded records dynamically.

---

## 2. Windows Desktop Compatibility

Unlike native external vector databases (such as Chroma, Qdrant, or custom C++ SQLite extensions) which often fail or corrupt inside packaged Tauri Windows applications due to DLL loading issues:
- AUTONOM's vector store is 100% self-contained in pure Python and SQLite.
- Fully portable across Windows 11 desktop sidecars and headless servers without external daemon dependencies.
