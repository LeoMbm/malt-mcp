from dataclasses import dataclass

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

from malt_mcp_server.core.browser import BrowserManager
from malt_mcp_server.tools.missions import register_missions_tools
from malt_mcp_server.tools.profile import register_profile_tools
from malt_mcp_server.tools.stats import register_stats_tools


@dataclass
class _BrowserConfig:
    headless: bool = False
    timeout: int = 30_000


_config = _BrowserConfig()


def configure_browser(
    *,
    headless: bool = False,
    timeout: int = 30_000,
) -> None:
    _config.headless = headless
    _config.timeout = timeout


@lifespan
async def browser_lifespan(server: FastMCP) -> dict[str, BrowserManager]:  # noqa: ARG001
    browser = BrowserManager(headless=_config.headless, timeout=_config.timeout)
    await browser.start()
    try:
        yield {"browser": browser}
    finally:
        await browser.stop()


mcp = FastMCP(
    "malt-mcp",
    lifespan=browser_lifespan,
    instructions="MCP server for managing your Malt.fr freelance account.",
)

register_profile_tools(mcp)
register_stats_tools(mcp)
register_missions_tools(mcp)
