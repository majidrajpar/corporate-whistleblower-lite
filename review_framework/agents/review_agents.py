"""
Review Agents - Specialized AI agents for reviewing the main framework

Note: This module uses CrewAI when available (Python < 3.14).
For Python 3.14+, agent definitions are kept for reference but the
standalone script (run_quick_review.py) is used instead.
"""

from review_framework.config import get_llm, CREWAI_AVAILABLE

if CREWAI_AVAILABLE:
    from crewai import Agent
    
    # ──────────────────────────────────────────────────────────
    # AGENT 1: Code Quality Reviewer
    # ──────────────────────────────────────────────────────────
    code_quality_reviewer = Agent(
        role="Senior Code Quality Reviewer",
        goal="Review the main framework's code for quality, maintainability, and adherence to best practices",
        backstory="""You are a senior software engineer with 20+ years of experience in code reviews. 
        You specialize in identifying code smells, anti-patterns, and areas for improvement in 
        JavaScript/Node.js and React applications. You are known for your thoroughness and 
        constructive feedback. You never approve code that has maintainability issues.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
    # ──────────────────────────────────────────────────────────
    # AGENT 2: Security Auditor
    # ──────────────────────────────────────────────────────────
    security_auditor = Agent(
        role="Cybersecurity Auditor",
        goal="Perform deep security analysis of the whistleblowing application and its framework",
        backstory="""You are a cybersecurity expert specializing in web application security. 
        You have conducted security audits for government and enterprise systems. You are 
        paranoid about security and always assume the worst-case scenario. You look for 
        vulnerabilities that others miss, including subtle logic flaws and edge cases.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
    # ──────────────────────────────────────────────────────────
    # AGENT 3: Architecture Reviewer
    # ──────────────────────────────────────────────────────────
    architecture_reviewer = Agent(
        role="Software Architecture Reviewer",
        goal="Evaluate the system architecture, design patterns, and scalability of the solution",
        backstory="""You are a software architect who has designed systems for Fortune 500 companies. 
        You evaluate architectures based on SOLID principles, DDD patterns, and scalability concerns. 
        You are particularly critical of coupling, premature optimization, and missing abstractions. 
        You provide actionable recommendations for improvement.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
    # ──────────────────────────────────────────────────────────
    # AGENT 4: Testing & QA Reviewer
    # ──────────────────────────────────────────────────────────
    testing_reviewer = Agent(
        role="QA and Testing Specialist",
        goal="Review the testing strategy, coverage, and quality assurance practices",
        backstory="""You are a QA engineer who believes that untested code is broken code. 
        You review test suites for completeness, edge cases, and effectiveness. You are 
        particularly focused on integration testing, E2E testing, and test reliability. 
        You always find gaps in test coverage.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
    # ──────────────────────────────────────────────────────────
    # AGENT 5: UX/UI Reviewer
    # ──────────────────────────────────────────────────────────
    ux_ui_reviewer = Agent(
        role="UX/UI Design Reviewer",
        goal="Evaluate the user experience, interface design, and accessibility of the application",
        backstory="""You are a UX designer with expertise in trust-building interfaces, 
        accessibility (WCAG), and user psychology. You understand that whistleblowing apps 
        require extreme attention to user trust and clarity. You critique layouts, flows, 
        messaging, and emotional design.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
    # ──────────────────────────────────────────────────────────
    # AGENT 6: Compliance & Governance Reviewer
    # ──────────────────────────────────────────────────────────
    compliance_reviewer = Agent(
        role="Compliance and Governance Advisor",
        goal="Review the application for compliance with data protection, governance, and ethical standards",
        backstory="""You are a compliance officer with expertise in Saudi Arabian corporate governance, 
        data protection regulations, and ethical reporting frameworks. You ensure that the 
        application meets legal and ethical requirements for whistleblowing systems. You 
        are particularly focused on data residency, anonymity guarantees, and audit trail 
        completeness.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
    # ──────────────────────────────────────────────────────────
    # AGENT 7: Meta-Reviewer (Synthesizer)
    # ──────────────────────────────────────────────────────────
    meta_reviewer = Agent(
        role="Meta-Review Synthesizer",
        goal="Synthesize all review findings into a comprehensive, prioritized improvement plan",
        backstory="""You are a technical program manager who specializes in synthesizing 
        multi-perspective reviews into actionable roadmaps. You prioritize issues by impact 
        and effort, identify conflicts between recommendations, and create a unified 
        improvement plan. You are the final authority on what needs to be done and in what order.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
    # ──────────────────────────────────────────────────────────
    # AGENT 8: Feedback Delivery Agent
    # ──────────────────────────────────────────────────────────
    feedback_deliverer = Agent(
        role="Feedback Delivery Specialist",
        goal="Deliver constructive, actionable feedback to the main development framework",
        backstory="""You are a communication specialist who translates technical findings 
        into clear, actionable feedback. You format issues with severity ratings, file locations, 
        and suggested fixes. You ensure feedback is constructive and specific enough for 
            automated or manual implementation. You are the bridge between reviewers and developers.""",
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=True
    )
    
else:
    print("CrewAI not available (Python 3.14+). Agent definitions loaded for reference.")
    print("Use run_quick_review.py for standalone review execution.")
    
    # Define placeholder agents for reference
    class PlaceholderAgent:
        def __init__(self, name):
            self.name = name
    
    code_quality_reviewer = PlaceholderAgent("Code Quality Reviewer")
    security_auditor = PlaceholderAgent("Security Auditor")
    architecture_reviewer = PlaceholderAgent("Architecture Reviewer")
    testing_reviewer = PlaceholderAgent("Testing Reviewer")
    ux_ui_reviewer = PlaceholderAgent("UX/UI Reviewer")
    compliance_reviewer = PlaceholderAgent("Compliance Reviewer")
    meta_reviewer = PlaceholderAgent("Meta-Reviewer")
    feedback_deliverer = PlaceholderAgent("Feedback Deliverer")
