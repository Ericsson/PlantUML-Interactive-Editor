# Routes

All routes are organized into Blueprints: `shared_bp` (in `shared/routes.py`) for general/render/encode routes, `sequence_bp` (in `sequence/routes.py`) for sequence diagram routes, and `activity_bp` (in `activity/routes.py`) for activity diagram routes. All are mounted at `/`. Unless stated otherwise, every route accepts `Content-Type: application/json` and returns plain text (the modified puml). Routes returning JSON are noted.

## General

- **GET /** — Serves `index.html`. No input. Returns HTML.
- **GET /changelog** — No input. Returns: JSON array of version objects with `version`, `date`, and `entries` (list of strings). Only includes External changelog entries.

## Render

- **POST /render** — Input: `plantuml`. Returns: SVG string.
- **POST /renderPNG** — Input: `plantuml`. Returns: PNG file download (`image/png`).

## Encode / Decode

- **POST /encode** — Input: `plantuml`. Returns: URL-encoded string.
- **POST /decode** — Input: `hash`. Returns: decoded puml text.

## Activity

- **POST /editText** — Input: `plantuml`, `svg`, `newname`, `svgelement`. Returns: modified puml.
- **POST /getText** — Input: `svg`, `svgelement`. Returns: activity text content.
- **POST /deleteActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addNoteActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addToActivity** — Input: `plantuml`, `svg`, `type`, `svgelement`. Returns: modified puml.
- **POST /detachActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /breakActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /checkBackward** — Input: `plantuml`, `svg`, `svgelement`. Returns: result text.
- **POST /getActivityLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": [start, end]}`.
- **POST /addArrowLabel** — Input: `plantuml`, `svg`, `where`, `svgelement`. Returns: modified puml.

## If Statements

- **POST /checkWhatPoly** — Input: `plantuml`, `svg`, `svgelement`. Returns: result indicating polygon type.
- **POST /checkIfRepeatHasBackward** — Input: `plantuml`, `svg`, `svgelement`. Returns: result.
- **POST /addBackwards** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /editTextIf** — Input: `plantuml`, `svg`, `statement`, `branch1`, `branch2`, `svgelement`. Returns: modified puml.
- **POST /getTextPoly** — Input: `plantuml`, `svg`, `svgelement`. Returns: polygon text content.
- **POST /delIf** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /switchAgain** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /getIfLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.
- **POST /addToIf** — Input: `plantuml`, `svg`, `svgelement`, `where`, `type`. Returns: modified puml.
- **POST /detachIf** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Ellipses (Start/Stop/End)

- **POST /addToEllipse** — Input: `plantuml`, `svg`, `where`, `type`, `svgelement`. Returns: modified puml.
- **POST /deleteEllipse** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /getEllipseLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.

## Title

- **POST /addTitle** — Input: `plantuml`. Returns: modified puml.
- **POST /getTextTitle** — Input: `plantuml`. Returns: title text.
- **POST /editTitle** — Input: `plantuml`, `title`. Returns: modified puml.
- **POST /getTitleLine** — Input: `plantuml`. Returns: JSON `{"result": [start, end]}`.
- **POST /deleteTitle** — Input: `plantuml`. Returns: modified puml.

## Fork

- **POST /deleteFork** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /forkAgain** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /forkToggle** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /forkToggle2** — Input: `plantuml`, `line` (int). Returns: modified puml.
- **POST /deleteFork2** — Input: `plantuml`, `line` (int). Returns: modified puml.
- **POST /addToFork** — Input: `plantuml`, `line` (int), `type`. Returns: modified puml.

## Note

- **POST /getNoteText** — Input: `plantuml`, `svg`, `svgelement`. Returns: note text.
- **POST /editNote** — Input: `plantuml`, `svg`, `text`, `svgelement`. Returns: modified puml.
- **POST /deleteNote** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /noteToggle** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /getNoteLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.

## Group

- **POST /getGroupText** — Input: `plantuml`, `svg`, `svgelement`. Returns: group text.
- **POST /getGroupLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.
- **POST /editGroup** — Input: `plantuml`, `svg`, `svgelement`, `text`. Returns: modified puml.
- **POST /deleteGroup** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Merge

- **POST /getMergeLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.
- **POST /addToMerge** — Input: `plantuml`, `svg`, `svgelement`, `type`. Returns: modified puml.

## While

- **POST /getTextWhile** — Input: `svg`, `svgelement`. Returns: while text.
- **POST /editTextWhile** — Input: `plantuml`, `svg`, `svgelement`, `whilestatement`, `break`, `loop`. Returns: modified puml.
- **POST /delWhile** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addToWhile** — Input: `plantuml`, `svg`, `svgelement`, `type`, `where`. Returns: modified puml.
- **POST /getWhileLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.

## Connector

- **POST /editCharConnector** — Input: `plantuml`, `svg`, `text`, `svgelement`. Returns: modified puml.
- **POST /getCharConnector** — Input: `plantuml`, `svg`, `svgelement`. Returns: connector character.
- **POST /connectorDelete** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /getConnectorLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.
- **POST /detachConnector** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addToConnector** — Input: `plantuml`, `svg`, `svgelement`, `where`, `type`. Returns: modified puml.

## Arrow

- **POST /delArrow** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /checkDuplicateArrow** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": bool, "type": str}`.
- **POST /getArrowText** — Input: `svg`, `svgelement`. Returns: arrow text.
- **POST /editArrow** — Input: `plantuml`, `svg`, `text`, `svgelement`. Returns: modified puml.
- **POST /getArrowLine** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": int}`.

## Sequence Diagram (Participants)

- **POST /addParticipant** — Input: `plantuml`, `svg`, `svgelement`, `direction` ('left'/'right'). Returns: modified puml.
- **POST /addMessage** — Input: `plantuml`, `svg`, `message`, `firstcoordinates` ([x,y]), `secondcoordinates` ([x,y]). Returns: modified puml. Y-coordinate determines insertion position between existing messages.
- **POST /getParticipantPositions** — Input: `plantuml`, `svg`. Returns: JSON `{"positions": [{name, cx, yTop, yBottom}, ...]}`. Called once per render for hover detection.
- **POST /getParticipantName** — Input: `plantuml`, `svg`, `svgelement`. Returns: participant name string.
- **POST /editParticipantName** — Input: `plantuml`, `svg`, `name`, `svgelement`. Returns: modified puml.
- **POST /deleteParticipant** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Sequence Diagram (Messages)

- **POST /getMessageText** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"text": message_label}`.
- **POST /editMessageText** — Input: `plantuml`, `svg`, `svgelement`, `text`. Returns: JSON `{"plantuml": modified_puml}`.
- **POST /deleteMessage** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"plantuml": modified_puml}`.
- **POST /getMessagePositions** — Input: `plantuml`, `svg`. Returns: JSON `{"positions": [{cy, index, text}, ...]}` — one entry per message with its SVG Y-coordinate, puml line index, and label. Called once per render so the frontend can snap activation-bar endpoints to the nearest message.

## Sequence Diagram (Activation Bars)

- **POST /addActivation** — Input: `plantuml`, `participant`, `startMessageIndex` (int), `endMessageIndex` (int), `endType` ('deactivate'/'destroy'). Returns: JSON `{"plantuml": modified_puml}`. Inserts a matched `activate <participant>` line just before the message at `startMessageIndex` and a closing `deactivate <participant>` (or `destroy <participant>`) line just after the message at `endMessageIndex`. The indexes are puml line numbers; the frontend obtains them from `/getMessagePositions`. `endType` defaults to 'deactivate' for any value other than 'destroy'.

## Sequence Diagram (Notes)

- **POST /addNote** — Input: `plantuml`, `svg`, `participant`, `placement` ('over'/'left'/'right'/'spanning'), `text`, `yPosition`, optional `secondParticipant`. Returns: JSON `{"plantuml": modified_puml}`. Y-coordinate determines insertion position.
- **POST /getSeqNoteText** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"text": note_text}`.
- **POST /editSeqNote** — Input: `plantuml`, `svg`, `svgelement`, `text`. Returns: JSON `{"plantuml": modified_puml}`.
- **POST /deleteSeqNote** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"plantuml": modified_puml}`.
