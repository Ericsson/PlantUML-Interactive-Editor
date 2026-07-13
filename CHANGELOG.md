# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### External

- Fixed downloaded PNG diagrams being low resolution and blurry: PlantUML's default PNG rasterization renders at ~96 DPI, so the exported image was much lower quality than the in-app SVG preview; PNG export now renders at 300 DPI (roughly 3x the pixel dimensions)
- Fixed the PNG toolbar button opening the rendered diagram in a new tab instead of downloading it; it now triggers a `diagram.png` file download, matching its "Download diagram as PNG" tooltip
- Added a visible Import button in the code toolbar (left of the Download button, separated by a divider) to load a `.puml`/`.txt` file into the editor; previously this was only reachable via a hidden button. The Download button no longer uses the blue accent style, matching the other toolbar buttons
- Fixed multi-line message text producing invalid PlantUML for sequence diagrams (newlines are now escaped as `\n` in the generated code)
- Fixed multi-line note text producing invalid PlantUML for sequence diagrams (newlines are now escaped as `\n` in the generated code)
- Editor-to-diagram hover highlighting for activity diagrams: hovering or moving the cursor to a line in the editor highlights the matching diagram element for all element types (activities, if/switch/repeat and while statements, notes, partitions, start/stop, connectors, merge markers, arrow labels, forks, title), matching the sequence diagram behavior
- Label texts (partition labels, arrow labels) are highlighted in bold instead of grey, both from the editor side and when hovered in the diagram, matching how sequence diagrams bold message text
- Fixed activity boxes after a `repeat` block without a `backward:` line highlighting the wrong editor line on hover
- Fixed the editor-to-diagram highlight lingering on a sequence diagram element after the pointer left the editor: leaving the editor now clears the editor-side highlight
- Fixed the editor line staying highlighted after hovering an activity diagram element and moving away: the diagram-to-editor hover marker is now cleared when the pointer leaves a diagram element
- Bidirectional hover highlighting for sequence diagrams: hovering a message, participant, note, or group box in the diagram highlights the matching line(s) in the editor, and hovering or moving the cursor to a line in the editor highlights the matching element in the diagram
- Group blocks for sequence diagrams: right-click a lifeline → Add Group sub-menu to pick group/alt/opt/loop, then click two messages to define the range (ghost box preview), type a label, and the group is created
- Rename or delete a sequence group block: right-click the keyword tab or its header text → Rename (edits only the title, keeps the keyword) or Delete Group (unwraps the block, keeping its contents)
- Activation bars for sequence diagrams: right-click a lifeline → Activate, drag down to preview a ghost bar, then left-click and choose Deactivate or Destroy to end it (supports nested activations)
- Delete an activation bar: right-click the bar → Delete activation bar (removes the matched activate + deactivate/destroy pair)
### Internal

