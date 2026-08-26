"""
Review Tools - Custom tools for the review agents
"""

import os
import json
from crewai.tools import BaseTool
from typing import Type, Optional

class FileReaderTool(BaseTool):
    """Read files from the main framework for review."""
    name: str = "file_reader"
    description: str = "Read file contents for review and analysis"
    
    def _run(self, file_path: str) -> str:
        try:
            # Resolve relative paths
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            full_path = os.path.join(base_dir, file_path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class DirectoryListerTool(BaseTool):
    """List files in a directory."""
    name: str = "directory_lister"
    description: str = "List files in a directory for review scope"
    
    def _run(self, directory: str, pattern: str = "*") -> str:
        try:
            import glob
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            full_path = os.path.join(base_dir, directory, pattern)
            files = glob.glob(full_path, recursive=True)
            return "\n".join(files[:50])  # Limit to 50 files
        except Exception as e:
            return f"Error listing directory: {str(e)}"

class CodeMetricsTool(BaseTool):
    """Calculate code metrics."""
    name: str = "code_metrics"
    description: str = "Calculate code complexity and metrics for review"
    
    def _run(self, file_path: str) -> str:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            full_path = os.path.join(base_dir, file_path)
            
            with open(full_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('//')])
            comment_lines = len([l for l in lines if l.strip().startswith('//')])
            blank_lines = total_lines - code_lines - comment_lines
            
            # Simple complexity estimate (count of if/for/while/switch/catch)
            complexity = sum(1 for l in lines if any(kw in l for kw in ['if ', 'for ', 'while ', 'switch', 'catch', 'else if']))
            
            return json.dumps({
                "file": file_path,
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "estimated_complexity": complexity
            }, indent=2)
        except Exception as e:
            return f"Error calculating metrics: {str(e)}"

class SecurityScannerTool(BaseTool):
    """Scan code for security issues."""
    name: str = "security_scanner"
    description: str = "Scan code for common security vulnerabilities"
    
    def _run(self, file_path: str) -> str:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            full_path = os.path.join(base_dir, file_path)
            
            with open(full_path, 'r') as f:
                content = f.read()
            
            issues = []
            
            # Check for common patterns
            if 'eval(' in content:
                issues.append("CRITICAL: eval() usage found - potential code injection")
            if 'innerHTML' in content:
                issues.append("HIGH: innerHTML usage - potential XSS")
            if 'localStorage.setItem(' in content and 'token' in content:
                issues.append("MEDIUM: Token stored in localStorage - vulnerable to XSS")
            if 'process.env.' in content:
                # Check if env vars are validated
                if 'JWT_SECRET' in content and 'if (!process.env.JWT_SECRET)' not in content:
                    issues.append("HIGH: JWT_SECRET not validated before use")
            if 'req.params' in content and 'parseInt' not in content:
                issues.append("LOW: req.params used without type conversion")
            if 'bcrypt' not in content and 'password' in content.lower():
                issues.append("CRITICAL: Password handling without bcrypt")
            
            if not issues:
                return json.dumps({"file": file_path, "status": "No obvious security issues found", "issues": []})
            
            return json.dumps({"file": file_path, "issues": issues}, indent=2)
        except Exception as e:
            return f"Error scanning file: {str(e)}"

class WriteFeedbackTool(BaseTool):
    """Write feedback reports to files."""
    name: str = "write_feedback"
    description: str = "Write structured feedback to output files"
    
    def _run(self, content: str, filename: str = "feedback.md") -> str:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_dir = os.path.join(base_dir, "review_output")
            os.makedirs(output_dir, exist_ok=True)
            
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote feedback to {file_path}"
        except Exception as e:
            return f"Error writing feedback: {str(e)}"

# Tool instances
file_reader = FileReaderTool()
directory_lister = DirectoryListerTool()
code_metrics = CodeMetricsTool()
security_scanner = SecurityScannerTool()
write_feedback = WriteFeedbackTool()
