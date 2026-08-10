# PlantUML Interactive Editor (VS Code)

Edit PlantUML diagrams by clicking them. Opens a diagram panel beside a `.puml`
file: right-click elements for context menus, double-click to edit text, and
every change is written back into the document as a single undoable edit.

Internal extension, distributed as a `.vsix`.

## Requirements

Two things have to exist on your machine before the extension can render
anything.

**A Python interpreter with the `plantuml-gui` package installed.** The
extension does not render diagrams itself; it runs that package as a local
backend. Any interpreter will do as long as the package is importable from it:

```
pip install /path/to/PlantUML-Interactive-Editor
```

There is no fallback to whatever `python3` is on PATH, because an interpreter
found that way almost certainly cannot import the package, and the resulting
error would blame the wrong thing.

**Java and a `plantuml.jar`.** Rendering shells out to
`java -jar plantuml.jar`. Inside Ericsson the provisioned install is used
automatically; elsewhere, point the extension at your own copy.

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

Architecture, the sidecar protocol and the webview contract are documented in
[`docs/extension.md`](../docs/extension.md).
