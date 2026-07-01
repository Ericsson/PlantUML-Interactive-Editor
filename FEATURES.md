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
  - Delete message (right-click message → Delete Message)
  - Self-messages supported (same participant as sender and receiver)
  - Messages inserted at correct vertical position between existing messages
- Notes
  - Add note from lifeline context menu (over, left of, right of, spanning)
  - Edit note text (right-click note → Edit Note)
  - Delete note (right-click note → Delete Note)
  - Notes inserted at correct vertical position based on click Y-coordinate
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
