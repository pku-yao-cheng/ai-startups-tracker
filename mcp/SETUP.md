# MCP Server Setup

This project uses several MCP (Model Context Protocol) servers to gather real-time data from news sources, community platforms, and research tools.

## Required MCP Servers

### 1. Trends Hub
Aggregates trending news from multiple sources (NYTimes, BBC, The Verge, 36kr, Zhihu, etc.)

```bash
# Auto-installed via npx
npx -y mcp-trends-hub
```

### 2. Hacker News
Access top/best/new/show stories and comments from Hacker News.

```bash
npx -y mcp-hacker-news
```

### 3. Reddit
Browse Reddit subreddits for AI community signals.

```bash
# Requires uvx (install via: pip install uv)
uvx mcp-server-reddit
```

## Optional MCP Servers

### 4. Deep Research
Comprehensive research agent for company deep dives.

- Source: [Claude Code Deep Research](https://github.com/anthropics/claude-code-deep-research)
- Setup: Clone the repo, create a Python venv, and point the MCP config to `deep_research.py`

### 5. Notion
Sync research notes to Notion pages.

- Source: [@notionhq/notion-mcp-server](https://www.npmjs.com/package/@notionhq/notion-mcp-server)
- Requires: `NOTION_TOKEN` environment variable

## Installation

Add the MCP servers to your `~/.claude.json` file. See `mcp-servers.json` for the full configuration template.

Example for `~/.claude.json`:

```json
{
  "mcpServers": {
    "trends-hub": {
      "type": "stdio",
      "command": "/opt/homebrew/bin/npx",
      "args": ["-y", "mcp-trends-hub"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    },
    "hacker-news": {
      "type": "stdio",
      "command": "/opt/homebrew/bin/npx",
      "args": ["-y", "mcp-hacker-news"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    },
    "reddit": {
      "type": "stdio",
      "command": "/opt/homebrew/bin/uvx",
      "args": ["mcp-server-reddit"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

## Built-in Tools Also Used

The skill also relies on Claude Code's built-in tools:
- **WebSearch** - Targeted searches with `site:` filters (TechCrunch, Bloomberg, CNBC, etc.)
- **WebFetch** - Fetch and analyze specific URLs
