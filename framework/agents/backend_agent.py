"""Backend Agent: Generates production-ready Node.js/Express/Prisma code."""
from framework.config import invoke_llm
from framework.tools.file_tool import write_file, ensure_dir
from framework.tools.shell_tool import run_command

SYSTEM_PROMPT = """You are a Backend Development Agent specialized in Node.js, Express, and Prisma.
You write production-ready, secure code following best practices:
- Input validation and sanitization
- Proper error handling
- JWT authentication
- Rate limiting
- Secure file uploads
- SQL injection prevention (via Prisma)
- Structured logging

You generate complete, runnable code files."""

class BackendAgent:
    def __init__(self):
        self.name = "BackendAgent"
        self.backend_dir = "app/backend"
    
    def run(self, state):
        print(f"[{self.name}] Starting backend generation...")
        ensure_dir(self.backend_dir)
        ensure_dir(f"{self.backend_dir}/src")
        ensure_dir(f"{self.backend_dir}/src/routes")
        ensure_dir(f"{self.backend_dir}/src/middleware")
        ensure_dir(f"{self.backend_dir}/src/utils")
        ensure_dir(f"{self.backend_dir}/uploads")
        ensure_dir(f"{self.backend_dir}/tests")
        
        architecture = state.get("architecture_doc", "")
        
        # Generate package.json
        self._generate_package_json()
        
        # Generate .env.example
        self._generate_env_example()
        
        # Generate main server file
        self._generate_server(architecture)
        
        # Generate auth middleware
        self._generate_auth_middleware()
        
        # Generate route files
        self._generate_routes(architecture)
        
        # Generate seed script
        self._generate_seed_script()
        
        # Generate Jest test file
        self._generate_tests()
        
        print(f"[{self.name}] Backend generation complete.")
        
        return {
            **state,
            "backend_code": "generated",
            "current_step": "backend_complete"
        }
    
    def _generate_package_json(self):
        content = """{
  "name": "whistleblowing-backend",
  "version": "1.0.0",
  "description": "Anonymous whistleblowing reporting backend",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js",
    "test": "jest --coverage",
    "db:generate": "prisma generate",
    "db:migrate": "prisma migrate dev",
    "db:seed": "node prisma/seed.js"
  },
  "dependencies": {
    "@prisma/client": "^5.10.0",
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "crypto": "^1.0.1",
    "dotenv": "^16.4.5",
    "express": "^4.18.3",
    "express-rate-limit": "^7.2.0",
    "helmet": "^7.1.0",
    "jsonwebtoken": "^9.0.2",
    "multer": "^1.4.5-lts.1",
    "prisma": "^5.10.0"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "nodemon": "^3.1.0",
    "supertest": "^6.3.4"
  },
  "license": "MIT"
}"""
        write_file(f"{self.backend_dir}/package.json", content)
    
    def _generate_env_example(self):
        content = """# Database
DATABASE_URL="file:./dev.db"

# JWT
JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"
JWT_EXPIRES_IN="24h"

# Initial Users (set on first run)
INITIAL_AUDITOR_USER="auditor"
INITIAL_AUDITOR_PASS="auditor123"
INITIAL_CEO_USER="ceo"
INITIAL_CEO_PASS="ceo123"

# Server
PORT=3001
NODE_ENV="development"
"""
        write_file(f"{self.backend_dir}/.env.example", content)
    
    def _generate_server(self, architecture):
        user_prompt = f"""Generate the complete main server.js file for an Express whistleblowing backend.

Architecture Context:
{architecture[:2000]}

Requirements:
- Express app with JSON parsing
- CORS configuration (allow frontend origin)
- Helmet.js for security headers
- Rate limiting: 5 reports per hour per IP (anonymous route)
- General rate limit: 100 requests per 15 min per IP
- JWT auth middleware
- File upload configuration (Multer): images and PDFs, max 5MB
- Routes: /api/auth, /api/reports, /api/upload, /api/audit-log
- Error handling middleware
- 404 handler
- Start server on PORT from env

Generate complete, production-ready code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        server_code = self._extract_code(response.content, 'javascript')
        write_file(f"{self.backend_dir}/src/server.js", server_code)
        print(f"[{self.name}] Generated src/server.js")
    
    def _generate_auth_middleware(self):
        user_prompt = """Generate the auth middleware for JWT verification and role checking.

Requirements:
- verifyToken: validates JWT from Authorization header
- requireRole(role): checks if user has specific role (AUDITOR or CEO)
- hashPassword and comparePassword utilities using bcryptjs
- generateToken utility

Generate complete code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file(f"{self.backend_dir}/src/middleware/auth.js", code)
        print(f"[{self.name}] Generated src/middleware/auth.js")
    
    def _generate_routes(self, architecture):
        routes = {
            "auth": "Auth routes: POST /login with username/password, returns JWT",
            "reports": "Report routes: POST / (anonymous create), GET / (auditor list with filters), PUT /:id/status (auditor update), POST /:id/escalate (auditor escalate to CEO), GET /escalated (CEO view only)",
            "upload": "Upload route: POST / single file upload with Multer, returns file path",
            "audit-log": "Audit log route: GET / (auditor/CEO view), POST / (create log entry)"
        }
        
        for route_name, route_desc in routes.items():
            user_prompt = f"""Generate the complete {route_name}.js route file for Express.

Description: {route_desc}

Requirements:
- Use Prisma client for database operations
- Proper error handling with try/catch
- Return JSON responses
- Include relevant middleware (auth, role checks)
- For anonymous routes (report creation), do NOT require auth but DO hash IP for rate limiting
- For audit log creation, automatically log user actions

Generate complete code."""
            
            response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
            code = self._extract_code(response.content, 'javascript')
            write_file(f"{self.backend_dir}/src/routes/{route_name}.js", code)
            print(f"[{self.name}] Generated src/routes/{route_name}.js")
    
    def _generate_seed_script(self):
        user_prompt = """Generate a Prisma seed script (prisma/seed.js) that creates initial users from environment variables.

Requirements:
- Read INITIAL_AUDITOR_USER, INITIAL_AUDITOR_PASS, INITIAL_CEO_USER, INITIAL_CEO_PASS from env
- Hash passwords with bcryptjs
- Create users with roles AUDITOR and CEO
- Skip if users already exist
- Use Prisma client

Generate complete code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file(f"{self.backend_dir}/prisma/seed.js", code)
        print(f"[{self.name}] Generated prisma/seed.js")
    
    def _generate_tests(self):
        user_prompt = """Generate Jest test file (tests/app.test.js) for the whistleblowing backend.

Test cases:
1. POST /api/reports - anonymous report creation (success)
2. POST /api/reports - rate limiting (should block after 5)
3. POST /api/auth/login - valid credentials
4. POST /api/auth/login - invalid credentials
5. GET /api/reports - authenticated auditor access
6. GET /api/reports/escalated - CEO access only
7. PUT /api/reports/:id/status - status update
8. POST /api/reports/:id/escalate - escalation

Use supertest for HTTP requests. Use a test database or in-memory mock.

Generate complete code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file(f"{self.backend_dir}/tests/app.test.js", code)
        print(f"[{self.name}] Generated tests/app.test.js")
    
    def _extract_code(self, content: str, lang: str) -> str:
        """Extract code block from LLM response."""
        import re
        pattern = rf'```{lang}\\n(.*?)```'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try without language specifier
        pattern = r'```\n(.*?)```'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
        
        # Return raw content if no code block found
        return content
