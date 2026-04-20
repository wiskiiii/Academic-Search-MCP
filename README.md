# scholar-mcp

A combined stdio MCP server for Google Scholar and Semantic Scholar.

## Requirements

- Python managed through `uv`
- `SERPAPI_API_KEY` for Google Scholar via SerpApi
- Optional `SEMANTIC_SCHOLAR_API_KEY` for higher Semantic Scholar rate limits

## Local development

```bash
uv run scholar-mcp
```

## Environment variables

- `SERPAPI_API_KEY`: required for Google Scholar via SerpApi
- `SEMANTIC_SCHOLAR_API_KEY`: optional, increases Semantic Scholar rate limits

## Legacy scripts

The original standalone scripts are kept under `archive/` for reference during migration.

## Run from git

```bash
uvx --from git+https://github.com/<owner>/<repo> scholar-mcp
```

## Claude Code MCP config

```json
{
  "mcpServers": {
    "scholar": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/<owner>/<repo>",
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
