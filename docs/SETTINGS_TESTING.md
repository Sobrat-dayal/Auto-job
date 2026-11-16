# AUTONOM — Settings & Operational Controls Test Suite & Verification Matrix

## 1. Overview & Quality Assurance Objectives

The test suite for **Stage 10 (Settings, Integration Configuration, Security Controls, and Operational Management)** establishes end-to-end verification across the entire desktop architecture:

1. **Backend Layer**: Pydantic v2 validation, atomic SQLite WAL persistence, reset fallbacks, and safe export/import.
2. **Frontend Layer**: Component rendering, two-pane navigation, dirty-state tracking, save/discard flows, confirmation modals, and truthful status attribution.
3. **Shared Type Contracts**: Strict synchronization between Python Pydantic models and TypeScript interfaces.
4. **Native Rust Layer**: Tauri IPC commands, window management, and native process supervisor safety.

---

## 2. Test Execution Commands & Verified Results

### 2.1 Backend Pytest Suite

```powershell
# Run settings API test suite specifically
services/api/.venv/Scripts/python.exe -m pytest services/api/tests/test_api_settings.py -v

# Run full backend test suite (all endpoints and repositories)
services/api/.venv/Scripts/python.exe -m pytest services/api/tests -v
```

**Results**:

- `test_api_settings.py`: **9 passed** in 0.52s.
- Total Backend Suite: **66 passed** in 5.51s (100% pass rate).
- Ruff Linter: Clean (`All checks passed!`).

### 2.2 Frontend Vitest & Testing Library Suite

```powershell
# Run settings workspace tests specifically
pnpm --filter @autonom/desktop test settings

# Run full desktop Vitest test suite
pnpm --filter @autonom/desktop test
```

**Results**:

- Settings test files:
  - `apps/desktop/src/test/features/settings-workspace.test.tsx`: **5 passed**
  - `apps/desktop/src/test/features/settings-categories.test.tsx`: **6 passed**
  - `apps/desktop/src/test/features/settings-export-import.test.tsx`: **3 passed**
- Total Frontend Suite: **29 test files, 104 passed** in 20.35s (100% pass rate).

### 2.3 Rust Native Host Suite

```powershell
# Run Cargo unit tests
cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml

# Run Cargo clippy linter
cargo clippy --manifest-path apps/desktop/src-tauri/Cargo.toml -- -D warnings
```

**Results**:

- Cargo test: **6 passed** in 0.96s.
- Cargo clippy: Clean (0 errors, 0 warnings).

### 2.4 Production Build & Type Verification

```powershell
# TypeScript contract check
pnpm --filter @autonom/shared-types typecheck
pnpm --filter @autonom/desktop typecheck

# Vite production bundle build
pnpm --filter @autonom/desktop build
```

**Results**:

- `shared-types` typecheck: Code 0.
- `desktop` typecheck: Code 0.
- Vite build: Completed in 2.65s (SettingsWorkspace chunk: 106.41 kB / gzip 24.80 kB).

---

## 3. Test Coverage Matrix

| Category / Area               | Test File                         | Test Cases                     | Scope Verified                                                                            |
| ----------------------------- | --------------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------- |
| **REST API: Read All**        | `test_api_settings.py`            | `test_get_all_settings`        | Returns all 13 categories with valid schemas and default values                           |
| **REST API: Category Read**   | `test_api_settings.py`            | `test_get_single_category`     | Retrieves isolated category with exact JSON structure                                     |
| **REST API: Category Update** | `test_api_settings.py`            | `test_patch_category_partial`  | Atomic partial PATCH merges updates without wiping existing fields                        |
| **REST API: Schema Meta**     | `test_api_settings.py`            | `test_get_settings_schema`     | Returns JSON Schema definition with restart flags & types                                 |
| **REST API: Reset Category**  | `test_api_settings.py`            | `test_reset_category`          | Restores default configuration values for a specific category                             |
| **REST API: Global Reset**    | `test_api_settings.py`            | `test_reset_all_settings`      | Restores default configuration across all 13 categories                                   |
| **REST API: Export Payload**  | `test_api_settings.py`            | `test_export_settings`         | Generates sanitised JSON export omitting DPAPI secrets                                    |
| **REST API: Valid Import**    | `test_api_settings.py`            | `test_import_settings_valid`   | Validates and restores imported settings bundle                                           |
| **REST API: Invalid Import**  | `test_api_settings.py`            | `test_import_settings_invalid` | Rejects corrupted or malformed payloads with 422 Unprocessable                            |
| **UI: Workspace Layout**      | `settings-workspace.test.tsx`     | 5 test cases                   | Two-pane layout, category navigation, search filtering, dirty badge indicator             |
| **UI: Category Pages**        | `settings-categories.test.tsx`    | 6 test cases                   | General, Appearance, AI Providers, Permissions, Storage, Diagnostics rendering & controls |
| **UI: Export / Import**       | `settings-export-import.test.tsx` | 3 test cases                   | Trigger export download, file upload import parsing, error banner on bad JSON             |

---

## 4. Key Verification Patterns & Fixes

### 4.1 Case-Insensitive Testing Library Matchers

In `settings-categories.test.tsx`, testing uppercase CSS text transforms requires case-insensitive regex matchers to ensure reliable DOM evaluation across testing environments:

```typescript
// Correct pattern:
expect(screen.getByText(/anthropic/i)).toBeInTheDocument();
```

### 4.2 Anchor Click Mocking in JSDOM

In `settings-export-import.test.tsx`, simulated JSON download links trigger `a.click()`. Because JSDOM does not implement native navigation, the click method was cleanly mocked:

```typescript
beforeEach(() => {
  HTMLAnchorElement.prototype.click = vi.fn();
});
```

### 4.3 Parallel CPU Contention Resiliency

When running all 29 test suites simultaneously in parallel worker threads, lazy-loaded route imports can take longer to settle. Vitest `waitFor` calls are configured with `{ timeout: 5000 }` to eliminate timing jitter.
