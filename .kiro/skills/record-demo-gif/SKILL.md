---
name: record-demo-gif
description: Record or re-record the animated demo GIFs shown in the README and the app's Help modal by driving the running editor with Playwright and encoding the frames with ImageMagick. Use when the UI changed visibly enough that a demo GIF is outdated, or when asked to add or update a demo recording.
license: MIT
compatibility: Requires uv, the PlantUML JAR configured in .env, Playwright's Chromium and ImageMagick's `convert` on PATH.
---

# Record Demo GIF

`scripts/record_demo_gif.py` starts the app on a free local port, drives it in headless Chromium through a scripted editing flow, captures a frame after every small step and stitches the frames into a GIF. A fake cursor is drawn into the page, since headless screenshots don't include the real one.

## Scenarios

| Scenario | Shows | Output |
| --- | --- | --- |
| `activity-editing` | Building a small activity diagram from scratch | `src/plantuml_gui/static/help/activity-editing.gif` |
| `activity-demo-tour` | Interacting with the built-in Activity Demo | `images/activity-demo-tour.gif` |
| `activity-demo-code-edit` | The same, renaming the added activity in the code | `images/activity-demo-code-edit.gif` (the README demo) |
| `sequence-editing` | Building a small sequence diagram | `src/plantuml_gui/static/help/sequence-editing.gif` |

## Steps

1. Make sure the prerequisites are in place (once per machine):

   ```bash
   uv sync
   uv run playwright install chromium
   which convert   # ImageMagick
   ```

2. From the repository root, record one or more scenarios (no arguments records all of them):

   ```bash
   uv run python .kiro/skills/record-demo-gif/scripts/record_demo_gif.py activity-demo-code-edit
   ```

3. Inspect the written GIF before committing it: the flow should finish cleanly and the file size stays reasonable (the script prints it; the README demo is about 0.5 MB).

## When a scenario fails

The script saves a screenshot of the page at the point of failure to `<tmp>/<scenario>-failed.png` and prints how many frames it captured. The usual cause is a changed selector, menu item ID or modal in the UI; update the scenario function (`record_<scenario>`) to match.

## Changing or adding a scenario

- Each scenario is a `record_<name>(rec: Recorder)` function registered in `SCENARIOS`. Use the `Recorder` helpers (`move`, `click_at`, `type_into`, `hold`) so every step is captured, and `_settle` to wait for the diagram to re-render.
- Output goes to `images/` by default; add the scenario to `SCENARIO_OUTPUT_DIRS` if it belongs in the Help modal, to `SCENARIO_VIEWPORTS` for a larger (zoomed-out) viewport, and to `FULL_RESOLUTION` to skip downscaling.
- Update the scenario table above when you add or rename a scenario.
