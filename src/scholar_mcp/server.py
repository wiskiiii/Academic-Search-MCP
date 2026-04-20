from mcp.server.fastmcp import FastMCP

from scholar_mcp.tools.google_scholar import register_google_scholar_tools
from scholar_mcp.tools.semantic_scholar import register_semantic_scholar_tools

mcp = FastMCP("Scholar MCP")

register_google_scholar_tools(mcp)
register_semantic_scholar_tools(mcp)


def main() -> None:
    mcp.run()
