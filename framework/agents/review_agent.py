"""Review Agent: Validates that all functional requirements are met."""
from framework.config import invoke_llm
from framework.tools.file_tool import read_file, write_file, list_files

SYSTEM_PROMPT = """You are a Review Agent acting as a stakeholder/product owner.
You validate that all functional requirements have been implemented correctly.
You check:
- Feature completeness
- Correct behavior
- Edge cases
- User experience
- Business logic

You produce a structured review report with PASS/FAIL status for each requirement."""

class ReviewAgent:
    def __init__(self):
        self.name = "ReviewAgent"
    
    def run(self, state):
        print(f"[{self.name}] Starting stakeholder review...")
        
        # Collect all relevant files
        backend_files = self._get_files("app/backend/src")
        frontend_files = self._get_files("app/frontend/src")
        
        all_code = ""
        for f in backend_files + frontend_files:
            content = read_file(f)
            all_code += f"\n\n--- FILE: {f} ---\n{content[:2000]}\n"
        
        user_prompt = f"""Review the following code against the functional requirements for a KSA real estate company whistleblowing app.

Code:
{all_code[:6000]}

Requirements to validate:

1. ANONYMOUS REPORTING
   - Can submit report without login?
   - Is any identifying information stored (IP, tracking)?
   - Is there trust messaging on the form?

2. REPORT CATEGORIES
   - Are there exactly 5 categories?
   - Categories: Financial Misconduct, Fraud/Corruption, Harassment/Workplace, Health/Safety, Other

3. FILE UPLOADS
   - Can upload optional files?
   - Accepted types: JPG, PNG, PDF?
   - Size limit: 5MB?
   - Is there security validation?

4. RATE LIMITING
   - Is there rate limiting on anonymous submissions?
   - Limit: 5 per hour per IP?

5. INTERNAL AUDIT DASHBOARD
   - Can auditors log in?
   - Can they view all reports?
   - Can they filter by status/category?
   - Can they update status (NEW → IN_REVIEW → RESOLVED)?
   - Can they escalate to CEO?

6. CEO DASHBOARD
   - Is it a separate view from auditor dashboard?
   - Can CEO log in with separate credentials?
   - Can they view only escalated reports?
   - Are summary statistics shown?

7. AUDIT TRAIL
   - Is there logging of who viewed/escalated/resolved reports?
   - Is reporter identity kept anonymous?

8. SECURITY
   - Is there JWT authentication?
   - Is there password hashing?
   - Is there input validation?
   - Are uploads secure?

9. INITIAL SETUP
   - Are initial users created from environment variables?

10. OVERALL
    - Is the code production-ready?
    - Are there proper error messages?
    - Is the UI trust-building?

For each requirement, mark as:
- PASS (fully implemented)
- PARTIAL (implemented but incomplete)
- FAIL (not implemented or incorrect)

Overall assessment: PASSED or FAILED (require ALL requirements to be PASS for overall PASS)."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        review_report = response.content
        
        passed = self._check_passed(review_report)
        
        write_file("workspace/review_report.md", review_report)
        print(f"[{self.name}] Review report saved. Status: {'PASSED' if passed else 'FAILED'}")
        
        return {
            **state,
            "review_report": review_report,
            "review_passed": passed,
            "current_step": "review_complete"
        }
    
    def _get_files(self, directory: str) -> list:
        import glob as glob_module
        import os
        files = []
        for ext in ['js', 'jsx', 'ts', 'tsx']:
            pattern = os.path.join(directory, f"**/*.{ext}")
            files.extend(glob_module.glob(pattern, recursive=True))
        return files
    
    def _check_passed(self, report: str) -> bool:
        report_lower = report.lower()
        # Look for specific requirement failure markers (e.g., "Status: FAIL")
        import re
        # Find all status lines
        fail_count = len(re.findall(r'status:\s*fail', report_lower))
        partial_count = len(re.findall(r'status:\s*partial', report_lower))
        
        # If any requirements are FAIL, overall is FAILED
        if fail_count > 0:
            return False
        
        # Must explicitly say PASSED overall
        if 'overall: passed' in report_lower or 'overall assessment: passed' in report_lower:
            return True
            
        return False
