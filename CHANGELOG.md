# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
