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
    """Download button exists with accent styling."""
    btn = page.locator(".code-toolbar #save")
    assert btn.is_visible()
    assert "toolbar-btn--accent" in btn.get_attribute("class")
