# Archive: Development Artifacts

## Why Archived

These files were generated during the active development and testing of the **Corporate Whistleblower Lite** project. They are not part of the production application and have been moved here to keep the repository root clean and focused on deliverable code.

## Contents

| File/Folder | Description | Date |
|-------------|-------------|------|
| `.playwright-mcp/` | Playwright browser automation snapshots and session data captured during GitHub page verification | 2026-08-26 |
| `final-check.png` | Screenshot of the live GitHub repository taken for visual verification before publication | 2026-08-26 |

## Project Context

**Corporate Whistleblower Lite** is an open-source, self-hosted whistleblowing platform built for internal audit and compliance teams. It enables anonymous reporting, file uploads, role-based dashboards (Internal Audit & CEO), and audit trails — deployable in minutes on a single server.

### Original Development Scope

The project was initially developed using a **dual-AI-framework architecture**:
- **LangGraph** as the main builder
- **CrewAI** as the external reviewer

Both frameworks used `kimi-k2.6` via the Ollama Cloud API. The development process involved:
1. LangGraph agents generating application code
2. CrewAI agents reviewing for security, quality, and compliance
3. Feedback incorporation into the main codebase
4. Security audit passes (all CRITICAL/HIGH issues fixed)

### KSA Origins → Global Applicability

The project originated from a request to build a whistleblowing platform for a **KSA (Saudi Arabia) real estate company**. During the security and compliance review, KSA-specific references were identified and subsequently removed to make the tool globally applicable for any organization.

### Post-Development: AuditMind Brainstorm

After completing the whistleblower project, the discussion evolved toward a more ambitious system: **AuditMind** — an autonomous AI audit engagement partner that would:

- Receive audit scope from a human auditor
- Plan the engagement (risk assessment, materiality, sampling)
- Generate Information Request Lists (IRL)
- Review client responses and flag missing data
- Execute tests (anomaly detection, completeness, control effectiveness)
- Draft findings with root cause and recommendations
- Discuss findings with the auditor via chat interface
- Advise on next steps (escalation, remediation, re-audit)
- Generate final audit reports in **IIA Global Standards** format
- Maintain full evidence traceability (SHA-256 hashes)

### Key Design Tension: Meta-Framework vs. Direct Build

A significant strategic question emerged:

| Approach | Description | Timeline | Risk |
|----------|-------------|----------|------|
| **Meta-Framework** | Build LangGraph + CrewAI agents that *build* AuditMind autonomously, with human-like reasoning (holding contradictions, asking questions instead of assuming) | 60-90 days | High complexity, may never ship |
| **Direct Build** | Build AuditMind directly with embedded human-like reasoning | 15-30 days | Lower risk, ships faster |

**Decision:** The project was archived for future reconsideration. The recommendation was to ship the practical tool first, then extract framework patterns if needed.

### AuditMind Feature Ideas (Deferred)

- Multi-LLM router (OpenAI, Anthropic, Ollama, local models)
- Evidence chain of custody (SHA-256 hashes)
- Audit Committee dashboard (read-only executive view)
- Continuous learning / memory across engagements
- Red team / stress-test mode (AI argues against its own findings)
- Automated standards mapping (IIA, COSO, ISO, NIST)
- Arabic language support (RTL, Hijri dates)
- ERP integration adapters (SAP, Oracle, NetSuite)
- Time-tracking & cost attribution per engagement
- Peer review simulation (QA review before issuance)

## Current Status

- **Whistleblower project:** ✅ Published and live
- **AuditMind:** ⏸️ Archived for future development
- **Portfolio:** ✅ Updated with whistleblower project link

## Resuming Development

To resume AuditMind:
1. Review `PROJECT_BRAINSTORM.md` in parent Coding folder
2. Decide: meta-framework vs. direct build
3. Recommended: 15-day MVP sprint with procurement process
4. Start with: React + Vite + Node.js + Prisma + SQLite + LangGraph

---

*Archived: 2026-08-27*
*Maintained by: Majid Mumtaz*
*Contact: https://majidrajpar.github.io/portfolio_my/*
