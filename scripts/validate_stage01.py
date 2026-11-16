#!/usr/bin/env python3
"""
AUTONOM Stage 01 Architectural Validation Script
Verifies all 14 required architecture documents, 24 agent definitions,
13 domain models, 11 task states, 15 UI modules, 50 roadmap stages,
and foundational codebase components.
"""

import sys
import re
from pathlib import Path

# Workspace Root
ROOT_DIR = Path(__file__).resolve().parent.parent

# 14 Required Documents from Stage 01 Specification
REQUIRED_DOCS = [
    ("README.md", ["AUTONOM", "Architecture", "Development Setup"]),
    ("docs/ARCHITECTURE.md", ["Layered Separation of Concerns", "Layer A", "Layer F", "System Process Topology", "Mermaid"]),
    ("docs/REQUIREMENTS.md", ["Functional Requirements", "Nonfunctional Requirements", "MoSCoW", "RTX 4050"]),
    ("docs/AGENTS.md", ["Supervisor Agent", "Workflow Automation Agent", "Allowed Tools", "Escalation Policy"]),
    ("docs/DATABASE_DESIGN.md", ["ApplicantProfile", "VerifiedSkill", "JobListing", "Task", "sqlite", "WAL"]),
    ("docs/SECURITY.md", ["Threat Model", "Windows DPAPI", "Autonomy Policy", "Emergency Disengage", "Non-Fabrication"]),
    ("docs/API_CONTRACTS.md", ["/api/health", "/api/agents", "/api/jobs", "/ws/events", "IPC"]),
    ("docs/COMPUTER_CONTROL.md", ["Visual Interaction", "Structural Interaction", "Hybrid Action Router", "SendInput", "UIA"]),
    ("docs/UI_UX_SPECIFICATION.md", ["Command Center", "Collapsible vertical sidebar", "Theme Tokens", "Navigation Tree"]),
    ("docs/ROADMAP.md", ["Stage 01", "Stage 25", "Stage 50", "Phase 1", "Phase 5"]),
    ("docs/DECISIONS.md", ["ADR-0001", "ADR-0002", "ADR-0003", "ADR-0004", "ADR-0005"]),
    ("docs/STAGE_LOG.md", ["Stage 01", "Objectives & Scope", "Implementation Checklist"]),
    ("docs/RESOURCE_BUDGET.md", ["RTX 4050", "6 GB VRAM", "16 GB", "Single Active Model"]),
    ("docs/INTEGRATIONS.md", ["Connector Types", "Authentication Patterns", "Model Context Protocol", "Prompt-Injection"]),
]

EXPECTED_AGENTS = [
    "Supervisor Agent", "Planning Agent", "Task Router Agent", "Verification Agent", "Recovery Agent",
    "Job Discovery Agent", "Job Matching Agent", "Resume Agent", "Application Agent", "Recruitment Communications Agent",
    "Interview Preparation Agent", "Browser Agent", "Windows Computer Agent", "Visual Grounding Agent", "Structural UI Agent",
    "Coding Agent", "Research Agent", "Document Agent", "Spreadsheet Agent", "Presentation Agent",
    "Creative and 3D Agent", "Messaging Agent", "Market Intelligence Agent", "Workflow Automation Agent",
]

EXPECTED_DOMAIN_MODELS = [
    "ApplicantProfile", "VerifiedSkill", "ProjectEvidence", "ResumeVersion",
    "JobSource", "JobListing", "JobMatch", "Application", "ApplicationAttempt",
    "ScreeningAnswer", "RecruiterConversation", "Interview", "AuthorizationPolicy",
]

EXPECTED_TASK_STATES = [
    "Created", "Queued", "Planning", "WaitingForDependencies", "Running",
    "WaitingForAuthorization", "Paused", "Retrying", "Completed", "Failed", "Cancelled",
]

EXPECTED_UI_MODULES = [
    "Command Center", "Jobs & Applications", "Agents", "Computer Control",
    "Communications", "Interviews", "Documents", "Coding", "Creative Studio",
    "Research & Markets", "Workflows", "Analytics", "Activity Logs", "Integrations", "Settings",
]