- Generalized sequence-diagram note line matching (`sequence/util.py`: `note_line_keyword`, `is_note_line`) to recognize `note`, `hnote`, and `rnote` prefixes uniformly, with an optional `#color` token, instead of only the literal `"note "` prefix. Applied to `_find_note_line_index` and the participant cascade-delete note check in `participant.py`. Not yet wired into SVG-side detection (`extract_note_positions`) - that's the next step.
- Added `classify_note_shape` (`sequence/util.py`): identifies a sequence-diagram note's PlantUML type (`note`/`hnote`/`rnote`) from its SVG shape structure (path/polygon/rect and point count) instead of fill color, laying the groundwork for note-type support without breaking once note colors become user-customizable. Not yet wired into note detection/creation.
- Fixed off-by-one bug in `_nth_ellipse_row` (`activity/positions.py`): `lines[index - 1]` at index 0 wrapped to the last line in Python, silently skipping a `start` on the first line whenever the last line began with "note"; guarded with `index > 0`
- Fixed race condition in `setHandlersForActivityDiagram` (`activity.js`): `fetchActivityPositions` was called without `await`, so the loading overlay could disappear before `activityRowMap` was populated, causing editor-to-diagram hover highlighting to silently do nothing until the fetch completed
- Fixed `test_second_bar_uses_refreshed_message_positions` becoming flaky on slow CI: replaced fixed `wait_for_timeout` calls with `wait_for_function` conditions that wait until `messagePositions` is populated and the puml is updated, matching the approach already used in `TestDeleteActivationFlow`
- Fixed sequence group-box counting mismatch between backend and frontend (`sequence-operations.js`): `get_group_positions` counts only real boxes (those following their `#EEEEEE` tab path, via `_count_group_boxes`), but `setupGroupHandlers` and `highlightSequenceForRow` still advanced their ordinal on every `fill="none"` rect, so PlantUML's invisible layout rect could shift the ordinal and highlight the wrong group; both frontend counters now apply the same tab-pairing rule
- Refactored sequence editor-to-diagram highlighting to the activity diagram pattern (`sequence-operations.js`): the `setup*Handlers` render walk now registers each element into a `sequenceRowMap` (editor row -> elements) via `registerSequenceRow`, and `highlightSequenceForRow` is a map lookup instead of re-walking the whole SVG and re-deriving each element's ordinal on every hover; removes the duplicated ordinal logic that caused the group-count mismatch and matches `highlightActivityForRow`
- Extracted the shared editor-to-diagram hover-highlight core into `static/hover-highlight.js` (pure functions `registerHoverRow`/`highlightHoverRow`/`clearHoverHighlight`/`findActiveHighlight` over a passed-in row map and active list, plus `attributeHighlight`/`stylePropertyHighlight` style factories); both `activity.js` and `sequence-operations.js` now build on it instead of each maintaining its own row-map machinery
- Moved the editor-side hover/cursor dispatch into `hover-highlight.js` (`initEditorHoverHighlighting`, `highlightEditorRow`, `resetEditorHighlight`, `lastEditorHoverRow`), so the mousemove, mouseleave and cursor-change paths share one dispatcher; `script.js` now just calls `initEditorHoverHighlighting(editor)`. Removed the now-redundant `resetActivityHighlight()` from activity's diagram-side element mouseover (the editor mouseleave handler clears the lingering highlight), so both diagram types clear it the same way
- Deduplicated the five hover position-fetchers (participant, message, note, group, activity) behind a shared `fetchDiagramData(endpoint)` helper in `hover-highlight.js` that posts the current puml + SVG and returns the parsed JSON (or null); standardized their error handling to silently disable hover highlighting for that render on failure, where previously `extractLifelinePositions` alone surfaced an error dialog
- Activity diagram-to-editor hover highlighting now reads the cached per-render positions (an element→rows map built in `buildActivityRowMap`, marked via `markEditorForElement`) instead of a per-hover backend fetch; removed the ten `processXLine` functions and their per-hover `getXLine` requests, so hovering a diagram element marks the editor line synchronously, matching how sequence diagrams already work. The `getXLine` activity routes are now unused by the frontend.
- Removed the ten now-unused activity `getXLine` routes (`/getActivityLine`, `/getIfLine`, `/getEllipseLine`, `/getTitleLine`, `/getNoteLine`, `/getGroupLine`, `/getMergeLine`, `/getWhileLine`, `/getConnectorLine`, `/getArrowLine`) and their tests, plus the three orphaned functions `get_note_line`/`get_group_line`/`get_arrow_line` and now-unused imports. The shared line-finders they used stay (still used by `positions.py` and the edit/delete operations).
- Consolidated the four per-render sequence position endpoints (`/getParticipantPositions`, `/getMessagePositions`, `/getSeqNotePositions`, `/getSeqGroupPositions`) into a single `/getSequencePositions` (new `sequence/positions.py` aggregator), matching the activity diagram's one-fetch-per-render pattern; a render now costs one round-trip with one puml+SVG payload instead of four serialized requests each re-sending the payload. The frontend's four fetchers are replaced by one `fetchSequencePositions`; each element type's sub-table keeps its own shape since sequence elements are matched spatially, so the data model is unchanged.
- Fixed the activity ellipse diagram-side hover writing `fill` as `'#818181 '` (trailing space) in `activity.js`: the editor→diagram `ELLIPSE_HIGHLIGHT` applies the space-free `'#818181'`, so during a simultaneous editor+diagram hover the `apply` guard (`old === value`) failed to match, captured the spaced value as the "original", and restored it — the trailing space is removed so both directions use the identical value

## [0.30] - 2026-07-03

### External

- Added group blocks for sequence diagrams (group, alt, opt, loop) with visual two-click range selection
- Added rename and delete for sequence group blocks (delete unwraps the block, keeping its contents)
- Added activation bars for sequence diagrams with visual ghost-bar preview (supports nested activations)
- Added delete activation bar
- Added notes for sequence diagrams with placement options (over, left of, right of, spanning participants)
- Added edit and delete for sequence messages via right-click context menu
- Added visual hover-based "Add Message" interaction with ghost arrow preview and arrow style choice (solid/dashed)
- Added self-message support (send message to same participant)
- Deleting a participant now also deletes any notes referencing that participant
- Fixed note placement incorrectly attaching to a message when clicking outside its horizontal span
- Fixed note near a self-message incorrectly using message-attached syntax

### Internal

