# VS Code Extension

Reference for `plantuml-extension/`, the VS Code extension that gives the same
interactive diagram editing as the web app, using the VS Code text editor in
place of Ace.

Read this before changing anything under `plantuml-extension/`. The design
depends on several non-obvious invariants, and most of them fail *silently* —
the diagram still renders correctly while nothing responds to clicks.

## The one-paragraph version

The extension does not reimplement anything. It runs the existing Flask app as a
child process ("the sidecar") and loads the web app's own frontend
(`activity.js`, `sequence-*.js`, the Bootstrap context menus) into a webview
unmodified. Two shims make that possible: one rewrites the frontend's relative
`fetch` URLs to the sidecar, the other presents an Ace-shaped `editor` object
backed by the VS Code document. Every interaction the web app has therefore
works in the extension, for the same reason and through the same code.

## Three processes

```
  ┌───────────────────────────────────────────────────────────┐
  │ 1. Extension host (Node)          extension.js            │
  │    owns the TextDocument; the only writer                 │
  │    starts and stops process 3                             │
  └───────────────────────────────────────────────────────────┘
        ▲  postMessage: applyPuml, setHighlight, log
        ▼  postMessage: documentChanged, cursorMoved
  ┌───────────────────────────────────────────────────────────┐
  │ 2. Webview (Chromium)             media/                  │
  │    renders the SVG, shows the context menus               │
  │    runs the mirrored web app frontend                     │
  │    cannot touch the file; it asks process 1               │
  └───────────────────────────────────────────────────────────┘
        │  HTTP to 127.0.0.1:<ephemeral port>
        ▼
  ┌───────────────────────────────────────────────────────────┐
  │ 3. Sidecar (Python)               plantuml_gui/serve.py   │
  │    the unmodified Flask app: all ~71 routes               │
  │    shells out to java -jar plantuml.jar                   │
  └───────────────────────────────────────────────────────────┘
```

The sidecar exists because the puml-rewriting logic is ~4,500 lines of
PyQuery-based SVG parsing with its own test suite. Porting it to JavaScript would
fork it, and the two copies would drift. Cost of this choice: the extension needs
a Python interpreter with `plantuml-gui` installed.

## File map

```
plantuml-extension/
├── extension.js                 host: sidecar lifecycle, document writes,
│                                decorations, cursor reporting
├── src/
│   ├── sidecar.js               spawn Python, port handshake, health, dispose
│   └── webviewContent.js        builds the webview page (a shell, no logic)
├── media/                       everything the webview loads
│   ├── fetchShim.js             HAND-WRITTEN  relative URLs -> sidecar
│   ├── editorShim.js            HAND-WRITTEN  the fake ace / editor
│   ├── webviewInit.js           HAND-WRITTEN  boots the frontend
│   ├── app/                     GENERATED from src/plantuml_gui/static
│   ├── menus/                   GENERATED from templates/partials (via Jinja)
│   └── vendor/                  GENERATED from node_modules
├── scripts/
│   ├── sync_assets.py           the mirror; --check for CI
│   └── sync-assets.mjs          finds an interpreter, runs the above
└── test/                        45 tests, run by @vscode/test-cli
```

## How one interaction flows

Renaming a sequence message, end to end:

```
 1. [webview]  dblclick -> sequence-message.js records lastclickedsvgelement
 2. [webview]  fetch("getMessageText", {plantuml, svg, svgelement})
                 fetchShim rewrites the URL and adds the auth token
                 `plantuml` comes from editor.session.getValue() -> the shim
 3. [sidecar]  sequence/message.py matches svgelement against the parsed SVG,
                 resolves the puml line, returns its text
 4. [webview]  Bootstrap modal, prefilled; user submits
 5. [webview]  fetch("editMessageText", {..., text}) -> new full puml
 6. [webview]  setPuml(new) -> indentPuml -> editor.session.setValue(text)
                 SHIM: cachedText = text; postMessage({type:'applyPuml', text})
 7. [host]     text !== document.getText(), so apply a WorkspaceEdit
                 the file updates, dirty, on VS Code's native undo stack
 8. [host]     onDidChangeTextDocument -> postMessage documentChanged
 9. [webview]  incoming text === cachedText -> recognised as our own echo
                 LOOP TERMINATES HERE
```

## The two shims

### `media/fetchShim.js`

