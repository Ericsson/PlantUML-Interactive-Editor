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

"""Tests for the venv the VS Code extension installs the backend into.

Nothing here builds a real virtual environment: `venv.create` and pip would
make every test a network round trip and several seconds long, and what needs
covering is the surrounding logic -- the version gate, the atomic claim, the
idempotency, the cleanup. The two expensive steps are stubbed, and each stub
records that it was called so a test can tell "did nothing" from "did the work".
"""

import builtins
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
from plantuml_gui import install_venv

# The interpreter floor is declared in two files that cannot import each other.
PYPROJECT = Path(install_venv.__file__).parent.parent.parent / "pyproject.toml"

# The extension mirrors the exit codes, since it selects on them.
BACKEND_INSTALL_JS = (
    Path(install_venv.__file__).parent.parent.parent
    / "plantuml-extension"
    / "src"
    / "backendInstall.js"
)


@pytest.fixture()
def fake_venv(monkeypatch):
    """Replace the two steps that cost time with records of being asked.

    `create_venv` makes the directory it is given, because claim() renames it
    and install() cleans it up -- both need something on disk to act on.
    """
    calls = {"created": [], "installed": []}

    def create_venv(directory):
        calls["created"].append(directory)
        os.makedirs(os.path.join(directory, "bin"))
        Path(directory, "bin", "python").touch()

    def pip_install(python, wheel):
        calls["installed"].append((python, wheel))

    monkeypatch.setattr(install_venv, "create_venv", create_venv)
    monkeypatch.setattr(install_venv, "pip_install", pip_install)

    return calls


class TestTheVersionGate:
    def test_accepts_the_interpreter_running_the_tests(self):
        # The suite runs on a supported interpreter by definition: the package
        # requires 3.10 and pytest imported it.
        assert install_venv.interpreter_is_supported()

    def test_rejects_anything_below_the_floor(self, monkeypatch):
        monkeypatch.setattr(install_venv.sys, "version_info", (3, 9, 0))

        assert not install_venv.interpreter_is_supported()

    def test_accepts_the_floor_itself(self, monkeypatch):
        monkeypatch.setattr(install_venv.sys, "version_info", install_venv.MIN_PYTHON)

        assert install_venv.interpreter_is_supported()

    def test_the_floor_matches_requires_python(self):
        """The gate and the metadata pip enforces have to agree.

        A gate above requires-python would refuse interpreters that work; below
        it, the install would get as far as pip and fail there, blaming the
        wheel for the interpreter's age.
        """
        declared = re.search(
            r'requires-python\s*=\s*"[><=]*(\d+)\.(\d+)"',
            PYPROJECT.read_text(encoding="utf-8"),
        )

        assert declared, "no requires-python found in pyproject.toml"
        assert install_venv.MIN_PYTHON == (
            int(declared.group(1)),
            int(declared.group(2)),
        )

    def test_an_unsuitable_interpreter_is_reported_before_the_arguments(
        self, monkeypatch, capsys
    ):
        """The gate runs first, so a bad interpreter is not masked by bad args."""
        monkeypatch.setattr(install_venv.sys, "version_info", (3, 8, 0))

        assert install_venv.main([]) == install_venv.EXIT_UNSUITABLE_INTERPRETER
        assert "3.10 or newer" in capsys.readouterr().err

    def test_the_exit_codes_match_the_extension(self):
        source = BACKEND_INSTALL_JS.read_text(encoding="utf-8")
        declared = re.search(r"EXIT_UNSUITABLE_INTERPRETER = (\d+);", source)

        assert declared, "backendInstall.js does not declare the exit code"
        assert install_venv.EXIT_UNSUITABLE_INTERPRETER == int(declared.group(1))


class TestWhereTheInterpreterIs:
    def test_is_inside_the_venv(self, tmp_path):
        assert install_venv.venv_python(str(tmp_path)) == str(
            tmp_path / "bin" / "python"
        )

    def test_matches_the_path_the_extension_looks_for(self):
        """managedVenv() in backendInstall.js computes the same path."""
        source = BACKEND_INSTALL_JS.read_text(encoding="utf-8")

        assert "'bin', 'python'" in source


