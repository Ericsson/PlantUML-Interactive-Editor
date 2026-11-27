#!/usr/bin/env python
# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Record the demo GIFs shown in the README.

Starts the app on a free local port, drives it with Playwright (headless
Chromium) through a scripted editing flow, captures a frame after every small
step, and stitches the frames into a GIF with ImageMagick's ``convert``. A fake
cursor is drawn into the page, since headless screenshots don't include the
real one.

Scenarios (each writes ``images/<name>.gif``, except the two shown in the
app's Help modal, which go to ``src/plantuml_gui/static/help/<name>.gif``):

- ``activity-editing``: build a small activity diagram from scratch
- ``activity-demo-tour``: interact with the built-in Activity Demo
- ``activity-demo-code-edit``: the same, renaming the added activity in the code
- ``sequence-editing``: build a small sequence diagram

Requires the PlantUML JAR configured in ``.env`` (as for running the app),
Playwright's Chromium (``uv run playwright install chromium``) and ImageMagick.

    uv run python .kiro/skills/record-demo-gif/scripts/record_demo_gif.py [scenario ...]
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path

from playwright.sync_api import Page, ViewportSize, sync_playwright

# This file lives in .kiro/skills/record-demo-gif/scripts/, four directories
# below the repo root.
ROOT = Path(__file__).resolve().parents[4]
IMAGES = ROOT / "images"
# The app's Help modal shows these scenarios, so they are written where Flask
# serves static files (and the wheel packages them) instead of to images/.
HELP_IMAGES = ROOT / "src" / "plantuml_gui" / "static" / "help"
SCENARIO_OUTPUT_DIRS = {
    "activity-editing": HELP_IMAGES,
    "sequence-editing": HELP_IMAGES,
}
VIEWPORT: ViewportSize = {"width": 1280, "height": 720}
# Per-scenario viewport overrides. A larger viewport, scaled down to the same
# GIF width, acts as zooming out: more code and diagram fit on screen.
SCENARIO_VIEWPORTS: dict[str, ViewportSize] = {
    "activity-demo-tour": {"width": 1440, "height": 810},
    "activity-demo-code-edit": {"width": 1440, "height": 810},
}
# Scenarios encoded at full recorded resolution (no downscaling), so they stay
# sharp when the README stretches them to the full column width.
FULL_RESOLUTION = {"activity-demo-tour", "activity-demo-code-edit"}
FRAME_DELAY_CS = 8  # per-frame delay in centiseconds (ImageMagick -delay)
OUTPUT_WIDTH = 960

# Drawn into the page so the pointer shows up in screenshots.
CURSOR_JS = """
() => {
    if (document.getElementById('demo-cursor')) return;
    const c = document.createElement('div');
    c.id = 'demo-cursor';
    c.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24">
        <path d="M3 2 L3 20 L8 15 L11.5 22 L14.5 20.5 L11 14 L18 14 Z"
              fill="#111" stroke="#fff" stroke-width="1.5"/></svg>`;
    Object.assign(c.style, {position: 'fixed', left: '0px', top: '0px',
        zIndex: 2147483647, pointerEvents: 'none'});
    document.body.appendChild(c);
    const ring = document.createElement('div');
    ring.id = 'demo-click';
    Object.assign(ring.style, {position: 'fixed', width: '26px', height: '26px',
        marginLeft: '-13px', marginTop: '-13px', borderRadius: '50%',
        border: '3px solid #e8590c', zIndex: 2147483646, pointerEvents: 'none',
        display: 'none'});
    document.body.appendChild(ring);
    document.addEventListener('mousemove', e => {
        c.style.left = e.clientX + 'px';
        c.style.top = e.clientY + 'px';
    }, true);
}
"""

# Maps a diagram (svg user-space) point to client coordinates.
TO_CLIENT_JS = """([x, y]) => {
    const svg = document.querySelector('#colb svg');
    const pt = svg.createSVGPoint();
    pt.x = x; pt.y = y;
    const s = pt.matrixTransform(svg.getScreenCTM());
    return [s.x, s.y];
}"""


class Recorder:
    """Drives the page and saves a numbered screenshot per captured frame."""

    def __init__(self, page: Page, frames_dir: Path) -> None:
        self.page = page
        self.frames_dir = frames_dir
        self.count = 0
        size = page.viewport_size or VIEWPORT
        self.pos = (size["width"] / 2, size["height"] / 2)

    def snap(self, repeat: int = 1) -> None:
        """Capture the current view; ``repeat`` > 1 holds it on screen longer."""
        path = self.frames_dir / f"{self.count:05d}.png"
        self.page.screenshot(path=str(path))
        self.count += 1
        for _ in range(repeat - 1):
            shutil.copy(path, self.frames_dir / f"{self.count:05d}.png")
            self.count += 1

    def hold(self, seconds: float) -> None:
        self.snap(repeat=max(1, round(seconds * 100 / FRAME_DELAY_CS)))

    def move(self, x: float, y: float, steps: int = 10) -> None:
        """Glide the cursor to (x, y), capturing a frame per step."""
        x0, y0 = self.pos
        for i in range(1, steps + 1):
            t = i / steps
            t = t * t * (3 - 2 * t)  # ease in/out
            self.page.mouse.move(x0 + (x - x0) * t, y0 + (y - y0) * t)
            self.snap()
        self.pos = (x, y)

    def _ring(self, show: bool) -> None:
        x, y = self.pos
        self.page.evaluate(
            "([x, y, show]) => { const r = document.getElementById('demo-click');"
            " r.style.left = x + 'px'; r.style.top = y + 'px';"
            " r.style.display = show ? 'block' : 'none'; }",
            [x, y, show],
        )

    def click(self, button: str = "left", double: bool = False) -> None:
        self._ring(True)
        self.snap(repeat=2)
        x, y = self.pos
        if double:
            self.page.mouse.dblclick(x, y)
        else:
            self.page.mouse.click(x, y, button=button)  # type: ignore[arg-type]
        self._ring(False)

    def click_at(
        self, x: float, y: float, steps: int = 10, **kwargs: bool | str
    ) -> None:
        self.move(x, y, steps=steps)
        self.click(**kwargs)  # type: ignore[arg-type]

    def type_into(self, selector: str, text: str) -> None:
        self.page.fill(selector, "")
        for i in range(0, len(text), 3):
            self.page.type(selector, text[i : i + 3])
            self.snap()

    def drag(self, dx: float, dy: float, steps: int = 14) -> None:
        """Press, move by (dx, dy) and release: pans the diagram canvas."""
        x, y = self.pos
        self.page.mouse.down()
        for i in range(1, steps + 1):
            t = i / steps
            t = t * t * (3 - 2 * t)
            self.page.mouse.move(x + dx * t, y + dy * t)
            self.snap()
        self.page.mouse.up()
        self.pos = (x + dx, y + dy)


# --- page helpers -----------------------------------------------------------


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _start_server() -> str:
    from plantuml_gui.app import app

    port = _free_port()
    threading.Thread(
        target=app.run,
        kwargs={"host": "127.0.0.1", "port": port, "use_reloader": False},
        daemon=True,
    ).start()
    for _ in range(100):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.1)
    return f"http://127.0.0.1:{port}"


