"""Tests for the ribbon UI layout structure."""


def test_global_bar_visible(app_url, page):
    """The global bar element exists and is visible."""
    bar = page.locator(".global-bar")
    bar.wait_for(state="visible", timeout=5000)
    assert bar.is_visible()


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
