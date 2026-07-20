# Frontend-Backend Contract

This document describes the JSON payloads exchanged between the JavaScript frontend and the Flask backend.

## Common Request Fields

Most POST requests from the frontend include some subset of these fields:

- `plantuml` — The current puml text from the Ace editor (whitespace-trimmed via `trimlines()`)
- `svg` — The rendered SVG's inner HTML (`element.querySelector('g').innerHTML`)
- `svgelement` — The `outerHTML` of the specific SVG element that was clicked/right-clicked (`lastclickedsvgelement.outerHTML`)

These three fields together give the backend everything it needs to identify what was clicked and where it lives in the source.

## Common Response Format

- **Modified puml (activity routes)** — Activity routes return plain text (the full modified puml string). The frontend calls `setPuml(responseText)` which indents and sets the editor value, triggering a re-render.
- **Modified puml (sequence routes)** — Sequence routes return `jsonify({"plantuml": updated_puml})`. The frontend parses JSON and calls `setPuml(data.plantuml)`.
- **JSON results** — Routes that return line numbers or boolean checks use `jsonify({"result": value})`. Some return additional fields like `{"result": bool, "type": str}`.

## activity.js Requests

`activity.js` handles all activity diagram interactions. It sends requests in two patterns:

**Pattern 1 — Direct element operations:**

```json
{
  "plantuml": "...",
  "svg": "...",
  "svgelement": "..."
}
```

Used by: deleteActivity, detachActivity, breakActivity, checkBackward, addNoteActivity, getText

**Pattern 3 — Whole-diagram queries (no `svgelement`):**

- getActivityPositions: `{plantuml, svg}`; returns per-type row lists (see below) — fetched once per render for editor→diagram hover highlighting

**Pattern 2 — Operations with extra parameters:**

- editText: adds `newname` (new activity text)
- addToActivity: adds `type` (activity, if, while, repeat, fork, switch, stop, start, end, connector)
- addArrowLabel: adds `where` (above/below)
- editTextIf: adds `statement`, `branch1`, `branch2`
- addToIf: adds `where`, `type`
- editTextWhile: adds `whilestatement`, `break`, `loop`
- addToWhile: adds `type`, `where` (loop/break)
- addToEllipse: adds `where`, `type`
- editCharConnector: adds `text`
- addToConnector: adds `where`, `type`
- editNote: adds `text`
- editGroup: adds `text`
- editArrow: adds `text`
- addToFork: adds `line` (int), `type`
- forkToggle2: adds `line` (int)
- deleteFork2: adds `line` (int)

## sequence.js Requests

`sequence.js` handles sequence diagram interactions:

