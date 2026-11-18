# Stage 19: Hardware & Resource-Conscious Computer Interaction

## 1. Resource Consumption Hierarchy

Operating multi-modal automation on Windows requires balancing speed, CPU, GPU, memory, and physical user disruption:

| Interaction Method | Average Latency | CPU Usage | GPU Usage | Memory Impact | Physical Disruption |
|---|---|---|---|---|---|
| **`BROWSER_DOM`** | 10 – 35 ms | Very Low (< 1%) | Zero | Minimal (DOM nodes) | Zero (Runs in background) |
| **`WINDOWS_UIA`** | 15 – 50 ms | Low (< 2%) | Zero | Minimal (COM pointers) | Zero for ValuePattern; Low for clicks |
| **`WINDOWS_WIN32`** | 5 – 20 ms | Negligible (< 0.5%)| Zero | Negligible (Win32 messages)| Low |
| **`VISUAL_GROUNDING`**| 120 – 450 ms | Moderate (5–12%)| High (OCR/VLM inference)| High (Frame buffers) | High (Moves system cursor & steals focus) |

---

## 2. Resource-Aware Routing Strategy

1. **Structural-First Default:**
   - The engine automatically routes to `BROWSER_DOM` or `WINDOWS_UIA` whenever targets are structural.
   - Heavy visual inference (MSS screen capture, WinRT OCR, coordinate grounding) is deferred unless the application is custom-rendered (e.g. Canvas/DirectX) or structural methods have failed.

2. **Input Ownership Lease Coordination:**
   - Physical input methods (`SendInput` via `VISUAL_GROUNDING` or `WINDOWS_WIN32`) require acquiring an exclusive lease from `HybridInputOwnershipCoordinator`.
   - The lease prevents multiple agents from fighting over the mouse cursor or interleaving keystrokes.
   - Non-intrusive operations (`BROWSER_DOM` fill or `WINDOWS_UIA` ValuePattern) bypass the lease and execute concurrently.

3. **Adapter Health Tracking & Backoff:**
   - `MethodHealthTracker` tracks rolling success rates and latency averages.
   - Adapters exhibiting consecutive timeouts or exceptions have their routing confidence decayed, steering subsequent tasks to healthier alternatives.
