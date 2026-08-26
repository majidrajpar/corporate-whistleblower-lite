"""
Review Tasks - Tasks assigned to each review agent
"""

from crewai import Task
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

# ──────────────────────────────────────────────────────────
# TASK 1: Code Quality Review
# ──────────────────────────────────────────────────────────
code_quality_task = Task(
    description="""Review the main framework's code files for quality issues.
    
    Files to review:
    - app/backend/src/server.js
    - app/backend/src/middleware/auth.js
    - app/backend/src/routes/*.js
    - app/frontend/src/**/*.jsx
    - app/frontend/src/**/*.css
    
    Evaluate:
    1. Code readability and maintainability
    2. DRY principle adherence
    3. Error handling completeness
    4. Async/await usage patterns
    5. Variable naming conventions
    6. Function complexity (cyclomatic complexity)
    7. Comment quality and documentation
    8. Consistency across the codebase
    9. Potential refactoring opportunities
    10. Anti-patterns and code smells
    
    Provide specific file names and line numbers for each issue found.
    Rate each area from 1-10 and provide overall code quality score.""",
    expected_output="""A detailed code quality report containing:
    - Overall quality score (1-100)
    - Specific issues found with file paths and line numbers
    - Ratings for each evaluation area (1-10)
    - Top 10 improvement recommendations
    - Priority ranking of fixes (Critical/High/Medium/Low)""",
    agent=code_quality_reviewer
)

# ──────────────────────────────────────────────────────────
# TASK 2: Security Deep Dive
# ──────────────────────────────────────────────────────────
security_audit_task = Task(
    description="""Perform a comprehensive security audit of the whistleblowing application.
    
    Scope:
    - Authentication and authorization mechanisms
    - Session management and JWT handling
    - Input validation and sanitization
    - File upload security
    - Database query security
    - API endpoint protection
    - Rate limiting effectiveness
    - Error message information disclosure
    - CORS and CSRF protection
    - Secrets management
    - Encryption at rest and in transit
    - Anonymity guarantees for reporters
    
    Test for:
    - OWASP Top 10 vulnerabilities
    - Business logic flaws
    - Race conditions
    - Timing attacks
    - IDOR (Insecure Direct Object Reference)
    - Mass assignment vulnerabilities
    
    Provide exploit scenarios and proof-of-concept where applicable.""",
    expected_output="""A comprehensive security audit report containing:
    - Risk matrix (Likelihood x Impact)
    - Vulnerability details with CVSS scores
    - Exploit scenarios and proof-of-concepts
    - Remediation steps with code examples
    - Defense-in-depth recommendations
    - Residual risk assessment after fixes""",
    agent=security_auditor
)

# ──────────────────────────────────────────────────────────
# TASK 3: Architecture Evaluation
# ──────────────────────────────────────────────────────────
architecture_review_task = Task(
    description="""Evaluate the system architecture and design patterns.
    
    Evaluate:
    1. Separation of concerns (MVC/SOLID adherence)
    2. Database schema design (normalization, indexes, relationships)
    3. API design (RESTfulness, consistency, versioning strategy)
    4. Frontend component architecture
    5. State management approach
    6. Scalability considerations
    7. Coupling and cohesion analysis
    8. Dependency management
    9. Configuration management
    10. Logging and observability strategy
    11. Technology choice justifications
    12. Technical debt assessment
    
    Consider:
    - What happens when concurrent users submit reports?
    - How does the system handle database connection failures?
    - What is the upgrade path for JWT secrets rotation?
    - How would you scale beyond a single server?""",
    expected_output="""An architecture evaluation report containing:
    - Architecture diagram description
    - Strengths and weaknesses analysis
    - Scalability assessment
    - Technical debt inventory
    - Refactoring recommendations
    - Alternative technology suggestions
    - Future-proofing strategies""",
    agent=architecture_reviewer
)

# ──────────────────────────────────────────────────────────
# TASK 4: Testing Strategy Review
# ──────────────────────────────────────────────────────────
testing_review_task = Task(
    description="""Review the testing strategy and implementation.
    
    Review:
    1. Unit test coverage and quality
    2. Integration test completeness
    3. E2E test scenarios
    4. Test data management
    5. Mocking strategy
    6. Test reliability (flakiness)
    7. Edge case coverage
    8. Performance testing
    9. Security testing (SAST/DAST)
    10. CI/CD integration
    11. Test documentation
    
    Identify:
    - Untested code paths
    - Missing test scenarios
    - Brittle tests that may fail intermittently
    - Tests that don't actually verify behavior
    - Missing assertions
    - Opportunities for property-based testing""",
    expected_output="""A testing review report containing:
    - Coverage analysis (estimated %)
    - Missing test scenarios list
    - Test quality issues
    - Recommended testing tools and frameworks
    - CI/CD pipeline recommendations
    - Test strategy improvement plan""",
    agent=testing_reviewer
)

