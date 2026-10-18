# Keep Screen On for RotorHazard

A [RotorHazard](https://github.com/RotorHazard/RotorHazard) plugin that keeps your phone or tablet screen awake while you're flying, so the race page doesn't go dark between heats.

It adds a small round button to the bottom-right corner of every RotorHazard page:

| Button | Meaning |
| --- | --- |
| Grey | Off. Tap to keep the screen on. |
| Green | The screen stays awake. Tap to turn off. |
| Amber, pulsing | Switched on for this device, but the page was just (re)loaded. Tap anywhere once to resume. |

Browsers only allow keeping the screen awake after a tap on the page, which is why a freshly loaded page shows amber until you touch it. Your choice is remembered per device.

## How it works

RotorHazard is served over plain HTTP, where the browser's Screen Wake Lock API isn't available. The plugin bundles [NoSleep.js](https://github.com/richtr/NoSleep.js), which falls back to playing a tiny invisible looping video to keep the screen on. Where the Wake Lock API is available (HTTPS, or a browser flag), NoSleep.js uses that instead.

On the server, the plugin registers a Flask blueprint that serves the scripts and adds two `<script>` tags just before `</body>` on HTML pages. Stream/overlay pages (`/stream*`) and non-HTML responses are left alone.

## Installation

**From a release (recommended):** download `keep_screen_on.zip` from the [Releases](../../releases) page and unzip it into your RotorHazard data folder:

```bash
cd ~/rh-data/plugins
unzip ~/Downloads/keep_screen_on.zip
sudo systemctl restart rotorhazard
```

You should end up with `~/rh-data/plugins/keep_screen_on/__init__.py`. After the restart, the log shows `Keep Screen On plugin loaded`.

**From source:** copy `custom_plugins/keep_screen_on` into `~/rh-data/plugins/` and restart.

## Settings

On the **Settings** page, the **Keep Screen On** panel has one option: **Show keep-screen-on button**. Turn it off to hide the button on all devices.

## Requirements

- RotorHazard with RHAPI 1.1 or newer
- A browser that can play inline video (any current Chrome, Firefox or Safari)

## Development

### Project layout

```
custom_plugins/keep_screen_on/   the plugin (this folder is what gets installed)
  __init__.py                    server side: settings panel, blueprint, script injection
  manifest.json                  plugin metadata (version lives here)
  static/keep_screen_on.js       the button and on/off logic
  static/NoSleep.min.js          bundled NoSleep.js v0.12.0 (MIT)
tests/test_plugin.py             tests against a stand-in for RotorHazard's API
scripts/build_zip.sh             builds dist/keep_screen_on.zip
```

### Test

Only Flask is needed (the same version RotorHazard uses):

```bash
pip install flask
python3 tests/test_plugin.py
```

### Build the zip

```bash
bash scripts/build_zip.sh
```

This creates `dist/keep_screen_on.zip` with the `keep_screen_on/` folder at the top level, ready to unzip into `~/rh-data/plugins/`.

### Release

1. Bump `version` in `custom_plugins/keep_screen_on/manifest.json` (SemVer, e.g. `1.0.1`).
2. Commit and push.
3. Create a GitHub release with a tag matching the version, e.g. `v1.0.1`.

The **Release** workflow checks that the tag matches the manifest, runs the tests, builds the zip and attaches it to the release. The **RHFest** workflow validates the plugin against the [RotorHazard Community Plugins](https://rotorhazard.github.io/community-plugins/) rules on every push.

### Updating NoSleep.js

Replace `static/NoSleep.min.js` with the `dist/NoSleep.min.js` file from a newer [NoSleep.js release](https://github.com/richtr/NoSleep.js/releases), and update the version mentioned in `LICENSE`.

## License

MIT, see [LICENSE](LICENSE). Bundles NoSleep.js by Rich Tibbett (MIT).
