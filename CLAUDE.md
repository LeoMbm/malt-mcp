# Philosophy
- Scraping is fragile — keep selectors isolated in `scraping/`, never in `tools/`
- One browser tab at a time — tool calls are serialized, never concurrent
- Headed mode only — Cloudflare blocks headless, don't try to work around it
- Session persistence — browser profile in `~/.malt-mcp/` must survive restarts

# What this project does
MCP server that lets AI assistants manage a Malt.fr freelance account via browser automation (Patchright). No API — everything is scraped from the real site.

# Stack
- Patchright (not Playwright) — anti-detection fork, required for Malt/Cloudflare
- FastMCP v3 with lifespan for browser lifecycle management
- `uv run patchright install chromium` required before first use (bootstrap.py auto-runs this)
- Managed Chromium stored in `~/.malt-mcp/patchright-browsers/` — never uses system Chrome

# Commands
- `uv run malt-mcp --login` — manual browser login (Google OAuth broken, use email/password only)
- `uv run mcp dev malt_mcp_server/server.py` — MCP Inspector for local testing
- `uv run ty check` — type checker (runs in pre-commit, not mypy)

# Architecture decisions
- `tools/` are thin MCP wrappers: auth check → navigate → delegate to `scraping/`
- `scraping/` contains all DOM selectors and page interaction logic
- Tools register via `register_*_tools(mcp)` pattern in `server.py` to avoid circular imports
- `constants.py` holds all Malt URLs and timeouts — never hardcode URLs elsewhere
- `core/browser.py` manages Patchright lifecycle — BrowserManager is injected via FastMCP lifespan context
- Navigation uses `wait_until="commit"` — `networkidle` hangs because Malt SPA never stops fetching

# Patterns to follow
- Every new tool: create `scraping/<name>.py` + `tools/<name>.py`, register in `server.py`
- Scroll-to-load: Malt lazy-loads lists — scroll the conversation list to get all items before scraping
- Auth is checked per-tool call via `require_auth()` — never assume session is valid
- Raise `ToolError` from tool layer, domain exceptions (`MaltAuthError`, etc.) from scraping/core

# Development workflow
See `.claude/rules/dev-workflow.md` for the full mandatory workflow. Summary:
1. **Research first** — tavily search, context7 docs, check linkedin-mcp-server repo for patterns
2. **Design with /mcp-builder** — use the skill when creating/modifying MCP tools
3. **Write clean** — internalize /deslop rules BEFORE coding, not after
4. **Review** — use ECC python-reviewer agent on all code changes
5. **Final /deslop pass** — catch any remaining slop before commit

# Do NOT
- Do not use `channel="chrome"` or system Chrome — use Patchright's managed Chromium to avoid conflicts with running Chrome
- Do not use `headless=True` — Cloudflare will block every request
- Do not use `networkidle` wait strategy — Malt SPA never settles, use `commit`
- Do not put CSS selectors in `tools/` — all DOM access belongs in `scraping/`
- Do not support Google OAuth login — it's detected and blocked by Google
- Do not write code without researching first — check docs, tavily, linkedin-mcp-server
- Do not skip /deslop — AI slop accumulates fast in scraping code

## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
