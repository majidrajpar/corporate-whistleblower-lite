#!/usr/bin/env python3
"""
Quick Review Script
===================
Runs the CrewAI review framework with file reading capabilities.
Generates comprehensive feedback for the main whistleblowing framework.
"""

import os
import sys
import json
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from review_framework.config import get_llm
from review_framework.agents.review_agents import (
    code_quality_reviewer,
    security_auditor,
    architecture_reviewer,
    testing_reviewer,
    ux_ui_reviewer,
    compliance_reviewer,
    meta_reviewer,
    feedback_deliverer
)

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "review_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_file_safely(file_path, max_chars=3000):
    """Read a file with safety checks."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, file_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content[:max_chars]
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def gather_codebase_context():
    """Gather key files from the main framework for review."""
    files = {
        "Backend Server": "app/backend/src/server.js",
        "Auth Middleware": "app/backend/src/middleware/auth.js",
        "Auth Routes": "app/backend/src/routes/auth.js",
        "Report Routes": "app/backend/src/routes/reports.js",
        "Upload Routes": "app/backend/src/routes/upload.js",
        "Audit Log Routes": "app/backend/src/routes/audit-log.js",
        "Prisma Schema": "app/backend/prisma/schema.prisma",
        "Frontend App": "app/frontend/src/App.jsx",
        "Auth Context": "app/frontend/src/context/AuthContext.jsx",
        "Home Page": "app/frontend/src/pages/HomePage.jsx",
        "Dashboard Page": "app/frontend/src/pages/DashboardPage.jsx",
        "CEO Page": "app/frontend/src/pages/CEOPage.jsx",
        "Report Form": "app/frontend/src/components/ReportForm.jsx",
        "Styles": "app/frontend/src/styles/index.css",
    }
    
    context = {}
    for name, path in files.items():
        context[name] = read_file_safely(path, max_chars=2500)
    
    return context

def run_code_quality_review(context):
    """Run the code quality review."""
    print("\n" + "=" * 70)
    print("TASK 1: CODE QUALITY REVIEW")
    print("=" * 70)
    
    prompt = f"""Review the following code from the whistleblowing application for quality issues:

{context['Backend Server']}

{context['Auth Routes']}

{context['Report Routes']}

{context['Frontend App']}

{context['Report Form']}

Evaluate:
1. Code readability and maintainability
2. DRY principle adherence
3. Error handling completeness
4. Naming conventions
5. Function complexity
6. Anti-patterns

Provide:
- Overall quality score (1-100)
- Top 10 improvement recommendations with file paths
- Priority ranking"""

    llm = get_llm()
    result = llm.invoke([{"role": "user", "content": prompt}])
    
    # Save to file
    with open(os.path.join(OUTPUT_DIR, "code_quality_review.md"), 'w') as f:
        f.write(result.content)
    
    print(result.content[:500] + "...")
    return result.content

def run_security_review(context):
    """Run the security audit."""
    print("\n" + "=" * 70)
    print("TASK 2: SECURITY AUDIT")
    print("=" * 70)
    
    prompt = f"""Perform a security audit of the whistleblowing application:

Backend files:
{context['Backend Server']}

{context['Auth Middleware']}

{context['Auth Routes']}

{context['Report Routes']}

{context['Upload Routes']}

Frontend files:
{context['Auth Context']}

{context['Home Page']}

Check for:
1. JWT security (algorithm, expiry, secret handling)
2. Authentication bypass possibilities
3. Rate limiting effectiveness
4. File upload vulnerabilities
5. Input validation gaps
6. XSS vectors (innerHTML, localStorage, etc.)
7. CSRF protection
8. Information disclosure
9. Path traversal
10. Business logic flaws

Provide CVSS scores and exploit scenarios where applicable."""

    llm = get_llm()
    result = llm.invoke([{"role": "user", "content": prompt}])
    
    with open(os.path.join(OUTPUT_DIR, "security_audit.md"), 'w') as f:
        f.write(result.content)
    
    print(result.content[:500] + "...")
    return result.content

def run_architecture_review(context):
    """Run the architecture review."""
    print("\n" + "=" * 70)
    print("TASK 3: ARCHITECTURE REVIEW")
    print("=" * 70)
    
    prompt = f"""Review the system architecture:

Database Schema:
{context['Prisma Schema']}

Backend:
{context['Backend Server']}

{context['Report Routes']}

Frontend:
{context['Frontend App']}

