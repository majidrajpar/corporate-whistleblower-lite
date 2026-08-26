"""
Whistleblowing App - LangGraph Multi-Agent Orchestrator
Runs specialized AI agents in a directed graph with feedback loops.
INCLUDES: CrewAI External Review Integration Phase
"""

import sys
import os

# Add framework to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from framework.state import get_initial_state
from framework.agents.research_agent import ResearchAgent
from framework.agents.architect_agent import ArchitectAgent
from framework.agents.backend_agent import BackendAgent
from framework.agents.frontend_agent import FrontendAgent
from framework.agents.security_agent import SecurityAgent
from framework.agents.test_agent import TestAgent
from framework.agents.review_agent import ReviewAgent
from framework.agents.fixer_agent import FixerAgent
from framework.agents.external_review_agent import ExternalReviewAgent, ExternalFixerAgent

# Initialize agents
research_agent = ResearchAgent()
architect_agent = ArchitectAgent()
backend_agent = BackendAgent()
frontend_agent = FrontendAgent()
security_agent = SecurityAgent()
test_agent = TestAgent()
review_agent = ReviewAgent()
fixer_agent = FixerAgent()
external_review_agent = ExternalReviewAgent()
external_fixer_agent = ExternalFixerAgent()

# ── PHASE FUNCTIONS ──────────────────────────────────────

def run_research(state):
    """Execute ResearchAgent."""
    print("\n" + "="*70)
    print("PHASE 1: RESEARCH")
    print("="*70)
    return research_agent.run(state)

def run_architecture(state):
    """Execute ArchitectAgent."""
    print("\n" + "="*70)
    print("PHASE 2: ARCHITECTURE")
    print("="*70)
    return architect_agent.run(state)

def run_backend(state):
    """Execute BackendAgent."""
    print("\n" + "="*70)
    print("PHASE 3: BACKEND DEVELOPMENT")
    print("="*70)
    return backend_agent.run(state)

def run_frontend(state):
    """Execute FrontendAgent."""
    print("\n" + "="*70)
    print("PHASE 4: FRONTEND DEVELOPMENT")
    print("="*70)
    return frontend_agent.run(state)

def run_security(state):
    """Execute SecurityAgent."""
    print("\n" + "="*70)
    print("PHASE 5: SECURITY AUDIT (Internal)")
    print("="*70)
    return security_agent.run(state)

def run_tests(state):
    """Execute TestAgent."""
    print("\n" + "="*70)
    print("PHASE 6: TESTING")
    print("="*70)
    return test_agent.run(state)

def run_review(state):
    """Execute ReviewAgent."""
    print("\n" + "="*70)
    print("PHASE 7: INTERNAL STAKEHOLDER REVIEW")
    print("="*70)
    return review_agent.run(state)

# ── EXTERNAL REVIEW PHASES ────────────────────────────────

def run_external_review(state):
    """Execute External Review (CrewAI integration)."""
    print("\n" + "="*70)
    print("PHASE 8: EXTERNAL REVIEW (CrewAI Meta-Review)")
    print("="*70)
    print("Loading feedback from review_output/feedback_issues.json...")
    return external_review_agent.run(state)

def run_external_fix(state):
    """Apply fixes from external review."""
    print("\n" + "="*70)
    print("PHASE 9: APPLY EXTERNAL FIXES")
    print("="*70)
    return external_fixer_agent.run(state)

def run_final_verification(state):
    """Final verification after all fixes."""
    print("\n" + "="*70)
    print("PHASE 10: FINAL VERIFICATION")
    print("="*70)
    
    # Summarize all findings
    critical = state.get("critical_count", 0)
    high = state.get("high_count", 0)
    medium = state.get("medium_count", 0)
    low = state.get("low_count", 0)
    fixes = state.get("external_fixes_applied", 0)
    
    print(f"\n📊 Final Status:")
    print(f"   Internal Security: {'PASSED' if state.get('security_passed') else 'FAILED'}")
    print(f"   Internal Tests: {'PASSED' if state.get('tests_passed') else 'FAILED'}")
    print(f"   Internal Review: {'PASSED' if state.get('review_passed') else 'FAILED'}")
    print(f"   External Review: {'COMPLETED' if state.get('external_review_completed') else 'SKIPPED'}")
    print(f"\n📋 External Issues Found: {critical + high + medium + low + state.get('info_count', 0)}")
    if critical + high > 0:
        print(f"   CRITICAL: {critical}")
        print(f"   HIGH: {high}")
    print(f"   MEDIUM: {medium}")
    print(f"   LOW: {low}")
    print(f"\n🔧 External Fixes Applied: {fixes}")
    
    if critical > 0:
        print("\n⚠️  WARNING: {critical} CRITICAL issues remain. Manual review required.")
    elif high > 0:
        print(f"\n⚠️  WARNING: {high} HIGH severity issues remain. Address before production.")
    else:
        print("\n✅ All CRITICAL and HIGH issues addressed or flagged.")
    
    return {**state, "current_step": "final_verification"}

