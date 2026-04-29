# Changelog

## 0.4.0

### Breaking

- **Browser engine switched from system Chrome to managed Chromium.** Patchright now installs its own Chromium in `~/.malt-mcp/patchright-browsers/` instead of using the system Chrome. This avoids conflicts when Chrome is already running. Existing users must run `--logout` then `--login` to create a new browser profile.

### Added

- `get_profile` now works without a username — omit it to fetch your own profile. Malt redirects `/profile/` to the logged-in user's profile page.

### Fixed

- Browser launch no longer fails when Google Chrome is already open (`channel="chrome"` removed).
- First-run browser install now shows download progress instead of hanging silently.

## 0.3.1

- Trailing newline fix + uv.lock update.
- Added MCP registry `server.json`.

## 0.3.0

- Initial public release on PyPI.
- Tools: `authenticate`, `get_profile`, `get_statistics`, `get_missions`, `get_mission_details`, `close_session`.
