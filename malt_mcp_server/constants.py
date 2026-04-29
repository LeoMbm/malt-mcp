from pathlib import Path

# Browser profile
DEFAULT_USER_DATA_DIR = Path.home() / ".malt-mcp" / "profile"
BROWSER_DIR = Path.home() / ".malt-mcp"
PRIVATE_DIR_MODE = 0o700

# Malt URLs
MALT_BASE_URL = "https://www.malt.fr"
MALT_LOGIN_URL = f"{MALT_BASE_URL}/login"
MALT_DASHBOARD_URL = f"{MALT_BASE_URL}/dashboard"
MALT_PROFILE_URL = f"{MALT_BASE_URL}/profile"
MALT_MESSAGES_URL = f"{MALT_BASE_URL}/project/messages"

# Browser defaults
DEFAULT_TIMEOUT_MS = 5000
TOOL_TIMEOUT_SECONDS = 60

# Viewport
DEFAULT_VIEWPORT = {"width": 1280, "height": 720}