The frontend calls `fetch("editText", ...)` with relative URLs, which resolve
against the Flask origin in a browser and against nothing useful in a webview.
The shim rewrites them to `http://127.0.0.1:<port>/` and attaches
`X-PlantUML-Token`. That is the only change ~150 call sites need.

Must load before any app script.

### `media/editorShim.js`

The frontend reaches the source through Ace's `editor`, and uses a small slice of
its API — 58 `session.getValue()`, two `setValue()`, a few markers, one cursor
read. The shim supplies that shape, backed by the VS Code document.

| Frontend calls | Shim behaviour |
|---|---|
| `ace.require("ace/range")` | a 4-number `Range` class |
| `editor.session.getValue()` | returns `cachedText` |
| `editor.session.setValue(t)` | **the important one** — posts `applyPuml`, fires `change` |
| `editor.session.on('change')` | called after a document update |
| `selection.on('changeCursor')` | called when the host reports a caret move |
| `getCursorPosition()` | last reported caret position |
| `session.addMarker/removeMarker/getMarkers` | row list -> `setHighlight` -> editor decorations |
| `editor.on()`, `container` | inert (see *Not implemented*) |
| `setTheme`, `setMode`, `setOption`, `resize` | no-ops |

`setPuml()` → `session.setValue()` is the single door all ~71 diagram operations
exit through. Pointing it at a `WorkspaceEdit` is what makes every one of them
write to the file.

The shim also no-ops `window.history.replaceState`, which `renderPlantUml()` uses
to mirror the diagram into a shareable URL — meaningless in a webview, and it can
throw.

## Invariants

Break one of these and the diagram usually still renders while nothing works.

### Script load order

1. `vendor/*` — jQuery before Bootstrap
2. `fetchShim.js` — before anything calls `fetch`
3. `editorShim.js` — **`app/script.js` dereferences `ace` at load time**, so a
   later shim throws mid-parse
4. `app/*.js`
5. `webviewInit.js` — **last**: it assigns `app/script.js`'s `let editor`, a
   global *lexical* binding that only another classic script in the same scope
   can write

Asserted by tests in `test/webviewContent.test.js`.

### `webviewInit.js` must not call two web app functions

- `initeditor()` — builds an Ace instance and, finding no `?hash` in the URL,
  calls `setDemo()`, **overwriting the user's file with the demo diagram**.
- `addUtilEventListeners()` → `buttonEventListeners()` — binds the web app's
  toolbar (New/Undo/Save/PNG), which does not exist here;
  `getElementById(...).addEventListener` on `null` throws.

But `initeditor()` is *also* where the web app registers its listeners, so
`webviewInit.js` re-registers them explicitly:

```js
editor.session.on('change', () => debouncedRenderPlantUml());
editor.session.selection.on('changeCursor', () => { clearMarkers(); cursorChangeListener(); });
```

Omitting the first one is a real bug that has happened: the diagram renders once
at panel open and then never updates, from either a diagram edit or typing.
Pinned by `test/appScripts.test.js`, which asserts the *new puml reaches the
backend* — counting requests is not enough, because the boot render's own
trailing fetches keep arriving and mask the failure.

### The echo loop

The document is the single source of truth; the webview holds only `cachedText`.
Two stateless equality checks, one on each side:

```js
// host, before writing
if (message.text === document.getText()) return;
```
```js
// webview, on receiving an update
if (incoming === cachedText) { /* our own echo: re-render only */ }
```

They compare values rather than tracking whose turn it is, which is why nothing
can be swallowed. The `applyingEdit` flag in `extension.js` guards reentrancy
only; the equality checks are the actual defence.

### The mirror must stay byte-identical

`sync_assets.py --check` compares `media/{app,menus,vendor}` byte-for-byte
against freshly generated output, and CI fails a stale mirror. Anything that
rewrites those files after generation breaks the check permanently:

- `.pre-commit-config.yaml` excludes them from `end-of-file-fixer` and
  `trailing-whitespace`. Both *did* rewrite them before that exclusion existed.
- `.gitattributes` marks them `-text`. With `core.autocrlf=true` they would
  otherwise be committed as LF and checked out as CRLF, while the script always
  generates LF — so a fresh Windows clone reports a stale mirror for nobody's
  fault.

The hand-written shims live directly in `media/` and are deliberately still
covered by both.

