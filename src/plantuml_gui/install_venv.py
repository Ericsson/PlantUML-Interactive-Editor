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

"""Create the virtual environment the VS Code extension runs the backend in.

The extension ships this package as a wheel inside its .vsix and installs it
itself, so that installing the extension is the whole install. This module is
that install, and it runs *out of the wheel*: a wheel is a zip and Python
imports straight out of one, so the extension spawns::

    PYTHONPATH=<the bundled wheel> python3 -m plantuml_gui.install_venv \\
        --wheel <the same wheel> --target <the venv to create>

The wheel is named twice on purpose: PYTHONPATH is how this module is found,
``--wheel`` is what gets installed.

Who is responsible for what
---------------------------
The division with plantuml-extension/src/backendInstall.js:

*JavaScript discovers, this module judges.* Enumerating candidate
interpreters -- ``python3``, ``python3.13`` and so on -- is the extension's
job. It spawns each one against this module and reads the exit code.
``EXIT_UNSUITABLE_INTERPRETER`` means "not this one, try the next"; any other
non-zero exit is a real failure and stops the search, reported distinctly
from "no Python found".

That puts the version rule in one place, next to ``requires-python``, checked
*by* the interpreter being judged.

Progress reporting, notifications and the Settings escape hatch belong to the
extension. This module's whole interface is its arguments, its exit code, and
what it writes to stderr, which the extension appends to its output channel the
same way it does the sidecar's.

Syntax floor
------------
This runs on whichever interpreter the user happens to have, which may be older
than the one the rest of this package requires. Python compiles the whole
module before running any of it, so the message explaining that 3.10 is needed
must itself be valid on an older interpreter to ever print. So: no ``match``,
no PEP 604 ``X | Y`` annotations, nothing else newer than 3.8, whatever the
rest of the codebase is free to use. The floor is 3.8 because f-strings are
used.

Run directly with ``python -m plantuml_gui.install_venv --wheel W --target T``.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import typing

# Must match requires-python in pyproject.toml, which pip enforces when the
# wheel is installed below.
MIN_PYTHON = (3, 10)

# Exit codes. Must match the copies in
# plantuml-extension/src/backendInstall.js, which selects on them.
EXIT_OK = 0
EXIT_FAILED = 1
EXIT_UNSUITABLE_INTERPRETER = 2

# Suffix of the directory the venv is built in before it is renamed into place;
# see install(). The pid keeps two of our own processes apart, so that one
# window's half-built venv is never the other's build directory.
TMP_SUFFIX = ".tmp-"


class InstallError(Exception):
    """A step of the install failed, with a message worth showing the user."""


def interpreter_is_supported() -> bool:
    """Whether the interpreter running this module can host the backend."""
    return sys.version_info[:2] >= MIN_PYTHON


def venv_python(venv_dir: str) -> str:
    """The interpreter inside a venv at `venv_dir`.

    ``bin/python``, and so Linux and macOS only. Must agree with managedVenv()
    in plantuml-extension/src/backendInstall.js, which computes the same path
    to decide whether an install is needed and to spawn the backend with.
    """
    return os.path.join(venv_dir, "bin", "python")


def require_ensurepip() -> None:
    """Fail early, and by name, when the venv would come out without pip.

    Debian and Ubuntu ship ``ensurepip`` in a separate ``python3-venv`` package,
    so ``venv.create(with_pip=True)`` fails there on an otherwise perfectly good
    interpreter. Checked in this process so the message can name the package to
    install.
    """
    try:
        import ensurepip  # noqa: F401
    except ImportError:
        raise InstallError(
            f"the interpreter at {sys.executable} cannot create a virtual "
            "environment with pip in it: the ensurepip module is missing. On "
            "Debian and Ubuntu this is the python3-venv package "
            f"(python{sys.version_info[0]}.{sys.version_info[1]}-venv)."
        ) from None


def create_venv(directory: str) -> None:
    """Build an empty venv, with pip, at `directory`."""
    # Imported here so a stdlib missing its venv module reports through
    # InstallError like every other failure.
    try:
        import venv
    except ImportError:
        raise InstallError(
            f"the interpreter at {sys.executable} has no venv module."
        ) from None

    require_ensurepip()

    try:
        venv.create(directory, with_pip=True, clear=True)
    except subprocess.CalledProcessError as error:
        # venv shells out to ensurepip; its own output is the only account of
        # what went wrong.
        detail = error.output or error.stderr or ""
        raise InstallError(
            f"could not create a virtual environment at {directory}: "
            f"{detail.strip() or error}"
        ) from None
    except OSError as error:
        raise InstallError(
            f"could not create a virtual environment at {directory}: {error}"
        ) from None


def pip_install(python: str, wheel: str) -> None:
    """Install `wheel` into the venv `python` belongs to.

    Everything pip says goes to stderr, whether or not it worked: the extension
    captures that into its output channel, where a slow first install can be
    watched.
    """
    process = subprocess.run(
        [
            python,
            "-m",
            "pip",
            "install",
            # No terminal to prompt at.
            "--no-input",
            "--disable-pip-version-check",
            wheel,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if process.stdout:
        print(process.stdout, end="", file=sys.stderr, flush=True)

    if process.returncode != 0:
        raise InstallError(
            f"pip could not install {os.path.basename(wheel)} "
            f"(exit code {process.returncode}); see the output above."
        )


def claim(built: str, target: str) -> bool:
    """Move a finished venv to where the extension looks for it.

    Returns whether this process was the one that put it there.

    The rename is what makes the install atomic, and both reasons matter:

    *A half-built venv is never visible.* The extension decides the backend is
    installed by looking for the interpreter inside `target`. Building
    directly at `target` and only renaming a finished result means an install
    interrupted between ``venv.create`` and pip -- a cancelled window, a
    killed process, a full disk -- never leaves a `target` with that
    interpreter present and importable but without the package. `target`
    either does not exist or is complete.

    *Two windows racing settle through the filesystem.* Each VS Code window is
    its own extension host, so both may find the venv missing and both start
    building. They build in separate pid-suffixed directories and then race to
    rename: the loser finds `target` already a directory, discards its own
    work, and uses the winner's. That is safe precisely because of the
    previous paragraph -- a `target` that exists is a finished venv, whoever
    made it.

    Renaming a venv works for the two ways this one is ever used:
    ``pyvenv.cfg`` records the *base* interpreter's location, not the venv's
    own, and ``sys.prefix`` is derived at run time from the path the
    interpreter was invoked by. A move does break the absolute shebang written
    into ``bin/pip`` and any other console script, so both this module and the
    extension go through the interpreter instead: ``python -m pip`` here,
    ``python -m plantuml_gui.serve`` there. This package installs no console
    scripts of its own.
    """
    try:
        os.rename(built, target)
        return True
    except OSError:
        # Somebody else claimed target first; keep their result and drop ours.
        if os.path.isdir(target):
            shutil.rmtree(built, ignore_errors=True)
            return False
        raise


def install(wheel: str, target: str) -> None:
    """Create the venv at `target` and install `wheel` into it.

    Idempotent: an existing `target` is a finished install by the invariant
    claim() maintains, so it is left alone. Checking here, on top of the
    extension's own check before spawning this, closes the window between
    that check and this call, which belongs to whatever the user's other
    editor windows are doing.
    """
    if os.path.isdir(target):
        print(f"already installed at {target}", file=sys.stderr, flush=True)
        return

    # The extension's global storage directory is promised to it but not
    # created for it, and os.rename below needs the parent to exist.
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)

    built = f"{target}{TMP_SUFFIX}{os.getpid()}"
    shutil.rmtree(built, ignore_errors=True)

    try:
        print(
            f"creating a virtual environment at {target}", file=sys.stderr, flush=True
        )
        create_venv(built)
        pip_install(venv_python(built), wheel)
        if claim(built, target):
            print(f"installed the backend into {target}", file=sys.stderr, flush=True)
        else:
            print(
                f"another window installed {target} first; using that",
                file=sys.stderr,
                flush=True,
            )
    except BaseException:
        # Including KeyboardInterrupt and SystemExit: the build directory's name
        # carries this pid, so nothing else would ever clean it up.
        shutil.rmtree(built, ignore_errors=True)
        raise


def parse_args(
    argv: typing.Optional[typing.Sequence[str]] = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m plantuml_gui.install_venv",
        description="Create the virtual environment the VS Code extension runs the backend in.",
    )
    parser.add_argument(
        "--wheel", required=True, help="the plantuml_gui wheel to install"
    )
    parser.add_argument(
        "--target", required=True, help="the virtual environment to create"
    )
    return parser.parse_args(argv)


def main(argv: typing.Optional[typing.Sequence[str]] = None) -> int:
    # Before the arguments are looked at: an unsuitable interpreter is a
    # failure the caller acts on -- trying the next candidate -- not one that
    # is reported to the user.
    if not interpreter_is_supported():
        running = f"{sys.version_info[0]}.{sys.version_info[1]}"
        wanted = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
        print(
            f"{sys.executable} is Python {running}; the PlantUML backend needs "
            f"{wanted} or newer.",
            file=sys.stderr,
            flush=True,
        )
        return EXIT_UNSUITABLE_INTERPRETER

    args = parse_args(argv)

    try:
        install(args.wheel, args.target)
    except InstallError as error:
        print(f"error: {error}", file=sys.stderr, flush=True)
        return EXIT_FAILED

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
