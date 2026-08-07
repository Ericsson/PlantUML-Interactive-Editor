# VS Code Extension

The `plantuml-extension/` directory holds a VS Code extension that puts the interactive
diagram next to a `.puml` file open in the editor. Clicking the diagram rewrites the
document; typing in the document re-renders the diagram.

The extension does **not** reimplement the editor. It runs the existing Flask app as a
child process (a *sidecar*), loads that app's own frontend into a VS Code webview, and
swaps out the two things that cannot work unchanged there: the Ace editor (replaced by the
VS Code document) and the relative `fetch()` URLs (repointed at the sidecar). Everything
else — the 56 puml-rewriting routes, the context menus, the render pipeline — is the web
app, running as-is.

## The four runtimes

| Runtime | What it is | Code |
| --- | --- | --- |
| Extension host (Node.js) | The process VS Code loads the extension into. Owns the document, spawns the sidecar. | `plantuml-extension/` |
| Webview (browser) | A sandboxed Chromium frame in a VS Code panel. No Node, no filesystem, strict CSP. | `templates/webview.html` + `static/` |
| Sidecar (Python) | The Flask app as a child process, on a random loopback port. | `src/plantuml_gui/serve.py` |
| PlantUML (Java) | `java -jar plantuml.jar`, spawned per render by the sidecar. | — |

```
┌─ VS CODE ────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                              │
│ ┌─ diagram.puml ─────────────────────┐                                                       │
│ │ the open TextDocument. VS Code     │                                                       │
│ │ owns undo, dirty state and saving  │                                                       │
│ └────────────────┬───────────────────┘                                                       │
│                  │ getText · applyEdit(WorkspaceEdit) — the only write path                  │
│                  ▼                                                                           │
│ EXTENSION HOST · Node.js                    WEBVIEW PANEL · sandboxed Chromium frame         │
│ plantuml-extension/                         no Node · no filesystem · strict CSP             │
│ ┌────────────────────────────────────┐      ┌─────────────────────────────────────────────┐  │
│ │ extension.js    panel · listeners  │      │ served by the sidecar — ③ then ④:           │  │
│ │                 message handlers   │      │   page    webview.html                      │  │
│ │ sidecar.js      spawn · handshake  │  ①   │   shims   fetchShim · editorShim ·          │  │
│ │                 token · /health    │◄────►│           webviewInit                       │  │
│ │ plantumlJar.js  validate the jar   │      │   app     script.js · title.js ·            │  │
│ │ webviewPage.js  fetch the page     │      │           hover-highlight ·                 │  │
│ │                                    │      │           sequence-*.js · activity.js       │  │
│ │ ★ the ONLY writer of the document  │      │   css     styles.css · webview.css          │  │
│ │                                    │      │                                             │  │
│ │ owns: TextDocument · WorkspaceEdit │      │ shipped in the extension (node_modules):    │  │
│ │       decorations · output channel │      │   vendor  jQuery · Bootstrap · panzoom ·    │  │
│ │                                    │      │           diff   — no Ace, no Popper        │  │
│ └────────────────────────────────────┘      └─────────────────────────────────────────────┘  │
│         │              │                                        │                            │
│      ②  │ spawn +   ③  │ GET /webview                        ④  │ the app's own HTTP,        │
│         │ stdio        │ once per panel                         │ every interaction          │
└─────────┼──────────────┼────────────────────────────────────────┼────────────────────────────┘
          ▼              ▼                                        ▼
┌─ SIDECAR · Python · Flask ───────────────────────────────────────────────────────────────────┐
│ src/plantuml_gui/ , spawned as `python -m plantuml_gui.serve`                                │
│ http://127.0.0.1:<port>   port picked by the OS at bind, token minted by Node at spawn       │
│ X-PlantUML-Token required on every request but GET /static/*                                 │
│                                                                                              │
│ serve.py         ephemeral port · /health · /webview · token auth · CORS · jar override      │
│ templates/       webview.html · app_scripts · activity_menus · sequence_menus                │
│ static/          every script and stylesheet the page loads, incl. vscode/ shims             │
│ 79 POST routes   56 rewrite the source   /editText · /addNote · /deleteActivity …            │
│                  23 query or render      /getText · /getActivityPositions · /render …        │
│ 4 GET routes     / · /changelog  (web app)   ·   /health · /webview  (sidecar only)          │
│                                                                                              │
│ stateless about files: every route takes the whole source in and hands it back out           │
└──────────────────────────────────────────────────────────────────────┼───────────────────────┘
                                                                       │ ⑤ one process per render
                                                                       ▼
                                        ┌─ PLANTUML · Java ─────────────────────────────────┐
                                        │ java -jar plantuml.jar -pipe -tsvg  →  SVG        │
                                        │ jar path resolved by Node, injected at spawn      │
                                        └───────────────────────────────────────────────────┘
```

