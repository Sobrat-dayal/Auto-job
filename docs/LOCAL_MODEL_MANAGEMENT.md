# AUTONOM — Local Model & Hardware Optimization (Stage 11)

## 1. Target Hardware Specifications

- **Target Operating System**: Windows 11 Home / Pro (x64)
- **Target GPU**: NVIDIA GeForce RTX 4050 Laptop GPU (6,144 MB / 6.0 GB GDDR6 VRAM)
- **Target System RAM**: 16.0 GB DDR5
- **Local Model Runtime**: Ollama (Windows native binary, default port 11434)

---

## 2. Strict Hardware Guardrails

### A. Single Active Local Model in VRAM
To avoid GPU Out-Of-Memory (OOM) fatal crashes and Windows Desktop Window Manager (DWM) freezes on laptop hardware:
- **Strict Single-Model Policy**: Only **one language model** is permitted in VRAM at any time.
- **Model Switching Orchestration**: Before loading a new model `B`, the resource controller explicitly unloads model `A` via `POST /api/chat` with `{"model": "A", "keep_alive": 0}`.
- **Local Concurrency Semaphore**: Local inference concurrency is strictly gated by an `asyncio.Semaphore(1)` to prevent concurrent token generation requests from corrupting GPU memory buffers.

### B. VRAM Allocation Ceiling (5,120 MB / 5.0 GB)
Of the 6,144 MB total VRAM:
- **1,024 MB Reserved**: Kept free for Windows OS, WebView2 desktop rendering, and display drivers.
- **5,120 MB Usable Budget**: Maximum allocation for model weights and KV-cache.
- **Supported Quantizations**:
  - `3B` models (Q4_K_M): ~1.8 – 2.2 GB VRAM (Safe headroom: >3.5 GB free).
  - `7B / 8B` models (Q4_K_M): ~4.2 – 4.8 GB VRAM (Fits entirely within 5.0 GB budget).
  - `14B+` models: Prohibited from full GPU offloading to prevent paging into system RAM.

---

## 3. NVML Real-Time Telemetry

The resource monitor queries GPU status directly via the NVIDIA Management Library (`pynvml` / `nvidia-ml-py`):

```python
# Direct NVML Hardware Probe
nvmlInit()
handle = nvmlDeviceGetHandleByIndex(0)
mem_info = nvmlDeviceGetMemoryInfo(handle)
vram_total_mb = mem_info.total // (1024 * 1024)      # 6141 MB
vram_used_mb = mem_info.used // (1024 * 1024)        # Exact used VRAM
vram_free_mb = mem_info.free // (1024 * 1024)        # Exact free VRAM
```

Host RAM is monitored concurrently using `psutil.virtual_memory()`. If NVML is unavailable (e.g. running on non-NVIDIA test machines or virtualized containers), the telemetry engine falls back gracefully to system RAM metrics without crashing.
