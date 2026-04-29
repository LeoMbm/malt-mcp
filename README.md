# Malt MCP Server

[![PyPI](https://img.shields.io/pypi/v/malt-mcp?color=blue)](https://pypi.org/project/malt-mcp/)
[![Python](https://img.shields.io/badge/python-3.12+-3776ab?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-%233fb950?labelColor=32383f)](LICENSE)

Give Claude and any MCP-compatible AI assistant access to your [Malt.fr](https://www.malt.fr) freelance account — profile, stats, and missions.

## Tools

| Tool | Description | Status |
|------|-------------|--------|
| `get_profile` | Get freelance profile info (bio, daily rate, skills, rating) | working |
| `get_statistics` | View profile stats (views, response rate, missions) | working |
| `get_missions` | List mission conversations from messaging | working |
| `get_mission_details` | Get full details of a specific mission (budget, skills, messages) | working |

## 📦 Installation

### uvx (recommended)

**Prerequisites:** [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

This opens a browser window where you log into Malt manually. Your session is saved locally in `~/.malt-mcp/profile/` and persists across restarts.

> [!NOTE]
> Only email/password login is supported. Google OAuth is detected and blocked by Google when automated.

### Docker (coming soon)

### MCP Bundle for Claude Desktop (coming soon)

## ⚙️ CLI Options

| Option | Description |
|--------|-------------|
| `--login` | Open browser to log in and save session |
| `--logout` | Clear stored browser profile |
| `--no-headless` | Show browser window (debug) |
| `--log-level` | Set log level (DEBUG, INFO, WARNING, ERROR) |
| `--timeout` | Browser timeout in ms (default: 5000) |

## ❗ Troubleshooting

**Login issues:**

- Only email/password login works. Google OAuth will fail.
- If your session expires, re-run `uvx malt-mcp@latest --login`.
- Malt may show a Cloudflare challenge on first load — the browser handles it automatically, but it may take a few seconds.

**Timeout issues:**

- If pages fail to load or elements aren't found, increase the timeout: `--timeout 10000`
- Slow connections may need higher values (e.g., `15000`)

**Browser issues:**

- This server requires a **headed** (visible) browser. Headless mode is blocked by Cloudflare.
- On first run, Patchright downloads a Chromium browser (~200 MB). This is automatic.

## 🔒 Privacy & Security

This server uses browser automation ([Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)) to interact with Malt.fr through a real browser session. No unofficial APIs are used.

- **Your credentials stay local.** Login happens in your browser; cookies are stored in `~/.malt-mcp/profile/`.
- **Read-only.** All current tools only read data — nothing is modified on your Malt account.
- **No data leaves your machine.** The MCP server runs locally and communicates only with Malt.fr.

> [!IMPORTANT]
> Malt's Terms of Service may prohibit automated tools. With normal usage (not bulk scraping) you should be fine. Use responsibly.

## 🐍 Development

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture guidelines.

```bash
git clone https://github.com/LeoMbm/malt-mcp-server.git
cd malt-mcp-server
uv sync --group dev
pre-commit install
```

**Run the MCP Inspector** (local testing):

```bash
uv run mcp dev malt_mcp_server/server.py
```

**Run tests:**

```bash
uv run pytest --cov -v
```

**Type check:**

```bash
uv run ty check
```

## License

[Apache 2.0](LICENSE)
