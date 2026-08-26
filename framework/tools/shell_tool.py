"""Shell tool for executing commands."""
import subprocess
import os

def run_command(command: str, cwd: str = None, timeout: int = 120) -> dict:
    """Run a shell command and return stdout, stderr, and return code."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "returncode": -1,
            "success": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "success": False
        }

def npm_install(cwd: str) -> dict:
    """Run npm install in a directory."""
    return run_command("npm install", cwd=cwd, timeout=300)

def npm_test(cwd: str) -> dict:
    """Run npm test in a directory."""
    return run_command("npm test", cwd=cwd, timeout=120)

def npx_prisma_generate(cwd: str) -> dict:
    """Generate Prisma client."""
    return run_command("npx prisma generate", cwd=cwd, timeout=120)

def npx_prisma_migrate(cwd: str) -> dict:
    """Run Prisma migration."""
    return run_command("npx prisma migrate dev --name init", cwd=cwd, timeout=120)

def npx_playwright_test(cwd: str) -> dict:
    """Run Playwright tests."""
    return run_command("npx playwright test", cwd=cwd, timeout=180)

def check_node_version() -> dict:
    """Check Node.js version."""
    return run_command("node --version")

def check_npm_version() -> dict:
    """Check npm version."""
    return run_command("npm --version")
