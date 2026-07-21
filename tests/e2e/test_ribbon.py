"""Tests for the ribbon UI layout structure."""


def test_global_bar_visible(app_url, page):
    """The global bar element exists and is visible."""
    bar = page.locator(".global-bar")
    bar.wait_for(state="visible", timeout=5000)
    assert bar.is_visible()


def test_global_bar_app_name(app_url, page):
    """The app name is displayed in the global bar."""
    name = page.locator(".app-name")
    assert name.is_visible()
    assert name.inner_text() == "PlantUML Interactive Editor"


def test_global_bar_undo_redo(app_url, page):
    """Undo and redo buttons exist in the global bar."""
    assert page.locator("#undo").is_visible()
    assert page.locator("#restore").is_visible()


def test_global_bar_add_title(app_url, page):
    """Add title button exists in the global bar."""
    assert page.locator("#addTitleButton").is_visible()


def test_global_bar_version_badge(app_url, page):
    """Version badge is displayed."""
    badge = page.locator("#version")
    assert badge.is_visible()
    assert badge.inner_text().startswith("v")


def test_left_pane_visible(app_url, page):
    """The left pane (code) exists and is visible."""
    pane = page.locator(".left-pane")
    pane.wait_for(state="visible", timeout=5000)
    assert pane.is_visible()


def test_right_pane_visible(app_url, page):
    """The right pane (diagram) exists and is visible."""
    pane = page.locator(".right-pane")
    pane.wait_for(state="visible", timeout=5000)
    assert pane.is_visible()


def test_divider_visible(app_url, page):
    """The resizable divider exists and is visible."""
    divider = page.locator(".divider")
    divider.wait_for(state="visible", timeout=5000)
    assert divider.is_visible()


def test_divider_toggle_visible(app_url, page):
    """The collapse/expand toggle button exists inside the divider and is visible."""
    toggle = page.locator("#divider-toggle")
    toggle.wait_for(state="visible", timeout=5000)
    assert toggle.is_visible()
    assert page.locator(".divider #divider-toggle").count() == 1


def test_divider_toggle_collapses_and_expands_pane(app_url, page):
    """Clicking the toggle collapses the left pane to a thin strip, and clicking
    again restores its previous width."""
    page.wait_for_timeout(1000)
    initial_width = page.evaluate(
        "() => document.querySelector('.left-pane').offsetWidth"
    )

    page.locator("#divider-toggle").click()
    page.wait_for_timeout(100)
    collapsed_width = page.evaluate(
        "() => document.querySelector('.left-pane').offsetWidth"
    )
    assert collapsed_width < 200
    assert "collapsed" in page.locator(".left-pane").get_attribute("class")

    page.locator("#divider-toggle").click()
    page.wait_for_timeout(100)
    restored_width = page.evaluate(
        "() => document.querySelector('.left-pane').offsetWidth"
    )
    assert abs(restored_width - initial_width) <= 1
    assert "collapsed" not in page.locator(".left-pane").get_attribute("class")


def test_collapsed_pane_hides_editor_content_but_preserves_ace_state(app_url, page):
    """While collapsed, the code toolbar and Ace editor are visually hidden, but
    the Ace instance stays mounted and its content/cursor position survive an
    expand."""
    page.wait_for_timeout(1000)
    page.evaluate(
        "() => { editor.session.setValue('@startuml\\nAlice -> Bob\\n@enduml'); "
        "editor.moveCursorTo(1, 5); }"
    )
    content_before = page.evaluate("() => editor.session.getValue()")
    cursor_before = page.evaluate(
        "() => { const c = editor.getCursorPosition(); return [c.row, c.column]; }"
    )

    page.locator("#divider-toggle").click()
    page.wait_for_timeout(100)
    toolbar_opacity = page.evaluate(
        "() => getComputedStyle(document.querySelector('.code-toolbar')).opacity"
    )
    editor_opacity = page.evaluate(
        "() => getComputedStyle(document.getElementById('editor')).opacity"
    )
    assert toolbar_opacity == "0"
    assert editor_opacity == "0"

    page.locator("#divider-toggle").click()
    page.wait_for_timeout(100)
    toolbar_opacity = page.evaluate(
        "() => getComputedStyle(document.querySelector('.code-toolbar')).opacity"
    )
    editor_opacity = page.evaluate(
        "() => getComputedStyle(document.getElementById('editor')).opacity"
    )
    assert toolbar_opacity == "1"
    assert editor_opacity == "1"

    content_after = page.evaluate("() => editor.session.getValue()")
    cursor_after = page.evaluate(
        "() => { const c = editor.getCursorPosition(); return [c.row, c.column]; }"
    )
    assert content_after == content_before
    assert cursor_after == cursor_before


