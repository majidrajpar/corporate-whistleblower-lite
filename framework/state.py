from typing import TypedDict, List, Optional

class WhistleblowingState(TypedDict):
    # Current step in the workflow
    current_step: str
    
    # Research outputs
    research_report: Optional[str]
    mockups: Optional[str]
    
    # Architecture outputs
    architecture_doc: Optional[str]
    decision_log: Optional[str]
    
    # Code outputs
    backend_code: Optional[str]
    frontend_code: Optional[str]
    
    # Security outputs
    security_report: Optional[str]
    security_passed: bool
    
    # Testing outputs
    test_report: Optional[str]
    tests_passed: bool
    
    # Review outputs (internal)
    review_report: Optional[str]
    review_passed: bool
    
    # ── EXTERNAL REVIEW (CrewAI) ─────────────────────────────
    # Flag indicating if external review was requested/completed
    external_review_requested: bool
    external_review_completed: bool
    
    # External feedback data (structured JSON from CrewAI)
    external_feedback: Optional[List[dict]]
    external_feedback_summary: Optional[str]
    
    # Priority counts from external review
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    
    # External fixes applied
    external_fixes_applied: int
    
    # ── FIXER TRACKING ──────────────────────────────────────
    fix_attempts: int
    max_fix_attempts: int
    
    # Errors and logs
    errors: List[str]
    logs: List[str]

# Initial state factory
def get_initial_state() -> WhistleblowingState:
    return {
        "current_step": "start",
        "research_report": None,
        "mockups": None,
        "architecture_doc": None,
        "decision_log": None,
        "backend_code": None,
        "frontend_code": None,
        "security_report": None,
        "security_passed": False,
        "test_report": None,
        "tests_passed": False,
        "review_report": None,
        "review_passed": False,
        # External review defaults
        "external_review_requested": True,  # Auto-enable
        "external_review_completed": False,
        "external_feedback": None,
        "external_feedback_summary": None,
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
        "info_count": 0,
        "external_fixes_applied": 0,
        # Fixer tracking
        "fix_attempts": 0,
        "max_fix_attempts": 3,
        "errors": [],
        "logs": []
    }