class TestClaimingTheBuiltVenv:
    def test_moves_the_build_into_place(self, tmp_path):
        built = tmp_path / "venv.tmp-1"
        built.mkdir()
        (built / "marker").touch()
        target = tmp_path / "venv"

        assert install_venv.claim(str(built), str(target)) is True
        assert (target / "marker").exists()
        assert not built.exists()

    def test_yields_to_a_venv_that_arrived_first(self, tmp_path):
        """The loser of a two-window race uses the winner's venv."""
        built = tmp_path / "venv.tmp-2"
        built.mkdir()
        (built / "mine").touch()
        target = tmp_path / "venv"
        target.mkdir()
        (target / "theirs").touch()

        assert install_venv.claim(str(built), str(target)) is False
        assert (target / "theirs").exists()
        assert not (target / "mine").exists()

    def test_discards_its_own_build_when_it_loses(self, tmp_path):
        built = tmp_path / "venv.tmp-3"
        built.mkdir()
        target = tmp_path / "venv"
        target.mkdir()
        (target / "keep").touch()

        install_venv.claim(str(built), str(target))

        assert not built.exists()

    def test_a_failure_that_is_not_a_race_is_raised(self, tmp_path):
        """A target whose parent does not exist is a bug, not a lost race."""
        built = tmp_path / "venv.tmp-4"
        built.mkdir()

        with pytest.raises(OSError):
            install_venv.claim(str(built), str(tmp_path / "absent" / "venv"))


class TestInstalling:
    def test_creates_the_venv_and_installs_the_wheel(self, tmp_path, fake_venv):
        target = tmp_path / "storage" / "venv-0.31"

        install_venv.install("/wheels/plantuml_gui-0.31.whl", str(target))

        assert target.is_dir()
        # Into the build directory's interpreter: pip runs before the rename.
        python, wheel = fake_venv["installed"][0]
        assert wheel == "/wheels/plantuml_gui-0.31.whl"
        assert python == install_venv.venv_python(fake_venv["created"][0])

    def test_builds_somewhere_else_and_renames(self, tmp_path, fake_venv):
        """What makes the target's existence mean the install finished."""
        target = tmp_path / "venv-0.31"

        install_venv.install("/wheels/w.whl", str(target))

        built = fake_venv["created"][0]
        assert built != str(target)
        assert built.startswith(f"{target}{install_venv.TMP_SUFFIX}")
        assert not Path(built).exists()

    def test_creates_the_storage_directory(self, tmp_path, fake_venv):
        """VS Code promises the global storage path, not the directory."""
        target = tmp_path / "never" / "made" / "venv-0.31"

        install_venv.install("/wheels/w.whl", str(target))

        assert target.is_dir()

    def test_leaves_an_existing_venv_alone(self, tmp_path, fake_venv):
        target = tmp_path / "venv-0.31"
        target.mkdir()

        install_venv.install("/wheels/w.whl", str(target))

        assert fake_venv["created"] == []
        assert fake_venv["installed"] == []

    def test_says_so_when_there_is_nothing_to_do(self, tmp_path, fake_venv, capsys):
        target = tmp_path / "venv-0.31"
        target.mkdir()

        install_venv.install("/wheels/w.whl", str(target))

        assert "already installed" in capsys.readouterr().err

    def test_removes_the_build_when_pip_fails(self, tmp_path, monkeypatch, fake_venv):
        """A failed install leaves nothing behind for anything to find."""
        target = tmp_path / "venv-0.31"

        def explode(python, wheel):
            raise install_venv.InstallError("pip said no")

        monkeypatch.setattr(install_venv, "pip_install", explode)

        with pytest.raises(install_venv.InstallError):
            install_venv.install("/wheels/w.whl", str(target))

        assert not target.exists()
        assert list(tmp_path.iterdir()) == []

    def test_removes_the_build_when_interrupted(self, tmp_path, monkeypatch, fake_venv):
        target = tmp_path / "venv-0.31"

        def interrupt(python, wheel):
            raise KeyboardInterrupt

        monkeypatch.setattr(install_venv, "pip_install", interrupt)

        with pytest.raises(KeyboardInterrupt):
            install_venv.install("/wheels/w.whl", str(target))

        assert list(tmp_path.iterdir()) == []

    def test_reuses_a_venv_that_appeared_while_building(
        self, tmp_path, monkeypatch, fake_venv, capsys
    ):
        """The other window's install finished between the check and the claim."""
        target = tmp_path / "venv-0.31"

        def pip_install(python, wheel):
            target.mkdir(parents=True)
            (target / "theirs").touch()

        monkeypatch.setattr(install_venv, "pip_install", pip_install)

        install_venv.install("/wheels/w.whl", str(target))

        assert (target / "theirs").exists()
        assert "another window installed" in capsys.readouterr().err