### `webviewContent.js` builds a script inside a template literal

**No backticks anywhere in that string, including in comments.** A backtick ends
the template literal and turns the rest into live `webviewContent.js` code.
This has happened; `getWebviewContent()` threw on every call. Guarded by a test
asserting the generated script contains no backtick and no unresolved `${`.

### The DOM contract

The frontend calls `getElementById` on 114 ids and dereferences the result with
no null check, so one missing id throws during setup and kills every interaction.
95 come from the mirrored menu partials. The webview shell supplies the rest:

`colb`, `colb-container`, `loading-overlay`, `popup`, `editor`, `version`,
`version-panel`

`#editor` exists only because `hover-highlight.js` reads `editor.container`;
`#version-panel` only because `script.js` registers a top-level document click
handler that dereferences it. Both are hidden. Pinned by
`test/webviewContent.test.js`.

## The sidecar

`python -m plantuml_gui` is unsuitable as a child process: fixed port 5000, and
the reloader forks a second process the parent cannot cleanly kill. `serve.py`
instead binds an ephemeral port and prints `PLANTUML_GUI_PORT=<n>` on stdout.

`sidecar.js` **scans** stdout for that prefix rather than reading the first line,
because anything printed during import would otherwise be mistaken for it. That
was a real failure: `puml_encoder.py` had module-level debug prints, so the first
line was `Bob -> Alice : hello`.

### Environment contract

| Variable | Purpose |
|---|---|
| `PLANTUML_GUI_PORT=` | stdout announcement, parent reads it |
| `PLANTUML_GUI_TOKEN` | shared secret; unset means no auth check |
| `PLANTUML_GUI_JAR_OVERRIDE` | jar path, **not** `PLANTUML_JAR` — see below |
| `PLANTUML_GUI_PYTHON` | interpreter override, used by `launch.json` |

The jar is passed as `PLANTUML_GUI_JAR_OVERRIDE` because `shared/render.py` calls
`load_dotenv(override=True)` at import, so a repo `.env` beats the environment
the process was launched with. `serve.py` applies the override *after* that
import, which wins without changing web app behaviour.

### Authentication and CORS

Loopback is not a trust boundary: any local process can reach the server, and
every route rewrites the user's source. Hence the per-launch token.

The webview's page origin differs from the sidecar's, so every request is
cross-origin — unlike the web app, where page and Flask share an origin. Neither
`Content-Type: application/json` nor `X-PlantUML-Token` is CORS-safelisted, so
the browser sends an `OPTIONS` preflight first. Two consequences, both of which
surfaced as an opaque `Failed to fetch`:

- **`OPTIONS` is exempt from the token check.** Browsers strip custom headers
  from a preflight, listing them in `Access-Control-Request-Headers`, so the
  preflight cannot carry the token. Exempting it gives nothing away: the
  response carries no data, and the real request behind it is still checked.
- **CORS headers go on every response,** not just preflights. Without
  `Access-Control-Allow-Origin` the browser completes the request and then hides
  the response from JavaScript.

`Access-Control-Allow-Origin: *` is used because the webview's uuid changes per
panel. That grants any page permission to *attempt* a request, not to succeed —
the token check still rejects it — and `*` also bars cookies, of which there are
none.

### Interpreter resolution

`sidecar.js` tries, in order: the `plantumlInteractive.pythonPath` setting,
`PLANTUML_GUI_PYTHON`, the Python extension's selected interpreter, a workspace
`.venv`, then `python`/`python3`. An explicit setting wins even if broken, so a
bad value produces a clear error instead of silently running a different
interpreter.

Note that the Extension Development Host launches **without a workspace folder**,
so workspace-scoped settings are not read at all. During development, configure
via the `env` block in `.vscode/launch.json`.

## Working on the frontend

`media/app` and `media/menus` are **generated**. Editing them does nothing
lasting — the next sync overwrites it, and CI fails the stale mirror.

To change diagram behaviour, edit the web app:

```
src/plantuml_gui/static/*.js              interaction code
src/plantuml_gui/templates/partials/*.html context menus
```

then:

```bash
cd plantuml-extension && npm run sync-assets
```

The menu partials are **rendered through Jinja**, not copied:
`sequence_menus.html` defines and calls a `color_select` macro, and a plain copy
would leave `{{ color_select(...) }}` as literal text, silently dropping the
colour dropdowns.

