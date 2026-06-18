# Frontend-Backend Contract

This document describes the JSON payloads exchanged between the JavaScript frontend and the Flask backend.

## Common Request Fields

Most POST requests from the frontend include some subset of these fields:

- `plantuml` — The current puml text from the Ace editor (whitespace-trimmed via `trimlines()`)
- `svg` — The rendered SVG's inner HTML (`element.querySelector('g').innerHTML`)
- `svgelement` — The `outerHTML` of the specific SVG element that was clicked/right-clicked (`lastclickedsvgelement.outerHTML`)

These three fields together give the backend everything it needs to identify what was clicked and where it lives in the source.

## Common Response Format

- **Modified puml** — The majority of routes return plain text (the full modified puml string). The frontend calls `setPuml(responseText)` which indents and sets the editor value, triggering a re-render.
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

Used by: deleteActivity, detachActivity, breakActivity, checkBackward, addNoteActivity, getText, getActivityLine

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

- **addParticipant:** `{plantuml, svg, svgelement, direction}` — direction is 'left' or 'right'
- **getParticipantName:** `{plantuml, svg, svgelement}`
- **editParticipantName:** `{plantuml, svg, name, svgelement}`
- **deleteParticipant:** `{plantuml, svg, svgelement}`
- **addMessage:** `{plantuml, svg, message, svgelement, firstcoordinates, secondcoordinates}` — coordinates are `[x, y]` arrays from two clicks
- **checkIfInsideParticipant:** `{plantuml, svg, coordinates}` — coordinates is `[x, y]`

## script.js Requests

`script.js` handles core operations:

- **render:** `{plantuml}` → returns SVG text
- **renderPNG:** `{plantuml}` → returns PNG blob
- **encode:** `{plantuml}` → returns URL-encoded string
- **decode:** `{hash}` → returns puml text
- **addTitle:** `{plantuml}` → returns modified puml

## How Click Coordinates Reach the Backend

For activity diagrams, the frontend captures `lastclickedsvgelement` on right-click (the actual SVG DOM element). Its `outerHTML` is sent as `svgelement`. The backend reconstructs the element's geometric identity (x/y for rects, points for polygons, cx/cy for ellipses) to match it against the parsed SVG.

For sequence diagrams, the frontend computes `cx` from the clicked rect's x + width/2. For messages, it captures raw `[x, y]` coordinates from two sequential clicks on the SVG.

## Response Handling

The frontend handles responses uniformly:

```javascript
const response = await fetch(endpoint, { method: 'POST', headers: {...}, body: JSON.stringify(payload) });
const pumlcontentcode = await response.text();
setPuml(pumlcontentcode);
```

`setPuml()` processes fork/switch keywords, re-indents the puml, and sets the Ace editor value — which triggers the debounced `renderPlantUml()` to re-render the diagram.

For JSON responses (line numbers), the frontend uses them to highlight the corresponding editor line:

```javascript
const data = await response.json();
getmarker(data.result);
```

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
