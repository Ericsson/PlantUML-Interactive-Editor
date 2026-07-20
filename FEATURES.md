# PlantUML Activity Diagrams

PlantUML Activity Diagram documentation: [Activity Diagram (New Syntax) on plantuml.com](https://plantuml.com/activity-diagram-beta)


# Activity diagram features

## Supported Features
### General Features
- Automatic Indentation
- Syntax Highlighting
- Copy / Paste buttons to replace from or copy to clipboard
- Undo / Redo using buttons or CTRL + X / CTRL + Y
- Syntax and server error popups
- Version History modal showing external changelog



### Creating and editing

- Activities
  - Colored
  - Embedded Link
- If statements
  - Embedded Link
- While statements
- Repeat While Statements
- Fork statements
- Start/Stop/End
- Connectors
- Notes
- Titles
- Detach elements
- Break elements
- Switch Statements
- Bidirectional hover highlighting
  - Hovering an element in the diagram highlights its line(s) in the editor
  - Hovering a line in the editor, or moving the cursor to it, highlights the matching element in the diagram (activities, if/switch/repeat and while statements, notes, partitions, start/stop, connectors, merge markers, arrow labels, forks, title)
  - Shapes are highlighted with a fill color; label texts (partitions, arrow labels) turn bold

## Partially Supported Features

- Groups & Partitions
  - Can be deleted and edited, but cannot be created or moved interactively
- Break is currently only supported for Activities, but could easily be added for more types.
- Arrow labels and switch cases are fully supported as long as they are not identical.
- Split Processing actions are editable and removable but cannot interactively created or deleted.

## Unsupported Features

Unsupported in this context means activity diagram features that cannot be interacted with in the diagram,
but adding them to the PlantUML code should still work.

- Goto and Label Processing
- Swimlanes
- SDL (Specification and Description Language)
- Lines without arrows


# Sequence diagram features

## Supported Features

- Participants
  - Add participant (left or right of existing)
  - Rename participant
  - Delete participant (cascades to messages)
- Messages
  - Add message between participants (hover lifeline → right-click → ghost arrow → click destination)
  - Edit message text (right-click message → Edit Message)
  - Edit message arrow color (Edit Message modal → Color dropdown; a preset palette or None); rendered as an `-[#color]>` arrow
  - Delete message (right-click message → Delete Message)
  - Self-messages supported (same participant as sender and receiver)
  - Messages inserted at correct vertical position between existing messages
- Notes
  - Add note from lifeline context menu, choosing a type (Note, H Note, or R Note) then a placement (over, left of, right of, spanning)
  - Edit note text and/or change its type (right-click note → Edit Note)
  - Both single-line (`note over A : text`) and multi-line block (`note over A` ... `end note`) syntax are supported for editing and deleting
  - Edit note background color (Edit Note modal → Color dropdown; a preset palette or None); works for all three note types
  - Delete note (right-click note → Delete Note)
  - Notes inserted at correct vertical position based on click Y-coordinate
  - Right-click, hover, and editor-to-diagram highlighting work for all three note types (previously note-only)
- Activation bars
  - Activate a participant from the lifeline context menu (hover lifeline → right-click → Activate)
  - Drag down to preview a ghost bar, then left-click and choose Deactivate or Destroy to end it
  - Deactivate ends the bar; Destroy ends the lifeline with an X
  - Nested activations supported (overlapping bars stack)
  - activate/deactivate/destroy lines inserted at the correct vertical position based on click Y-coordinate
  - Delete an activation bar (right-click the bar → Delete activation bar); removes the matched activate + deactivate/destroy pair, leaving nested bars intact
- Group blocks
  - Add group from lifeline context menu (right-click → Add Group → choose type)
  - Supported types: group, alt, opt, loop
  - Two-click gesture to select message range (with live ghost box preview)
  - Ghost box snaps to message positions with padding and can grow/shrink freely
  - Range selection works in both directions (first click can be above or below second click)
  - Label entered via modal dialog after selecting the range
  - Rename a group's title (right-click the keyword tab or its header text → Rename); the keyword (group/alt/opt/loop) itself is unchanged
  - Delete a group (right-click the keyword tab or its header text → Delete Group); unwraps the block, removing only the header and matching `end` line and keeping its contents in place
- Participant boxes
  - Add a box from the participant context menu (right-click a participant → Box)
  - Hover another participant to grow a live ghost box across the range, then click to create it
  - Wraps the selected contiguous participants in a `box ... end box` block (created untitled/uncolored; edit afterwards to add a title or color)
  - Nested boxes supported: when the selected range nests inside or contains an existing box, `!pragma teoz true` is added automatically so PlantUML can render the nesting
  - A range that partially overlaps (crosses) an existing box is rejected with an error, since PlantUML cannot render crossing boxes
  - Edit a box (right-click anywhere inside the box → Edit Box); a modal lets you set a title and pick a background color from a preset palette (or None). Right-clicking a lifeline inside a box shows the normal lifeline actions with Edit Box / Delete Box added; right-clicking inside the box off a lifeline shows just the box options
  - Delete a box (right-click inside the box → Delete Box); unwraps it, removing only the `box` header and matching `end box` line and keeping the participants
- Bidirectional hover highlighting
  - Hovering a message, participant, note, group box, or participant box in the diagram highlights its line(s) in the editor
  - Hovering a line in the editor, or moving the cursor to it, highlights the matching element in the diagram