# ──────────────────────────────────────────────────────────
# TASK 5: UX/UI Review
# ──────────────────────────────────────────────────────────
ux_ui_review_task = Task(
    description="""Evaluate the user experience and interface design.
    
    Evaluate:
    1. Anonymous reporter flow (trust building, clarity, ease of use)
    2. Internal Auditor workflow efficiency
    3. CEO dashboard clarity and insights
    4. Trust indicators and security messaging
    5. Error messages (user-friendly vs technical)
    6. Loading states and feedback
    7. Form validation UX
    8. Mobile responsiveness (even though laptop-focused)
    9. Accessibility (WCAG compliance)
    10. Color scheme and emotional design
    11. Typography and readability
    12. Navigation clarity
    13. Information architecture
    
    Consider:
    - Would a scared employee feel safe using this?
    - Is the language clear and non-technical?
    - Are users informed about what happens next?
    - Is there sufficient reassurance about anonymity?""",
    expected_output="""A UX/UI review report containing:
    - Heuristic evaluation results
    - Accessibility assessment
    - Trust-building effectiveness score
    - Specific UI improvement recommendations
    - Copy and messaging suggestions
    - Wireframe recommendations
    - User journey analysis""",
    agent=ux_ui_reviewer
)

# ──────────────────────────────────────────────────────────
# TASK 6: Compliance Review
# ──────────────────────────────────────────────────────────
compliance_review_task = Task(
    description="""Review the application for compliance and governance.
    
    Review:
    1. Data residency compliance (KSA requirements)
    2. Anonymity guarantee verification
    3. Audit trail completeness
    4. Retention policy implementation
    5. GDPR/privacy considerations
    6. Saudi corporate governance alignment
    7. Evidence handling procedures
    8. Chain of custody for reports
    9. Non-repudiation mechanisms
    10. Data classification and handling
    11. Incident response readiness
    12. Legal admissibility of reports
    
    Check:
    - Are there sufficient controls to prevent retaliation?
    - Is the audit log tamper-evident?
    - Can the system survive a legal challenge?
    - Are there data deletion capabilities?""",
    expected_output="""A compliance review report containing:
    - Compliance checklist results
    - Gaps and risks identified
    - Remediation recommendations
    - Policy and procedure suggestions
    - Legal considerations
    - Governance framework recommendations""",
    agent=compliance_reviewer
)

# ──────────────────────────────────────────────────────────
# TASK 7: Meta-Review Synthesis
# ──────────────────────────────────────────────────────────
meta_review_task = Task(
    description="""Synthesize all review findings into a unified improvement plan.
    
    Inputs:
    - Code Quality Review findings
    - Security Audit findings
    - Architecture Review findings
    - Testing Review findings
    - UX/UI Review findings
    - Compliance Review findings
    
    Synthesize:
    1. Identify conflicting recommendations
    2. Find cross-cutting concerns
    3. Prioritize by impact vs effort
    4. Create implementation phases
    5. Identify quick wins vs long-term investments
    6. Estimate effort for each recommendation
    7. Create a timeline for implementation
    8. Identify dependencies between fixes
    
    Output a unified roadmap that balances:
    - Security criticality
    - User experience impact
    - Technical debt reduction
    - Compliance requirements""",
    expected_output="""A comprehensive improvement roadmap containing:
    - Unified priority matrix
    - Implementation phases (Quick Wins / Short-term / Long-term)
    - Effort estimates and timeline
    - Dependency graph
    - Resource requirements
    - Success metrics and KPIs
    - Risk mitigation strategies""",
    agent=meta_reviewer,
    context=[
        code_quality_task,
        security_audit_task,
        architecture_review_task,
        testing_review_task,
        ux_ui_review_task,
        compliance_review_task
    ]
)

# ──────────────────────────────────────────────────────────
# TASK 8: Feedback Delivery
# ──────────────────────────────────────────────────────────
feedback_delivery_task = Task(
    description="""Format and deliver actionable feedback to the main development framework.
    
    Format the meta-review findings into:
    1. Structured JSON for programmatic consumption
    2. Markdown report for human review
    3. GitHub-style issue list
    4. Code review comments with file locations
    
    Each feedback item must include:
    - Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO
    - Category: Security / Quality / Architecture / UX / Compliance / Testing
    - File location (if applicable)
    - Current state (what's wrong)
    - Expected state (what it should be)
    - Suggested fix (code example or approach)
    - Impact assessment
    - Effort estimate
    
    Save outputs to:
    - review_output/feedback_report.md
    - review_output/feedback_issues.json
    - review_output/improvement_plan.md""",
    expected_output="""Complete feedback package containing:
    - Structured JSON with all findings
    - Human-readable markdown report
    - Prioritized issue list
    - Code review comments ready for implementation
    - Improvement timeline and phases""",
    agent=feedback_deliverer,
    context=[meta_review_task]
)