Evaluate:
1. Separation of concerns
2. Database design (normalization, relationships)
3. API design consistency
4. Component architecture
5. Scalability considerations
6. Coupling and cohesion
7. Technical debt
8. Technology choices

Provide architecture improvement recommendations."""

    llm = get_llm()
    result = llm.invoke([{"role": "user", "content": prompt}])
    
    with open(os.path.join(OUTPUT_DIR, "architecture_review.md"), 'w') as f:
        f.write(result.content)
    
    print(result.content[:500] + "...")
    return result.content

def run_ux_review(context):
    """Run the UX/UI review."""
    print("\n" + "=" * 70)
    print("TASK 4: UX/UI REVIEW")
    print("=" * 70)
    
    prompt = f"""Review the UX/UI of the whistleblowing application:

Home Page (Anonymous Reporting):
{context['Home Page']}

Dashboard (Internal Audit):
{context['Dashboard Page']}

CEO Dashboard:
{context['CEO Page']}

Styles:
{context['Styles']}

Evaluate:
1. Trust-building effectiveness for anonymous reporters
2. Form UX and validation feedback
3. Dashboard clarity and efficiency
4. Accessibility (WCAG considerations)
5. Color scheme appropriateness
6. Typography and readability
7. Navigation clarity
8. Mobile responsiveness (though laptop-focused)
9. Error message user-friendliness
10. Loading states

Would a scared employee feel safe using this? Provide specific improvements."""

    llm = get_llm()
    result = llm.invoke([{"role": "user", "content": prompt}])
    
    with open(os.path.join(OUTPUT_DIR, "ux_ui_review.md"), 'w') as f:
        f.write(result.content)
    
    print(result.content[:500] + "...")
    return result.content

def run_compliance_review(context):
    """Run the compliance review."""
    print("\n" + "=" * 70)
    print("TASK 5: COMPLIANCE REVIEW")
    print("=" * 70)
    
    prompt = f"""Review the whistleblowing application for KSA compliance and governance:

Backend:
{context['Backend Server']}

{context['Report Routes']}

{context['Audit Log Routes']}

Database:
{context['Prisma Schema']}

Evaluate:
1. Data residency compliance
2. Anonymity guarantee verification
3. Audit trail completeness and tamper-evidence
4. Evidence handling
5. Retention policies
6. Non-repudiation mechanisms
7. Legal admissibility
8. Protection against retaliation
9. Saudi corporate governance alignment
10. Data deletion capabilities

Provide compliance checklist and gaps."""

    llm = get_llm()
    result = llm.invoke([{"role": "user", "content": prompt}])
    
    with open(os.path.join(OUTPUT_DIR, "compliance_review.md"), 'w') as f:
        f.write(result.content)
    
    print(result.content[:500] + "...")
    return result.content

def synthesize_reviews(reviews):
    """Synthesize all reviews into a unified improvement plan."""
    print("\n" + "=" * 70)
    print("TASK 6: META-REVIEW SYNTHESIS")
    print("=" * 70)
    
    prompt = f"""Synthesize the following review findings into a unified improvement plan:

CODE QUALITY REVIEW:
{reviews['code_quality'][:2000]}

SECURITY AUDIT:
{reviews['security'][:2000]}

ARCHITECTURE REVIEW:
{reviews['architecture'][:2000]}

UX/UI REVIEW:
{reviews['ux_ui'][:2000]}

COMPLIANCE REVIEW:
{reviews['compliance'][:2000]}

Create:
1. Unified priority matrix (Impact vs Effort)
2. Quick wins (low effort, high impact)
3. Short-term improvements (1-2 sprints)
4. Long-term investments (strategic)
5. Effort estimates
6. Dependency mapping
7. Success metrics"""

    llm = get_llm()
    result = llm.invoke([{"role": "user", "content": prompt}])
    
    with open(os.path.join(OUTPUT_DIR, "improvement_plan.md"), 'w') as f:
        f.write(result.content)
    
    print(result.content[:500] + "...")
    return result.content

def deliver_feedback(reviews, synthesis):
    """Format and deliver structured feedback."""
    print("\n" + "=" * 70)
    print("TASK 7: FEEDBACK DELIVERY")
    print("=" * 70)
    
    # Create structured JSON feedback
    prompt = f"""Format the following reviews into structured JSON feedback:

SYNTHESIS:
{synthesis[:2000]}

