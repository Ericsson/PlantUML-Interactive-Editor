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

from flask import Blueprint, jsonify, request

from .participant import (
    add_message,
    add_participant,
    check_if_inside_participant,
    edit_participant_name,
    get_participant_name,
)

sequence_bp = Blueprint("sequence", __name__)


@sequence_bp.route("/addParticipant", methods=["POST"])
def addparticipant():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    cx = data["cx"]
    return add_participant(puml, svg, cx)


@sequence_bp.route("/addMessage", methods=["POST"])
def addmessage():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    message = data["message"]
    firstcoordinates = data["firstcoordinates"]
    secondcoordinates = data["secondcoordinates"]
    return add_message(puml, svg, message, firstcoordinates, secondcoordinates)


@sequence_bp.route("/checkIfInsideParticipant", methods=["POST"])
def checkifinsideparticipant():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    coordinates = data["coordinates"]
    is_inside = check_if_inside_participant(puml, svg, coordinates)
    return jsonify({"isValid": is_inside})


@sequence_bp.route("/getParticipantName", methods=["POST"])
def getparticipantname():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    return get_participant_name(puml, svg, svgelement)


@sequence_bp.route("/editParticipantName", methods=["POST"])
def editparticipantname():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    name = data["name"]
    svgelement = data["svgelement"]
    return edit_participant_name(puml, svg, name, svgelement)