The five edges, each specified in full under [Interfaces](#interfaces):

| | Between | Channel | When |
| --- | --- | --- | --- |
| ① | host ↔ webview | `postMessage` | continuous |
| ② | host → sidecar | `spawn` + stdio | once per window |
| ③ | host → sidecar | one HTTP `GET /webview` | once per panel |
| ④ | webview → sidecar | the frontend's own HTTP | every interaction |
| ⑤ | sidecar → java | `subprocess` | once per render |

Two independent channels, and the split is the whole design. The webview talks **HTTP to
Python** for everything about the diagram, and **`postMessage` to Node** for everything about
the document. Node never proxies ④ — its only HTTP request is ③, made once, before the page
exists. Python never learns that a file is involved: every route takes the full source in the
request body and returns the full source back.

Note where the frontend lives. Only the browser libraries come from the extension; the page,
the shims, the CSS and the app's own scripts are all served by the sidecar out of
`src/plantuml_gui/`. That is why there is no HTML, no frontend copy and no build step in
`plantuml-extension/`.

## Component map

Node side, `plantuml-extension/`:

| File | Responsibility |
| --- | --- |
| `package.json` | Manifest: the `plantuml-interactive-editor.openDiagram` command, the two settings, and the browser libraries as runtime dependencies. |
| `extension.js` | Lifecycle, the command, the webview panel, document listeners, and the message handlers. The only writer of the document. |
| `src/sidecar.js` | Spawns and supervises the Python child; port handshake, token, health polling, error messages. |
| `src/plantumlJar.js` | Resolves and validates the jar path before anything is spawned. |
| `src/webviewPage.js` | Fetches the page from the sidecar and supplies the values Flask cannot know. |
| `test/` | Mocha unit tests run by `@vscode/test-cli`. |

Python side, `src/plantuml_gui/`:

| File | Responsibility |
| --- | --- |
| `serve.py` | The sidecar entry point. Same Flask `app`, different startup: ephemeral port, `/health`, `/webview`, token auth, CORS, jar override. |
| `templates/webview.html` | The page the panel loads. Standalone, not a child of `index.html`. |
| `templates/partials/app_scripts.html` | The frontend's script list, shared by `index.html` and `webview.html`. |
| `static/vscode/fetchShim.js` | Rewrites the app's relative `fetch()` URLs and attaches the token. |
| `static/vscode/editorShim.js` | An Ace-shaped object backed by the VS Code document. |
| `static/vscode/webviewInit.js` | Boots the reused app code inside the webview. |
| `static/vscode/webview.css` | Hides the DOM elements that exist only to satisfy the app's code. |

Nothing under `static/vscode/` is loaded by the web app at `/`. It lives in this package
rather than in the extension because it is `<script src>` on a page Flask renders — serving
it next to `script.js` costs nothing, and the alternative is the extension resolving a
webview URI for each file and passing it in.

## Interfaces

Six links, no two alike, each specified below as transport, who speaks first, payload,
authentication and failure. None of it comes from a shared schema — every contract here is
upheld by hand, so the constants are listed in
[Cross-runtime contracts](#cross-runtime-contracts).

Which pairs can talk at all is itself part of the design, and the empty cells matter as much
as the full ones:

| | host | webview | sidecar | java |
| --- | --- | --- | --- | --- |
| **host** | — | postMessage | spawn, and 2 HTTP GETs | never |
| **webview** | postMessage | — | HTTP, continuously | never |
| **sidecar** | stdout, stderr | HTTP responses | — | subprocess |

### 1. Host → sidecar: process control

`spawn(pythonPath, ['-m', 'plantuml_gui.serve'], { env })`, from `src/sidecar.js`. Node
speaks first; the child can only answer through its own stdio. Environment is the only way
to configure a process before it starts, so all of it rides in there:

| Variable | Set when | Read by | Effect |
| --- | --- | --- | --- |
| `PLANTUML_GUI_TOKEN` | always | `install_token_auth()` | The per-launch secret. **Absent means no auth is installed at all**, which is what keeps plain `python -m plantuml_gui` usable. |
| `PLANTUML_GUI_JAR_OVERRIDE` | only if a jar resolved | `apply_jar_override()` | Assigns `PLANTUML_JAR` from inside the process, after `load_dotenv`. See [Jar override](#jar-override). |
| `PYTHONUNBUFFERED` | always `1` | CPython | Without it the port line sits in a block buffer and the handshake times out. |

Coming back: **stdout** carries exactly one meaningful line, `PLANTUML_GUI_PORT=<port>\n`,
and everything else on it is ignored (see [Port handshake](#port-handshake)); **stderr**
carries unstructured tracebacks mixed with werkzeug's request log, streamed to the output
channel and kept in a rolling 8 KB buffer (see [Failure reporting](#failure-reporting)).

One sidecar per window, shared by every panel, killed in `deactivate()`. Spawn `ENOENT`, an
import error, and no port line within 30 s all end the same way: panel disposed, notification
naming the setting to fix.

### 2. Host → sidecar: HTTP

Two requests in the extension's whole lifetime — Node is not a proxy for the frontend. Both
carry `X-PlantUML-Token`.

| Request | When | Response | On failure |
| --- | --- | --- | --- |
| `GET /health` | Every 100 ms after the port line until it answers or 30 s passes; 2 s per attempt. | `{"status": "ok"}` — the body is never read, only the fact that something answered. | Not-ready-yet; the deadline is what gives up. |
| `GET /webview?…` | Once per panel, 5 s timeout. | `text/html`, assigned verbatim to `panel.webview.html`. | `400` + `{"error": …}` on a bad parameter, `WebviewPageError` otherwise. |

The `/webview` query string is the whole of what the extension tells Flask about the panel:

| Parameter | Repeated | Value |
| --- | --- | --- |
| `base` | no | Where the *webview* reaches the sidecar, via `vscode.env.asExternalUri`. Must be an http(s) URL. |
| `csp_source` | no | `webview.cspSource`. Validated more laxly than the rest, since spaces and single quotes are legal CSP grammar. |
| `vendor_script`, `vendor_style` | yes | Webview URIs for the browser libraries. Sent with `append`, read with `getlist`, because **order is load order**. |

Flask derives `origin`, `token`, `token_header` and `script_hash` itself rather than
accepting them from the caller.

### 3. Host ↔ webview: `postMessage`

The only channel between Node and the browser frame — no shared memory, no filesystem, no
HTTP. Host side: `panel.webview.postMessage()` and `.onDidReceiveMessage()`. Webview side:
`acquireVsCodeApi()` once in `webviewInit.js`, then `.postMessage()` and a `window`
`message` listener.

Payloads go through the structured clone algorithm, so they must be plain data — strings,
numbers, arrays and object literals survive; functions, `Error`s, DOM nodes and class
instances do not. Every message carries a `type` discriminator.

| Direction | Message | Payload | Sent when |
| --- | --- | --- | --- |
| host → webview | `documentChanged` | `{ text }` | Once after the panel opens, then on every document change, debounced 300 ms. |
| host → webview | `cursorMoved` | `{ row, column }` | On `onDidChangeTextEditorSelection`, undebounced, zero-based. |
| webview → host | `applyPuml` | `{ text }` | A diagram operation produced new source. |
| webview → host | `setHighlight` | `{ rows }`, zero-based line numbers | The shim's marker table changed. |
| webview → host | `ready` | `{}` | The page finished booting. |

Four properties of the channel shape the code on both sides. There is **no
request/response** — no ids, no acks, no replies — which is why the write-back loop has to be
terminated by [comparing values](#why-the-write-back-loop-terminates). **Unknown types are
silently ignored**, both handlers being `if`/`else if` with no `else`, so adding a message
type is backwards-compatible but a typo in one end fails quietly. **Delivery starts only
once the receiver is listening**, which is the entire reason `ready` exists. And nothing is
authenticated or reported: the channel is private to the panel by VS Code's guarantee, and
posting to a disposed panel is a no-op rather than an error.

### 4. Webview → sidecar: HTTP

The app's own unmodified traffic — the same calls `index.html` makes. `fetchShim.js` adds
exactly two things in flight: a relative URL becomes `base + path`, and every request gets
the token header.

All 79 POST routes take the same envelope:

```
POST <base><route>
Content-Type: application/json
X-PlantUML-Token: <token>

{ "plantuml": "<the entire .puml source>",
  "svg":      "<the currently rendered SVG>",
  "svgelement": "<outerHTML of the clicked element>",
  …operation-specific fields, e.g. "newname" }
```

Note what is *not* there: no file path, no document uri, no revision, no session id. The
whole source goes out and the whole source comes back, which is why one sidecar can serve
every panel without knowing that panels exist.

Responses are **not** uniform, and the split follows blueprint rather than what the route
does:

| Routes | Content type | Body |
| --- | --- | --- |
| `activity/`, 46 of 48 | `text/html`, a bare Flask `str` | The whole new source, or the queried value. Read with `response.text()` — not JSON, and not a diff. |
| `activity/`: `/getActivityPositions`, `/checkDuplicateArrow` | `application/json` | The blueprint's two exceptions: a row table, and `{"result", "type"}`. |
| `sequence/`, all 23 | `application/json` | Always an envelope — `{"plantuml": …}` for a rewrite, `{"name": …}` or `{"text", "color"}` or a row table for a query. `/addGroup` and `/addBox` can answer `400` + `{"error": …}`. |
| `shared/`: `/render`, `/encode`, `/decode`, the four title routes | `text/html` | Bare text; `/render` returns the SVG itself. |
| `shared/`: `/renderPNG` | `image/png` | Bytes, as an attachment. |

That inconsistency is historical rather than a rule being followed: the newer sequence
blueprint standardised on JSON envelopes and the activity blueprint never did. The frontend
matches it correctly today, but it is a trap when adding a route, because reading a JSON
response with `.text()` yields a JSON *string* that flows onward into the document without
erroring anywhere.

Two things sit outside that shape. `GET /static/...` is issued by `<script src>` and
`<link href>`, so it carries no token and is exempted by endpoint name (see
[Token authentication](#token-authentication)). And every request here is cross-origin,
since the page origin is `vscode-webview://<uuid>`, so the browser preflights anything
carrying JSON or the token header; `install_cors()` answers with
`Access-Control-Allow-Origin: *`, `Allow-Headers: Content-Type, X-PlantUML-Token`,
`Allow-Methods: GET, POST, OPTIONS` and `Max-Age: 7200`.

A bad or missing token gets `403` + `{"error": "invalid or missing token"}`. The app's code
never anticipated a 403, so it surfaces as a failed render rather than a message — check the
webview devtools network tab.

### 5. Sidecar → PlantUML: subprocess

One `java` process per render, from `shared/render.py`, source in on stdin and image out on
stdout:

```
java -DPLANTUML_LIMIT_SIZE=16384 -jar $PLANTUML_JAR -pipe -tsvg
java -DPLANTUML_LIMIT_SIZE=16384 -jar $PLANTUML_JAR -pipe -tpng -Sdpi=300
```

`PLANTUML_JAR` is read per call rather than captured at import, which is precisely what makes
the `PLANTUML_GUI_JAR_OVERRIDE` indirection work.

### 6. Host ↔ the document

Not cross-process, but the link that closes the loop. The host reads with
`document.getText()` and writes with a `WorkspaceEdit` replacing the full range — one edit,
so one undo step, so Ctrl+Z undoes a diagram click. It is the **only** write path to the
file; neither the webview nor the sidecar can reach it.

## Startup sequence

1. VS Code loads `extension.js` and calls `activate()`, which creates the
   `PlantUML Interactive` output channel, registers sidecar disposal, and registers the
   command. Nothing is spawned yet.
2. The command runs `openDiagramPanel()` against the active editor's document.
3. `resolvePlantUmlJarPath()` resolves the jar from the setting, else `PLANTUML_JAR`, and
   checks it exists. This happens **before** spawning, because `check_jar()` in `serve.py`
   only warns on stderr — an unchecked bad path would first appear as a 500 on the user's
   first render.
4. `ensureSidecar()` starts the child if one is not already running. One sidecar is shared
   by every panel in the window; concurrent callers await the same start rather than racing
   to spawn two servers.
5. `startSidecar()` resolves the interpreter, generates a per-launch token, and spawns
   `python -m plantuml_gui.serve`.
6. The sidecar applies the jar override, warns if the jar is unusable, installs its routes,
   binds an ephemeral port, and prints `PLANTUML_GUI_PORT=<port>` to stdout.
7. Node reads that line off stdout, then polls `GET /health` until it answers.
8. `createWebviewPanel()` opens the panel beside the editor, with `enableScripts`,
   `node_modules` as the single `localResourceRoots` entry, and `retainContextWhenHidden`
   — without the last one, VS Code tears the page down whenever the panel is hidden, and
   restoring it costs a full render plus a rewalk of every handler the frontend attached.
9. `fetchWebviewPage()` GETs `/webview` from the sidecar and assigns the result to
   `panel.webview.html`.
10. The page loads its scripts in a fixed order and posts `ready`.
11. The host posts `documentChanged` with the file's text; the webview renders.

Any failure between steps 3 and 9 becomes a notification naming the setting to change, and
the panel is disposed rather than left blank.

## The sidecar

### Why `serve.py` and not `__main__.py`

`python -m plantuml_gui` runs `app.run(debug=True)` on port 5000. That is wrong for a child
process on three counts: the fixed port may be taken and we want one server per editor
window; the debug reloader forks a second process the parent cannot cleanly kill; and there
is no way to report the bound port back. `serve.py` is a second entry point onto the *same*
Flask `app` object. Running the web app normally is unaffected.

### Port handshake

The child binds port `0` — "any free port" — via `make_server`, which binds immediately, so
the port is known rather than guessed at or raced for.

Two details in `readPortLine()` are not incidental. It keeps only complete lines, because a
pipe chunk boundary can fall mid-number; and it scans for the prefix rather than reading the
first line, because anything printed during import would otherwise be mistaken for the port.

### Readiness

A bound socket is not a serving one, which is why the parent polls `/health` instead of
trusting the port line — no caller ever sends a real request to a socket that is bound but
not yet answering. `/health` is registered by the sidecar only, so the web app's route table
is unchanged.

### Token authentication

Loopback is not a trust boundary: any local process can reach the server, and every route
rewrites the user's source. `startSidecar()` generates 24 random bytes per launch and passes
them as `PLANTUML_GUI_TOKEN`; `install_token_auth()` rejects any request without a matching
`X-PlantUML-Token` header. No token configured means no check installed, so normal web use
is unaffected.

Two exemptions:

- **`OPTIONS`** — browsers strip custom headers from CORS preflights by design, so a
  preflight cannot carry the token. Rejecting it would fail the preflight and the real
  request would never happen. The preflight response carries no data, and the real request
  that follows is still checked.
- **`GET`/`HEAD` on the `static` endpoint** — `<script src>` and `<link href>` cannot send
  headers, so authenticating them would mean putting the secret in a query string, where it
  would land in werkzeug's request log. These are non-secret read-only files any process
  able to reach loopback could already read off disk. Every source-rewriting route is a POST
  and stays checked. The exemption is matched by *endpoint name*, not URL prefix, so a route
  mounted under `/static` later cannot silently inherit it.

### CORS

The webview's page origin is `vscode-webview://<uuid>`, so every request from it is
cross-origin — unlike the web app, where page and Flask share an origin. The client sends
`Content-Type: application/json` and a token header, neither CORS-safelisted, so the browser
preflights and blocks the real request unless the response permits it.

The allowed origin is `*`, because the webview's uuid changes per panel. That is not a hole:
it grants any page permission to *attempt* a request, while the token check still rejects
anything that cannot produce the secret. `*` also bars the browser from sending cookies, and
this server has no cookie or session state.

### Jar override

`shared/render.py` calls `load_dotenv(..., override=True)` at import time, so a repo-root
`.env` beats the environment the process was launched with. Passing `PLANTUML_JAR` directly
would therefore be silently ignored. Instead the extension passes
`PLANTUML_GUI_JAR_OVERRIDE`, and `apply_jar_override()` assigns `PLANTUML_JAR` itself, after
`.app` has been imported and therefore after `load_dotenv` has run. It works because
`render.py` reads the variable per call rather than at import.

Consequence: the jar enters the child's environment at spawn time, so changing the setting
takes effect on the next backend start, not the next render.

### Failure reporting

The child's stderr is streamed to the output channel and kept in a rolling 8 KB buffer
(capped because werkzeug logs every request there for the life of the process).
`describeStartFailure()` turns it into actionable text: `ENOENT` names the `pythonPath`
setting, `No module named plantuml_gui` says to install the package into that interpreter,
and anything else is reported with the traceback.

## The webview page

A webview is a sandboxed frame whose HTML you supply as a **string**, so the page has an
artificial origin and relative URLs resolve to nothing. Local files must be converted with
`webview.asWebviewUri()` and their directory listed in `localResourceRoots`. A strict CSP
applies. The only channel to the extension host is `postMessage`.

### Why Flask renders it

The page's content *is* the web app's frontend — its markup, its CSS, its context-menu
partials — and the sidecar is already a server that has all of it plus the Jinja to render
it. So `install_webview_route()` renders `templates/webview.html` and `fetchWebviewPage()`
asks for it over HTTP.

The result: no HTML in the extension, no copy of the frontend, no build or sync step, and no
way for the webview to run a stale copy of a file edited in `src/plantuml_gui/`.

### Why the parameters are validated, not escaped

The four query parameters themselves are listed under *Host → sidecar: HTTP* in
[Interfaces](#interfaces). What matters here is that all of them are reflected into the
document, so `serve.py` validates rather than escapes them. Jinja escapes quotes, but that does not help here: a semicolon inside a CSP source
starts a new directive of the caller's choosing, and whitespace splits one value into
several. `csp_source` gets a laxer rule than the rest — spaces and single quotes are
legitimate CSP grammar, and a compound `cspSource` is what VS Code Remote-SSH produces.

### CSP

```
default-src 'none';
img-src     {csp_source} {origin} data:;
style-src   {csp_source} {origin} 'unsafe-inline';
script-src  {csp_source} {origin};
font-src    {csp_source} {origin};
connect-src {origin}
```

Two sources and nothing else: the sidecar, for the frontend, and the webview's own source,
for the browser libraries. This is what makes it safe to `innerHTML` PlantUML-rendered SVG
from an untrusted `.puml` file — injected markup can carry neither origin, so an inline
`<script>` or an SVG `onload` handler is blocked. `'unsafe-inline'` is style-only; there is
no script equivalent and no nonce, because the page has no inline script at all. What the
shims need is on `<body data-*>` instead.

### Browser libraries

`index.html` loads jQuery, Bootstrap, panzoom and jsdiff from CDNs, which the CSP blocks. The
extension declares them as npm **runtime** dependencies (so `vsce` packages them into the
VSIX), lists `node_modules` as the single `localResourceRoots` entry, and passes their
webview URIs in `VENDOR_SCRIPTS` / `VENDOR_STYLES`. The order matters: jQuery before
Bootstrap, and jQuery pinned to 3.x because Bootstrap 4 requires <4.

Three libraries `index.html` loads are deliberately absent:

- **Ace** — `editorShim.js` replaces it.
- **Popper** — Bootstrap 4 needs it only for dropdowns, tooltips and popovers instantiated
  through Bootstrap's own JS. The page uses Bootstrap for modals, which do not need it, and
  the context menus are `.dropdown-menu` markup positioned and toggled by the app's own code
  rather than by `data-toggle="dropdown"`. The one `data-toggle="dropdown"` in the codebase
  is on `index.html`'s toolbar, which this page does not have.
- **tippy.js** — only ever bound to `[data-tippy-content]`, which is exclusively
  `index.html`'s toolbar buttons.

### DOM the app assumes

`webview.html` contains `#popup`, `#editor`, `#version` and `#version-panel`, all hidden by
`webview.css`. They exist because the app's code dereferences those ids without null checks;
one missing id throws during setup and kills every interaction while the diagram still
renders.

## The shims

### `fetchShim.js`

The app calls `fetch("editText", ...)`, `fetch("render", ...)` and so on with relative URLs,
which in a browser resolve against the Flask origin and in a webview resolve to nonsense.
The shim wraps `window.fetch`: relative URLs get the `base` prefix, absolute ones are left
alone, and every request gets the token header. It reads the base, token and header name
from `document.body.dataset`, which is what keeps it a static file rather than a template.

Must load before any app script. Rewriting the URLs here is the only change the app's 75
`fetch()` call sites need — 42 of them in `activity.js` alone.

### `editorShim.js`

The app reaches the source through exactly one object — Ace's `editor` — and through a small
slice of its API: 58 `session.getValue()` calls, two `session.setValue()`, a few markers and
a cursor read. This file supplies an object of that shape backed by the VS Code document.

The single most important method is `session.setValue()`. Every diagram operation ends by
calling `setPuml()` — 43 call sites across the frontend — and `setPuml()` calls
`setValue()`. Instead of mutating an Ace buffer, the shim posts `applyPuml` to the host and
fires the `change` handlers so the app re-renders as it expects to. Pointing that one method
at the document is what routes all 56 source-rewriting routes into the file.

It also provides:

- a `window.ace` global with a four-number `Range`, which must exist before `script.js` is
  even parsed, because that file runs `ace.require("ace/range").Range` at load time;
- an Ace-shaped marker table, whose shape matters because `clearMarkers()` iterates it and
  filters on `marker.clazz == "hover"`; markers classed `hover` are pushed to the host as
  `setHighlight`;
- `applyDocumentText`, `primeDocumentText` and `applyCursor`, which the host drives;
- no-ops for `setMode`, `setOption`, `setTheme`, `resize` and `on`;
- a stubbed `history.replaceState`, because `renderPlantUml()` mirrors the diagram into the
  page URL as a shareable hash and a webview has no address bar.

### `webviewInit.js`

Loaded last, because `script.js` declares `let editor;` at top level — a lexical binding, not
a property of `window` — and only another classic script sharing that global scope can
assign it.

It deliberately does not call the web app's own bootstrap:

- `initeditor()` builds an Ace instance and, finding no `?hash` in the URL, calls
  `setDemo()`, which would overwrite the user's file with the demo diagram.
- `addUtilEventListeners()` calls `buttonEventListeners()`, which binds the web toolbar
  (New/Undo/Save/PNG). Those buttons do not exist here, and `addEventListener` on `null`
  throws.

So the listeners `initeditor()` would have registered are re-registered explicitly —
`session.on('change')` and `selection.on('changeCursor')` — without which the diagram would
render once at boot and never again. It then calls `titleEventListeners()`, binds Ctrl+Enter
for modal submit (Ctrl+Z is deliberately *not* rebound, since every edit is a `WorkspaceEdit`
and already on VS Code's undo stack), sets up panzoom on `#colb`, and posts `ready`.

The context menus need no attention here: they are wired by `checkDiagramType()` during
`renderPlantUml()`.

## Message protocol

The five message types, their payloads and the guarantees the channel does and does not give
are specified under *Host ↔ webview* in [Interfaces](#interfaces). What follows is the part
that the message list does not show: why the two directions do not chase each other forever.

### Why the write-back loop terminates

A diagram edit posts `applyPuml`; the host writes the document; the write fires
`onDidChangeTextDocument`; the host posts `documentChanged`; the webview receives its own
change back. The loop is broken by **value comparison on both sides**:

- `applyPuml()` returns early when the text equals `document.getText()`.
- `applyDocumentText()` returns `false` when the text equals what the shim already has, so
  no `change` fires and no re-render happens.

The `applyingEdit` flag in `extension.js` is only a reentrancy guard around `applyEdit`.
Comparing values rather than tracking whose turn it is means a genuine edit can never be
swallowed, which a turn-based flag would eventually do.

`webviewInit.js` treats the first `documentChanged` specially: it primes the text without
firing `change`, then calls `renderPlantUml()` once explicitly, so the initial render does
not go through the debounce and race the handler setup.

## Worked example: renaming an activity box

```
webview   click handler (activity.js, bound by checkDiagramType) captures
          lastclickedsvgelement.outerHTML, shows the modal, reads the new text
          fetch("editText", {plantuml, svg, svgelement, newname})
            ↳ fetchShim → http://127.0.0.1:<port>/editText + token header
sidecar   token check → activity_bp route → PyQuery finds this is the Nth rect,
          finds the Nth activity line, rewrites it → returns the full puml text
webview   setPuml(text) → indentPuml → editor.session.setValue(text)
            → postMessage {applyPuml, text}
            → fire change → debouncedRenderPlantUml()
host      applyPuml(): text differs, so a WorkspaceEdit replacing the full range
          → the file is dirty in VS Code, as one undo step
          → onDidChangeTextDocument → 300 ms → postMessage {documentChanged}
webview   applyDocumentText(text) → identical → returns false. Loop ends.
          Meanwhile the debounced render POSTed /render and swapped in the new SVG.
```

Typing directly in the VS Code editor enters the same flow at
`onDidChangeTextDocument`, where `applyDocumentText` returns `true` and a re-render follows.

## Highlighting

**Diagram → editor** works fully. Hovering a diagram element makes the app call
`session.addMarker(range, "hover", ...)`; the shim collects the marked rows and posts
`setHighlight`; `applyHighlight()` filters out-of-range rows and calls `setDecorations` on
every visible editor showing the document. The decoration type is created once at module
level, since each one is a resource VS Code tracks.

**Editor → diagram** is degraded by design. VS Code exposes no per-line mouse-hover event
for text editors, so the shim's `editor.on()` is a no-op and
`initEditorHoverHighlighting()` binds to nothing. It is still called so the wiring is
complete if that ever changes. The feature instead follows the caret:
`onDidChangeTextEditorSelection` → `cursorMoved` → `applyCursor` → the app's
`cursorChangeListener` → `highlightEditorRow()`, which uses the row tables fetched once per
render from `/getActivityPositions` and `/getSequencePositions`.

## Configuration

| Setting | Meaning |
| --- | --- |
| `plantumlInteractive.plantumlJar` | Absolute path to `plantuml.jar`. Defaults to a shared install path usable only where it is provisioned; clear it to fall back to the `PLANTUML_JAR` environment variable. |
| `plantumlInteractive.pythonPath` | Absolute path to a Python interpreter that has `plantuml-gui` installed. Required. |

Nothing is guessed. `resolvePythonPath()` will not fall back to a `python` on `PATH`,
because the backend is a package no machine has by default: an interpreter found by
searching almost certainly cannot import `plantuml_gui`, and spawning it would report the
failure against the wrong thing. Failing early names the knob to turn.

## Development

Backend or frontend changes:

1. Edit `src/plantuml_gui/` — templates, `static/`, `static/vscode/`, routes.
2. Reopen the diagram panel. The page is fetched fresh on every open, so there is no build
   or sync step.

Cache busting is handled by `generate_static_js_hash()` in `shared/routes.py`, which hashes
every `.js` under `static/` (including subdirectories, for the shims) and appends
`?v=<hash>` to every script tag. It is cached for the life of the process.

Extension changes:

1. `npm install` in `plantuml-extension/`.
2. Press F5 to launch the Extension Development Host.
3. `npm test` runs the Mocha suite via `@vscode/test-cli`.

The Extension Development Host launches **without a workspace folder**, so workspace-scoped
settings are not read there at all. `.vscode/launch.json` sets `PLANTUML_GUI_PYTHON` in its
`env` block instead, which `resolvePythonPath()` accepts as a second source.

## Cross-runtime contracts

There is no shared schema, so these values are duplicated and must be kept in step by hand.
Each site carries a comment naming the other.

| Value | Node | Python |
| --- | --- | --- |
| `PLANTUML_GUI_PORT=` | `src/sidecar.js` (`PORT_LINE_PREFIX`) | `serve.py` (`PORT_LINE_PREFIX`) |
| `X-PlantUML-Token` | `src/sidecar.js` (`TOKEN_HEADER`) | `serve.py` (`TOKEN_HEADER`) |
| `/webview` | `src/webviewPage.js` (`WEBVIEW_PATH`) | `serve.py` (`WEBVIEW_ROUTE`) |
| `PLANTUML_GUI_TOKEN`, `PLANTUML_GUI_JAR_OVERRIDE` | `src/sidecar.js` (`buildEnv`) | `serve.py` (`TOKEN_ENV`, `JAR_ENV`) |
| The five message types | `extension.js` | `static/vscode/` shims |

One more invariant lives entirely in the page: the script load order in `webview.html` —
vendor, then shims, then app, then boot. Every step of it is justified in that file.

## Troubleshooting

| Symptom | Where to look |
| --- | --- |
| Notification on opening the panel | The message names the setting to change. |
| Diagram never renders, menus work | Jar problem. Check the `PlantUML Interactive` output channel for `check_jar`'s warning. |
| Nothing is interactive but the diagram renders | Likely a missing DOM id throwing during setup. Open the webview devtools: *Developer: Open Webview Developer Tools*. |
| Python traceback | The `PlantUML Interactive` output channel, which receives the sidecar's stderr. |
| Frontend change not visible | Reopen the panel; the page is only fetched on open. |
