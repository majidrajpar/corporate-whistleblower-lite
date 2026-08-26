"""Security Agent: Audits code for vulnerabilities."""
from framework.config import invoke_llm
from framework.tools.file_tool import read_file, list_files

SYSTEM_PROMPT = """You are a Security Agent specialized in web application security auditing.
You check for:
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting)
- Insecure file uploads
- Hardcoded secrets
- Insecure JWT configuration
- Missing input validation
- Insecure CORS settings
- Path traversal
- CSRF vulnerabilities
- Insecure direct object references

You produce a structured security report with severity levels (CRITICAL, HIGH, MEDIUM, LOW)."""

class SecurityAgent:
    def __init__(self):
        self.name = "SecurityAgent"
    
    def run(self, state):
        print(f"[{self.name}] Starting security audit...")
        
        # Collect all backend and frontend files
        backend_files = self._get_files("app/backend/src")
        frontend_files = self._get_files("app/frontend/src")
        
        # Read all files
        all_code = ""
        for f in backend_files + frontend_files:
            content = read_file(f)
            all_code += f"\n\n--- FILE: {f} ---\n{content}\n"
        
        user_prompt = f"""Audit the following code for security vulnerabilities.

Code to audit:
{all_code[:8000]}

Check for:
1. SQL injection (even with Prisma, check raw queries)
2. XSS in frontend (dangerous innerHTML, unsanitized output)
3. File upload security (path traversal, executable uploads)
4. Hardcoded secrets (JWT secrets, passwords)
5. JWT security (algorithm confusion, weak secrets)
6. Input validation (missing or insufficient)
7. CORS configuration (overly permissive)
8. Rate limiting effectiveness
9. Authentication bypass possibilities
10. Path traversal in file serving

For each finding:
- File location
- Severity (CRITICAL, HIGH, MEDIUM, LOW)
- Description
- Recommended fix

If no critical/high issues found, mark as PASSED."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        security_report = response.content
        
        # Determine if passed
        passed = self._check_passed(security_report)
        
        # Save report
        from framework.tools.file_tool import write_file
        write_file("workspace/security_report.md", security_report)
        print(f"[{self.name}] Security report saved. Status: {'PASSED' if passed else 'FAILED'}")
        
        return {
            **state,
            "security_report": security_report,
            "security_passed": passed,
            "current_step": "security_complete"
        }
    
    def _get_files(self, directory: str) -> list:
        """Get all JS/JSX files in a directory."""
        import glob as glob_module
        import os
        files = []
        for ext in ['js', 'jsx']:
            pattern = os.path.join(directory, f"**/*.{ext}")
            files.extend(glob_module.glob(pattern, recursive=True))
        return files
    
    def _check_passed(self, report: str) -> bool:
        """Determine if security audit passed."""
        report_lower = report.lower()
        if 'critical' in report_lower or 'high' in report_lower:
            return False
        if 'failed' in report_lower and 'passed' not in report_lower:
            return False
        return True
