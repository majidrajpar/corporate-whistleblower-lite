"""
Fixer Agent: Fixes code based on feedback from other agents.
Enhanced to consume external CrewAI review feedback.
"""
import json
from framework.config import invoke_llm
from framework.tools.file_tool import read_file, write_file, edit_file, list_files

SYSTEM_PROMPT = """You are a Fixer Agent specialized in surgical code modifications.
You receive structured feedback (security issues, test failures, review gaps) and fix the code.
You:
- Make minimal, targeted changes
- Preserve existing logic where possible
- Follow the existing code style
- Only modify what's necessary to fix the issue
- Never introduce new bugs

You read files, identify issues, and apply fixes."""

class FixerAgent:
    def __init__(self):
        self.name = "FixerAgent"
    
    def run(self, state):
        print(f"[{self.name}] Starting fix phase...")
        
        # Determine what needs fixing (internal + external)
        fixes_needed = []
        
        # Check internal issues
        if not state.get("security_passed"):
            report = state.get("security_report", "")
            fixes_needed.append(("security", report))
        
        if not state.get("tests_passed"):
            report = state.get("test_report", "")
            fixes_needed.append(("tests", report))
        
        if not state.get("review_passed"):
            report = state.get("review_report", "")
            fixes_needed.append(("review", report))
        
        # Check external issues (CrewAI feedback)
        external_feedback = state.get("external_feedback", [])
        if external_feedback:
            critical = [i for i in external_feedback if i.get('severity', '').upper() == 'CRITICAL']
            high = [i for i in external_feedback if i.get('severity', '').upper() == 'HIGH']
            if critical or high:
                print(f"[{self.name}] External review found {len(critical)} CRITICAL and {len(high)} HIGH issues")
                fixes_needed.append(("external", f"Critical: {len(critical)}, High: {len(high)}"))
        
        if not fixes_needed:
            print(f"[{self.name}] No fixes needed.")
            return {
                **state,
                "current_step": "fix_complete"
            }
        
        # Apply fixes
        for fix_type, report in fixes_needed:
            print(f"[{self.name}] Fixing {fix_type} issues...")
            if fix_type == "external":
                self._fix_external_issues(state)
            else:
                self._fix_issues(fix_type, report)
        
        # Increment fix attempts
        fix_attempts = state.get("fix_attempts", 0) + 1
        
        return {
            **state,
            "fix_attempts": fix_attempts,
            "current_step": "fix_complete"
        }
    
    def _fix_external_issues(self, state):
        """Apply fixes from CrewAI external review."""
        print(f"[{self.name}] Processing external review fixes...")
        
        issues = state.get("external_feedback", [])
        if not issues:
            return
        
        # Priority order
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        fixes_applied = 0
        
        for severity in severity_order:
            severity_issues = [i for i in issues if i.get('severity', '').upper() == severity]
            
            for issue in severity_issues:
                title = issue.get('title', '')
                file_path = issue.get('file_path', '')
                suggestion = issue.get('suggestion', '')
                
                print(f"[{self.name}] Processing [{severity}] {title}")
                
                if not file_path or not suggestion:
                    continue
                
                # Try to apply fix using LLM
                try:
                    success = self._apply_external_fix(file_path, title, suggestion)
                    if success:
                        fixes_applied += 1
                        print(f"[{self.name}] ✅ Fixed: {title}")
                    else:
                        print(f"[{self.name}] ⚠️ Could not auto-fix: {title}")
                except Exception as e:
                    print(f"[{self.name}] ❌ Fix failed: {str(e)}")
        
        print(f"[{self.name}] Applied {fixes_applied} external fixes")
        
        # Update state
        state["external_fixes_applied"] = fixes_applied
    
    def _apply_external_fix(self, file_path: str, title: str, suggestion: str) -> bool:
        """Apply a single external fix using LLM."""
        # Read current file
        content = read_file(file_path)
        if content.startswith("Error"):
            return False
        
        # Generate fix via LLM
        prompt = f"""Fix the following issue in the code:

Issue: {title}
Suggestion: {suggestion}

File: {file_path}

Current code:
```
{content[:4000]}
```

Provide the fix in this format:
OLD:
```
<old code>
```
NEW:
```
<new code>
```"""
        
        response = invoke_llm(SYSTEM_PROMPT, prompt, temperature=0.1)
        return self._parse_and_apply_fix(response.content, file_path)
    
    def _fix_issues(self, fix_type: str, report: str):
        """Parse report and apply fixes (original method)."""
        # Get all code files
        backend_files = self._get_files("app/backend/src")
        frontend_files = self._get_files("app/frontend/src")
        all_files = backend_files + frontend_files
        
        # Read all files for context
        all_code = ""
        for f in all_files:
            content = read_file(f)
            all_code += f"\n\n--- FILE: {f} ---\n{content[:800]}\n"
        
        user_prompt = f"""You need to fix the following {fix_type} issues in a whistleblowing app.

Issue Report:
{report[:4000]}

Current Code:
{all_code[:5000]}

For each issue:
1. Identify the file that needs fixing
2. Provide the exact code change needed
3. Show the old code and new code

Format your response as:
FILE: <filepath>
OLD:
```
<old code snippet>
```
NEW:
```
<new code snippet>
```

Make minimal, surgical changes."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        fix_output = response.content
        
        # Parse and apply fixes
        self._parse_and_apply_fix(fix_output, None)
    
    def _parse_and_apply_fix(self, fix_output: str, file_path_override: str = None) -> bool:
        """Parse fix output and apply changes to files."""
        import re
        
        # Extract file fixes using regex
        pattern = r'FILE:\s*(.+?)\nOLD:\s*```\n(.*?)```\nNEW:\s*```\n(.*?)```'
        matches = re.findall(pattern, fix_output, re.DOTALL)
        
        applied_any = False
        for filepath, old_code, new_code in matches:
            filepath = filepath.strip()
            if file_path_override:
                filepath = file_path_override  # Use provided file path
            old_code = old_code.strip()
            new_code = new_code.strip()
            
            if old_code and new_code:
                try:
                    result = edit_file(filepath, old_code, new_code)
                    if "Successfully" in result:
                        print(f"[{self.name}] Applied fix to {filepath}")
                        applied_any = True
                    else:
                        print(f"[{self.name}] {result}")
                except Exception as e:
                    print(f"[{self.name}] Error editing {filepath}: {str(e)}")
        
        return applied_any
    
    def _get_files(self, directory: str) -> list:
        import glob as glob_module
        import os
        files = []
        for ext in ['js', 'jsx', 'ts', 'tsx']:
            pattern = os.path.join(directory, f"**/*.{ext}")
            files.extend(glob_module.glob(pattern, recursive=True))
        return files