def run_fix(state):
    """Execute FixerAgent (internal)."""
    print("\n" + "="*70)
    print("PHASE: FIXING ISSUES (Internal)")
    print("="*70)
    return fixer_agent.run(state)

# ── DECISION FUNCTIONS ────────────────────────────────────

def should_fix_security(state):
    """Decision: Fix security issues or proceed?"""
    if not state.get("security_passed"):
        attempts = state.get("fix_attempts", 0)
        max_attempts = state.get("max_fix_attempts", 3)
        if attempts < max_attempts:
            print(f"Security audit FAILED. Fix attempt {attempts + 1}/{max_attempts}")
            return "fix"
        else:
            print("Max fix attempts reached for security. Proceeding with warnings.")
            return "tests"
    return "tests"

def should_fix_tests(state):
    """Decision: Fix test failures or proceed?"""
    if not state.get("tests_passed"):
        attempts = state.get("fix_attempts", 0)
        max_attempts = state.get("max_fix_attempts", 3)
        if attempts < max_attempts:
            print(f"Tests FAILED. Fix attempt {attempts + 1}/{max_attempts}")
            return "fix"
        else:
            print("Max fix attempts reached for tests. Proceeding with warnings.")
            return "review"
    return "review"

def should_fix_review(state):
    """Decision: Fix review gaps or proceed to external review?"""
    if not state.get("review_passed"):
        attempts = state.get("fix_attempts", 0)
        max_attempts = state.get("max_fix_attempts", 3)
        if attempts < max_attempts:
            print(f"Review FAILED. Fix attempt {attempts + 1}/{max_attempts}")
            return "fix"
        else:
            print("Max fix attempts reached for review. Proceeding to external review.")
            return "external_review"
    return "external_review"

def should_run_external_review(state):
    """Decision: Run external review or skip?"""
    if state.get("external_review_requested", True):
        print("External review ENABLED. Proceeding to CrewAI review.")
        return "external_review"
    else:
        print("External review DISABLED. Skipping.")
        return "final_verification"

def should_apply_external_fixes(state):
    """Decision: Apply external fixes or skip?"""
    if state.get("external_review_completed"):
        critical = state.get("critical_count", 0)
        high = state.get("high_count", 0)
        
        if critical + high > 0:
            print(f"External review found {critical} CRITICAL and {high} HIGH issues.")
            print("Applying automated fixes...")
            return "external_fix"
        else:
            print("No critical/high external issues found. Proceeding to verification.")
            return "final_verification"
    else:
        print("External review not completed. Skipping external fixes.")
        return "final_verification"

# ── BUILD THE GRAPH ──────────────────────────────────────

workflow = StateGraph(dict)

# Add all nodes
workflow.add_node("research", run_research)
workflow.add_node("architecture", run_architecture)
workflow.add_node("backend", run_backend)
workflow.add_node("frontend", run_frontend)
workflow.add_node("security", run_security)
workflow.add_node("tests", run_tests)
workflow.add_node("review", run_review)
workflow.add_node("fix_security", run_fix)
workflow.add_node("fix_tests", run_fix)
workflow.add_node("fix_review", run_fix)

# NEW: External review nodes
workflow.add_node("external_review", run_external_review)
workflow.add_node("external_fix", run_external_fix)
workflow.add_node("final_verification", run_final_verification)

# Define edges
workflow.set_entry_point("research")
workflow.add_edge("research", "architecture")
workflow.add_edge("architecture", "backend")
workflow.add_edge("backend", "frontend")
workflow.add_edge("frontend", "security")