def _puml(page: Page) -> str:
    return str(page.evaluate("() => editor.session.getValue()"))


def _settle(
    page: Page, puml_snippet: str | None = None, before: str | None = None
) -> None:
    """Wait for the editor to hold ``puml_snippet`` (or to differ from
    ``before``), then for the diagram to re-render and its handlers to attach."""
    if puml_snippet is not None:
        page.wait_for_function(
            "s => editor.session.getValue().includes(s)",
            arg=puml_snippet,
            timeout=20000,
        )
    if before is not None:
        page.wait_for_function(
            "b => editor.session.getValue() !== b", arg=before, timeout=20000
        )
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1200)  # SVG handlers attach asynchronously after render


def _text_center(page: Page, text: str) -> tuple[float, float]:
    """Screen center of the first diagram <text> whose content starts with
    ``text``. Labels have pointer-events disabled, so a click on a label
    lands on the shape underneath it."""
    finder = (
        "Array.from(document.querySelectorAll('#colb svg text'))"
        ".find(e => e.textContent.trim().startsWith(t))"
    )
    page.wait_for_function(f"t => Boolean({finder})", arg=text, timeout=20000)
    box = page.evaluate(
        f"t => {{ const b = {finder}.getBoundingClientRect();"
        " return [b.x + b.width / 2, b.y + b.height / 2]; }",
        text,
    )
    return float(box[0]), float(box[1])


def _element_center(page: Page, selector: str) -> tuple[float, float]:
    b = page.locator(selector).bounding_box()
    assert b is not None, selector
    return b["x"] + min(40, b["width"] / 2), b["y"] + b["height"] / 2


def _zoom(page: Page, scale: float) -> None:
    """Zoom the canvas (panzoom) about the top center of the diagram."""
    page.evaluate(
        "s => { const b = document.querySelector('#colb svg').getBoundingClientRect();"
        " const o = document.getElementById('colb').getBoundingClientRect();"
        " window.panzoomInstance.zoomAbs(b.x + b.width / 2 - o.x, 0, s); }",
        scale,
    )
    page.wait_for_timeout(300)


