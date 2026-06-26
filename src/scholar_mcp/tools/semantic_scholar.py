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
        offset: int = 0,
        fields: str = "title,authors,year,citationCount,abstract,url,paperId",
    ) -> str:
        """
        Search for academic papers on Semantic Scholar using keywords. 
        Use this for broad literature queries. 
        Returns paginated results containing basic metadata: Title, Authors, Year, Citations, Paper ID, URL, and a short Abstract preview. 
        Use offset to paginate through results.
        """
        params = {
            "query": query,
            "limit": min(limit, 100),
            "offset": offset,
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

        response_text = "\n".join(formatted_results)

        next_offset = data.get("next")
        total = data.get("total", 0)

        pagination_info = f"\n[Pagination] Showing {len(items)} of {total} total results."
        if next_offset is not None:
            pagination_info += f" To see the next page, call this tool again with offset={next_offset}."
        else:
            pagination_info += " No more results."

        return response_text + pagination_info

    @mcp.tool()
    async def get_paper_bibtex(paper_id: str) -> str:
        """
        Get the exact BibTeX citation for a specific paper by its Semantic Scholar Paper ID. 
        Use this when you only need to cite a paper you already have the ID for. 
        Returns a raw BibTeX string.
        """
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
        """
        Get BibTeX citations for multiple papers at once. 
        Use this to format references for multiple papers efficiently. 
        Returns a list of raw BibTeX strings.
        """
        results = []
        for index, paper_id in enumerate(paper_ids, start=1):
            if index > 1:
                await asyncio.sleep(delay)
            bibtex = await get_paper_bibtex(paper_id)
            results.append(f"# Paper {index}: {paper_id}\n{bibtex}\n")
        return "\n".join(results)

    @mcp.tool()
    async def search_paper_by_title(title: str) -> str:
        """
        Search for a paper by exact title match. 
        Use this when you know the exact name of a paper and want to quickly retrieve its ID, basic metadata, and BibTeX citation in one call. 
        Returns Title, Authors, Year, Paper ID, and BibTeX.
        """
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

    def _format_paper_details(item: dict) -> str:
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
        tldr = (item.get("tldr") or {}).get("text", "")

        lines = [
            f"Title: {title}",
            f"Authors: {author_names}",
            f"Year: {year}",
            f"Citations: {citations}",
            f"Paper ID: {paper_id}",
            f"URL: {url_link}",
        ]
        if tldr:
            lines.append(f"TLDR: {tldr}")
        lines.append(f"Abstract: {abstract_preview}")
        lines.append("---")
        return "\n".join(lines)

    @mcp.tool()
    async def get_paper_recommendations(
        positive_paper_ids: list[str],
        negative_paper_ids: list[str] = None,
        limit: int = 10,
    ) -> str:
        """
        Get recommended papers based on a list of positive (and optionally negative) seed Paper IDs. 
        Use this to discover similar high-quality papers ('snowballing'). 
        Returns full metadata for each recommended paper, including a concise AI-generated TLDR summary.
        """
        data = {"positivePaperIds": positive_paper_ids, "negativePaperIds": negative_paper_ids or []}
        params = {"fields": "title,authors,year,citationCount,abstract,url,paperId,tldr", "limit": min(limit, 500)}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.post("https://api.semanticscholar.org/recommendations/v1/papers", json=data, params=params, headers=_build_headers(), timeout=30.0)
                response.raise_for_status()
                items = response.json().get("recommendedPapers", [])
            except Exception as e:
                return f"Error getting recommendations: {e}"
        if not items:
            return "No recommendations found."
        return "\n".join(_format_paper_details(item) for item in items)

    @mcp.tool()
    async def get_paper_citations(paper_id: str, limit: int = 10, offset: int = 0) -> str:
        """
        Get a list of papers that cite the given Paper ID (Forward citation tracing). 
        Use this to see how a specific paper's research has been built upon by others. 
        Returns paginated full metadata for citing papers, including TLDR summaries.
        """
        params = {"fields": "title,authors,year,citationCount,abstract,url,paperId,tldr", "limit": min(limit, 100), "offset": offset}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations", params=params, headers=_build_headers(), timeout=30.0)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error getting citations: {e}"
        items = [item.get("citingPaper", {}) for item in data.get("data", [])]
        if not items:
            return "No citations found."
        res = "\n".join(_format_paper_details(item) for item in items if item)
        next_offset = data.get("next")
        if next_offset is not None:
            res += f"\n[Pagination] To see the next page, call this tool again with offset={next_offset}."
        return res

    @mcp.tool()
    async def get_paper_references(paper_id: str, limit: int = 10, offset: int = 0) -> str:
        """
        Get a list of papers that are referenced by the given Paper ID (Backward citation tracing). 
        Use this to explore the foundational work a specific paper builds on. 
        Returns paginated full metadata for referenced papers, including TLDR summaries.
        """
        params = {"fields": "title,authors,year,citationCount,abstract,url,paperId,tldr", "limit": min(limit, 100), "offset": offset}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references", params=params, headers=_build_headers(), timeout=30.0)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error getting references: {e}"
        items = [item.get("citedPaper", {}) for item in data.get("data", [])]
        if not items:
            return "No references found."
        res = "\n".join(_format_paper_details(item) for item in items if item)
        next_offset = data.get("next")
        if next_offset is not None:
            res += f"\n[Pagination] To see the next page, call this tool again with offset={next_offset}."
        return res

    @mcp.tool()
    async def get_paper_details(paper_id: str) -> str:
        """
        Get full, in-depth details of a specific paper by its ID. 
        Use this when you need comprehensive information about a single paper. 
        Returns complete metadata including a concise AI-generated TLDR summary and an Open Access PDF URL for full-text reading if available.
        """
        params = {"fields": "title,authors,year,citationCount,abstract,url,paperId,tldr,openAccessPdf"}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}", params=params, headers=_build_headers(), timeout=30.0)
                response.raise_for_status()
                item = response.json()
            except Exception as e:
                return f"Error getting paper details: {e}"
        pdf = item.get("openAccessPdf")
        pdf_url = pdf.get("url") if pdf else "Not available"
        res = _format_paper_details(item)
        res += f"\nOpen Access PDF: {pdf_url}"
        return res

    @mcp.tool()
    async def search_author(query: str, limit: int = 5, offset: int = 0) -> str:
        """
        Search for academic authors by name. 
        Use this to find an author's exact ID and basic metrics. 
        Returns paginated basic profiles including Name, Author ID, H-Index, Total Paper Count, and Total Citations.
        """
        params = {"query": query, "fields": "name,url,paperCount,hIndex,citationCount", "limit": min(limit, 100), "offset": offset}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get("https://api.semanticscholar.org/graph/v1/author/search", params=params, headers=_build_headers(), timeout=30.0)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error searching author: {e}"
        items = data.get("data", [])
        if not items:
            return "No authors found."
        formatted = []
        for a in items:
            formatted.append(f"Name: {a.get('name')}\nAuthor ID: {a.get('authorId')}\nH-Index: {a.get('hIndex')}\nPaper Count: {a.get('paperCount')}\nCitations: {a.get('citationCount')}\nURL: {a.get('url')}\n---")
        res = "\n".join(formatted)
        next_offset = data.get("next")
        if next_offset is not None:
            res += f"\n[Pagination] To see the next page, call this tool again with offset={next_offset}."
        return res

    @mcp.tool()
    async def get_author_details(author_id: str) -> str:
        """
        Get detailed metrics for a specific author and a list of their published papers. 
        Use this to analyze a researcher's output and expertise. 
        Returns Name, Author ID, H-Index, Paper Count, Citations, and a list of their papers with titles, years, and citation counts.
        """
        params = {"fields": "name,url,paperCount,hIndex,citationCount,papers.title,papers.year,papers.citationCount,papers.paperId"}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(f"https://api.semanticscholar.org/graph/v1/author/{author_id}", params=params, headers=_build_headers(), timeout=30.0)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error getting author details: {e}"
        res = f"Name: {data.get('name')}\nAuthor ID: {data.get('authorId')}\nH-Index: {data.get('hIndex')}\nPaper Count: {data.get('paperCount')}\nCitations: {data.get('citationCount')}\nURL: {data.get('url')}\n\nPapers:\n"
        papers = data.get("papers", [])
        for p in papers:
            res += f"- {p.get('title')} ({p.get('year')}) | Citations: {p.get('citationCount')} | ID: {p.get('paperId')}\n"
        return res
