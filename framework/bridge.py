"""
Framework Bridge / Adapter
============================
Provides a unified interface for communication between LangGraph and CrewAI frameworks.
Enables the main framework to:
1. Trigger external reviews programmatically
2. Consume structured feedback
3. Apply automated fixes
4. Track review state across frameworks

Usage:
    from framework.bridge import FrameworkBridge
    
    bridge = FrameworkBridge()
    
    # Trigger external review
    bridge.trigger_review()
    
    # Get prioritized issues
    critical_issues = bridge.get_issues_by_severity("CRITICAL")
    
    # Apply automated fixes
    bridge.apply_fixes(critical_issues)
"""

import json
import os
from typing import List, Dict, Optional

class FrameworkBridge:
    """
    Bridge between LangGraph (main) and CrewAI (review) frameworks.
    
    Handles:
    - File path resolution between frameworks
    - Feedback data transformation
    - Review status tracking
    - Fix application coordination
    """
    
    def __init__(self, 
                 feedback_file: str = "review_output/feedback_issues.json",
                 summary_file: str = "review_output/feedback_report.md",
                 plan_file: str = "review_output/improvement_plan.md"):
        """
        Initialize the bridge with file paths.
        
        Args:
            feedback_file: Path to structured feedback JSON
            summary_file: Path to human-readable summary
            plan_file: Path to improvement plan
        """
        self.feedback_file = feedback_file
        self.summary_file = summary_file
        self.plan_file = plan_file
        self._cached_feedback = None
    
    # ── REVIEW TRIGGERS ────────────────────────────────────
    
    def trigger_review(self, review_types: List[str] = None) -> bool:
        """
        Trigger the CrewAI review framework to generate fresh feedback.
        
        Args:
            review_types: List of review types to run (None = all)
                Options: ["code_quality", "security", "architecture", 
                         "ux_ui", "compliance", "testing"]
        
        Returns:
            True if review triggered successfully
        """
        print("[FrameworkBridge] Triggering CrewAI external review...")
        
        # Check if review framework exists
        if not os.path.exists("review_framework"):
            print("[FrameworkBridge] ERROR: review_framework/ not found")
            print("[FrameworkBridge] Ensure CrewAI framework is set up")
            return False
        
        # Run the quick review script
        import subprocess
        try:
            result = subprocess.run(
                ["python", "review_framework/run_quick_review.py"],
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes
            )
            
            if result.returncode == 0:
                print("[FrameworkBridge] ✅ Review completed successfully")
                self._cached_feedback = None  # Invalidate cache
                return True
            else:
                print(f"[FrameworkBridge] ❌ Review failed: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[FrameworkBridge] ⏱️ Review timed out after 15 minutes")
            return False
        except Exception as e:
            print(f"[FrameworkBridge] ❌ Error triggering review: {str(e)}")
            return False
    
    # ── FEEDBACK CONSUMPTION ────────────────────────────────
    
    def get_feedback(self, force_reload: bool = False) -> List[Dict]:
        """
        Load and return structured feedback from CrewAI review.
        
        Args:
            force_reload: Ignore cache and reload from disk
            
        Returns:
            List of feedback issue dictionaries
        """
        if self._cached_feedback is not None and not force_reload:
            return self._cached_feedback
        
        if not os.path.exists(self.feedback_file):
            print(f"[FrameworkBridge] No feedback file found at {self.feedback_file}")
            return []
        
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                feedback = json.load(f)
            
            # Normalize format
            if isinstance(feedback, dict):
                if 'items' in feedback:
                    issues = feedback['items']
                else:
                    issues = [feedback]
            elif isinstance(feedback, list):
                issues = feedback
            else:
                issues = []
            
            self._cached_feedback = issues
            print(f"[FrameworkBridge] Loaded {len(issues)} feedback items")
            return issues
            
        except Exception as e:
            print(f"[FrameworkBridge] Error loading feedback: {str(e)}")
            return []
    
    def get_issues_by_severity(self, severity: str) -> List[Dict]:
        """
        Get issues filtered by severity.
        
        Args:
            severity: "CRITICAL", "HIGH", "MEDIUM", "LOW", or "INFO"
            
        Returns:
            Filtered list of issues
        """
        issues = self.get_feedback()
        severity_upper = severity.upper()
        filtered = [i for i in issues if i.get('severity', '').upper() == severity_upper]
        print(f"[FrameworkBridge] Found {len(filtered)} {severity} issues")
        return filtered
    
    def get_issues_by_category(self, category: str) -> List[Dict]:
        """
        Get issues filtered by category.
        
        Args:
            category: "Security", "Quality", "Architecture", "UX", "Compliance"
            
        Returns:
            Filtered list of issues
        """
        issues = self.get_feedback()
        filtered = [i for i in issues if i.get('category', '').lower() == category.lower()]
        print(f"[FrameworkBridge] Found {len(filtered)} {category} issues")
        return filtered
    
    def get_issues_by_file(self, file_pattern: str) -> List[Dict]:
        """
        Get issues related to specific files.
        
        Args:
            file_pattern: Substring to match in file_path
            
        Returns:
            Matching issues
        """
        issues = self.get_feedback()
        filtered = [i for i in issues if file_pattern.lower() in i.get('file_path', '').lower()]
        print(f"[FrameworkBridge] Found {len(filtered)} issues for {file_pattern}")
        return filtered
    
    def get_priority_queue(self) -> List[Dict]:
        """
        Get all issues sorted by priority (CRITICAL first).
        
        Returns:
            Prioritized list of issues
        """
        issues = self.get_feedback()
        
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        
        sorted_issues = sorted(
            issues,
            key=lambda x: severity_order.get(x.get('severity', 'INFO').upper(), 99)
        )
        
        return sorted_issues
    
    # ── FIX APPLICATION ────────────────────────────────────
    
    def apply_fix(self, issue: Dict) -> bool:
        """
        Apply a single fix for a given issue.
        
        Args:
            issue: Feedback issue dictionary with fix details
            
        Returns:
            True if fix applied successfully
        """
        title = issue.get('title', 'Unknown')
        file_path = issue.get('file_path', '')
        suggestion = issue.get('suggestion', '')
        
        print(f"[FrameworkBridge] Applying fix: {title}")
        
        if not file_path or not suggestion:
            print(f"[FrameworkBridge] ⚠️ Skipping - missing file_path or suggestion")
            return False
        
        # Try to apply the fix using LLM
        try:
            from framework.config import invoke_llm
            from framework.tools.file_tool import read_file
            
            # Read current file content
            current_content = read_file(file_path)
            if current_content.startswith("Error"):
                print(f"[FrameworkBridge] ❌ Cannot read file: {file_path}")
                return False
            
            # Ask LLM to generate the fix
            prompt = f"""Apply the following fix to the code:

Issue: {title}
Suggestion: {suggestion}

Current file ({file_path}):
```
{current_content[:3000]}
```

Provide the fix in this format:
OLD:
```
<old code to replace>
```
NEW:
```
<new code>
```"""
            
            response = invoke_llm(
                "You are a code fixer. Apply the suggested fix precisely.",
                prompt,
                temperature=0.1
            )
            
            # Parse and apply fix
            return self._parse_and_apply(response.content, file_path)
            
        except Exception as e:
            print(f"[FrameworkBridge] ❌ Fix failed: {str(e)}")
            return False
    
    def apply_fixes(self, issues: List[Dict], auto_confirm: bool = False) -> Dict[str, int]:
        """
        Apply fixes for multiple issues.
        
        Args:
            issues: List of issues to fix
            auto_confirm: If True, apply all without confirmation
            
        Returns:
            Summary dict with counts: {"applied": N, "failed": N, "skipped": N}
        """
        results = {"applied": 0, "failed": 0, "skipped": 0}
        
        for issue in issues:
            if not auto_confirm:
                # In practice, you'd ask for confirmation here
                pass
            
            success = self.apply_fix(issue)
            if success:
                results["applied"] += 1
            else:
                results["failed"] += 1
        
        print(f"[FrameworkBridge] Fix summary: {results}")
        return results
    
    def apply_critical_fixes(self) -> Dict[str, int]:
        """
        Apply all CRITICAL fixes automatically.
        
        Returns:
            Summary of applied fixes
        """
        critical = self.get_issues_by_severity("CRITICAL")
        if not critical:
            print("[FrameworkBridge] No CRITICAL issues to fix")
            return {"applied": 0, "failed": 0, "skipped": 0}
        
        print(f"[FrameworkBridge] Applying {len(critical)} CRITICAL fixes...")
        return self.apply_fixes(critical, auto_confirm=True)
    
    # ── STATUS TRACKING ──────────────────────────────────────
    
    def get_review_status(self) -> Dict:
        """
        Get current review status summary.
        
        Returns:
            Status dictionary with counts and metadata
        """
        issues = self.get_feedback()
        
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        category_counts = {}
        
        for issue in issues:
            sev = issue.get('severity', 'INFO').upper()
            if sev in severity_counts:
                severity_counts[sev] += 1
            
            cat = issue.get('category', 'Unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "total_issues": len(issues),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "feedback_file_exists": os.path.exists(self.feedback_file),
            "summary_file_exists": os.path.exists(self.summary_file),
            "plan_file_exists": os.path.exists(self.plan_file)
        }
    
    def print_review_summary(self):
        """Print a formatted review summary."""
        status = self.get_review_status()
        
        print("\n" + "=" * 70)
        print("EXTERNAL REVIEW STATUS (CrewAI)")
        print("=" * 70)
        print(f"Total Issues: {status['total_issues']}")
        print(f"\nSeverity Breakdown:")
        for sev, count in status['severity_breakdown'].items():
            if count > 0:
                icon = "🚨" if sev == "CRITICAL" else "⚠️" if sev == "HIGH" else "ℹ️"
                print(f"  {icon} {sev}: {count}")
        
        print(f"\nCategory Breakdown:")
        for cat, count in status['category_breakdown'].items():
            print(f"  {cat}: {count}")
        
        print(f"\nFiles Available:")
        print(f"  Feedback JSON: {'✅' if status['feedback_file_exists'] else '❌'}")
        print(f"  Summary Report: {'✅' if status['summary_file_exists'] else '❌'}")
        print(f"  Improvement Plan: {'✅' if status['plan_file_exists'] else '❌'}")
        print("=" * 70)
    
    # ── INTERNAL HELPERS ─────────────────────────────────────
    
    def _parse_and_apply(self, fix_output: str, file_path: str) -> bool:
        """Parse LLM fix output and apply to file."""
        import re
        from framework.tools.file_tool import edit_file
        
        # Extract file fixes using regex
        pattern = r'OLD:\s*```\n(.*?)```\nNEW:\s*```\n(.*?)```'
        matches = re.findall(pattern, fix_output, re.DOTALL)
        
        if not matches:
            print(f"[FrameworkBridge] Could not parse fix output")
            return False
        
        applied = False
        for old_code, new_code in matches:
            old_code = old_code.strip()
            new_code = new_code.strip()
            
            if old_code and new_code:
                try:
                    result = edit_file(file_path, old_code, new_code)
                    if "Successfully" in result:
                        print(f"[FrameworkBridge] ✅ Applied fix to {file_path}")
                        applied = True
                    else:
                        print(f"[FrameworkBridge] ⚠️ {result}")
                except Exception as e:
                    print(f"[FrameworkBridge] ❌ Edit failed: {str(e)}")
        
        return applied


# ── CONVENIENCE FUNCTIONS ────────────────────────────────

def get_bridge() -> FrameworkBridge:
    """Get a configured FrameworkBridge instance."""
    return FrameworkBridge()

def quick_review_status():
    """Quick function to print review status without instantiating bridge."""
    bridge = FrameworkBridge()
    bridge.print_review_summary()

def apply_critical_fixes():
    """Quick function to apply all CRITICAL fixes."""
    bridge = FrameworkBridge()
    return bridge.apply_critical_fixes()


if __name__ == "__main__":
    # Demo usage
    print("Framework Bridge Demo")
    print("=" * 70)
    
    bridge = get_bridge()
    bridge.print_review_summary()
    
    # Example: Get critical issues
    critical = bridge.get_issues_by_severity("CRITICAL")
    print(f"\nCritical issues: {len(critical)}")
    for issue in critical:
        print(f"  - {issue.get('title', 'Untitled')}")
    
    # Example: Get security issues
    security = bridge.get_issues_by_category("Security")
    print(f"\nSecurity issues: {len(security)}")
    for issue in security:
        print(f"  - {issue.get('title', 'Untitled')}")