`mode-plantuml.js` is deliberately not mirrored — it is Ace's syntax mode, and
there is no Ace here.

## Not implemented

- **Editor → diagram hover highlighting.** VS Code exposes no per-line
  mouse-hover event for text editors, so `initEditorHoverHighlighting` binds to
  an inert `editor.on()`. The direction degrades to following the **caret** via
  `onDidChangeTextEditorSelection`. Diagram → editor works normally.
- **The web app's undo history.** Every edit is a `WorkspaceEdit` and therefore
  already on VS Code's undo stack, so `script.js`'s private history array is left
  unbound — binding both causes double-undo bugs. Use Ctrl+Z.
- **The web app toolbar** — New/Demo, Save, Load, PNG export, version history.
- **Minimal-diff edits.** A change replaces the document's full range. Cursor
  position, folding state and undo granularity would survive better with a
  line-diff `WorkspaceEdit`.
- **Marketplace distribution.** Requires Python plus `plantuml-gui` installed.
  Bundling an embedded interpreter would confine the change to `sidecar.js`.

## Known rough edges

- **Re-indentation.** `setPuml` reformats the *entire* document on every
  interaction (`indentPuml` in `script.js`). Harmless for a browser scratch
  buffer; in VS Code one right-click can show up as a hundred changed lines in
  `git diff`. Kept for parity with the web app; a
  `plantumlInteractive.reindentOnEdit` setting would be the fix.
- **Saving.** Edits land as unsaved changes, like typing. Expected VS Code
  behaviour; the extension deliberately does not save for you.
- **Two ruff versions.** `.pre-commit-config.yaml` pins ruff 0.4.8 while
  `pyproject.toml` dev deps have 0.7.3, and they disagree about whether
  `plantuml_gui` is first-party. **`uvx ruff@0.4.8` is the one that matches
  CI**; `uv run ruff` reports import-order errors across the whole test suite
  that are not real.
- **Partial staging fights pre-commit.** A file with both staged and unstaged
  changes makes pre-commit stash, auto-fix, then fail to reconcile
  (`Stashed changes conflicted with hook auto-fixes... Rolling back`). Stage
  whole files.

## Running it

Requirements: Java, a Python interpreter with `plantuml-gui` installed, and
`plantuml.jar`.

```bash
cd plantuml-extension
npm install
npm run sync-assets      # only if media/ is missing or stale
```

Then F5 (`Run Extension`), open a file containing PlantUML — **any extension,
including `.txt`** — and run **PlantUML: Open Interactive Diagram**.

Settings: `plantumlInteractive.plantumlJar`, `plantumlInteractive.pythonPath`.
In the dev host these are not read (no workspace folder); use `launch.json`'s
`env` with `PLANTUML_JAR` and `PLANTUML_GUI_PYTHON`.

### Debugging

The **PlantUML Interactive** output channel carries the chosen interpreter, the
sidecar's stderr including Python tracebacks, and `[webview]` messages. A script
error in the webview shows in the red banner (`#popup`) at the top of the panel.

Symptom-to-cause shortcuts:

| Symptom | Look at |
|---|---|
| Diagram renders, nothing clickable | an app script threw at load; check for a missing DOM id or a load-order change |
| Diagram never updates after an edit | the `change` listener in `webviewInit.js` |
| `Failed to fetch` | CORS/token handling in `serve.py`, or the CSP `connect-src` |
| Edits apply to the wrong line | a participant/message index; verify against a real render, not by reading |
| CI says the mirror is stale | run `npm run sync-assets`; if it recurs, something is rewriting `media/` after generation |

## Testing

```bash
cd plantuml-extension && npm test     # 45 tests
uv run pytest tests/                  # includes tests/shared/test_serve.py
```

The highest-value test is in `test/appScripts.test.js`: it loads **all nine app
scripts against the editor shim in a `vm` sandbox and asserts none of them
throw**. That is the failure mode that matters — the diagram renders and nothing
is interactive — and it is close to undiagnosable from the UI.

When asserting that something re-rendered, assert on the request **body**
carrying the new puml. Counting requests passes even when the feature is broken,
because the boot render's async follow-up fetches keep arriving.

Note that comparing arrays built inside a `vm` sandbox needs `Array.from(...)`
first: `deepStrictEqual` compares prototypes, and the sandbox has its own realm.
