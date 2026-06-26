import os
import httpx
import asyncio

API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

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

async def test_get_paper_details(paper_id: str):
    params = {"fields": "title,authors,year,citationCount,abstract,url,paperId,tldr,openAccessPdf"}
    headers = {"x-api-key": API_KEY, "User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}", params=params, headers=headers, timeout=30.0)
        item = response.json()
        
    pdf = item.get("openAccessPdf")
    pdf_url = pdf.get("url") if pdf else "Not available"
    res = _format_paper_details(item)
    res += f"\nOpen Access PDF: {pdf_url}"
    print(res)

if __name__ == "__main__":
    # Test using the paper ID we used previously
    asyncio.run(test_get_paper_details("649def34f8be52c8b66281af98ae884c09aef38b"))