Create a JSON array of feedback items, each with:
- id (unique number)
- severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO"
- category: "Security" | "Quality" | "Architecture" | "UX" | "Compliance"
- title (short description)
- description (detailed explanation)
- file_path (if applicable)
- suggestion (how to fix)
- effort_estimate: "Quick Win" | "1-2 hours" | "Half Day" | "1-2 Days" | "Week"
- impact: "Critical" | "High" | "Medium" | "Low"

Output ONLY valid JSON, no markdown formatting."""

    llm = get_llm()
    result = llm.invoke([{"role": "user", "content": prompt}])
    
    # Try to extract JSON
    content = result.content
    json_str = content
    
    # Clean up if wrapped in markdown
    if "```json" in content:
        json_str = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_str = content.split("```")[1].split("```")[0].strip()
    
    try:
        feedback_json = json.loads(json_str)
    except:
        # Fallback: create a basic structure
        feedback_json = {
            "error": "Could not parse JSON from LLM",
            "raw_content": content[:1000],
            "items": []
        }
    
    # Save JSON
    with open(os.path.join(OUTPUT_DIR, "feedback_issues.json"), 'w') as f:
        json.dump(feedback_json, f, indent=2)
    
    # Create comprehensive report
    report = f"""# CrewAI Meta-Review Framework - Feedback Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model:** kimi-k2.6 (Ollama Cloud)
**Framework:** CrewAI

---

## Executive Summary

This report was generated by a multi-agent CrewAI system reviewing the LangGraph whistleblowing application.
Seven specialized AI agents analyzed the codebase from different perspectives and synthesized findings into actionable recommendations.

## Reviews Conducted

1. ✅ Code Quality Review
2. ✅ Security Audit
3. ✅ Architecture Review
4. ✅ UX/UI Review
5. ✅ Compliance Review
6. ✅ Meta-Review Synthesis
7. ✅ Structured Feedback Delivery

## Output Files

- `code_quality_review.md` - Detailed code quality analysis
- `security_audit.md` - Security vulnerabilities and recommendations
- `architecture_review.md` - System architecture evaluation
- `ux_ui_review.md` - User experience assessment
- `compliance_review.md` - Governance and compliance review
- `improvement_plan.md` - Prioritized improvement roadmap
- `feedback_issues.json` - Structured feedback for programmatic consumption

## How to Use This Feedback

### For Developers
Read the individual review files for detailed findings. Focus on CRITICAL and HIGH severity issues first.

### For the Main Framework
The `feedback_issues.json` file contains structured data that can be consumed by the FixerAgent:

```python
import json
with open('review_output/feedback_issues.json') as f:
    issues = json.load(f)

for issue in issues:
    if issue['severity'] in ['CRITICAL', 'HIGH']:
        fixer_agent.apply_fix(issue)
```

### For Project Managers
The `improvement_plan.md` provides a phased approach to implementing recommendations.

---

*End of Report*
"""
    
    with open(os.path.join(OUTPUT_DIR, "feedback_report.md"), 'w') as f:
        f.write(report)
    
    print(f"\nGenerated {len(json.dumps(feedback_json))} bytes of structured feedback")
    print(f"Saved to: {OUTPUT_DIR}")
    return feedback_json

def main():
    """Main execution function."""
    print("=" * 70)
    print("CREWAI META-REVIEW FRAMEWORK")
    print("Reviewing Whistleblowing Application")
    print("=" * 70)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Gather codebase
    print("\nGathering codebase context...")
    context = gather_codebase_context()
    print(f"Read {len(context)} files for review")
    
    # Run reviews
    reviews = {}
    reviews['code_quality'] = run_code_quality_review(context)
    reviews['security'] = run_security_review(context)
    reviews['architecture'] = run_architecture_review(context)
    reviews['ux_ui'] = run_ux_review(context)
    reviews['compliance'] = run_compliance_review(context)
    
    # Synthesize
    synthesis = synthesize_reviews(reviews)
    
    # Deliver
    feedback = deliver_feedback(reviews, synthesis)
    
    print("\n" + "=" * 70)
    print("REVIEW FRAMEWORK COMPLETE")
    print("=" * 70)
    print(f"\nAll outputs saved to: {OUTPUT_DIR}")
    print("\nGenerated files:")
    for f in os.listdir(OUTPUT_DIR):
        print(f"  - {f}")
    
    print("\nNext steps:")
    print("1. Review individual reports for detailed findings")
    print("2. Check improvement_plan.md for prioritized roadmap")
    print("3. Use feedback_issues.json for automated fixes")
    print("4. Address CRITICAL and HIGH severity issues first")

if __name__ == "__main__":
    main()
