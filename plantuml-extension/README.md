# PlantUML Interactive Editor (VS Code)

Edit PlantUML diagrams by clicking them. Opens a diagram panel beside a `.puml`
file: right-click elements for context menus, double-click to edit text, and
every change is written back into the document as a single undoable edit.

Internal extension, distributed as a `.vsix`.

## Requirements

**Python 3.10 or newer** on your `PATH` (check with `python3 --version`) — used
to create the virtual environment the extension runs as a local child process.

**Java and a `plantuml.jar`.** Rendering shells out to
`java -jar plantuml.jar`. A shared internal install is used when the machine has
one; otherwise set `plantumlInteractive.plantumlJar` to your own copy.

## Installing

The `.vsix` carries the extension alone; the frontend and the diagram-rewriting
routes live in the Python wheel. Install both from the same build — an older
wheel means an older UI. Check the internal setup guide for where to get them,
or build them yourself (see "Development" below).

From the directory containing the wheel and `.vsix`:

```
python3 -m venv ~/.local/share/plantuml-gui/venv
~/.local/share/plantuml-gui/venv/bin/pip install plantuml_gui-<version>-py3-none-any.whl
code --install-extension plantuml-editor-<version>.vsix
```

The extension looks there, so there is nothing to configure. Installing
somewhere else works too — point `plantumlInteractive.pythonPath` at that
interpreter instead. Any interpreter will do so long as `import plantuml_gui`
succeeds from it.

## Settings

| Setting | Environment variable | What it is |
| --- | --- | --- |
| `plantumlInteractive.pythonPath` | `PLANTUML_GUI_PYTHON` | Absolute path to the interpreter described above. Optional if the venv is in the standard location. |
| `plantumlInteractive.plantumlJar` | `PLANTUML_JAR` | Absolute path to `plantuml.jar`. Optional if one of the fallbacks below applies. |

Both settings can be overridden by their environment variable. `PLANTUML_JAR`
is the same variable the web app reads, so a repository `.env` already
configures the extension. The VS Code setting takes precedence over the
environment variable; if you do set one and the path is wrong, you get an
error naming it — the fallbacks are not tried, so a typo cannot look like it
worked.

Both settings are `machine-overridable`: set them in machine settings, not in
a repository's `.vscode/settings.json`. In a remote window they appear under the
Settings editor's **Remote** tab.

Whitespace and one matching pair of surrounding quotes are stripped, so a path
pasted from a terminal works as-is. Nothing else is expanded — `~`,
`${workspaceFolder}` and `${env:...}` are taken literally.

Both paths reach the backend when it starts, so a changed setting takes effect
on the next start — reload the window if a diagram panel is already open.

## Usage

With a `.puml` file open in the active editor, run **PlantUML: Open Interactive
Diagram** from the Command Palette.

## Development

`F5` runs the Extension Development Host from `.vscode/launch.json`. That host
launches **without a workspace folder**, so workspace-scoped settings are not
read there; the `env` block in `launch.json` sets `PLANTUML_GUI_PYTHON` instead,
which is why that variable exists.

```
npm run lint     # eslint
npm test         # eslint, then the Mocha suites inside a real VS Code
```

`npm test` launches an actual editor, so it needs a display — under a headless
shell, run it with `xvfb-run`.

A release is those two files, built from the same commit. Both end up in the
repo root's `dist/` directory:

```
uv build --wheel                                    # from repo root -> dist/*.whl
cd plantuml-extension && npm run package -- -o ../dist/  # -> dist/plantuml-editor-<version>.vsix
```

Architecture, the sidecar protocol and the webview contract are documented in
[`docs/extension.md`](../docs/extension.md).