def _load(page: Page, puml: str) -> None:
    page.evaluate("p => editor.session.setValue(p)", puml)
    _settle(page, puml.splitlines()[1])


def _start(rec: Recorder) -> None:
    rec.page.evaluate(CURSOR_JS)
    rec.page.mouse.move(*rec.pos)
    rec.hold(1.0)


def _open_submenu_item(rec: Recorder, parent: str, item: str) -> None:
    """Hover a ``parent`` menu entry, then glide into its submenu ``item``.

    The cursor enters the submenu horizontally first: a diagonal path would
    cross the sibling entry below ``parent`` and close the submenu."""
    rec.move(*_element_center(rec.page, parent))
    rec.hold(0.2)
    target_x, target_y = _element_center(rec.page, item)
    rec.move(target_x, rec.pos[1], steps=6)
    rec.move(target_x, target_y, steps=6)
    rec.click()


def _choose(rec: Recorder, selector: str, steps: int = 8) -> None:
    """Glide to a visible menu item or button and click it."""
    rec.page.wait_for_selector(selector, state="visible", timeout=10000)
    rec.hold(0.2)
    rec.click_at(*_element_center(rec.page, selector), steps=steps)


def _modal(rec: Recorder, modal: str) -> None:
    rec.page.wait_for_selector(f"{modal}.show", state="visible", timeout=10000)
    rec.page.wait_for_timeout(400)
    rec.snap()


# --- sequence helpers -------------------------------------------------------


def _lifeline(page: Page, name: str) -> dict[str, float]:
    page.wait_for_function(
        "n => participantLifelines.some(l => l.name === n)", arg=name, timeout=20000
    )
    lifelines = page.evaluate("() => participantLifelines")
    return next(lifeline for lifeline in lifelines if lifeline["name"] == name)


def _lifeline_point(page: Page, name: str, svg_y: float) -> tuple[float, float]:
    x, y = page.evaluate(TO_CLIENT_JS, [_lifeline(page, name)["cx"], svg_y])
    return float(x), float(y)


def _message_y(page: Page, text: str) -> float:
    messages = page.evaluate("() => messagePositions")
    return float(next(m["cy"] for m in messages if m["text"] == text))


def _participant_header(page: Page, name: str) -> tuple[float, float]:
    """Screen center of the participant's top header box."""
    cx = _lifeline(page, name)["cx"]
    box = page.evaluate(
        """cx => Array.from(document.querySelectorAll('#colb svg rect'))
            .filter(r => r.hasAttribute('rx') && Math.abs(
                parseFloat(r.getAttribute('x')) +
                parseFloat(r.getAttribute('width')) / 2 - cx) <= 3)
            .map(r => r.getBoundingClientRect())
            .sort((a, b) => a.top - b.top)
            .map(b => [b.x + b.width / 2, b.y + b.height / 2])[0]""",
        cx,
    )
    return float(box[0]), float(box[1])


# --- scenarios --------------------------------------------------------------


def _demo_tour_intro(rec: Recorder) -> None:
    """Start in the Activity Demo, retitle it and add an activity below the
    yellow box (shared by both demo tours)."""
    page = rec.page
    page.evaluate("() => setDemo()")
    _settle(page, "Right-click to open the menu")
    _zoom(page, 0.85)  # the demo is wider than the diagram pane
    _start(rec)

    # Double-click the title and change it.
    rec.click_at(*_text_center(page, "This is not an ordinary"), steps=8, double=True)
    _modal(rec, "#modalFormTitle")
    rec.type_into(
        "#title-text", "Hello World! Welcome to this Interactive PlantUML Editor! :D"
    )
    _choose(rec, "#submit-title", steps=6)
    _settle(page, "Hello World! Welcome")
    rec.hold(0.6)

    # Right-click the yellow activity and add an activity below it.
    before = _puml(page)
    rec.click_at(
        *_text_center(page, "Right-click to open the menu"), steps=8, button="right"
    )
    _open_submenu_item(
        rec, "#activity-menu a:has-text('Add Below')", "#addBelowActivity"
    )
    _settle(page, before=before)
    rec.hold(0.8)


def _demo_tour_hover(rec: Recorder) -> None:
    """Hover elements: their code is highlighted in the editor."""
    page = rec.page
    rec.move(*_text_center(page, "Right-click to open the menu"), steps=8)
    rec.hold(0.6)
    rec.move(*_text_center(page, "To edit the activity"), steps=8)
    rec.hold(1.5)


