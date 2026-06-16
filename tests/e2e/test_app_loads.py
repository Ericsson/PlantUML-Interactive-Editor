def test_page_loads(app_url, page):
    """Smoke test: the app loads and has the correct title."""
    assert page.title() == "PlantUML Interactive Editor"


def test_editor_visible(app_url, page):
    """The Ace editor element is present and visible."""
    editor = page.locator("#editor")
    editor.wait_for(state="visible", timeout=5000)
    assert editor.is_visible()
