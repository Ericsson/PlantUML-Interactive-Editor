# PlantUML Interactive Editor (VS Code)

Edit PlantUML diagrams by clicking them. Opens a diagram panel beside a `.puml`
file: right-click elements for context menus, double-click to edit text, and
every change is written back into the document as a single undoable edit.

Internal extension, distributed as a `.vsix`.

## Requirements

**A Python interpreter with the `plantuml-gui` package installed**:

```
pip install /path/to/PlantUML-Interactive-Editor
```

**Java and a `plantuml.jar`.** Rendering shells out to
`java -jar plantuml.jar`. A default install is used automatically if present;
otherwise, point the extension at your own copy.

## Settings

| Setting | Environment variable | What it is |
| --- | --- | --- |
| `plantumlInteractive.pythonPath` | `PLANTUML_GUI_PYTHON` | Absolute path to the interpreter described above. Required. |
| `plantumlInteractive.plantumlJar` | `PLANTUML_JAR` | Absolute path to `plantuml.jar`. Optional if one of the fallbacks below applies. |

Both settings can be overridden by their environment variable, read from the
environment the extension host was launched with. `PLANTUML_JAR` is the same
variable the web app reads, so a repository `.env` already configures the
extension.

Both settings are `machine-overridable`, because both are absolute paths to things
installed on one particular machine: they are not carried between machines by
Settings Sync, and they do not belong in a repository's
`.vscode/settings.json`.

Surrounding whitespace and one matching pair of surrounding quotes are stripped,
so a path pasted out of a terminal works as-is. Nothing else is expanded — `~`,
`${workspaceFolder}` and `${env:...}` are taken literally.

## Which value wins

For both, the VS Code setting takes precedence over the environment variable.
If neither is set, the jar falls back to the shared internal install, if this
machine has it.

The jar path is handed to the backend when it starts, so changed settings take
effect on restart — reload the window if a diagram panel is already open.

## Usage

With a `.puml` file open in the active editor, run **PlantUML: Open Interactive
Diagram** from the Command Palette.

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