def record_activity_demo_tour(rec: Recorder) -> None:
    """Start in the built-in Activity Demo and follow a few of its hints."""
    page = rec.page
    _demo_tour_intro(rec)

    # Undo it.
    before = _puml(page)
    rec.click_at(*_element_center(page, "#undo"), steps=10)
    _settle(page, before=before)
    rec.hold(0.6)
    _demo_tour_hover(rec)


def _editor_point(page: Page, row: int, column: int) -> tuple[float, float]:
    """Screen point in the Ace editor just before (row, column), 0-based."""
    x, y = page.evaluate(
        """([row, column]) => {
            const p = editor.renderer.textToScreenCoordinates(row, column);
            return [p.pageX, p.pageY + editor.renderer.lineHeight / 2];
        }""",
        [row, column],
    )
    return float(x), float(y)


def record_activity_demo_code_edit(rec: Recorder) -> None:
    """Like the demo tour, but rename the added activity in the code editor."""
    page = rec.page
    _demo_tour_intro(rec)

    # Click into the new ":Activity 1;" line, delete the label and type a new
    # one: the diagram follows the code.
    lines = _puml(page).split("\n")
    row = next(i for i, line in enumerate(lines) if line.strip() == ":Activity 1;")
    column = lines[row].index(";")
    rec.click_at(*_editor_point(page, row, column), steps=12)
    rec.hold(0.4)
    for _ in range(len("Activity 1")):
        page.keyboard.press("Backspace")
        rec.snap()
    label = "Edited in the code!"
    for i in range(0, len(label), 3):
        page.keyboard.type(label[i : i + 3])
        rec.snap()
    _settle(page, f":{label};")
    _text_center(page, label)  # wait for the re-rendered diagram
    rec.hold(1.2)
    _demo_tour_hover(rec)


def record_activity_editing(rec: Recorder) -> None:
    """Build a small activity diagram: add, rename, add an if, hover."""
    page = rec.page
    _load(page, "@startuml\nstart\n:Receive order;\nstop\n@enduml")
    _zoom(page, 1.6)
    _start(rec)

    # Right-click an activity and add a new activity below it.
    rec.click_at(*_text_center(page, "Receive order"), steps=8, button="right")
    _open_submenu_item(
        rec, "#activity-menu a:has-text('Add Below')", "#addBelowActivity"
    )
    _settle(page, ":Activity")
    rec.hold(0.5)

    # Double-click the new activity to rename it.
    new_activity = page.evaluate(
        "() => editor.session.getValue().match(/^:(Activity[^;]*);/m)[1]"
    )
    rec.click_at(*_text_center(page, new_activity), steps=8, double=True)
    _modal(rec, "#modalForm")
    rec.type_into("#message-text", "Check stock")
    _choose(rec, "#submit", steps=6)
    _settle(page, ":Check stock;")
    rec.hold(0.5)

    # Add an if statement below it and label the condition and branches.
    rec.click_at(*_text_center(page, "Check stock"), steps=8, button="right")
    _open_submenu_item(rec, "#activity-menu a:has-text('Add Below')", "#addIfBelow")
    _settle(page, "if (")
    rec.hold(0.5)
    statement = page.evaluate(
        "() => (editor.session.getValue().match(/if \\((.*?)\\)/) || [])[1]"
    )
    rec.click_at(*_text_center(page, statement), steps=8, double=True)
    _modal(rec, "#modalFormif")
    rec.type_into("#statement", "In stock?")
    rec.type_into("#branch1", "yes")
    rec.type_into("#branch2", "no")
    _choose(rec, "#submitif", steps=6)
    _settle(page, "In stock?")
    rec.hold(0.8)

    # Hover elements: the matching code line is highlighted in the editor.
    rec.move(*_text_center(page, "Receive order"), steps=8)
    rec.hold(0.6)
    rec.move(*_text_center(page, "Check stock"), steps=8)
    rec.hold(1.5)


