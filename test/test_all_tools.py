import os
import httpx
import asyncio
import time

API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

def _build_headers():
    return {
        "x-api-key": API_KEY,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

async def search_papers():
    print("\n--- Testing search_papers ---")
    params = {"query": "generative ai", "limit": 1, "offset": 0, "fields": "title,authors,year,citationCount,abstract,url,paperId"}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = (await client.get("https://api.semanticscholar.org/graph/v1/paper/search", params=params, headers=_build_headers())).json()
    item = data.get("data", [{}])[0]
    author_names = ", ".join(a.get("name") for a in item.get("authors", [])[:3])
    print(f"Title: {item.get('title')}\nAuthors: {author_names}\nYear: {item.get('year')}\nCitations: {item.get('citationCount')}\nPaper ID: {item.get('paperId')}\nURL: {item.get('url')}\nAbstract: {item.get('abstract')[:50]}...\n---")

async def get_paper_bibtex():
    print("\n--- Testing get_paper_bibtex ---")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = (await client.get("https://api.semanticscholar.org/graph/v1/paper/649def34f8be52c8b66281af98ae884c09aef38b", params={"fields": "title,citationStyles"}, headers=_build_headers())).json()
    print(data.get('citationStyles', {}).get('bibtex'))

async def search_paper_by_title():
    print("\n--- Testing search_paper_by_title ---")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = (await client.get("https://api.semanticscholar.org/graph/v1/paper/search/match", params={"query": "Attention Is All You Need", "fields": "paperId,title,authors,year,citationStyles"}, headers=_build_headers())).json()
    paper = data.get("data", [{}])[0]
    author_names = ", ".join(a.get("name") for a in paper.get("authors", []))
    print(f"Found: {paper.get('title')}\nAuthors: {author_names}\nYear: {paper.get('year')}\nPaper ID: {paper.get('paperId')}\n\nBibTeX:\n{paper.get('citationStyles', {}).get('bibtex', '')}")

async def search_author():
    print("\n--- Testing search_author ---")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = (await client.get("https://api.semanticscholar.org/graph/v1/author/search", params={"query": "Yoshua Bengio", "fields": "name,url,paperCount,hIndex,citationCount", "limit": 1}, headers=_build_headers())).json()
    a = data.get("data", [{}])[0]
    print(f"Name: {a.get('name')}\nAuthor ID: {a.get('authorId')}\nH-Index: {a.get('hIndex')}\nPaper Count: {a.get('paperCount')}\nCitations: {a.get('citationCount')}\nURL: {a.get('url')}\n---")

async def get_author_details():
    print("\n--- Testing get_author_details ---")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = (await client.get("https://api.semanticscholar.org/graph/v1/author/144136932", params={"fields": "name,url,paperCount,hIndex,citationCount,papers.title,papers.year,papers.citationCount,papers.paperId"}, headers=_build_headers())).json()
    print(f"Name: {data.get('name')}\nAuthor ID: {data.get('authorId')}\nH-Index: {data.get('hIndex')}\nPaper Count: {data.get('paperCount')}\nCitations: {data.get('citationCount')}\nURL: {data.get('url')}\n\nPapers:\n- {data.get('papers', [{}])[0].get('title')}...")

async def main():
    print("Testing MCP tools logic with 1.5s delay...")
    await search_papers()
    time.sleep(1.5)
    await get_paper_bibtex()
    time.sleep(1.5)
    await search_paper_by_title()
    time.sleep(1.5)
    await search_author()
    time.sleep(1.5)
    await get_author_details()

if __name__ == "__main__":
    asyncio.run(main())
