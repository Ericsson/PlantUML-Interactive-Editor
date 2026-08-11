# PlantUML Interactive Editor (VS Code)

Edit PlantUML diagrams by clicking them. Opens a diagram panel beside a `.puml`
file: right-click elements for context menus, double-click to edit text, and
every change is written back into the document as a single undoable edit.

Internal extension, distributed as a `.vsix`.

## Requirements

**Python 3.10 or newer**, and the `plantuml-gui` package installed into it —
that package is the rendering backend, which the extension runs as a local child
process.

**Java and a `plantuml.jar`.** Rendering shells out to
`java -jar plantuml.jar`. A default install is used automatically if present;
otherwise, point the extension at your own copy.

## Installing

Two files, built from the same commit: the extension, and the backend it runs.
The frontend ships inside the wheel, so a mismatched pair means an old UI.

```
python3 -m venv ~/.venvs/plantuml
~/.venvs/plantuml/bin/pip install plantuml_gui-<version>-py3-none-any.whl
code --install-extension plantuml-editor-<version>.vsix
```

Then set `plantumlInteractive.pythonPath` to that interpreter's absolute path.
Any interpreter works so long as `import plantuml_gui` succeeds from it.

## Settings

| Setting | Environment variable | What it is |
| --- | --- | --- |
| `plantumlInteractive.pythonPath` | `PLANTUML_GUI_PYTHON` | Absolute path to the interpreter described above. Required. |
| `plantumlInteractive.plantumlJar` | `PLANTUML_JAR` | Absolute path to `plantuml.jar`. Optional if one of the fallbacks below applies. |

Both settings can be overridden by their environment variable. `PLANTUML_JAR`
is the same variable the web app reads, so a repository `.env` already
configures the extension.

Both settings are `machine-overridable`: set them in machine settings, not in
a repository's `.vscode/settings.json`. In a remote window they appear under the
Settings editor's **Remote** tab.

Surrounding whitespace and one matching pair of surrounding quotes are stripped,
so a path pasted out of a terminal works as-is. Nothing else is expanded — `~`,
`${workspaceFolder}` and `${env:...}` are taken literally.

## Which value wins

For both, the VS Code setting takes precedence over the environment variable.
If neither is set, the jar falls back to the shared internal install, if this
machine has it. The jar path is handed to the backend when it starts, so changed
settings take effect on restart — reload the window if a diagram panel is
already open.

## Usage

With a `.puml` file open in the active editor, run **PlantUML: Open Interactive
Diagram** from the Command Palette.

## Development

`F5` runs the Extension Development Host from `.vscode/launch.json`. That host
launches **without a workspace folder**, so workspace-scoped settings are not
read there at all; the `env` block in `launch.json` sets `PLANTUML_GUI_PYTHON`
instead, which is why that variable exists.

```
npm run lint     # eslint
npm test         # eslint, then the Mocha suites inside a real VS Code
```

`npm test` launches an actual editor, so it needs a display — under a headless
shell, run it with `xvfb-run`.

Building the two files a release needs:

```
uv build --wheel                            # repo root -> dist/*.whl
cd plantuml-extension && npm run package    # -> plantuml-editor-<version>.vsix
```

Architecture, the sidecar protocol and the webview contract are documented in
[`docs/extension.md`](../docs/extension.md).
