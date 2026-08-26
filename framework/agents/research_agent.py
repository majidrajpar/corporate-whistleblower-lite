"""Research Agent: Benchmarks whistleblowing apps and researches UI/UX patterns."""
from framework.config import invoke_llm
from framework.tools.file_tool import write_file
from framework.tools.search_tool import search_web
from framework.tools.crawl_tool import crawl_url_sync

SYSTEM_PROMPT = """You are a Research Agent specialized in analyzing whistleblowing and ethics reporting systems.
Your task is to research small-scale, open-source whistleblowing applications and identify best practices for:
1. Anonymous reporting UI/UX patterns that build trust
2. Dashboard designs for auditors and executives
3. Security considerations for anonymous systems
4. Feature comparison of existing solutions

You must produce:
- A comprehensive research report
- High-level Mermaid wireframe diagrams for the UI
- Specific recommendations for our KSA real estate company context"""

class ResearchAgent:
    def __init__(self):
        self.name = "ResearchAgent"
    
    def run(self, state):
        print(f"[{self.name}] Starting research phase...")
        
        # Search for whistleblowing apps and best practices
        search_queries = [
            "open source whistleblowing application small business",
            "anonymous reporting platform UI UX best practices",
            "whistleblowing dashboard design internal audit",
            "ethics hotline web application features"
        ]
        
        search_results = []
        for query in search_queries:
            print(f"[{self.name}] Searching: {query}")
            results = search_web(query, max_results=3)
            search_results.append(f"## Query: {query}\n{results}\n")
        
        # Compile research prompt
        research_input = "\n".join(search_results)
        
        user_prompt = f"""Based on the following web search results, produce a comprehensive research report for building a whistleblowing web application for a KSA real estate company.

Search Results:
{research_input}

Requirements:
- Anonymous reporting (no tracking)
- File upload capability (images, PDFs)
- Internal Audit dashboard
- CEO dashboard (separate view)
- Rate limiting (5/hour per IP)
- 5 report categories max
- Self-hosted, no external data sharing
- Laptop-optimized UI (not mobile-first)

Your output must include:
1. Executive Summary
2. Benchmark Analysis of small existing solutions
3. Trust-Building UI/UX Recommendations
4. Dashboard Layout Recommendations
5. Security Best Practices for Anonymous Systems
6. Feature Recommendations (prioritized)
7. High-Level Mermaid Wireframes for:
   - Anonymous Submission Page
   - Internal Audit Dashboard
   - CEO Dashboard
"""
        
        print(f"[{self.name}] Invoking LLM for research synthesis...")
        response = invoke_llm(SYSTEM_PROMPT, user_prompt, temperature=0.3)
        research_report = response.content
        
        # Save research report
        write_file("workspace/research_report.md", research_report)
        print(f"[{self.name}] Research report saved to workspace/research_report.md")
        
        # Extract mockups from the report and save separately
        # The LLM should include Mermaid diagrams in the report
        mockups = self._extract_mockups(research_report)
        write_file("workspace/mockups.mmd", mockups)
        print(f"[{self.name}] Mockups saved to workspace/mockups.mmd")
        
        return {
            **state,
            "research_report": research_report,
            "mockups": mockups,
            "current_step": "research_complete"
        }
    
    def _extract_mockups(self, report: str) -> str:
        """Extract Mermaid diagrams from the research report."""
        lines = report.split('\n')
        mockup_lines = []
        in_mockup = False
        
        for line in lines:
            if '```mermaid' in line.lower() or 'mermaid' in line.lower():
                in_mockup = True
                mockup_lines.append('```mermaid')
            elif in_mockup and line.strip().startswith('```'):
                mockup_lines.append('```')
                in_mockup = False
            elif in_mockup:
                mockup_lines.append(line)
        
        return '\n'.join(mockup_lines) if mockup_lines else "No mockups found in report"
