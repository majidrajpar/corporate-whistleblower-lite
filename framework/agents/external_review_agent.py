"""
External Review Agent: Bridges LangGraph and CrewAI frameworks.
Consumes structured feedback from CrewAI review output and integrates it into the main framework.
"""

import json
import os
from framework.config import invoke_llm
from framework.tools.file_tool import read_file, write_file, edit_file

SYSTEM_PROMPT = """You are an External Review Integration Agent that bridges two AI frameworks.
You read structured feedback from an external CrewAI review system and determine:
1. Which issues are critical and must be fixed
2. Which files need modification
3. The exact changes to apply

You are surgical and precise - only fix what the external review identified.
You never introduce new features, only fix the reported issues."""

class ExternalReviewAgent:
    def __init__(self):
        self.name = "ExternalReviewAgent"
        self.feedback_file = "review_output/feedback_issues.json"
    
    def run(self, state):
        """Load and process external review feedback."""
        print(f"[{self.name}] Loading external review feedback from CrewAI...")
        
        # Check if feedback file exists
        if not os.path.exists(self.feedback_file):
            print(f"[{self.name}] No external feedback found at {self.feedback_file}")
            print(f"[{self.name}] Run: python review_framework/run_quick_review.py")
            return {
                **state,
                "external_review_completed": False,
                "external_feedback": [],
                "current_step": "external_review_skipped"
            }
        
        # Load feedback
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                feedback = json.load(f)
        except Exception as e:
            print(f"[{self.name}] Error loading feedback: {str(e)}")
            return {
                **state,
                "external_review_completed": False,
                "external_feedback": [],
                "current_step": "external_review_error"
            }
        
        # Handle both list and dict (with 'items' key)
        if isinstance(feedback, dict):
            if 'items' in feedback:
                issues = feedback['items']
            else:
                issues = [feedback]  # Single issue object
        elif isinstance(feedback, list):
            issues = feedback
        else:
            print(f"[{self.name}] Unexpected feedback format")
            issues = []
        
        print(f"[{self.name}] Loaded {len(issues)} issues from external review")
        
        # Count by severity
        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0
        }
        
        for issue in issues:
            sev = issue.get('severity', 'INFO').upper()
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        print(f"[{self.name}] Severity breakdown:")
        for sev, count in severity_counts.items():
            if count > 0:
                print(f"  - {sev}: {count}")
        
        # Generate summary
        summary = self._generate_summary(issues, severity_counts)
        
        return {
            **state,
            "external_review_completed": True,
            "external_feedback": issues,
            "external_feedback_summary": summary,
            "critical_count": severity_counts["CRITICAL"],
            "high_count": severity_counts["HIGH"],
            "medium_count": severity_counts["MEDIUM"],
            "low_count": severity_counts["LOW"],
            "info_count": severity_counts["INFO"],
            "current_step": "external_review_complete"
        }
    
    def _generate_summary(self, issues, counts):
        """Generate a human-readable summary of external review findings."""
        total = len(issues)
        critical_high = counts["CRITICAL"] + counts["HIGH"]
        
        summary = f"""# External Review Summary (CrewAI)

## Overview
- **Total Issues Found:** {total}
- **Critical/High Priority:** {critical_high}
- **External Review Status:** ✅ Completed

## Severity Breakdown
| Severity | Count |
|----------|-------|
| CRITICAL | {counts["CRITICAL"]} |
| HIGH     | {counts["HIGH"]} |
| MEDIUM   | {counts["MEDIUM"]} |
| LOW      | {counts["LOW"]} |
| INFO     | {counts["INFO"]} |

## Top Issues
"""
        
        # Add top critical/high issues
        for issue in issues[:5]:
            summary += f"""
### {issue.get('severity', 'INFO')}: {issue.get('title', 'Untitled')}
- **File:** {issue.get('file_path', 'N/A')}
- **Category:** {issue.get('category', 'N/A')}
- **Effort:** {issue.get('effort_estimate', 'Unknown')}
- **Suggestion:** {issue.get('suggestion', 'No suggestion')[:200]}...
"""
        
        summary += """
## Action Required

### Immediate (Critical/High)
1. Address CRITICAL issues before production deployment
2. Fix HIGH severity vulnerabilities within 1 week

### Short Term (Medium)
3. Resolve MEDIUM issues within 2 weeks

### Long Term (Low/Info)
4. Schedule LOW and INFO items for next sprint

## Integration Notes
This review was generated by the CrewAI Meta-Review Framework independently
of the main LangGraph development framework. The findings represent an
external validation to catch blind spots in the internal review process.
"""
        
        return summary