def record_sequence_editing(rec: Recorder) -> None:
    """Build a small sequence diagram: participant, message, group."""
    page = rec.page
    _load(
        page,
        "@startuml\nparticipant Client\nparticipant Server\n"
        "Client -> Server: request\nServer --> Client: response\n@enduml",
    )
    _zoom(page, 1.8)
    _start(rec)

    # Add a participant to the right of Server and rename it.
    rec.click_at(*_participant_header(page, "Server"), steps=8, button="right")
    _choose(rec, "#addParticipantRight", steps=5)
    _settle(page, "participant participant")
    rec.hold(0.5)
    new_name = page.evaluate(
        "() => editor.session.getValue().match(/^participant (participant\\d+)/m)[1]"
    )
    rec.click_at(*_participant_header(page, new_name), steps=8, button="right")
    _choose(rec, "#renameParticipant", steps=5)
    _modal(rec, "#participant-name-modalForm")
    rec.type_into("#participant-name-text", "Database")
    _choose(rec, "#submit-participant-name", steps=6)
    _settle(page, "participant Database")
    rec.hold(0.6)

    # Right-click Server's lifeline between the messages and add a message
    # to Database: a ghost arrow follows the cursor to the target lifeline.
    mid_y = (_message_y(page, "request") + _message_y(page, "response")) / 2
    rec.click_at(*_lifeline_point(page, "Server", mid_y), steps=8, button="right")
    _choose(rec, "#addMessageSolid", steps=5)
    rec.move(*_lifeline_point(page, "Database", mid_y), steps=10)
    rec.click()
    _modal(rec, "#participant-modalForm")
    rec.type_into("#participant-message-text", "query order")
    _choose(rec, "#submit-participant-message", steps=6)
    _settle(page, "Server -> Database: query order")
    rec.hold(0.6)

    # Wrap the whole exchange in a loop: right-click where it starts, then
    # click where it ends (a ghost box shows the range).
    start_y = _message_y(page, "request") - 12
    rec.click_at(*_lifeline_point(page, "Client", start_y), steps=8, button="right")
    _choose(rec, "#seq-addGroup", steps=5)
    _choose(rec, "#seq-group-type-menu [data-group-type='loop']", steps=5)
    rec.move(
        *_lifeline_point(page, "Client", _message_y(page, "response") + 10), steps=10
    )
    rec.click()
    _modal(rec, "#seq-group-modalForm")
    rec.type_into("#seq-group-label-text", "until done")
    _choose(rec, "#seq-submit-group", steps=6)
    _settle(page, "loop until done")
    rec.hold(0.8)

    # Hover a message: its code line is highlighted in the editor.
    rec.move(*_text_center(page, "query order"), steps=8)
    rec.hold(1.5)


SCENARIOS: dict[str, Callable[[Recorder], None]] = {
    "activity-editing": record_activity_editing,
    "activity-demo-tour": record_activity_demo_tour,
    "activity-demo-code-edit": record_activity_demo_code_edit,
    "sequence-editing": record_sequence_editing,
}


def _encode(frames: Path, output: Path, resize: bool = True) -> None:
    subprocess.run(
        [
            "convert",
            "-delay", str(FRAME_DELAY_CS),
            "-loop", "0",
            str(frames / "*.png"),
            *(["-resize", f"{OUTPUT_WIDTH}x"] if resize else []),
            # One shared palette, no dithering: the dimmed backdrop behind a
            # modal has more shades than a 256-colour GIF palette, and
            # dithering them shows as noise. A shared palette also keeps the
            # frame-to-frame optimization effective.
            "+dither",
            "+remap",
            "-layers", "Optimize",
            str(output),
        ],
        check=True,
    )  # fmt: skip


def main() -> int:
    names = sys.argv[1:] or list(SCENARIOS)
    unknown = [n for n in names if n not in SCENARIOS]
    if unknown:
        print(
            f"unknown scenario(s): {', '.join(unknown)}; choose from {', '.join(SCENARIOS)}"
        )
        return 2
    if shutil.which("convert") is None:
        print("ImageMagick 'convert' not found on PATH", file=sys.stderr)
        return 1
    url = _start_server()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name in names:
            output = SCENARIO_OUTPUT_DIRS.get(name, IMAGES) / f"{name}.gif"
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory() as tmp:
                page = browser.new_page(viewport=SCENARIO_VIEWPORTS.get(name, VIEWPORT))
                page.goto(url)
                page.wait_for_selector("#colb svg", timeout=20000)
                page.wait_for_load_state("networkidle")
                rec = Recorder(page, Path(tmp))
                try:
                    SCENARIOS[name](rec)
                except Exception:
                    shot = Path(tempfile.gettempdir()) / f"{name}-failed.png"
                    page.screenshot(path=str(shot))
                    print(f"{name} failed after {rec.count} frames; see {shot}")
                    raise
                page.close()
                print(f"{name}: captured {rec.count} frames, encoding ...")
                _encode(Path(tmp), output, resize=name not in FULL_RESOLUTION)
            print(f"wrote {output} ({output.stat().st_size / 1e6:.1f} MB)")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
