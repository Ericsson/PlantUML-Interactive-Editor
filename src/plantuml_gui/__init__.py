# SPDX-License-Identifier: MIT

# MIT License

# Copyright (c) 2026 Ericsson

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""The PlantUML Interactive Editor backend.

Deliberately empty of code: importing this package must stay free, because
``plantuml_gui.install_venv`` is imported by the VS Code extension before any
dependency of this package has been installed.

This file is what makes ``plantuml_gui`` a regular package rather than an
implicit namespace one, and it is load-bearing for that same install:
``zipimport`` finds regular packages inside a zip but not namespace packages, and
the extension runs the installer straight out of the wheel, which is a zip. See
install_venv.py, and test_install_venv.py's TestRunningOutOfTheWheel.
"""
