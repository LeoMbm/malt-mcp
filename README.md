# Malt MCP Server

MCP server for [Malt.fr](https://www.malt.fr) that lets AI assistants manage your freelance profile, view stats, track missions, and update availability.

> [!NOTE]
> This project is in early development. Tools and APIs may change.

## Features & Tool Status

| Tool | Description | Status |
|------|-------------|--------|
| `get_profile` | Get freelance profile info (bio, daily rate, skills, rating) | planned |
| `get_statistics` | View profile stats (views, response rate, missions) | planned |
| `get_missions` | List mission conversations from messaging | planned |
| `get_mission_details` | Get details of a specific mission | planned |
| `update_profile` | Modify bio, daily rate, skills, headline | planned |
| `update_availability` | Change availability status | planned |

## Installation

**Prerequisites:** [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

```json
{
  "mcpServers": {
    "malt": {
      "command": "uvx",
      "args": ["malt-mcp@latest"],
      "env": { "UV_HTTP_TIMEOUT": "300" }
    }
  }
}
```

### First-time login

```bash
uvx malt-mcp@latest --login
```

This opens a browser window where you log into Malt manually. Your session is saved locally in `~/.malt-mcp/profile/`.

## CLI Options

| Option | Description |
|--------|-------------|
| `--login` | Open browser to log in and save session |
| `--logout` | Clear stored browser profile |
| `--no-headless` | Show browser window (debug) |
| `--log-level` | Set log level (DEBUG, INFO, WARNING, ERROR) |
| `--timeout` | Browser timeout in ms (default: 5000) |

## How it works

This server uses browser automation ([Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)) to interact with Malt.fr through a real browser session. No unofficial APIs are used.

**Is this safe?** This tool controls a real browser session. It doesn't exploit undocumented APIs or bypass authentication. With normal usage (not bulk scraping) you should be fine. Malt's TOS may prohibit automated tools, so use responsibly.

## Development

```bash
git clone https://github.com/LeoMbm/malt-mcp-server.git
cd malt-mcp-server
uv sync --group dev
pre-commit install
```

### Run tests

```bash
uv run pytest --cov -v
```

## License

[Apache 2.0](LICENSE)
