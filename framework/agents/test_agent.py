"""Test Agent: Generates and executes tests."""
from framework.config import invoke_llm
from framework.tools.file_tool import read_file, write_file
from framework.tools.shell_tool import run_command, npm_install, npm_test

SYSTEM_PROMPT = """You are a Test Agent specialized in software testing.
You write comprehensive tests covering:
- Unit tests (isolated component/function testing)
- Integration tests (API + database interactions)
- End-to-end tests (full user flows)
- Edge cases and error scenarios

You use Jest for backend, Vitest for frontend, and Playwright for E2E."""

class TestAgent:
    def __init__(self):
        self.name = "TestAgent"
    
    def run(self, state):
        print(f"[{self.name}] Starting testing phase...")
        
        # Install dependencies first
        self._install_dependencies()
        
        # Run backend tests
        backend_passed = self._run_backend_tests()
        
        # Run frontend tests
        frontend_passed = self._run_frontend_tests()
        
        # Run E2E tests (if Playwright is set up)
        e2e_passed = self._run_e2e_tests()
        
        passed = backend_passed and frontend_passed and e2e_passed
        
        report = f"""# Test Report

## Backend Tests: {'PASSED' if backend_passed else 'FAILED'}
## Frontend Tests: {'PASSED' if frontend_passed else 'FAILED'}
## E2E Tests: {'PASSED' if e2e_passed else 'FAILED'}

## Overall: {'PASSED' if passed else 'FAILED'}
"""
        
        write_file("workspace/test_report.md", report)
        print(f"[{self.name}] Test report saved. Status: {'PASSED' if passed else 'FAILED'}")
        
        return {
            **state,
            "test_report": report,
            "tests_passed": passed,
            "current_step": "testing_complete"
        }
    
    def _install_dependencies(self):
        """Install dependencies for both backend and frontend."""
        print(f"[{self.name}] Installing backend dependencies...")
        result = npm_install("app/backend")
        if not result["success"]:
            print(f"[{self.name}] Backend install issues: {result['stderr'][:200]}")
        
        print(f"[{self.name}] Installing frontend dependencies...")
        result = npm_install("app/frontend")
        if not result["success"]:
            print(f"[{self.name}] Frontend install issues: {result['stderr'][:200]}")
    
    def _run_backend_tests(self) -> bool:
        """Run backend Jest tests."""
        print(f"[{self.name}] Running backend tests...")
        
        # First check if package.json exists and has test script
        import json
        import os
        
        pkg_path = "app/backend/package.json"
        if not os.path.exists(pkg_path):
            print(f"[{self.name}] Backend package.json not found")
            return False
        
        # Run tests
        result = npm_test("app/backend")
        
        if result["success"]:
            print(f"[{self.name}] Backend tests passed")
            return True
        else:
            print(f"[{self.name}] Backend tests failed: {result['stderr'][:300]}")
            # Check if it's because tests don't exist yet
            if "no test" in result["stderr"].lower() or "not found" in result["stderr"].lower():
                print(f"[{self.name}] Tests may not be configured yet, will generate")
                return self._generate_missing_backend_tests()
            return False
    
    def _run_frontend_tests(self) -> bool:
        """Run frontend Vitest tests."""
        print(f"[{self.name}] Running frontend tests...")
        
        import os
        pkg_path = "app/frontend/package.json"
        if not os.path.exists(pkg_path):
            print(f"[{self.name}] Frontend package.json not found")
            return False
        
        result = run_command("npm test", cwd="app/frontend", timeout=120)
        
        if result["success"]:
            print(f"[{self.name}] Frontend tests passed")
            return True
        else:
            print(f"[{self.name}] Frontend tests failed: {result['stderr'][:300]}")
            if "no test" in result["stderr"].lower():
                return self._generate_missing_frontend_tests()
            return False
    
    def _run_e2e_tests(self) -> bool:
        """Run Playwright E2E tests."""
        print(f"[{self.name}] Running E2E tests...")
        
        # Check if Playwright is installed
        import os
        if not os.path.exists("app/frontend/playwright.config.js"):
            print(f"[{self.name}] Playwright not configured, generating E2E tests...")
            self._generate_e2e_tests()
            return False  # Will be tested in next iteration
        
        result = run_command("npx playwright test", cwd="app/frontend", timeout=180)
        
        if result["success"]:
            print(f"[{self.name}] E2E tests passed")
            return True
        else:
            print(f"[{self.name}] E2E tests failed: {result['stderr'][:300]}")
            return False
    
    def _generate_missing_backend_tests(self) -> bool:
        """Generate missing backend tests."""
        print(f"[{self.name}] Generating missing backend tests...")
        
        # Read existing server code
        server_code = read_file("app/backend/src/server.js")
        
        user_prompt = f"""Generate Jest tests for the following backend code:

{server_code[:3000]}

Requirements:
- Test all API endpoints
- Mock database where needed
- Test authentication
- Test rate limiting
- Test file upload

Generate complete test file."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file("app/backend/tests/app.test.js", code)
        
        return False  # Will test in next iteration
    
    def _generate_missing_frontend_tests(self) -> bool:
        """Generate missing frontend tests."""
        print(f"[{self.name}] Generating missing frontend tests...")
        
        user_prompt = """Generate Vitest tests for a React whistleblowing frontend.

Test:
1. ReportForm component rendering and submission
2. Login form validation
3. Dashboard report list rendering
4. Auth context login/logout

Use @testing-library/react and vitest.

Generate complete test file."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file("app/frontend/tests/App.test.jsx", code)
        
        return False
    
    def _generate_e2e_tests(self):
        """Generate Playwright E2E tests."""
        print(f"[{self.name}] Generating E2E tests...")
        
        # Generate Playwright config
        config = """import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
"""
        write_file("app/frontend/playwright.config.js", config)
        
        # Generate E2E test
        user_prompt = """Generate Playwright E2E tests for whistleblowing app.

Test flows:
1. Anonymous user submits report
2. Auditor logs in and views reports
3. Auditor escalates report to CEO
4. CEO logs in and views escalated reports
5. Rate limiting blocks excessive submissions

Use Playwright test syntax.

Generate complete test file."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file("app/frontend/e2e/whistleblowing.spec.js", code)
        
        # Add Playwright to package.json devDependencies
        import json
        pkg = json.loads(read_file("app/frontend/package.json"))
        if "devDependencies" not in pkg:
            pkg["devDependencies"] = {}
        pkg["devDependencies"]["@playwright/test"] = "^1.42.0"
        write_file("app/frontend/package.json", json.dumps(pkg, indent=2))
    
    def _extract_code(self, content: str, lang: str) -> str:
        import re
        pattern = rf'```{lang}\\n(.*?)```'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        pattern = r'```\n(.*?)```'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        return content
