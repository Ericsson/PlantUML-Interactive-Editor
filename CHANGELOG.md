# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### External

- Fixed sequence-diagram notes turning black when hovered while creating a group block (during the group ghost-box gesture). The note hover-highlight bails out during any add-mode gesture and so never captured the note's original color, but the matching mouse-out handler still wrote that (empty) color back, which blanked the fill attribute and rendered the note black. Hovering a note during a group (or any other add-mode) gesture now leaves the note's color untouched.
- Fixed editing, reading, and deleting multi-line block-form sequence notes (`note over X` ... `end note`), which previously only worked for the single-line form (`note over X : text`). On diagrams using the block form the Edit Note modal opened empty and Submit did nothing, because the parser looked for the note text after a `": "` on the opening line and found none. Notes are now parsed as line ranges: the opening line carries the type/color and the body lines carry the text, so the modal shows the current text, edits (text, type, and color) save correctly and keep the block form, and deleting a note (directly or by cascade when its participant is removed) removes the whole `note` ... `end note` block instead of orphaning the body. Larger diagrams, which more often use the block form, were the most affected.
- Added a Color dropdown to the sequence-diagram Edit Message and Edit Note modals (the same preset palette as the Edit Box modal, or None for the default color). Editing a message sets its arrow color (rendered as `A -[#color]> B`); editing a note sets its background color for all three note types (`note`/`hnote`/`rnote`). Choosing None removes any existing color. The color row appears only when editing; adding a message or note is unchanged.
- Fixed an existing box/message/note color that is not one of the preset palette options (e.g. a hex value, or a named color typed directly in the code) being silently reset to None when opening its edit modal (and thus cleared on save). The current color is now preserved in the dropdown, so editing round-trips it.
- Fixed sequence-diagram messages being mis-identified once any message had a colored arrow: message-to-line matching searched for the literal `->`, which a colored arrow (`-[#color]>`) does not contain, so a color could land on the wrong message and re-opening the edit modal showed the wrong (or no) color. Colored, dashed, and bidirectional arrows are now recognized.
- Fixed right-clicking a multi-line note in a sequence diagram opening the message context menu instead of the note menu on the second and later lines: PlantUML renders each note line as a separate text element, and the exclusion check only recognized the first line (whose previous element is the note shape). The check now walks back over the earlier lines to the anchoring note shape, so every line is treated as note text (non-interactive, clicks fall through to the note).
- Participant boxes for sequence diagrams: right-click a participant → Box, then hover another participant to grow a live ghost box across the range and click to create it. Boxes wrap the selected contiguous participants in a `box ... end box` block. Nested boxes are supported — when the range nests inside or contains an existing box, `!pragma teoz true` is added automatically so PlantUML renders the nesting; a range that crosses an existing box is rejected with an error. Right-click anywhere inside a box → Edit Box to set a title and pick a background color (preset palette or None), or → Delete Box to unwrap it (removing only the `box`/`end box` lines) and keep the participants. Right-clicking a lifeline inside a box shows the normal lifeline actions with Edit Box / Delete Box appended; right-clicking inside the box off a lifeline shows just the box options. Boxes also participate in bidirectional hover highlighting.
- Fixed rnote (and any note colored to match a participant header) sometimes being misparsed as an extra participant: participant headers and rnote share the same rect style, but headers always have rounded corners and rnote never does
- Added a note type selector (Note/H Note/R Note) to the Edit Note modal: editing an existing note preselects its detected type, and changing the selection before submitting converts the note to the chosen type. The Add Note modal does not show this selector, since the type is already chosen via the earlier type menu.
- Fixed H Note and R Note having no right-click menu, hover highlight, or editor-to-diagram highlighting after being created: the frontend's interaction handlers only ever recognized plain notes (by fill color), so H Note/R Note were effectively inert once placed in the diagram, even though they could already be created via the type menu
- Fixed the note placement menu (over/left/right/spanning) not appearing after picking a note type (Note/H Note/R Note): the click on the type choice was bubbling to Bootstrap's document-level dropdown auto-close handler, which immediately hid the placement menu right after it was shown
- Added note type selection for sequence diagrams: right-click a lifeline → Add Note now first asks for a type (Note, H Note, or R Note) before the existing placement choice (over, left of, right of, spanning); all three types support every placement identically
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

