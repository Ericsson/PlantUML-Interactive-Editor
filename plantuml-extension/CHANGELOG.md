# Change Log

The extension's version tracks the `plantuml-gui` backend it is built against,
since the two are installed as a pair and the frontend ships inside the backend.
A VS Code manifest requires three-component semver, so backend `0.31` is
extension `0.31.0`.

Changes to the diagram editing itself are listed in the repository's
[CHANGELOG.md](../CHANGELOG.md).

## [Unreleased]

- Added support for diagrams written in Markdown files. A `.md` file holding a
  ` ```plantuml ` block is followed by the diagram panel: put the caret in a
  block and the panel shows that diagram, and editing it in the panel rewrites
  the block's lines and leaves the prose around them alone. A file may hold
  several — moving the caret into another block switches to it, the caret in
  prose keeps the current one on screen, and the tab names the block by its
  fence line (`notes.md:12`). A fence indented inside a list item keeps its
  indentation, and the PNG button exports the diagram the panel is showing.
  A block counts once it opens with ` ```plantuml `, holds a `@start…` line and
  is closed.
- Switching the diagram the panel shows, or the file, now leaves the editor's
  change highlighting on the lines you edited. Arriving at another diagram
  previously marked most of its lines as freshly changed.

## [0.31.0]

- First packaged release.
