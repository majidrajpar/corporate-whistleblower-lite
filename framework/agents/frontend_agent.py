"""Frontend Agent: Generates React/Vite code for the whistleblowing app."""
from framework.config import invoke_llm
from framework.tools.file_tool import write_file, ensure_dir

SYSTEM_PROMPT = """You are a Frontend Development Agent specialized in React and Vite.
You write clean, accessible, and secure React code.
You follow these principles:
- Functional components with hooks
- Proper form validation
- Error handling and loading states
- CSS Modules for styling
- Fetch API for HTTP requests
- JWT token management in localStorage
- Role-based route guards
- Trust-building UI for anonymous reporting

You generate complete, runnable code files."""

class FrontendAgent:
    def __init__(self):
        self.name = "FrontendAgent"
        self.frontend_dir = "app/frontend"
    
    def run(self, state):
        print(f"[{self.name}] Starting frontend generation...")
        ensure_dir(self.frontend_dir)
        ensure_dir(f"{self.frontend_dir}/src")
        ensure_dir(f"{self.frontend_dir}/src/components")
        ensure_dir(f"{self.frontend_dir}/src/pages")
        ensure_dir(f"{self.frontend_dir}/src/context")
        ensure_dir(f"{self.frontend_dir}/src/utils")
        ensure_dir(f"{self.frontend_dir}/src/styles")
        ensure_dir(f"{self.frontend_dir}/public")
        ensure_dir(f"{self.frontend_dir}/tests")
        
        architecture = state.get("architecture_doc", "")
        
        # Generate package.json
        self._generate_package_json()
        
        # Generate index.html
        self._generate_index_html()
        
        # Generate main entry point
        self._generate_main_jsx()
        
        # Generate App component with routing
        self._generate_app_component(architecture)
        
        # Generate Auth context
        self._generate_auth_context()
        
        # Generate pages
        self._generate_pages(architecture)
        
        # Generate components
        self._generate_components()
        
        # Generate utility files
        self._generate_utils()
        
        # Generate CSS
        self._generate_styles()
        
        # Generate Vite config
        self._generate_vite_config()
        
        # Generate Vitest tests
        self._generate_tests()
        
        print(f"[{self.name}] Frontend generation complete.")
        
        return {
            **state,
            "frontend_code": "generated",
            "current_step": "frontend_complete"
        }
    
    def _generate_package_json(self):
        content = """{
  "name": "whistleblowing-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:ui": "vitest --ui"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.2.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@vitejs/plugin-react": "^4.2.0",
    "jsdom": "^24.0.0",
    "vite": "^5.1.0",
    "vitest": "^1.3.0"
  },
  "license": "MIT"
}"""
        write_file(f"{self.frontend_dir}/package.json", content)
    
    def _generate_index_html(self):
        content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/vite.svg" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Whistleblowing Portal</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>"""
        write_file(f"{self.frontend_dir}/index.html", content)
    
    def _generate_main_jsx(self):
        content = """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)"""
        write_file(f"{self.frontend_dir}/src/main.jsx", content)
    
    def _generate_app_component(self, architecture):
        user_prompt = f"""Generate the complete App.jsx component with React Router routes.

Architecture Context:
{architecture[:1500]}

Routes needed:
- / : Anonymous Report Submission (public)
- /login : Login page (public)
- /dashboard : Internal Audit Dashboard (protected, AUDITOR role)
- /ceo : CEO Dashboard (protected, CEO role)

Requirements:
- Use react-router-dom v6
- Protected route component that checks auth and role
- Redirect unauthorized users to login
- Simple navigation bar
- Logout functionality

Generate complete code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'jsx') or self._extract_code(response.content, 'javascript')
        write_file(f"{self.frontend_dir}/src/App.jsx", code)
        print(f"[{self.name}] Generated src/App.jsx")
    
    def _generate_auth_context(self):
        user_prompt = """Generate the complete AuthContext.jsx file.

Requirements:
- AuthContext with provider
- login(username, password): POST to /api/auth/login, store token in localStorage
- logout(): remove token from localStorage
- user state: { token, role, isAuthenticated }
- useAuth hook
- Automatic token retrieval from localStorage on mount

