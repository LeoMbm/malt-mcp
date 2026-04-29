"""Auto-install Patchright Chrome browser on first run."""

import logging
import subprocess
import sys

from malt_mcp_server.constants import BROWSER_DIR

logger = logging.getLogger(__name__)

_INSTALL_MARKER = BROWSER_DIR / ".chrome-installed"


def ensure_browser() -> None:
    """Install Chrome via Patchright if not already installed."""
    if _INSTALL_MARKER.exists():
        return

    logger.info("First run: installing Chrome browser via Patchright...")

    try:
        subprocess.run(
            [sys.executable, "-m", "patchright", "install", "chrome"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error("Failed to install Chrome: %s", e.stderr)
        msg = (
            "Could not install Chrome via Patchright. "
            "Run manually: uv run patchright install chrome"
        )
        raise RuntimeError(msg) from e

    BROWSER_DIR.mkdir(parents=True, exist_ok=True)
    _INSTALL_MARKER.touch()
    logger.info("Chrome installed successfully")