- **addParticipant:** `{plantuml, svg, svgelement, direction}` — direction is 'left' or 'right'; returns `{"plantuml": updated_puml}`
- **getParticipantName:** `{plantuml, svg, svgelement}`; returns `{"name": participant_name}`
- **editParticipantName:** `{plantuml, svg, name, svgelement}`; returns `{"plantuml": updated_puml}`
- **deleteParticipant:** `{plantuml, svg, svgelement}`; returns `{"plantuml": updated_puml}`
- **addMessage:** `{plantuml, svg, message, svgelement, firstcoordinates, secondcoordinates}` — coordinates are `[x, y]` arrays; y-coordinate determines insertion position between existing messages; returns `{"plantuml": updated_puml}`
- **getSequencePositions:** `{plantuml, svg}`; returns `{"participants": [{name, cx, yTop, yBottom, index}, ...], "messages": [{cy, index, text}, ...], "notes": [{cy, index}, ...], "groups": [{headerIndex, endIndex}, ...], "boxes": [{headerIndex, endIndex}, ...]}` — called once per render; bundles every sequence element type's position table into one response so a render costs a single round-trip. Fetched into `participantLifelines`, `messagePositions`, `notePositions`, `groupPositions`, `boxPositions`. Powers hover detection/highlighting, the ghost arrow, and the activation/group snapping gestures
- **getMessageText:** `{plantuml, svg, svgelement}`; returns `{"text": message_label, "color": arrow_color}` — fetches current message label and arrow color (leading `#` stripped, `""` when uncolored) for the edit modal
- **editMessageText:** `{plantuml, svg, svgelement, text, color?}`; returns `{"plantuml": updated_puml}` — replaces the message label text and sets the arrow color as a `[#color]` token; `color` omitted/`null` leaves any existing color unchanged, `""`/`"none"` removes it
- **deleteMessage:** `{plantuml, svg, svgelement}`; returns `{"plantuml": updated_puml}` — removes the message line from puml
- **addNote:** `{plantuml, svg, participant, placement, text, yPosition, secondParticipant?, noteType?}`; returns `{"plantuml": updated_puml}` — inserts a note at the Y-position; placement is 'over', 'left', 'right', or 'spanning'; noteType is 'note', 'hnote', or 'rnote' (defaults to 'note' if missing/unrecognized); all three types support the same placement grammar
- **getSeqNoteText:** `{plantuml, svg, svgelement}`; returns `{"text": note_text, "noteType": "note"|"hnote"|"rnote", "color": note_color}` — fetches current note text, detected type, and background color (leading `#` stripped, `""` when uncolored) for the edit modal
- **editSeqNote:** `{plantuml, svg, svgelement, text, noteType?, color?}`; returns `{"plantuml": updated_puml}` — replaces the note text and, if `noteType` differs from the note's current type, rewrites its keyword; `color` sets the note background as a `#color` token (e.g. `note over A #LightBlue : text`), omitted/`null` leaves any existing color unchanged, `""`/`"none"` removes it
- **deleteSeqNote:** `{plantuml, svg, svgelement}`; returns `{"plantuml": updated_puml}` — removes the note line from puml
- **addActivation:** `{plantuml, participant, startMessageIndex, endMessageIndex, endType}`; returns `{"plantuml": updated_puml}` — inserts a matched `activate` line after the message at `startMessageIndex` and a closing `deactivate`/`destroy` line after the message at `endMessageIndex`; `endType` is 'deactivate' or 'destroy' (defaults to 'deactivate')
- **deleteActivation:** `{plantuml, svg, svgelement}`; returns `{"plantuml": updated_puml}` — `svgelement` is the right-clicked activation-bar rect; removes that bar's `activate` line and its paired `deactivate`/`destroy` line (handles nested bars)
- **addGroup:** `{plantuml, groupType, label, startMessageIndex, endMessageIndex}`; returns `{"plantuml": updated_puml}` — wraps messages between `startMessageIndex` and `endMessageIndex` in a `<groupType> <label> ... end` block; `groupType` is 'group', 'alt', 'opt', or 'loop'; indexes are puml line numbers from `messagePositions`; range is normalized (order does not matter); returns 400 with `{"error": message}` for invalid group types
- **getSeqGroupLabel:** `{plantuml, svg, svgelement}`; returns `{"type": keyword, "label": label_text}` — `svgelement` is the clicked group's box rect (`fill="none"`); fetches the current title for the rename modal
- **renameSeqGroup:** `{plantuml, svg, svgelement, label}`; returns `{"plantuml": updated_puml}` — replaces only the text after the keyword on the header line
- **deleteSeqGroup:** `{plantuml, svg, svgelement}`; returns `{"plantuml": updated_puml}` — unwraps the group: removes the header and its matching `end` line, keeping the contents in place
- **addBox:** `{plantuml, startParticipantIndex, endParticipantIndex, title?, color?}`; returns `{"plantuml": updated_puml}` — wraps the contiguous participants between the two puml line indexes (from `participantLifelines`) in a `box ... end box` block; range is normalized; `title`/`color` are optional and the current UI omits both (bare `box`); inserts `!pragma teoz true` once if the range nests with an existing box; returns 400 with `{"error": message}` if the range crosses an existing box
- **deleteSeqBox:** `{plantuml, svg, svgelement}`; returns `{"plantuml": updated_puml}` — `svgelement` is the clicked box rect (participant-header style, no `rx`/`ry`, solid fill, enclosing a participant header); unwraps the box: removes the `box` header and its matching `end box` line, keeping the participants in place
- **getSeqBoxLabel:** `{plantuml, svg, svgelement}`; returns `{"title": title_text, "color": color}` — the clicked box's current title (HTML-unescaped) and color (leading `#` stripped, matching the palette option values); both `""` when absent; populates the Edit Box modal
- **editSeqBox:** `{plantuml, svg, svgelement, title?, color?}`; returns `{"plantuml": updated_puml}` — rewrites the clicked box's header with the new title (HTML-escaped, quoted; empty → bare `box`) and color (`#`-prefixed; `""`/`"none"` → omitted)

Message and note `text`/`message` fields may contain real newlines (the textareas allow multi-line input via Enter). Since messages and notes are single-line puml statements, `add_message`/`add_note`/`edit_message_text`/`edit_note` escape real newlines to a literal `\n` before writing the line (`escape_multiline_text` in `sequence/util.py`), and `get_message_text`/`get_note_text`/`get_message_positions` unescape `\n` back to real newlines before returning text to the frontend (`unescape_multiline_text`).

## script.js Requests

`script.js` handles core operations:

- **render:** `{plantuml}` → returns SVG text
- **renderPNG:** `{plantuml}` → returns PNG blob
- **encode:** `{plantuml}` → returns URL-encoded string
- **decode:** `{hash}` → returns puml text
- **addTitle:** `{plantuml}` → returns modified puml

## How Click Coordinates Reach the Backend

For activity diagrams, the frontend captures `lastclickedsvgelement` on right-click (the actual SVG DOM element). Its `outerHTML` is sent as `svgelement`. The backend reconstructs the element's geometric identity (x/y for rects, points for polygons, cx/cy for ellipses) to match it against the parsed SVG.