Generate complete code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'jsx') or self._extract_code(response.content, 'javascript')
        write_file(f"{self.frontend_dir}/src/context/AuthContext.jsx", code)
        print(f"[{self.name}] Generated src/context/AuthContext.jsx")
    
    def _generate_pages(self, architecture):
        pages = {
            "HomePage": "Anonymous report submission page with: category dropdown (5 options), message textarea, optional file upload, trust-building messaging, submit button",
            "LoginPage": "Login page with username/password form, error handling, link to report anonymously",
            "DashboardPage": "Internal Audit Dashboard: list all reports with filters (status, category), view details, update status, escalate to CEO",
            "CEOPage": "CEO Dashboard: view escalated reports only, summary statistics, view details"
        }
        
        for page_name, page_desc in pages.items():
            user_prompt = f"""Generate the complete {page_name}.jsx component.

Description: {page_desc}

Requirements:
- Use React hooks (useState, useEffect)
- Fetch data from backend API
- Handle loading and error states
- Form validation
- CSS classes for styling (not inline styles)
- Trust-building UI elements (security messaging, anonymity assurance)
- Role-based access (where applicable)

Generate complete code."""
            
            response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
            code = self._extract_code(response.content, 'jsx') or self._extract_code(response.content, 'javascript')
            write_file(f"{self.frontend_dir}/src/pages/{page_name}.jsx", code)
            print(f"[{self.name}] Generated src/pages/{page_name}.jsx")
    
    def _generate_components(self):
        components = {
            "ReportForm": "Form for anonymous report submission with category select, message textarea, file input, validation",
            "ReportList": "Table/list of reports with filtering and sorting for dashboard",
            "ReportDetail": "Modal or panel showing full report details with actions (escalate, resolve)",
            "StatsCards": "Summary statistics cards for CEO dashboard (total reports, by category, by status)",
            "Navbar": "Navigation bar with logo, links, logout button"
        }
        
        for comp_name, comp_desc in components.items():
            user_prompt = f"""Generate the complete {comp_name}.jsx component.

Description: {comp_desc}

Requirements:
- Reusable component with props
- Proper event handling
- Error handling
- CSS classes

Generate complete code."""
            
            response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
            code = self._extract_code(response.content, 'jsx') or self._extract_code(response.content, 'javascript')
            write_file(f"{self.frontend_dir}/src/components/{comp_name}.jsx", code)
            print(f"[{self.name}] Generated src/components/{comp_name}.jsx")
    
    def _generate_utils(self):
        user_prompt = """Generate utility files:
1. api.js: Base API configuration with fetch, automatic JWT header injection, error handling
2. validators.js: Form validation helpers (required fields, file size/type validation)

Generate complete code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file(f"{self.frontend_dir}/src/utils/api.js", code)
        print(f"[{self.name}] Generated src/utils/api.js")
    
    def _generate_styles(self):
        user_prompt = """Generate CSS styles for the whistleblowing app.

Requirements:
- Clean, professional design
- Trust-building color scheme (blues, whites - not aggressive colors)
- Laptop-optimized layout (not mobile-first, but responsive enough)
- Form styling with clear labels
- Dashboard table styling
- Button variants (primary, danger, secondary)
- Card components for statistics
- Loading and error state styling
- Animation for trust badges/messages

Generate complete CSS."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'css')
        write_file(f"{self.frontend_dir}/src/styles/index.css", code)
        print(f"[{self.name}] Generated src/styles/index.css")
    
    def _generate_vite_config(self):
        content = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
  },
})"""
        write_file(f"{self.frontend_dir}/vite.config.js", content)
    
    def _generate_tests(self):
        user_prompt = """Generate Vitest test files:
1. tests/components/ReportForm.test.jsx - Test form rendering, validation, submission
2. tests/pages/HomePage.test.jsx - Test page rendering and form integration
3. tests/context/AuthContext.test.jsx - Test login/logout functionality

Use @testing-library/react and vitest.

Generate complete code."""
        
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1)
        code = self._extract_code(response.content, 'javascript')
        write_file(f"{self.frontend_dir}/tests/App.test.jsx", code)
        print(f"[{self.name}] Generated tests/App.test.jsx")
    
    def _extract_code(self, content: str, lang: str) -> str:
        """Extract code block from LLM response."""
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
