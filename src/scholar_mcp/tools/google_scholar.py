from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

from scholar_mcp.config import SERPAPI_API_KEY


def register_google_scholar_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def search_google_scholar(query: str, num_results: int = 5) -> str:
        """
        Search Google Scholar for academic papers.

        Args:
            query: The search query.
            num_results: Number of results to return.
        """
        if not SERPAPI_API_KEY:
            return "SERPAPI_API_KEY is not set."

        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": num_results,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://serpapi.com/search", params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error querying SerpApi: {e}"

        items = data.get("organic_results")
        if not items:
            return "No results found."

        formatted_results = []
        for item in items:
            title = item.get("title", "No Title")
            link = item.get("link", "No Link")
            snippet = item.get("snippet", "No snippet available.")
            publication_info = item.get("publication_info", {}).get("summary", "")
            citations = item.get("inline_links", {}).get("cited_by", {}).get("total", 0)
            result_id = item.get("result_id", "")

            formatted_results.append(
                "\n".join(
                    [
                        f"Title: {title}",
                        f"Publication: {publication_info}",
                        f"Link: {link}",
                        f"Citations: {citations}",
                        f"Result ID: {result_id}",
                        f"Snippet: {snippet}",
                        "---",
                    ]
                )
            )

        return "\n".join(formatted_results)
