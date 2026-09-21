# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Renaming a participant in the puml source.

A rename is pure text surgery on the puml: it needs no SVG, only the participant
that was clicked (already resolved by ``participant.py``) and the new displayed
name. Which lines change depends on whether the declaration carries an alias,
because the alias -- not the displayed name -- is what the diagram body refers
to:

* **Aliased** -- only the declaration's displayed name changes. The body already
  refers to the alias, so it is left alone. This is also the only form that can
  carry a displayed name with spaces.
* **No alias, new name without spaces** -- the declaration and every reference
  change, since the displayed name doubles as the reference token.
* **No alias, new name with spaces** -- spaces are illegal in a bare reference
  token, so an alias is generated: the declaration gains ``as <Alias>`` and every
  reference switches to that alias.
"""

import html
import re

from .classes import (
    ARROW_RE,
    Participant,
    parse_participant_declaration,
    participant_declarations,
)
from .util import NOTE_KEYWORDS

# Stand-in token used to ask the rewriter whether a line holds a reference at
# all. A NUL byte cannot appear in a puml source, so it can never collide with a
# real participant name.
_REFERENCE_PROBE = "\x00"

# Characters allowed in a generated alias. An alias is an internal identifier
# that the user never sees -- the displayed name carries the punctuation -- so
# anything else is dropped rather than escaped or transliterated.
_NON_ALIAS_CHARS_RE = re.compile(r"[^0-9A-Za-z]")

# Used when a displayed name contains nothing alias-able at all ("___"). The
# collision suffix then makes it unique, so this never has to be unique itself.
_ALIAS_FALLBACK = "Participant"

# How a participant is spelled where a line expects one: a quoted displayed name
# or a bare token. ``#`` starts a color, ``,`` separates a participant list and
# ``:`` starts note/message text, so none of them can be part of a bare token.
_TARGET = r'(?:"[^"]*"|[^\s#,:]+)'
_TARGET_LIST = rf"{_TARGET}(?:\s*,\s*{_TARGET})*"

# Lines whose subject is a single participant. ``rest`` keeps a trailing color
# (``activate A #red``) out of the way.
_ACTIVATION_RE = re.compile(
    rf"^(?P<head>(?:activate|deactivate|destroy|create)\s+)(?P<targets>{_TARGET})(?P<rest>.*)$"
)

# Note placement: ``note over A``, ``rnote right of B``, ``hnote over A, B``,
# with the optional color that may sit directly after the keyword. Message-
# attached notes (``note left : text``) have no participant and no ``of``, so
# they do not match and are left alone.
_NOTE_PLACEMENT_RE = re.compile(
    rf"^(?P<head>(?:{'|'.join(NOTE_KEYWORDS)})(?:\s+#\S+)?\s+(?:over|left\s+of|right\s+of)\s+)"
    rf"(?P<targets>{_TARGET_LIST})(?P<rest>.*)$",
    re.IGNORECASE,
)

# ``ref over A, B``.
_REF_RE = re.compile(
    rf"^(?P<head>ref\s+over\s+)(?P<targets>{_TARGET_LIST})(?P<rest>.*)$",
    re.IGNORECASE,
)

# PlantUML's inline activation shorthand on a message endpoint (``A -> B++``).
# Stripped before comparing the endpoint, then put back, so the participant is
# still recognized and the shorthand survives.
_ENDPOINT_SHORTHAND_RE = re.compile(r"[+\-*!]+$")


def _pascal_case(name: str) -> str:
    """Join the words of ``name`` capitalized, dropping non-alphanumerics.

    Only the first letter of each word is forced to upper case; the rest is left
    as the user typed it, so "REST Gateway" keeps its acronym as "RESTGateway"
    instead of being flattened to "RestGateway".
    """
    words = (_NON_ALIAS_CHARS_RE.sub("", word) for word in name.split())
    return "".join(word[:1].upper() + word[1:] for word in words if word)


def taken_identifiers(puml: str, exclude_line: int) -> set[str]:
    """Every identifier already claimed by a declaration, ignoring one line.

    Both displayed names and aliases count: PlantUML resolves a reference
    against either, so reusing a displayed name as an alias would silently merge
    two lifelines into one. ``exclude_line`` is the declaration being rewritten,
    whose own identifiers must not block its replacement.
    """
    taken: set[str] = set()
    for line_index, declaration in participant_declarations(puml):
        if line_index == exclude_line:
            continue
        taken.add(declaration.name)
        if declaration.alias is not None:
            taken.add(declaration.alias)
    return taken


def generate_alias(new_name: str, taken: set[str]) -> str:
    """Build an alias for ``new_name`` that no other participant already uses.

    PascalCase with non-alphanumerics removed, because an alias appears as a
    bare token in the diagram body: no spaces, and no leading digit. Collisions
    are resolved with a numeric suffix (``SpaceRoom``, ``SpaceRoom2``, ...).
    """
    candidate = _pascal_case(new_name) or _ALIAS_FALLBACK
    if candidate[0].isdigit():
        candidate = f"P{candidate}"
    if candidate not in taken:
        return candidate
    suffix = 2
    while f"{candidate}{suffix}" in taken:
        suffix += 1
    return f"{candidate}{suffix}"


def _spellings_of(reference_name: str) -> set[str]:
    """Every way the diagram body may spell a reference to ``reference_name``.

    A participant declared without an alias but with a quoted displayed name
    (``participant "Old Name"``) is referred to in quotes, so both forms count.
    """
    return {reference_name, f'"{reference_name}"'}


def _rewritten_target(target: str, spellings: set[str], new_token: str) -> str:
    """Replace one participant slot, keeping the whitespace around it."""
    stripped = target.strip()
    if stripped not in spellings:
        return target
    leading = target[: len(target) - len(target.lstrip())]
    trailing = target[len(target.rstrip()) :]
    return f"{leading}{new_token}{trailing}"


def _rewritten_target_list(targets: str, spellings: set[str], new_token: str) -> str:
    """Replace matching participants in a comma-separated list (``over A, B``)."""
    return ",".join(
        _rewritten_target(target, spellings, new_token) for target in targets.split(",")
    )


def _rewritten_endpoint(endpoint: str, spellings: set[str], new_token: str) -> str:
    """Replace one side of a message arrow, preserving activation shorthand."""
    shorthand = _ENDPOINT_SHORTHAND_RE.search(endpoint.rstrip())
    if shorthand is None:
        return _rewritten_target(endpoint, spellings, new_token)
    suffix = shorthand.group(0)
    without_suffix = endpoint[: endpoint.rindex(suffix)]
    return f"{_rewritten_target(without_suffix, spellings, new_token)}{suffix}"


def _rewritten_message_line(
    line: str, spellings: set[str], new_token: str
) -> str | None:
    """Rewrite a message line's endpoints, or None if the line is not a message.

    Only the part before the first ``:`` is touched, so the message text is
    never rewritten even when it happens to mention the old name. Requiring a
    dash in the matched arrow keeps a name like ``Web-Server`` from being split
    down the middle -- the same guard :func:`is_message_line` uses.
    """
    colon = line.find(":")
    head = line if colon == -1 else line[:colon]
    tail = "" if colon == -1 else line[colon:]

    arrow = ARROW_RE.search(head)
    if arrow is None or "-" not in arrow.group(0):
        return None

    sender = _rewritten_endpoint(head[: arrow.start()], spellings, new_token)
    receiver = _rewritten_endpoint(head[arrow.end() :], spellings, new_token)
    return f"{sender}{arrow.group(0)}{receiver}{tail}"


def _rewritten_line(line: str, spellings: set[str], new_token: str) -> str:
    """Rewrite every participant reference on one line.

    Lines that do not put a participant in a structural position -- free text,
    group labels, ``box`` titles, note bodies, declarations -- are returned
    unchanged, so a rename can never corrupt text that merely mentions the name.
    """
    message = _rewritten_message_line(line, spellings, new_token)
    if message is not None:
        return message

    for pattern in (_ACTIVATION_RE, _NOTE_PLACEMENT_RE, _REF_RE):
        match = pattern.match(line.strip())
        if match is None:
            continue
        indentation = line[: len(line) - len(line.lstrip())]
        targets = _rewritten_target_list(match.group("targets"), spellings, new_token)
        return f"{indentation}{match.group('head')}{targets}{match.group('rest')}"

    return line


def rewrite_participant_references(
    puml: str, old_reference: str, new_token: str
) -> str:
    """Point every reference to ``old_reference`` at ``new_token`` instead.

    Rewrites only the positions where PlantUML expects a participant: message
    endpoints, ``activate``/``deactivate``/``destroy``/``create`` subjects, note
    placement, and ``ref over``. Declarations are not reference sites and are
    left to the caller, which rebuilds them from their parsed parts.
    """
    spellings = _spellings_of(old_reference)
    return "\n".join(
        _rewritten_line(line, spellings, new_token) for line in puml.splitlines()
    )


def _references_participant(line: str, spellings: set[str]) -> bool:
    """Whether ``line`` mentions the participant in a structural position.

    Answered by asking the rewriter whether it would change anything, so the
    definition of "is a reference" lives in exactly one place. The probe token
    cannot occur in a puml source, so a changed line means a real match.
    """
    return _rewritten_line(line, spellings, _REFERENCE_PROBE) != line


def _indentation(line: str) -> str:
    """The leading whitespace of a line, so rewrites keep it (boxes indent)."""
    return line[: len(line) - len(line.lstrip())]


def _declaration_line(
    indentation: str,
    display_name: str,
    alias: str | None,
    rest: str,
    quote_name: bool,
) -> str:
    """Assemble a declaration line from its parts.

    The keyword is always ``participant``: it is the only one the editor parses
    as a declaration, so it is the only one a rename can be looking at.

    ``rest`` carries the modifiers the rename does not understand (``order 10``,
    a color, a stereotype) straight through.
    """
    displayed = f'"{display_name}"' if quote_name else display_name
    alias_part = f" as {alias}" if alias is not None else ""
    return f"{indentation}participant {displayed}{alias_part}{rest}"


def _needs_alias(new_name: str) -> bool:
    """Whether ``new_name`` cannot serve as a bare reference token.

    Whitespace is the motivating case (``Space Room``). ``#``, ``,`` and ``:``
    are included because PlantUML reads them as a color, a list separator and
    the start of note/message text respectively, so a bare token containing one
    would be silently mis-parsed rather than rejected.
    """
    return any(character.isspace() or character in "#,:" for character in new_name)


def rename_participant(puml: str, participant: Participant, new_name: str) -> str:
    """Return ``puml`` with ``participant`` renamed to ``new_name``.

    Pure: no SVG, no request state. ``participant`` has already been resolved
    from the click by :mod:`participant`, and carries the declaration line index
    (or -1 when the participant was only introduced implicitly by a message).

    The displayed name is HTML-escaped because it arrives straight from a
    request and ends up as SVG text. The alias is derived from the raw name
    instead, since it is reduced to alphanumerics anyway.

    Whitespace in the incoming name is collapsed to single spaces: a declaration
    occupies one puml line, so an embedded newline (pasted into the rename field,
    or sent by another client) would split it and break the diagram. A name with
    nothing left after that leaves the diagram untouched, rather than producing
    an empty label.
    """
    new_name = " ".join(new_name.split())
    if not new_name:
        return puml

    lines = puml.splitlines()
    declaration = (
        parse_participant_declaration(lines[participant.index])
        if 0 <= participant.index < len(lines)
        else None
    )
    display_name = html.escape(new_name, quote=True)

    # Case 1: the body refers to the alias, so only the label has to change --
    # and this is the one form that may already hold a name with spaces.
    if declaration is not None and declaration.alias is not None:
        lines[participant.index] = _declaration_line(
            _indentation(lines[participant.index]),
            display_name,
            declaration.alias,
            declaration.rest,
            quote_name=True,
        )
        return "\n".join(lines)

    old_reference = participant.reference_name

    # Case 2: the displayed name doubles as the reference token, so declaration
    # and body move together and no alias is needed.
    if not _needs_alias(new_name):
        if declaration is not None:
            lines[participant.index] = _declaration_line(
                _indentation(lines[participant.index]),
                display_name,
                None,
                declaration.rest,
                quote_name=declaration.quoted,
            )
            puml = "\n".join(lines)
        return rewrite_participant_references(puml, old_reference, display_name)

    # Case 3: the new name cannot be a bare token, so the participant gains an
    # alias for the body to refer to.
    alias = generate_alias(new_name, taken_identifiers(puml, participant.index))
    if declaration is not None:
        lines[participant.index] = _declaration_line(
            _indentation(lines[participant.index]),
            display_name,
            alias,
            declaration.rest,
            quote_name=True,
        )
        puml = "\n".join(lines)
    else:
        inserted = _insert_declaration_for_implicit(
            puml, old_reference, display_name, alias
        )
        if inserted is None:
            return puml  # nothing refers to it, so there is nothing to rename
        puml = inserted

    return rewrite_participant_references(puml, old_reference, alias)


def _insert_declaration_for_implicit(
    puml: str, old_reference: str, display_name: str, alias: str
) -> str | None:
    """Give an implicitly-introduced participant a declaration line.

    A participant that only ever appears in a message has no declaration to
    rewrite, but a displayed name with spaces has nowhere else to live. The
    declaration goes immediately before the line that first refers to the
    participant, which is where PlantUML already places it in the diagram
    order, so the rename does not reshuffle the lifelines.

    Returns None when no line refers to the participant at all.
    """
    lines = puml.splitlines()
    spellings = _spellings_of(old_reference)
    for line_index, line in enumerate(lines):
        if not _references_participant(line, spellings):
            continue
        lines.insert(
            line_index,
            _declaration_line(
                _indentation(line),
                display_name,
                alias,
                "",
                quote_name=True,
            ),
        )
        return "\n".join(lines)
    return None