- Fixed the sequence note mouse-out handler in `sequence-operations.js` restoring an uncaptured fill during add-mode gestures. `attachNoteShapeHandlers`' `mouseover` returns early while `isSequenceAddMode()` is true (so `notecolor` stays `""`), but `mouseout` had no matching guard and ran `setAttribute('fill', "")`, blanking the paint attribute (rendered black). Added the same `isSequenceAddMode()` early-return to `mouseout` so the two handlers are symmetric. Added `tests/e2e/test_sequence_note_group_hover.py`, a JS-logic probe that wires a real rnote through `setupNoteHandlers` and asserts hover leaves the fill untouched (and unblanked) in group add mode while still highlighting/restoring in normal mode.

- Added color editing for sequence messages and notes across the stack. Backend: a shared `resolve_color` helper in `sequence/util.py` (None = keep existing, `""`/`"none"` = clear, else set; leading `#` stripped to match the palette option values) used by both `note.edit_note` and `message.edit_message_text`. `note.py` gained `_NOTE_COLOR_RE`/`_split_prefix_color`/`_note_color_from_line` (the color token is the trailing `#token` before `": "`, requiring a leading space so a `#` inside a participant name is not read as a color), and `get_note_text_and_type` now also returns the color. `message.py` gained `_ARROW_RE`/`_arrow_color_from_line`/`_apply_arrow_color`/`_set_arrow_color` (color inserted after the arrow's first dash, PlantUML's canonical placement), and a `_clicked_message_line` resolver shared by `get_message_text`/`get_message_color`/`get_message_label` (the last resolves once for the `/getMessageText` route, mirroring `get_note_text_and_type`). Routes `getMessageText`/`editMessageText`/`getSeqNoteText`/`editSeqNote` carry the `color` field. Frontend: a reusable `setColorSelect` helper and a Color `<select>` (Box palette) added to `seq-note-modalForm` and `participant-modalForm`, shown only in edit mode. The palette's option list is defined once as a `color_select(select_id)` Jinja macro in `sequence_menus.html` and reused by all three edit modals (box/note/message) so the colors live in a single place. `setColorSelect` matches palette options case-insensitively (so `#red` selects the canonical `Red`) and preserves a color that is not in the preset palette by injecting it as a temporary option (removed/replaced on the next open), and the Box edit handler now calls `setColorSelect` instead of its own inline fallback so all three modals share the behavior.
- Fixed `Diagram._assign_message_indexes`' `is_message_line` (`sequence/classes.py`) not recognizing colored message arrows: it detected messages by the literal `->` substring, but a colored arrow renders as `-[#color]>`. It now strips `[#color]` tokens before the check, so message-to-line index mapping stays correct once messages are colored (this was the root cause of colors landing on the wrong message).
- Tidied the participant-box code after review: moved the shared participant geometry (`participant_header_bounds`, `rect_encloses`) into `sequence/classes.py` (public) so `box.py` and `util.py` depend on the shared data module instead of `util.py` reaching into a `box.py` private; extracted `_resolve_box_line` to remove the duplicated "clicked box → header line" resolution across `get_box_label`/`edit_box`/`delete_box`; fixed `_parse_box_header` mistaking a `#` inside the title (e.g. `box "C#"`) for a color token by searching for the color only outside the quoted title; and split the growing `backgroundContextMenu` into `toggleLifelineMenuItems`/`toggleActivationDeleteItem`/`toggleBoxMenuItems` helpers.
- Updated the Help (`?`) toolbar button's Usage modal text to describe both activity and sequence diagram usage instead of only activity diagrams; added a Sequence Diagram Documentation link alongside the existing Activity Diagram one, moved the documentation links above the support contact with a divider between them, and removed the redundant footer Close button (the modal header's `×` already closes it).
- Hardened the real-click sequence note-menu e2e tests (`tests/e2e/test_sequence_note_menu.py`) against a re-render race that failed only on the very first sequence test (cold PlantUML JAR, slow first render). `_right_click_lifeline` now derives the click point from the rendered participant boxes' `getBoundingClientRect()` (true on-screen position, with the panzoom CSS transform baked in) instead of `svg.getScreenCTM()` math over possibly-stale backend positions, mirroring `_right_click_note`. `_right_click_until_menu` now recomputes coordinates each attempt and treats a `None` result (target not present because the svg is mid-re-render) as a retryable miss rather than throwing, and `_open_sequence_demo` waits for `networkidle` (and re-confirms the lifelines) after switching diagrams so the burst of background render/positions requests — including the activity diagram being replaced still finishing its calls — drains before the first interaction.
- Added `sequence/box.py` and `sequence-box.js` implementing participant boxes. `is_box_rect` identifies a box's `<rect>` by the shared participant-header style (`stroke:#181818;stroke-width:0.5;`) minus rounded corners, plus a solid fill, and — crucially — geometric enclosure of at least one participant header, which is what disambiguates it from an rnote (identical style/fill). `add_box` wraps a contiguous participant range and calls `_needs_teoz_or_raise` to classify the range against existing boxes (disjoint → no pragma, one-contains-the-other → insert `!pragma teoz true` once, partial overlap → `ValueError`); `delete_box`/`index_of_clicked_box` mirror the group ordinal-by-document-order approach with a depth-aware `end box` scan. Routes `/addBox` (400 on crossing) and `/deleteSeqBox`, plus a `boxes` table in `get_sequence_positions`. Frontend `sequence-box.js` owns a horizontal ghost rect and the two-step gesture (mirroring `sequence-group.js` but over participant center-x); `setupBoxHandlers` (`sequence-operations.js`) attaches the delete context menu and hover highlighting via `checkIfBoxRect` (the JS mirror of `is_box_rect`). Editing a box is supported via `get_box_label`/`edit_box` (`/getSeqBoxLabel`, `/editSeqBox`) and the `#seq-box-modalForm` modal (title input + a native color `<select>` whose options are tinted via `background-color`); `_parse_box_header`/`_box_header` round-trip the title (HTML-escape) and color (`#`-prefix) so the add flow stays bare while edits can set both. The box rect has no context-menu handler of its own (it covers the lifeline area and would hijack the lifeline right-click); instead `backgroundContextMenu` hit-tests recorded box bounds via `findEnclosingBox` (innermost wins for nested boxes) and shows Edit Box / Delete Box in the lifeline (`#sequence-menu`) menu — alongside the lifeline actions when over a lifeline, or alone when the click is inside a box off a lifeline. The clicked box is tracked in `contextBoxRect`. `setupNoteHandlers` skips box rects (via the JS `checkIfBoxRect`) so a box is never treated as an rnote.
- Refactored the sequence note lookup helpers (`sequence/note.py`) to remove duplicated "resolve clicked note → puml line" logic that had drifted: `get_note_text` was missing the not-found guard `get_note_type` already had, so an unmatched note silently returned the diagram's last line as text instead of empty. Extracted `_resolve_note_line` (single SVG parse + one place for the `-1`/not-found case) and pure `_note_text_from_line`/`_note_type_from_line` extractors; the public `get_note_text`/`get_note_type` signatures are unchanged. Added `get_note_text_and_type` so the `/getSeqNoteText` route resolves the note once instead of parsing the SVG twice per request. Also listed `tests/e2e/test_sequence_note_menu.py` in `structure.md` (it had been added but not documented).
- Fixed `is_participant_rect` (`sequence/classes.py`) and `checkIfParticipant` (`sequence-operations.js`) matching rnote's `<rect>` as a participant header: both only checked the `stroke-width:0.5` style string, which rnote shares, but participant headers are always rendered with `rx`/`ry` (rounded corners) and rnote never is. Without this, `Diagram.from_svg`/`setupParticipantHandlers` could add a phantom participant (using the note's text as its name) or attach the participant right-click/rename menu to an rnote instead of the note menu. Verified the exact PlantUML layout conditions that make the phantom coincidentally collide with a real participant's `cx` and hide the bug in some cases; regression tests use note text short enough to avoid that coincidence. Added `TestParticipantParsingIgnoresRnote` (Python) and a `checkIfParticipant` regression case (JS, real DOM) covering this.
- Added a Note/H Note/R Note radio selector to `seq-note-modalForm` (`sequence_menus.html`), shown only in Edit mode (the Add flow's type is already chosen via the earlier type submenu, so the selector stays hidden - same `display:none`/`block` toggling already used for the second-participant field). `getModalNoteType()`/`setModalNoteType()` (`sequence-operations.js`) read/preselect the checked radio; `submitNote()` reads it as the source of truth for `noteType` in both modes (in Add mode it's preselected but hidden, from the type submenu's `selectedNoteType`; in Edit mode it's preselected and visible, from `/getSeqNoteText`'s `noteType`).
- Rewrote `setupNoteHandlers` (`sequence-operations.js`) to attach right-click/hover/highlight behavior to hnote and rnote shapes, not just plain notes: added `classifyNoteShape`/`isNoteCandidate` JS equivalents of the Python functions from earlier tasks (tag + shape structure + `stroke-width:0.5`, never fill color), replacing the old `#FEFFDD`-fill-and-`<path>`-only loop. This was a real, separate gap from the backend detection work in earlier tasks - the frontend interaction layer had never been updated, so hnote/rnote notes had no right-click menu, hover highlight, or editor-to-diagram highlighting after being created, even though they were already creatable. Also fixed the same `#FEFFDD`-only assumption in the note-text `pointer-events` exclusion (both in `setupNoteHandlers` and `checkIfMessageElement`), which prevented right-clicks near hnote/rnote text from reaching the shape underneath.
- Updated three existing hover-highlight e2e test fixtures (`test_sequence_hover_highlight.py`) that constructed synthetic `<path>` elements with fill `#FEFFDD` but no real `d`/`style` attributes, relying on the old color-only detection; they now use geometrically valid note-shape data (6-point body path, 4-point fold-corner path, `stroke-width:0.5`) so they exercise the same shape-based detection as production code.
- Extended note editing to detect and expose the current note type (`sequence/note.py`: `get_note_type`, `edit_note` gained an optional `note_type` parameter). `/getSeqNoteText` now also returns `noteType` (detected from the clicked note, falling back to `"note"`); `/editSeqNote` accepts an optional `noteType` that rewrites the note's keyword while preserving its placement clause and any `#color` token, or leaves the keyword unchanged if omitted/unrecognized (existing text-only edit behavior).
- Root cause of the placement-menu regression above: `seq-note-type-menu`'s click handler showed `seq-note-placement-menu` but did not call `e.stopPropagation()`, so the click bubbled to `document`, where Bootstrap 4's dropdown module treats any click as "close open dropdown-menus" (it does not distinguish our manually-shown `.dropdown-menu` elements from ones it manages itself) and hid the placement menu immediately after this code showed it. `seq-addNote`'s handler already had `stopPropagation()` for the same reason; the group type-submenu (`seq-group-type-menu`) never needed it because it transitions straight into ghost-drag mode instead of showing a second `.dropdown-menu`, so it was never exposed to this interaction. Added 2 real-mouse-click e2e tests (`TestSequenceNoteTypeMenuRealClicks` in `test_sequence_note_menu.py`) using Playwright's `page.mouse.click`/`page.click` (not `dispatchEvent`) via a real "Sequence Demo" flow, since `dispatchEvent`-based tests do not bubble to `document` the same way and had missed this regression entirely.
- Wired `selectedNoteType` (from the new type submenu) into the note create request (`sequence-operations.js`: `submitNote()` now sends `noteType: selectedNoteType` to `/addNote`), completing the end-to-end flow from Task 5's menu through Task 4's backend parameterization. H Note and R Note are now genuinely creatable through the UI, not just detectable/creatable via direct API calls. 4 new integration e2e tests in `tests/e2e/test_sequence_note_menu.py` drive the full click sequence (type menu → placement menu → text modal → submit) against the live server and assert on the resulting PlantUML text for each type, plus a reset-after-create check.
- Added the "Add Note" type submenu to the sequence context menu (`seq-note-type-menu` in `sequence_menus.html`, wired in `sequence-operations.js`): clicking "Add Note" now replaces the context menu in place with a Note/H Note/R Note choice, which itself replaces in place with the existing placement menu, mirroring the "Add Group" type-submenu pattern. Stores the choice in `selectedNoteType`, reset to "note" by `cancelNoteAddMode()`. Frontend-only so far - `selectedNoteType` is not yet sent to the backend, so all notes created through the UI are still plain notes regardless of which type is picked; wiring it into the create request is the next step.
- Parameterized sequence note creation with `note_type` (`sequence/note.py`: `add_note`, `_build_note_line`, `_normalize_note_type`; `/addNote` route gained an optional `noteType` request field). All four placement forms and the message-attached shortcut now emit `note`/`hnote`/`rnote` uniformly based on the requested type, defaulting to `note` for a missing or unrecognized value (defensive, since the value comes from the client). Backend-only - the frontend does not yet send `noteType`, so all existing UI flows are unaffected and continue to create plain notes.
- Replaced fill-color-based note detection with shape-based detection in the backend (`sequence/util.py`: `iter_note_shapes`, `_is_note_candidate`; `sequence/note.py`: `index_of_clicked_note`, `_shapes_match`). `extract_note_positions` and `index_of_clicked_note` now identify note/hnote/rnote candidates by tag + shape signature + `stroke-width:0.5`, excluding look-alikes that share a tag or fill with notes (participant header rects via `rx`/`ry`, activation bars and group borders/tabs via `stroke-width`, message arrowheads via point count). This removes the dependency on the literal `#FEFFDD` note fill color in backend detection, ahead of a future note-color-editing feature. The frontend's hover-highlight matching (`sequence-operations.js`) still relies on `#FEFFDD` and is unchanged - only backend Python detection was touched.
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