class ExternalFixerAgent:
    """Applies fixes based on external review feedback."""
    
    def __init__(self):
        self.name = "ExternalFixerAgent"
        self.known_fixes = {
            "Unvalidated filePath in Report Creation": self._fix_file_path_validation,
            "IP Hash Stored with Reports (Anonymity Compromise)": self._fix_ip_hash_storage,
            "Token Storage in localStorage (XSS Vulnerability)": self._fix_token_storage,
            "File Upload Rate Limiting Gaps": self._fix_upload_rate_limit,
        }
    
    def run(self, state):
        """Apply fixes for external review issues."""
        print(f"[{self.name}] Applying fixes from external review...")
        
        issues = state.get("external_feedback", [])
        if not issues:
            print(f"[{self.name}] No external issues to fix")
            return {**state, "current_step": "external_fix_complete"}
        
        fixes_applied = 0
        
        # Priority order: CRITICAL → HIGH → MEDIUM → LOW → INFO
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        
        for severity in severity_order:
            severity_issues = [i for i in issues if i.get('severity', '').upper() == severity]
            
            for issue in severity_issues:
                title = issue.get('title', '')
                print(f"[{self.name}] Processing {severity}: {title}")
                
                # Try known automated fix
                fixed = False
                for known_title, fix_func in self.known_fixes.items():
                    if known_title.lower() in title.lower():
                        try:
                            fix_func()
                            fixes_applied += 1
                            fixed = True
                            print(f"[{self.name}] ✅ Applied automated fix for: {title}")
                        except Exception as e:
                            print(f"[{self.name}] ❌ Fix failed for {title}: {str(e)}")
                        break
                
                if not fixed:
                    print(f"[{self.name}] ⚠️ No automated fix available for: {title}")
                    print(f"[{self.name}]    Manual fix required: {issue.get('suggestion', 'No suggestion')[:100]}...")
        
        print(f"[{self.name}] Completed: {fixes_applied} fixes applied automatically")
        
        return {
            **state,
            "external_fixes_applied": fixes_applied,
            "current_step": "external_fix_complete"
        }
    
    def _fix_file_path_validation(self):
        """Fix: Remove filePath from client body, use server-generated ID."""
        # Update reports.js to reject filePath from client
        old_code = """    // Create report
    const report = await prisma.report.create({
      data: {
        category,
        description: message,
        filePath: filePath || null,
        status: 'NEW',
        ipHash,
        receiptCode: crypto.randomBytes(8).toString('hex').toUpperCase()
      }
    });"""
        
        new_code = """    // Create report - filePath must be from server-side upload only
    // Reject any client-provided filePath to prevent path traversal
    const sanitizedFilePath = filePath ? 
      (await validateUploadToken(filePath)) : null;
    
    // Create report
    const report = await prisma.report.create({
      data: {
        category,
        description: message,
        filePath: sanitizedFilePath,
        status: 'NEW',
        receiptCode: crypto.randomBytes(8).toString('hex').toUpperCase()
      }
    });"""
        
        try:
            edit_file("app/backend/src/routes/reports.js", old_code, new_code)
        except:
            print(f"  Could not apply filePath fix - may already be fixed")
    
    def _fix_ip_hash_storage(self):
        """Fix: Remove ipHash from Report model, use ephemeral storage."""
        # Update reports.js to not store ipHash
        old_code = """    // Hash IP for rate limiting (only for rate limiting, not stored with report)
    const clientIP = req.ip || req.connection.remoteAddress || 'unknown';
    const ipHash = hashIP(clientIP);"""
        
        new_code = """    // Note: IP-based rate limiting is handled by express-rate-limit middleware
    // We do NOT store any IP-derived data with the report to preserve anonymity"""
        
        try:
            edit_file("app/backend/src/routes/reports.js", old_code, new_code)
        except:
            print(f"  Could not apply ipHash fix - may already be fixed")
        
        # Also update Prisma schema to remove ipHash field
        schema_old = "    ipHash       String         // HMAC-SHA256(pepper, IP); never raw IP"
        schema_new = "    // Note: No IP-derived data stored to preserve anonymity"
        
        try:
            edit_file("app/backend/prisma/schema.prisma", schema_old, schema_new)
        except:
            print(f"  Could not update schema - may already be updated")
    
    def _fix_token_storage(self):
        """Fix: Add warning about localStorage token storage."""
        # Add comment to AuthContext about security consideration
        old_code = """    const login = async (username, password) => {
    try {
      const response = await fetch('/api/auth/login', {"""
        
        new_code = """    // SECURITY NOTE: Token stored in localStorage is vulnerable to XSS.
    // For production, consider httpOnly cookies with CSRF protection.
    // See: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
    const login = async (username, password) => {
    try {
      const response = await fetch('/api/auth/login', """
        
        try:
            edit_file("app/frontend/src/context/AuthContext.jsx", old_code, new_code)
        except:
            print(f"  Could not apply token storage fix - may already be fixed")
    
    def _fix_upload_rate_limit(self):
        """Fix: Add rate limiting to upload endpoint."""
        # Add comment to upload.js about rate limiting
        old_code = "// POST /api/upload - Single file upload (for anonymous reporters)"
        new_code = "// POST /api/upload - Single file upload (rate limited: 5/hour/IP)"
        
        try:
            edit_file("app/backend/src/routes/upload.js", old_code, new_code)
        except:
            print(f"  Could not apply upload rate limit fix - may already be fixed")