def test_split_container_visible(app_url, page):
    """The split container wraps both panes."""
    container = page.locator(".split-container")
    container.wait_for(state="visible", timeout=5000)
    assert container.is_visible()


def test_new_dropdown_opens(app_url, page):
    """Clicking New button opens the dropdown menu."""
    page.locator(".global-bar .dropdown-toggle").click()
    menu = page.locator(".global-bar .dropdown-menu")
    menu.wait_for(state="visible", timeout=2000)
    assert menu.is_visible()


def test_new_dropdown_items(app_url, page):
    """Dropdown has the correct items."""
    page.locator(".global-bar .dropdown-toggle").click()
    items = page.locator(".global-bar .dropdown-menu .dropdown-item")
    assert items.count() == 3
    assert items.nth(0).inner_text() == "Empty"
    assert items.nth(1).inner_text() == "Activity Demo"
    assert items.nth(2).inner_text() == "Sequence Demo"


def test_new_dropdown_demo_loads(app_url, page):
    """Clicking Activity Demo loads demo content in editor."""
    page.locator(".global-bar .dropdown-toggle").click()
    page.locator("#demo").click()
    page.wait_for_timeout(500)
    content = page.evaluate("() => editor.session.getValue()")
    assert "Right-click" in content


def test_code_toolbar_copy_button(app_url, page, context):
    """Copy button copies editor content to clipboard."""
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.evaluate("() => editor.session.setValue('test clipboard content')")
    page.locator(".code-toolbar #copybutton").click()
    page.wait_for_timeout(300)
    clip = page.evaluate("() => navigator.clipboard.readText()")
    assert clip == "test clipboard content"


def test_code_toolbar_paste_button(app_url, page, context):
    """Paste button pastes clipboard content into editor."""
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.evaluate("() => navigator.clipboard.writeText('pasted content')")
    page.locator(".code-toolbar #pastebutton").click()
    page.wait_for_timeout(500)
    content = page.evaluate("() => editor.session.getValue()")
    assert content == "pasted content"


def test_code_toolbar_download_button(app_url, page):
    """Download button exists and is visible."""
    btn = page.locator(".code-toolbar #save")
    assert btn.is_visible()
    assert "toolbar-btn" in btn.get_attribute("class")


def test_code_toolbar_import_button_loads_file(app_url, page):
    """Import button is visible left of the Download button and loads a file into the editor."""
    import_btn = page.locator(".code-toolbar #load")
    download_btn = page.locator(".code-toolbar #save")
    assert import_btn.is_visible()

    import_box = import_btn.bounding_box()
    download_box = download_btn.bounding_box()
    assert import_box["x"] < download_box["x"]

    with page.expect_file_chooser() as fc_info:
        import_btn.click()
    file_chooser = fc_info.value
    file_chooser.set_files(
        files=[
            {
                "name": "demo.puml",
                "mimeType": "text/plain",
                "buffer": b"@startuml\nfoo -> bar\n@enduml",
            }
        ]
    )
    page.wait_for_timeout(500)
    content = page.evaluate("() => editor.session.getValue()")
    assert "foo -> bar" in content


def test_diagram_toolbar_png_button_downloads_file(app_url, page):
    """PNG button downloads the diagram as a file instead of opening a new tab."""
    page.wait_for_timeout(1000)
    with page.expect_download() as download_info:
        page.locator("#png").click()
    download = download_info.value
    assert download.suggested_filename == "diagram.png"