- Added /getActivityPositions backend endpoint (activity/positions.py) returning, per element type, the puml rows owned by each element in SVG document order; reuses the existing per-type line finders and counts elements with the same rules as the per-element get*Line routes so frontend registration order matches by ordinal
- Added activityHoverTargets registration in the setHandlersForSvg walk plus buildActivityRowMap/highlightActivityForRow/resetActivityHighlight (activity.js) to resolve editor rows to diagram elements client-side; replaces the old text-matching highlightActivity/resetHighlight/colorqueue mechanism (which only handled plain activity boxes and mismatched on duplicate text)
- Fixed _activity_indices reserving a phantom index slot for a repeat block's backward box even when no backward line exists, which shifted the element-to-line mapping of every activity after the block
- Removed a leftover resetHighlight call from the sequence participant mouseover handler that could corrupt participant fills restored from the editor-highlight bookkeeping
- Added /getSeqNotePositions and /getSeqGroupPositions backend endpoints (get_note_positions, get_group_positions) providing note/group line-index tables for hover highlighting, mirroring the existing /getMessagePositions and /getParticipantPositions pattern
- Added highlightSequenceForRow/resetSequenceHighlight (sequence-operations.js) to resolve editor-row hover/cursor changes to diagram elements client-side, plus the sequenceHighlighted bookkeeping so it can coexist with diagram-side hover highlighting without clobbering restored styles
- Fixed get_group_positions double-counting group boxes when PlantUML's rendering environment causes its invisible per-group layout rect to also carry a literal fill="none" attribute; now pairs each box with its preceding keyword-tab path instead of counting all fill="none" rects
- Added backend logic for sequence group blocks (add_group) wrapping a message range in group/alt/opt/loop...end syntax
- Added /addGroup backend endpoint for sequence group blocks
- Added backend logic for sequence group rename and delete (index_of_clicked_group, get_group_label, rename_group, delete_group); delete unwraps a block by removing only its header and matching `end` line, tracking nesting depth to find the block's own closer
- Added /getSeqGroupLabel, /renameSeqGroup, /deleteSeqGroup backend endpoints for sequence groups (named with a Seq prefix to avoid colliding with the activity diagram's /getGroupLabel-style routes)
- Group context menu only responds to right-clicks on the keyword tab or its header text, not the rest of the box, so messages/notes inside a group keep their own context menus
- Added backend logic and endpoints for sequence group blocks: /addGroup, /getSeqGroupLabel, /renameSeqGroup, /deleteSeqGroup (Seq prefix avoids collision with activity diagram routes)
- Group delete unwraps a block by removing its header and matching `end` line, tracking nesting depth
- Group context menu only responds to right-clicks on the keyword tab or header text, preserving inner element context menus
- Fixed group keyword/label text (bold, font-size 13) being misclassified as message text by checkIfMessageElement
- Fixed seq-group-menu not being hidden by the outside-click handler in addSequenceEventListeners
- Added backend logic and endpoints for activation bars: /addActivation, /getMessagePositions, /deleteActivation
- Activation delete uses stack-paired nesting-aware matching
- Made sequence diagram parsing ignore activation-bar rects so message/participant parsing keeps working
- Cache-busting hash now covers all static JS files, not just script.js
- Added backend logic and endpoints for sequence notes: /addNote, /getSeqNoteText, /editSeqNote, /deleteSeqNote
- Added backend logic and endpoints for sequence messages: edit_message_text, delete_message
- Add message uses y-based insertion to place new messages between existing ones based on click position
- Added /getParticipantPositions endpoint for lifeline position and name extraction
- Fixed reflected XSS in sequence routes by returning `jsonify` instead of raw strings
- Fixed stored XSS in `edit_participant_name` by escaping user input with `html.escape` before writing to puml

## [0.29] - 2026-06-18

### External

- New toolbar interface with zoom in/out/reset controls and resizable divider between code and diagram panes
- Added delete participant for sequence diagrams (right-click on participant, cascade deletes messages)
- Added directional add participant (left/right) from participant context menu
- Added rename participant from participant context menu
- Added divider between add and delete commands in participant context menu
- Fixed undo crash when undoing to first history entry
- Fixed Save button to save content to file
- Made generated PNG copyable
- Added Version History modal showing release notes

### Internal

- Updated README screenshot
- Refactored sequence diagram participant identification to use SVG element matching (same pattern as activity diagrams) instead of coordinate proximity
- Fixed participant number generation to ignore occurrences in comments, notes, and messages
- Restructured HTML layout to ribbon UI shell (global bar + split panes)
- Split styles.css into modular CSS files under static/css/
- Added CSS design tokens for ribbon UI theming
- Updated project URLs to point to official repository (#93)
- Updated author and contact emails (#93)
- Added comments for AbortError handling (#83)

## [0.28] - 2025-08-18

### External

- Added Load and Save buttons
- Added resizable panes with realigning button groups
- Added sequence diagram support with participants and messages

### Internal

- Added diagram type detection function with configurable skip blocks
- Fixed issue where sequence diagram was wrongly identified

## [0.27] - 2025-04-08

### External

- Updated PlantUML syntax highlighter
- Added mailto hyperlink in usage tab
- Fixed error where indentation level went negative

### Internal

- Identifier in plantuml.js (#45)
- Updated scorecard workflow trigger
- Updated upload-action to v4

## [0.26] - 2025-02-04

### External

- Added hashed cache busting for static assets

### Internal

- Resolved #31
- Resolved #33

## [0.25] - 2024-12-04

### External

- Initial versioned release
- Interactive PlantUML activity diagram editing
- Real-time diagram preview
- Diagram sharing via URL
- Context menu on right-click
- Double-click to edit text
- Pan and zoom support
- Line highlighting on hover/click

### Internal
