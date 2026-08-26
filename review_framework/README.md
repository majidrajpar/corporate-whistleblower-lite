# CrewAI Meta-Review Framework

A sophisticated multi-agent system built with **CrewAI** that reviews, critiques, and provides actionable feedback to the main LangGraph whistleblowing application framework.

## Purpose

This framework acts as a **quality assurance layer** and **external reviewer** for the main development framework. It runs independent, specialized AI agents that examine the codebase from multiple perspectives and deliver comprehensive improvement recommendations.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           CREWAI META-REVIEW FRAMEWORK              │
├─────────────────────────────────────────────────────┤
│  8 Specialized Agents Working in Sequence           │
│                                                      │
│  Phase 1: Parallel Reviews (Independent)             │
│  ├── Code Quality Reviewer                          │
│  ├── Security Auditor                                │
│  ├── Architecture Reviewer                           │
│  ├── Testing & QA Reviewer                           │
│  ├── UX/UI Reviewer                                  │
│  └── Compliance & Governance Reviewer                │
│                                                      │
│  Phase 2: Synthesis                                  │
│  ├── Meta-Review Synthesizer                         │
│  └── Feedback Delivery Agent                         │
└─────────────────────────────────────────────────────┘
```

## Agents

### 1. Code Quality Reviewer
- **Expertise:** JavaScript/Node.js code quality, maintainability
- **Focus:** Code smells, anti-patterns, DRY principle, complexity
- **Output:** Quality score (1-100) + top 10 improvements

### 2. Security Auditor
- **Expertise:** Web application security, OWASP Top 10
- **Focus:** Authentication, authorization, input validation, file uploads
- **Output:** Risk matrix with CVSS scores + exploit scenarios

### 3. Architecture Reviewer
- **Expertise:** System design, scalability, SOLID principles
- **Focus:** Separation of concerns, database design, API design
- **Output:** Architecture assessment + refactoring recommendations

### 4. Testing & QA Reviewer
- **Expertise:** Test strategy, coverage analysis, CI/CD
- **Focus:** Unit tests, integration tests, E2E tests, edge cases
- **Output:** Coverage analysis + missing test scenarios

### 5. UX/UI Reviewer
- **Expertise:** User experience, accessibility, trust-building design
- **Focus:** Anonymous reporter flow, trust indicators, WCAG compliance
- **Output:** Heuristic evaluation + UX improvements

### 6. Compliance & Governance Reviewer
- **Expertise:** KSA corporate governance, data protection, legal compliance
- **Focus:** Data residency, anonymity guarantees, audit trail
- **Output:** Compliance checklist + governance recommendations

### 7. Meta-Review Synthesizer
- **Expertise:** Technical program management, prioritization
- **Focus:** Conflicting recommendations, cross-cutting concerns
- **Output:** Unified roadmap with phases and effort estimates

### 8. Feedback Delivery Agent
- **Expertise:** Technical communication, developer experience
- **Focus:** Actionable feedback, code examples, file locations
- **Output:** Structured JSON + Markdown reports + GitHub-style issues

## Tools

- **File Reader:** Read main framework files for analysis
- **Directory Lister:** Explore codebase structure
- **Code Metrics:** Calculate complexity and maintainability metrics
- **Security Scanner:** Automated security pattern detection
- **Feedback Writer:** Save structured feedback to files

## How to Run

### Prerequisites
```bash
pip install crewai langchain-openai
```

### Run the Review
```bash
cd review_framework
python crew_orchestrator.py
```

### Outputs
The framework generates three files in `review_output/`:
1. **feedback_report.md** - Human-readable comprehensive review
2. **feedback_issues.json** - Structured data for programmatic processing
3. **improvement_plan.md** - Prioritized implementation roadmap

## Review Process

1. **Initialization:** Crew orchestrator loads all agents and tasks
2. **Phase 1:** Six review agents analyze the codebase in parallel
3. **Phase 2:** Meta-reviewer synthesizes findings into unified plan
4. **Delivery:** Feedback agent formats everything into actionable outputs
5. **Iteration:** Main framework can consume JSON output for automated fixes

## Integration with Main Framework

The review framework is designed to feed back into the main LangGraph framework:

```python
# Main framework can read review output
import json
with open('review_output/feedback_issues.json') as f:
    issues = json.load(f)

# Fixer agent in main framework consumes these
for issue in issues:
    if issue['severity'] in ['CRITICAL', 'HIGH']:
        fixer_agent.apply_fix(issue)
```

## Configuration

Uses the same Ollama Cloud API as the main framework:
- **Model:** kimi-k2.6
- **Temperature:** 0.3 (balanced creativity/consistency)
- **Max Tokens:** 4096 per agent response

## License

MIT License - Same as the main whistleblowing application.

---

**Status:** ✅ Ready for execution
**Last Updated:** 2026-08-26
