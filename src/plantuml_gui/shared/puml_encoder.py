# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2024 Ericsson
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

import base64
import string
import zlib

plantuml_alphabet = (
    string.digits + string.ascii_uppercase + string.ascii_lowercase + "-_"
)
base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
b64_to_plantuml = bytes.maketrans(
    base64_alphabet.encode("utf-8"), plantuml_alphabet.encode("utf-8")
)
plantuml_to_b64 = bytes.maketrans(
    plantuml_alphabet.encode("utf-8"), base64_alphabet.encode("utf-8")
)


def plantuml_encode(plantuml_text):
    """zlib compress the plantuml text and encode it for the plantuml server"""
    zlibbed_str = zlib.compress(plantuml_text.encode("utf-8"))
    compressed_string = zlibbed_str[2:-4]
    return (
        base64.b64encode(compressed_string).translate(b64_to_plantuml).decode("utf-8")
    )


def plantuml_decode(plantuml_url):
    """decode plantuml encoded url back to plantuml text"""
    data = base64.b64decode(plantuml_url.translate(plantuml_to_b64).encode("utf-8"))
    dec = zlib.decompressobj()  # without check the crc.
    header = b"x\x9c"
    return dec.decompress(header + data).decode("utf-8")


url = "SyfFKj2rKt3CoKnELR1Io4ZDoSa700=="

print(plantuml_decode(url))
print(plantuml_encode(plantuml_decode(url)))
