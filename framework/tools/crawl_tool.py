"""Web crawling tool using crawl4ai."""
import asyncio
from crawl4ai import AsyncWebCrawler

def crawl_url_sync(url: str) -> str:
    """Crawl a URL and return markdown content (synchronous wrapper)."""
    try:
        return asyncio.run(_crawl_async(url))
    except Exception as e:
        return f"Error crawling URL: {str(e)}"

async def _crawl_async(url: str) -> str:
    """Async crawl implementation."""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown

def extract_text_from_markdown(markdown: str) -> str:
    """Extract clean text from markdown."""
    # Simple cleanup - remove markdown formatting
    lines = markdown.split('\n')
    cleaned = []
    for line in lines:
        # Remove images
        if line.strip().startswith('!['):
            continue
        # Keep the text
        cleaned.append(line)
    return '\n'.join(cleaned)