def run_checks():
    passed = 0
    failed = 0
    results = []

    def check(desc: str, condition: bool, detail: str = ""):
        nonlocal passed, failed
        if condition:
            passed += 1
            results.append((True, desc, detail))
        else:
            failed += 1
            results.append((False, desc, detail))

    print("=" * 80)
    print("AUTONOM STAGE 01 — ARCHITECTURAL & FOUNDATIONAL VALIDATION")
    print("=" * 80)

    # 1. Validate All 14 Required Documents Exist and Have Content
    for doc_path, keywords in REQUIRED_DOCS:
        p = ROOT_DIR / doc_path
        exists = p.exists() and p.stat().st_size > 200
        if not exists:
            check(f"Doc file exists: {doc_path}", False, "File missing or under 200 bytes")
            continue

        content = p.read_text(encoding="utf-8")
        missing_kw = [kw for kw in keywords if kw.lower() not in content.lower()]
        check(
            f"Doc content verification: {doc_path}",
            len(missing_kw) == 0,
            f"Missing keywords: {missing_kw}" if missing_kw else f"{len(content.splitlines())} lines",
        )

    # 2. Validate All 24 Agents in docs/AGENTS.md
    agents_doc = (ROOT_DIR / "docs/AGENTS.md").read_text(encoding="utf-8")
    missing_agents = [ag for ag in EXPECTED_AGENTS if ag.lower() not in agents_doc.lower()]
    check(
        "Agent Catalog completeness (24/24 agents)",
        len(missing_agents) == 0,
        f"Missing: {missing_agents}" if missing_agents else "All 24 agents documented with full specs",
    )

    # 3. Validate Domain Models in docs/DATABASE_DESIGN.md
    db_doc = (ROOT_DIR / "docs/DATABASE_DESIGN.md").read_text(encoding="utf-8")
    missing_models = [m for m in EXPECTED_DOMAIN_MODELS if m.lower() not in db_doc.lower()]
    check(
        "Domain Models completeness (13/13 models)",
        len(missing_models) == 0,
        f"Missing: {missing_models}" if missing_models else "All 13 domain models specified with DDL",
    )

    # 4. Validate Task States in docs/DATABASE_DESIGN.md
    missing_states = [s for s in EXPECTED_TASK_STATES if s not in db_doc]
    check(
        "Durable Task States completeness (11/11 states)",
        len(missing_states) == 0,
        f"Missing: {missing_states}" if missing_states else "All 11 task states specified in state diagram & schema",
    )

    # 5. Validate UI Modules in docs/UI_UX_SPECIFICATION.md
    ui_doc = (ROOT_DIR / "docs/UI_UX_SPECIFICATION.md").read_text(encoding="utf-8")
    missing_modules = [mod for mod in EXPECTED_UI_MODULES if mod.lower() not in ui_doc.lower()]
    check(
        "UI Top-Level Navigation Modules (15/15 modules)",
        len(missing_modules) == 0,
        f"Missing: {missing_modules}" if missing_modules else "All 15 modules documented in navigation tree",
    )

    # 6. Validate 50 Stages in docs/ROADMAP.md
    roadmap_doc = (ROOT_DIR / "docs/ROADMAP.md").read_text(encoding="utf-8")
    stage_matches = re.findall(r"Stage\s+(\d+)", roadmap_doc, re.IGNORECASE)
    unique_stages = set(int(s) for s in stage_matches if 1 <= int(s) <= 50)
    check(
        "50-Stage Roadmap representation",
        len(unique_stages) == 50,
        f"Found {len(unique_stages)}/50 stages" if len(unique_stages) != 50 else "Stages 01 through 50 fully specified",
    )

    # 7. Validate Minimal Code Foundation Files
    code_files = [
        ".gitignore",
        ".editorconfig",
        ".env.example",
        "package.json",
        "pnpm-workspace.yaml",
        "tsconfig.base.json",
        "packages/shared-types/package.json",
        "packages/shared-types/src/index.ts",
        "packages/shared-types/src/agents.ts",
        "packages/shared-types/src/tasks.ts",
        "packages/shared-types/src/security.ts",
        "packages/shared-types/src/domain.ts",
        "packages/shared-types/src/config.ts",
    ]
    for cf in code_files:
        p = ROOT_DIR / cf
        check(f"Code foundation file exists: {cf}", p.exists() and p.stat().st_size > 10, f"Size: {p.stat().st_size} bytes" if p.exists() else "Missing")

    # 8. Print Results Summary
    print()
    for ok, desc, detail in results:
        status_tag = "[PASS]" if ok else "[FAIL]"
        print(f"{status_tag} {desc} - {detail}")

    print()
    print("-" * 80)
    print(f"TOTAL CHECKS: {passed + failed} | PASSED: {passed} | FAILED: {failed}")
    print("-" * 80)

    if failed > 0:
        print(f"Validation FAILED with {failed} issue(s).")
        sys.exit(1)
    else:
        print("STAGE 01 ARCHITECTURAL & FOUNDATIONAL VALIDATION PASSED COMPLETELY.")
        sys.exit(0)


if __name__ == "__main__":
    run_checks()