# Security loop
workflow.add_conditional_edges(
    "security",
    should_fix_security,
    {
        "fix": "fix_security",
        "tests": "tests"
    }
)
workflow.add_edge("fix_security", "security")

# Testing loop
workflow.add_conditional_edges(
    "tests",
    should_fix_tests,
    {
        "fix": "fix_tests",
        "review": "review"
    }
)
workflow.add_edge("fix_tests", "tests")

# Review loop → External Review
workflow.add_conditional_edges(
    "review",
    should_fix_review,
    {
        "fix": "fix_review",
        "external_review": "external_review"
    }
)
workflow.add_edge("fix_review", "review")

# External Review → External Fix or Final
workflow.add_conditional_edges(
    "external_review",
    should_apply_external_fixes,
    {
        "external_fix": "external_fix",
        "final_verification": "final_verification"
    }
)

# External Fix → Final Verification
workflow.add_edge("external_fix", "final_verification")

# Final Verification → END
workflow.add_edge("final_verification", END)

# Compile with memory checkpointing
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# ── MAIN EXECUTION ──────────────────────────────────────

def run_pipeline():
    """Execute the complete pipeline with external review integration."""
    print("\n" + "#"*70)
    print("# WHISTLEBLOWING APP - LANGGRAPH MULTI-AGENT FRAMEWORK")
    print("# WITH CREWAI EXTERNAL REVIEW INTEGRATION")
    print("#"*70)
    print("\n🚀 Starting autonomous development pipeline...")
    print("🤖 Model: kimi-k2.6 via Ollama Cloud")
    print("🔧 Framework: LangGraph with advanced feedback loops")
    print("🔍 External Review: CrewAI Meta-Review Framework")
    print("📦 Integration: Automated feedback consumption")
    print()
    
    initial_state = get_initial_state()
    
    # Run the graph
    config = {"configurable": {"thread_id": "whistleblowing-app-v2"}}
    
    try:
        final_state = None
        for event in app.stream(initial_state, config, stream_mode="values"):
            current_step = event.get("current_step", "unknown")
            print(f"\n>>> Pipeline step: {current_step}")
            
            # Check for failures
            if event.get("errors"):
                print(f"Errors: {event['errors']}")
            
            final_state = event
        
        print("\n" + "="*70)
        print("PIPELINE COMPLETE")
        print("="*70)
        
        # Final status
        if final_state:
            print(f"\n📊 Final Results:")
            print(f"   Internal Security: {'✅ PASSED' if final_state.get('security_passed') else '❌ FAILED'}")
            print(f"   Internal Tests: {'✅ PASSED' if final_state.get('tests_passed') else '❌ FAILED'}")
            print(f"   Internal Review: {'✅ PASSED' if final_state.get('review_passed') else '❌ FAILED'}")
            print(f"   External Review: {'✅ COMPLETED' if final_state.get('external_review_completed') else '⏭️ SKIPPED'}")
            
            if final_state.get('external_review_completed'):
                print(f"\n📋 External Review Summary:")
                print(f"   Critical: {final_state.get('critical_count', 0)}")
                print(f"   High: {final_state.get('high_count', 0)}")
                print(f"   Medium: {final_state.get('medium_count', 0)}")
                print(f"   Low: {final_state.get('low_count', 0)}")
                print(f"   Info: {final_state.get('info_count', 0)}")
                print(f"   Fixes Applied: {final_state.get('external_fixes_applied', 0)}")
        
        print("\n📁 Generated artifacts:")
        print("   - workspace/research_report.md")
        print("   - workspace/architecture.md")
        print("   - workspace/mockups.mmd")
        print("   - workspace/decision_log.md")
        print("   - workspace/security_report.md")
        print("   - workspace/test_report.md")
        print("   - workspace/review_report.md")
        print("   - review_output/feedback_issues.json (External)")
        print("   - review_output/improvement_plan.md (External)")
        print("   - review_output/feedback_report.md (External)")
        print("   - app/backend/ (Node.js/Express/Prisma)")
        print("   - app/frontend/ (React/Vite)")
        
        print("\n🔗 Integration:")
        print("   The main framework can now consume CrewAI feedback automatically.")
        print("   See framework/agents/external_review_agent.py for the bridge.")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        return initial_state

if __name__ == "__main__":
    run_pipeline()