For sequence diagrams, the frontend computes `cx` from the clicked rect's x + width/2. For messages, the frontend fetches participant positions once per render via `/getSequencePositions` (the `participants` table) and uses them for hover detection (±15px tolerance from lifeline cx). It sends the lifeline cx and cursor y as `[x, y]` coordinates. The y-coordinate determines insertion position between existing messages.

## Editor <-> Diagram Hover Highlighting (Sequence Diagrams)

Each render, the frontend fetches all position tables in a single `/getSequencePositions` round-trip and stores them in module-level arrays: `messagePositions`, `participantLifelines`, `notePositions`, `groupPositions`, `boxPositions`. No further backend round-trip is needed for highlighting itself — both directions are resolved client-side against these cached tables:

- **Diagram → editor**: hovering an SVG element looks up its puml line index from the matching table and calls `setEditorMarkers`/`getmarker` to paint that line.
- **Editor → diagram**: moving the cursor or mouse over a line in the editor (`highlightSequenceForRow` in `sequence-operations.js`) checks the tables for that row, then finds the matching SVG element(s) by counting shapes in document order (e.g. the Nth note/hnote/rnote shape, identified by tag + shape structure + `stroke-width:0.5` rather than fill color; the Nth group box immediately following its `#EEEEEE` tab; the Nth participant box, identified by `is_box_rect`'s enclosure test) and highlights them directly — no fetch involved.

Highlights applied by the editor→diagram direction are tracked in `sequenceHighlighted` (`{el, kind, old}`) so the original style/fill can be restored exactly, and so that hovering the same element from the diagram side doesn't clobber the recorded original value.

## Editor <-> Diagram Hover Highlighting (Activity Diagrams)

Both directions are resolved client-side from a single per-render `getActivityPositions` fetch — no per-hover backend request. (This replaced the old per-element `get*Line` routes, which have been removed.)

- **getActivityPositions:** `{plantuml, svg}`; returns `{"activities": [[rows]...], "polys": [[rows]...], "whiles": [[rows]...], "notes": [[rows]...], "groups": [[rows]...], "ellipses": [[rows]...], "connectors": [[rows]...], "merges": [[rows]...], "arrows": [[rows]...], "title": [rows]}` — for each element type, the puml line indexes owned by the nth element of that type in SVG document order. Range types (activities, notes, arrows, title) list every row of the block; structural types list only their keyword rows (e.g. a group lists its header and closing line, an if lists `if`/`else`/`endif`).

During the handler-setup walk over the SVG, `activity.js` registers each hoverable element into `activityHoverTargets` per type, in the same document order the backend counts — the same ordinal-alignment invariant the removed `get*Line` routes once relied on. `buildActivityRowMap` joins the two by ordinal, building both `activityRowMap` (editor row → elements, for editor→diagram) and the inverse `activityElementRows` (element → rows, for diagram→editor). Fork rows come from the client-side `labelForks` data instead of the backend, and the walk mirrors two backend counting quirks: the first ellipse of an `end` marker's concentric pair is skipped, as are note-path candidates flagged `pointer-events: none`.

- **Editor → diagram**: `highlightActivityForRow(row)` highlights every element registered on that row: shapes get a fill (`#d8d8d8`; `#818181` for start/stop, `#c2c2c2` for connectors, `#e5e5e5` for the title box) while label texts (partition labels, arrow labels) get `font-weight: bold`, matching the sequence convention for text. Applied highlights are tracked in `activityHighlighted` (`{el, attr, old}`) and restored exactly by `resetActivityHighlight()`; elements already showing the highlight value (e.g. a diagram-side hover in progress) are skipped so the true original is never overwritten.
- **Diagram → editor**: hovering a diagram element calls `markEditorForElement(activityElementRows, el)`, a synchronous lookup in the cached inverse map that paints the owning editor line(s) — no per-hover fetch.

## Response Handling

Activity routes return plain text; the frontend reads it directly:

```javascript
const response = await fetch(endpoint, { method: 'POST', headers: {...}, body: JSON.stringify(payload) });
const pumlcontentcode = await response.text();
setPuml(pumlcontentcode);
```

Sequence routes return JSON; the frontend parses and extracts the field:

```javascript
const data = await response.json();
setPuml(data.plantuml); // or data.name for getParticipantName
```

`setPuml()` processes fork/switch keywords, re-indents the puml, and sets the Ace editor value — which triggers the debounced `renderPlantUml()` to re-render the diagram.

## Changelog

The Version History modal fetches release notes via a simple GET:

```javascript
const response = await fetch('/changelog');
const data = await response.json();
```

Response is a JSON array:

```json
[
  {"version": "0.28", "date": "2025-08-18", "entries": ["Added Load and Save buttons", ...]},
  ...
]
```

No request body. Only External changelog entries are included.
