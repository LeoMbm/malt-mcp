"""Browser lifecycle management using Patchright with persistent context."""

import logging
import os
import stat
from pathlib import Path
from typing import Any

from patchright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)
from patchright.async_api import Error as PlaywrightError

from malt_mcp_server.constants import (
    BROWSER_DIR,
    DEFAULT_TIMEOUT_MS,
    DEFAULT_USER_DATA_DIR,
    PRIVATE_DIR_MODE,
)
from malt_mcp_server.core.exceptions import MaltNetworkError

logger = logging.getLogger(__name__)


def _harden_directory(path: Path) -> None:
    """Ensure directories from path up to .malt-mcp are owner-only (0o700).

    Stops at the .malt-mcp anchor directory. Does nothing if the path
    is not inside a .malt-mcp tree.
    """
    if os.name == "nt":
        return
    d = path if path.is_dir() else path.parent
    if not any(p.name == ".malt-mcp" for p in (d, *d.parents)):
        return
    for p in (d, *d.parents):
        if p.name == ".malt-mcp":
            if p.is_dir() and stat.S_IMODE(p.stat().st_mode) != PRIVATE_DIR_MODE:
                p.chmod(PRIVATE_DIR_MODE)
            return
        if p.is_dir() and stat.S_IMODE(p.stat().st_mode) != PRIVATE_DIR_MODE:
            p.chmod(PRIVATE_DIR_MODE)


def _secure_mkdir(path: Path) -> None:
    """Create directory with owner-only permissions."""
    path.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        path.chmod(PRIVATE_DIR_MODE)


class BrowserManager:
    """Async context manager for Patchright browser with persistent profile."""

    def __init__(
        self,
        user_data_dir: str | Path = DEFAULT_USER_DATA_DIR,
        headless: bool = True,
        timeout: int = DEFAULT_TIMEOUT_MS,
        **launch_options: Any,  # noqa: ANN401
    ) -> None:
        self.user_data_dir = str(Path(user_data_dir).expanduser())
        self.headless = headless
        self.timeout = timeout
        self.launch_options = launch_options

        self._playwright: Playwright | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        """Launch browser with persistent context."""
        _secure_mkdir(BROWSER_DIR)
        _secure_mkdir(Path(self.user_data_dir))
        _harden_directory(Path(self.user_data_dir))

        self._playwright = await async_playwright().start()

        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            channel="chrome",
            headless=self.headless,
            no_viewport=True,
            **self.launch_options,
        )
        self._context.set_default_timeout(self.timeout)

        pages = self._context.pages
        self._page = pages[0] if pages else await self._context.new_page()
        logger.info("Browser started with profile: %s", self.user_data_dir)

    async def stop(self) -> None:
        """Close browser and clean up resources."""
        if self._context:
            await self._context.close()
            self._context = None
            self._page = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Browser stopped")

    @property
    def page(self) -> Page:
        if self._page is None:
            msg = "Browser not started. Call start() first."
            raise RuntimeError(msg)
        return self._page

    @property
    def context(self) -> BrowserContext:
        if self._context is None:
            msg = "Browser not started. Call start() first."
            raise RuntimeError(msg)
        return self._context

    async def navigate(self, url: str) -> Page:
        """Navigate to URL and wait for load."""
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
        except PlaywrightError as e:
            raise MaltNetworkError(f"Failed to navigate to {url}: {e}") from e
        return self.page

    async def __aenter__(self) -> "BrowserManager":
        await self.start()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.stop()
