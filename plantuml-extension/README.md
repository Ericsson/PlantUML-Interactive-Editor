# PlantUML Interactive Editor (VS Code)

Edit PlantUML diagrams by clicking them. Opens a diagram panel beside a `.puml`
file: right-click elements for context menus, double-click to edit text, and
every change is written back into the document as a single undoable edit.

Internal extension, distributed as a `.vsix`.

## Installing

Two artefacts, because the extension is a thin client: the diagram-rewriting
logic *and* the frontend both live in the Python backend, which the extension
runs as a local child process.

| File | What it is |
| --- | --- |
| `plantuml-editor-<version>.vsix` | the extension |
| `plantuml_gui-<version>-py3-none-any.whl` | the backend |

Install both from the same handover. The frontend ships inside the wheel, so a
newer `.vsix` paired with an older wheel gives you an older UI, and the two
processes agree on their protocol only when built together.

```bash
# 1. the backend, in an interpreter of its own
python3 -m venv ~/.venvs/plantuml
~/.venvs/plantuml/bin/pip install plantuml_gui-<version>-py3-none-any.whl

# 2. the extension
code --install-extension plantuml-editor-<version>.vsix
```

Then set one setting, `plantumlInteractive.pythonPath`, to that interpreter —
the absolute path, `/home/<user>/.venvs/plantuml/bin/python`, since `~` is not
expanded. In a remote window it lives under the Settings editor's **Remote**
tab. Nothing else needs configuring: `plantumlInteractive.plantumlJar` can stay
empty on a machine that has the shared PlantUML install.

Any interpreter works so long as `import plantuml_gui` succeeds from it; a venv
just keeps it away from your system packages. `pip` fetches Flask and the other
runtime dependencies during step 1, so that step needs access to a package
index.

## Requirements

**Python 3.10 or newer**, with the wheel above installed into it. There is no
fallback to whatever `python3` is on `PATH`, because an interpreter found that
way almost certainly cannot import the package, and the resulting error would
blame the wrong thing.

**Java, and a `plantuml.jar`.** Rendering shells out to `java -jar
plantuml.jar`. Inside Ericsson the provisioned install is found automatically;
elsewhere, point `plantumlInteractive.plantumlJar` at your own copy. Java itself
is expected on `PATH` and is not checked before use.

## Settings

| Setting | What it is |
| --- | --- |
| `plantumlInteractive.pythonPath` | Absolute path to the interpreter described above. Required. |
| `plantumlInteractive.plantumlJar` | Absolute path to `plantuml.jar`. Optional if one of the fallbacks below applies. |

Both are `machine-overridable`, because both are absolute paths to things
installed on one particular machine: they are not carried between machines by
Settings Sync, and they do not belong in a repository's
`.vscode/settings.json`.

Surrounding whitespace and one matching pair of surrounding quotes are stripped,
so a path pasted out of a terminal works as-is. Nothing else is expanded — `~`,
`${workspaceFolder}` and `${env:...}` are taken literally.

## Environment variables

Both settings have an environment variable equivalent, read from the
environment the extension host was launched with:

| Variable | Stands in for |
| --- | --- |
| `PLANTUML_GUI_PYTHON` | `plantumlInteractive.pythonPath` |
| `PLANTUML_JAR` | `plantumlInteractive.plantumlJar` |

`PLANTUML_JAR` is the same variable the web app reads, so a repository `.env`
already configures the extension.

## Which value wins

The interpreter:

1. `plantumlInteractive.pythonPath`
2. `PLANTUML_GUI_PYTHON`
3. otherwise an error naming both

The jar:

1. `plantumlInteractive.plantumlJar`
2. `PLANTUML_JAR`
3. the shared internal install, if this machine has it
4. otherwise an error naming both knobs and the path it looked for

In both cases a source that is set but does not point at a file **stops**
resolution rather than falling through to the next one, and the error says which
knob supplied the bad path. Falling through would mean a mistyped setting
silently rendering from something else — configuration that looks ignored.

Both paths are checked before the backend is started, so a mistake is a
notification naming the setting rather than a failure on your first render.
Those notifications carry an **Open Settings** button.

The jar path is handed to the backend when it starts, so changing either setting
takes effect the next time the backend starts — reload the window if a diagram
panel is already open.

## Usage

One command: **PlantUML: Open Interactive Diagram**, from the Command Palette,
with the `.puml` file you want open in the active editor.

## Contributing

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

## Building a release

```bash
uv build --wheel                            # repo root -> dist/*.whl
cd plantuml-extension && npm run package    # -> plantuml-editor-<version>.vsix
```

Build both from the same commit and hand them over together, for the reason
given under Installing. `uv build` without `--wheel` also writes a source
archive, which nobody installing the extension needs.

Architecture, the sidecar protocol and the webview contract are documented in
[`docs/extension.md`](../docs/extension.md).