def test_zoom_in_increases_scale(app_url, page):
    """Clicking zoom in increases the panzoom scale."""
    page.wait_for_timeout(2000)
    page.locator("#zoom-in").click()
    page.wait_for_timeout(300)
    scale = page.evaluate("() => panzoomInstance.getTransform().scale")
    assert scale > 1.0


def test_zoom_out_decreases_scale(app_url, page):
    """Clicking zoom out decreases the panzoom scale."""
    page.wait_for_timeout(2000)
    page.locator("#zoom-out").click()
    page.wait_for_timeout(300)
    scale = page.evaluate("() => panzoomInstance.getTransform().scale")
    assert scale < 1.0


def test_zoom_fit_resets_scale(app_url, page):
    """Clicking fit resets zoom to 100%."""
    page.wait_for_timeout(2000)
    page.locator("#zoom-in").click()
    page.locator("#zoom-in").click()
    page.wait_for_timeout(300)
    page.locator("#zoom-fit").click()
    page.wait_for_timeout(300)
    scale = page.evaluate("() => panzoomInstance.getTransform().scale")
    assert abs(scale - 1.0) < 0.01


def test_divider_drag_resizes_panes(app_url, page):
    """Dragging the divider changes the left pane width."""
    page.wait_for_timeout(2000)
    divider = page.locator("#pane-divider")
    box = divider.bounding_box()
    initial_width = page.evaluate(
        "() => document.querySelector('.left-pane').offsetWidth"
    )
    # Drag divider 100px to the right
    page.mouse.move(box["x"] + 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(box["x"] + 102, box["y"] + box["height"] / 2)
    page.mouse.up()
    page.wait_for_timeout(100)
    new_width = page.evaluate("() => document.querySelector('.left-pane').offsetWidth")
    assert new_width > initial_width


def test_divider_drag_past_threshold_collapses_pane(app_url, page):
    """Dragging the divider far enough to the left collapses the pane instead of
    stopping at the old 200px minimum."""
    page.wait_for_timeout(2000)
    divider = page.locator("#pane-divider")
    box = divider.bounding_box()
    # Drag divider all the way to the left
    page.mouse.move(box["x"] + 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(0, box["y"] + box["height"] / 2)
    page.mouse.up()
    page.wait_for_timeout(100)
    width = page.evaluate("() => document.querySelector('.left-pane').offsetWidth")
    assert width < 200
    assert "collapsed" in page.locator(".left-pane").get_attribute("class")


def test_divider_drag_out_of_collapsed_expands_pane(app_url, page):
    """Dragging the divider to the right while collapsed expands the pane again."""
    page.wait_for_timeout(2000)
    page.locator("#divider-toggle").click()
    page.wait_for_timeout(100)
    assert "collapsed" in page.locator(".left-pane").get_attribute("class")

    divider = page.locator("#pane-divider")
    box = divider.bounding_box()
    page.mouse.move(box["x"] + 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(box["x"] + 300, box["y"] + box["height"] / 2)
    page.mouse.up()
    page.wait_for_timeout(100)
    width = page.evaluate("() => document.querySelector('.left-pane').offsetWidth")
    assert width > 200
    assert "collapsed" not in page.locator(".left-pane").get_attribute("class")


def test_version_panel_opens(app_url, page):
    """Clicking version badge opens the version history panel."""
    page.wait_for_timeout(2000)
    page.locator("#version").click()
    panel = page.locator("#version-panel")
    panel.wait_for(state="visible", timeout=3000)
    assert panel.is_visible()
    # Should have changelog content
    assert "0.28" in panel.inner_text() or "0.27" in panel.inner_text()


def test_version_panel_closes_on_outside_click(app_url, page):
    """Clicking outside closes the version panel."""
    page.wait_for_timeout(2000)
    page.locator("#version").click()
    page.locator("#version-panel").wait_for(state="visible", timeout=3000)
    page.locator(".app-name").click()
    page.wait_for_timeout(300)
    assert not page.locator("#version-panel").is_visible()


def test_help_button_opens_modal(app_url, page):
    """Help button opens the usage modal."""
    page.wait_for_timeout(2000)
    page.locator(".global-bar [data-tippy-content='Help']").click()
    modal = page.locator("#usageModal")
    modal.wait_for(state="visible", timeout=2000)
    assert modal.is_visible()