class TestReportingFailures:
    def test_a_failed_install_exits_non_zero(self, tmp_path, monkeypatch, capsys):
        def explode(directory):
            raise install_venv.InstallError("no ensurepip here")

        monkeypatch.setattr(install_venv, "create_venv", explode)

        code = install_venv.main(
            ["--wheel", "/wheels/w.whl", "--target", str(tmp_path / "venv")]
        )

        assert code == install_venv.EXIT_FAILED
        assert "no ensurepip here" in capsys.readouterr().err

    def test_a_successful_install_exits_zero(self, tmp_path, fake_venv):
        code = install_venv.main(
            ["--wheel", "/wheels/w.whl", "--target", str(tmp_path / "venv")]
        )

        assert code == install_venv.EXIT_OK

    def test_both_arguments_are_required(self, tmp_path):
        with pytest.raises(SystemExit):
            install_venv.main(["--target", str(tmp_path / "venv")])

    def test_a_missing_ensurepip_names_the_distro_package(self, monkeypatch):
        """The Debian and Ubuntu case, where venv comes without pip."""
        real_import = builtins.__import__

        def no_ensurepip(name, *args, **kwargs):
            if name == "ensurepip":
                raise ImportError("No module named 'ensurepip'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", no_ensurepip)

        with pytest.raises(install_venv.InstallError) as raised:
            install_venv.require_ensurepip()

        assert "python3-venv" in str(raised.value)

    def test_pip_output_is_surfaced_on_failure(self, monkeypatch, capsys):
        def run(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 1, stdout="ERROR: no such file")

        monkeypatch.setattr(install_venv.subprocess, "run", run)

        with pytest.raises(install_venv.InstallError) as raised:
            install_venv.pip_install("/venv/bin/python", "/wheels/w.whl")

        assert "w.whl" in str(raised.value)
        assert "ERROR: no such file" in capsys.readouterr().err

    def test_pip_output_is_shown_when_it_works_too(self, monkeypatch, capsys):
        def run(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 0, stdout="Successfully installed")

        monkeypatch.setattr(install_venv.subprocess, "run", run)

        install_venv.pip_install("/venv/bin/python", "/wheels/w.whl")

        assert "Successfully installed" in capsys.readouterr().err

    def test_pip_is_run_through_the_venv_interpreter(self, monkeypatch):
        """Never bin/pip, whose shebang the rename would have broken."""
        seen = {}

        def run(argv, **kwargs):
            seen["argv"] = argv
            return subprocess.CompletedProcess(argv, 0, stdout="")

        monkeypatch.setattr(install_venv.subprocess, "run", run)

        install_venv.pip_install("/venv/bin/python", "/wheels/w.whl")

        assert seen["argv"][:4] == ["/venv/bin/python", "-m", "pip", "install"]


class TestRunningOutOfTheWheel:
    def test_imports_from_an_uninstalled_wheel(self, tmp_path):
        """How the extension runs this at all: the wheel is a zip on sys.path.

        The zip is assembled here rather than taken from a build, so the test
        needs no build toolchain and no wheel to exist. A wheel's layout is just
        the package at the root of a zip, which is the part that matters.
        """
        package_dir = Path(install_venv.__file__).parent
        wheel = tmp_path / "plantuml_gui-0.0-py3-none-any.whl"

        with zipfile.ZipFile(wheel, "w") as archive:
            for source in package_dir.rglob("*.py"):
                archive.write(
                    source, Path("plantuml_gui") / source.relative_to(package_dir)
                )

        probe = subprocess.run(
            [
                sys.executable,
                # -S so site initialisation is skipped: an editable install of
                # this package registers an import hook, which would otherwise
                # answer before anything on PYTHONPATH.
                "-S",
                "-c",
                "import plantuml_gui.install_venv as m; print(m.__file__)",
            ],
            capture_output=True,
            text=True,
            # cwd elsewhere, so the checkout is not what answers the import.
            cwd=tmp_path,
            env=dict(os.environ, PYTHONPATH=str(wheel)),
        )

        assert probe.returncode == 0, probe.stderr
        assert str(wheel) in probe.stdout

    def test_is_runnable_as_a_module_from_the_wheel(self, tmp_path):
        package_dir = Path(install_venv.__file__).parent
        wheel = tmp_path / "plantuml_gui-0.0-py3-none-any.whl"

        with zipfile.ZipFile(wheel, "w") as archive:
            for source in package_dir.rglob("*.py"):
                archive.write(
                    source, Path("plantuml_gui") / source.relative_to(package_dir)
                )

        probe = subprocess.run(
            [sys.executable, "-S", "-m", "plantuml_gui.install_venv", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path,
            env=dict(os.environ, PYTHONPATH=str(wheel)),
        )

        assert probe.returncode == 0, probe.stderr
        assert "--wheel" in probe.stdout
        assert "--target" in probe.stdout
