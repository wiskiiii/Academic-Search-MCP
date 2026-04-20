from __future__ import annotations

import asyncio

import httpx
from mcp.server.fastmcp import FastMCP

from scholar_mcp.config import SEMANTIC_SCHOLAR_API_KEY


def _build_headers() -> dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
    }
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
    return headers


def register_semantic_scholar_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def search_papers(
        query: str,
        limit: int = 5,
        fields: str = "title,authors,year,citationCount,abstract,url,paperId",
    ) -> str:
        """Search for academic papers on Semantic Scholar."""
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": fields,
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params=params,
                    headers=_build_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error querying Semantic Scholar: {e}"

        items = data.get("data", [])
        if not items:
            return "No results found."

        formatted_results = []
        for item in items:
            title = item.get("title") or "No Title"
            paper_id = item.get("paperId") or ""
            year = item.get("year") or "N/A"
            citations = item.get("citationCount") or 0
            url_link = item.get("url") or ""
            authors = item.get("authors") or []
            author_names = ", ".join((a.get("name") or "") for a in authors[:3])
            if len(authors) > 3:
                author_names += f" et al. ({len(authors)} authors)"
            abstract = item.get("abstract") or ""
            abstract_preview = abstract[:200] + "..." if len(abstract) > 200 else abstract

            formatted_results.append(
                "\n".join(
                    [
                        f"Title: {title}",
                        f"Authors: {author_names}",
                        f"Year: {year}",
                        f"Citations: {citations}",
                        f"Paper ID: {paper_id}",
                        f"URL: {url_link}",
                        f"Abstract: {abstract_preview}",
                        "---",
                    ]
                )
            )

        return "\n".join(formatted_results)

    @mcp.tool()
    async def get_paper_bibtex(paper_id: str) -> str:
        """Get BibTeX citation for a specific paper."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(
                    f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}",
                    params={"fields": "title,citationStyles"},
                    headers=_build_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error fetching paper: {e}"

        citation_styles = data.get("citationStyles", {})
        bibtex = citation_styles.get("bibtex")
        if not bibtex:
            return "BibTeX not available for this paper."
        return bibtex

    @mcp.tool()
    async def get_papers_bibtex_batch(paper_ids: list[str], delay: float = 1.0) -> str:
        """Get BibTeX citations for multiple papers with rate limiting."""
        results = []
        for index, paper_id in enumerate(paper_ids, start=1):
            if index > 1:
                await asyncio.sleep(delay)
            bibtex = await get_paper_bibtex(paper_id)
            results.append(f"# Paper {index}: {paper_id}\n{bibtex}\n")
        return "\n".join(results)

    @mcp.tool()
    async def search_paper_by_title(title: str) -> str:
        """Search for a paper by title match and return its BibTeX."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search/match",
                    params={"query": title, "fields": "paperId,title,authors,year,citationStyles"},
                    headers=_build_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 429:
                    return f"Error searching paper: {e}"
                try:
                    fallback_response = await client.get(
                        "https://api.semanticscholar.org/graph/v1/paper/search",
                        params={"query": title, "limit": 1, "fields": "paperId,title,authors,year,citationStyles"},
                        headers=_build_headers(),
                        timeout=30.0,
                    )
                    fallback_response.raise_for_status()
                    data = fallback_response.json()
                except Exception as fallback_error:
                    return f"Error searching paper: {fallback_error}"
            except Exception as e:
                return f"Error searching paper: {e}"

        items = data.get("data", [])
        if not items:
            return "No matching paper found."

        paper = items[0]
        authors = paper.get("authors") or []
        author_names = ", ".join((a.get("name") or "") for a in authors)
        bibtex = (paper.get("citationStyles") or {}).get("bibtex", "BibTeX not available")
        return "\n".join(
            [
                f"Found: {paper.get('title', '')}",
                f"Authors: {author_names}",
                f"Year: {paper.get('year', 'N/A')}",
                f"Paper ID: {paper.get('paperId', '')}",
                "",
                f"BibTeX:\n{bibtex}",
            ]
        )
