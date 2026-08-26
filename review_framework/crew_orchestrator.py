"""
Main Crew Orchestrator
Runs the CrewAI review framework with all agents and tasks.
"""

import os
import sys
from datetime import datetime
from crewai import Crew, Process
from review_framework.tasks.review_tasks import (
    code_quality_task,
    security_audit_task,
    architecture_review_task,
    testing_review_task,
    ux_ui_review_task,
    compliance_review_task,
    meta_review_task,
    feedback_delivery_task
)

def run_review_framework():
    """
    Execute the complete CrewAI review framework.
    This reviews the main whistleblowing application and generates feedback.
    """
    
    print("=" * 80)
    print("CREWAI META-REVIEW FRAMEWORK")
    print("Reviewing the Whistleblowing Application")
    print("=" * 80)
    print()
    
    # Create review_output directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "review_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Assemble the crew
    review_crew = Crew(
        agents=[
            code_quality_task.agent,
            security_audit_task.agent,
            architecture_review_task.agent,
            testing_review_task.agent,
            ux_ui_review_task.agent,
            compliance_review_task.agent,
            meta_review_task.agent,
            feedback_delivery_task.agent,
        ],
        tasks=[
            code_quality_task,
            security_audit_task,
            architecture_review_task,
            testing_review_task,
            ux_ui_review_task,
            compliance_review_task,
            meta_review_task,
            feedback_delivery_task,
        ],
        process=Process.sequential,
        verbose=True,
        memory=True,
        cache=True
    )
    
    print(f"Starting review at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {output_dir}")
    print(f"Agents: 8 specialized reviewers")
    print(f"Tasks: 8 review tasks with sequential execution")
    print()
    
    try:
        # Execute the crew
        result = review_crew.kickoff()
        
        print()
        print("=" * 80)
        print("REVIEW COMPLETE")
        print("=" * 80)
        print()
        print("Generated outputs:")
        print(f"  - review_output/feedback_report.md")
        print(f"  - review_output/feedback_issues.json")
        print(f"  - review_output/improvement_plan.md")
        print()
        print("Review the generated files for actionable feedback on the main framework.")
        
        return result
        
    except Exception as e:
        print(f"\nError during review execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_review_framework()
