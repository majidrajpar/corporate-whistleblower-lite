"""Web search tool using duckduckgo-search."""
from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            output = []
            for i, r in enumerate(results, 1):
                output.append(f"{i}. {r['title']}\n   {r['href']}\n   {r['body']}")
            return "\n\n".join(output)
    except Exception as e:
        return f"Error searching web: {str(e)}"

def search_news(query: str, max_results: int = 3) -> str:
    """Search news using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = ddgs.news(query, max_results=max_results)
            output = []
            for i, r in enumerate(results, 1):
                output.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['body']}")
            return "\n\n".join(output)
    except Exception as e:
        return f"Error searching news: {str(e)}"
