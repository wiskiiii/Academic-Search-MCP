# scholar-mcp

A combined stdio MCP server for Google Scholar and Semantic Scholar.

## Requirements

- Python managed through `uv`
- `SERPAPI_API_KEY` for Google Scholar via [SerpApi](https://serpapi.com/)
- Optional `SEMANTIC_SCHOLAR_API_KEY` for higher Semantic Scholar rate limits

## Local development

```bash
uv run scholar-mcp
```

## Environment variables

- `SERPAPI_API_KEY`: required for Google Scholar via [SerpApi](https://serpapi.com/)
- `SEMANTIC_SCHOLAR_API_KEY`: optional, increases Semantic Scholar rate limits


## Run from git

```bash
uvx --from git+https://github.com/wiskiiii/Academic-Search-MCP.git scholar-mcp
```

## Claude Code MCP config

```json
{
  "mcpServers": {
    "scholar": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/wiskiiii/Academic-Search-MCP.git",
        "scholar-mcp"
      ],
      "env": {
        "SERPAPI_API_KEY": "your-serpapi-key",
        "SEMANTIC_SCHOLAR_API_KEY": "your-semantic-scholar-key"
      },
      "type": "stdio"
    }
  }
}
```
