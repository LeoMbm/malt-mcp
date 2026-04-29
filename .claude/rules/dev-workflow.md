# Development Workflow — malt-mcp-server

This is the MANDATORY workflow for every feature, tool, or bug fix. No exceptions.

## Phase 0: Research (BEFORE writing any code)

1. **Search docs** — use `context7` MCP (`resolve-library-id` → `query-docs`) for FastMCP, Patchright, MCP protocol
2. **Search web** — use `tavily_search` for patterns, known issues, prior art
3. **Check linkedin-mcp-server** — reference repo at `github.com/stickerdaniel/linkedin-mcp-server`. Search it for patterns when adding new scraping tools, browser interactions, or MCP tool design
4. **Check existing codebase** — use code-review-graph MCP tools before Grep/Glob

Do NOT skip research. Even for "simple" changes — check how similar MCP servers handle it first.

## Phase 1: Design (use mcp-builder skill)

- Invoke `/mcp-builder` skill when creating or modifying MCP tools
- Follow its patterns for tool annotations, error handling, and server structure
- Design the tool interface before writing scraping logic

## Phase 2: Write clean code (no-slop principles)

Write code that doesn't need cleanup. Internalize these rules BEFORE writing:

- **No unnecessary comments** — if the code is clear, don't comment it. Match the existing file's comment density
- **No defensive overkill** — don't add try/catch or None-checks on trusted internal paths. Only validate at boundaries (user input, DOM scraping results)
- **No type escape hatches** — no `Any` casts, no `# type: ignore` unless genuinely unavoidable
- **No verbose wrappers** — if a function just calls another function, question whether it needs to exist
- **Match existing style** — read the file before editing. Match its patterns, naming, spacing
- **No AI tells** — no "robust", "comprehensive", "elegant" in comments. No docstrings that restate the function name. No TODO comments for things you're about to do

These come from the `/deslop` skill. The goal is to write code that passes deslop review on the first try.

## Phase 3: Review

- Use `everything-claude-code:python-reviewer` agent to review Python code
- Use `everything-claude-code:python-review` skill for detailed review
- Fix all CRITICAL and HIGH issues before considering done

## Phase 4: Final pass

- Run `/deslop` as a final check — remove anything that slipped through
- Don't wait for git diff — just run it on the current branch vs main

## Reference repo

linkedin-mcp-server (github.com/stickerdaniel/linkedin-mcp-server) is the architectural inspiration. When in doubt about how to structure a new tool or scraping module, check how they did it.
