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

from flask import Blueprint, jsonify, request

from .message import add_message, delete_message, edit_message_text, get_message_text
from .note import add_note, delete_note, edit_note, get_note_text
from .participant import (
    add_participant,
    delete_participant,
    edit_participant_name,
    get_participant_name,
    get_participant_positions,
)

sequence_bp = Blueprint("sequence", __name__)


@sequence_bp.route("/addParticipant", methods=["POST"])
def addparticipant():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    direction = data["direction"]
    return jsonify({"plantuml": add_participant(puml, svg, svgelement, direction)})


@sequence_bp.route("/addMessage", methods=["POST"])
def addmessage():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    message = data["message"]
    firstcoordinates = data["firstcoordinates"]
    secondcoordinates = data["secondcoordinates"]
    arrow_type = data.get("arrowtype", "->")
    return jsonify(
        {
            "plantuml": add_message(
                puml, svg, message, firstcoordinates, secondcoordinates, arrow_type
            )
        }
    )


@sequence_bp.route("/getParticipantName", methods=["POST"])
def getparticipantname():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    return jsonify({"name": get_participant_name(puml, svg, svgelement)})


@sequence_bp.route("/editParticipantName", methods=["POST"])
def editparticipantname():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    name = data["name"]
    svgelement = data["svgelement"]
    return jsonify({"plantuml": edit_participant_name(puml, svg, name, svgelement)})


@sequence_bp.route("/deleteParticipant", methods=["POST"])
def deleteparticipant():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    return jsonify({"plantuml": delete_participant(puml, svg, svgelement)})


@sequence_bp.route("/getParticipantPositions", methods=["POST"])
def getparticipantpositions():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    return jsonify({"positions": get_participant_positions(puml, svg)})


@sequence_bp.route("/getMessageText", methods=["POST"])
def getmessagetext():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    return jsonify({"text": get_message_text(puml, svg, svgelement)})


@sequence_bp.route("/editMessageText", methods=["POST"])
def editmessagetext():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    text = data["text"]
    return jsonify({"plantuml": edit_message_text(puml, svg, svgelement, text)})


@sequence_bp.route("/deleteMessage", methods=["POST"])
def deletemessage():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    return jsonify({"plantuml": delete_message(puml, svg, svgelement)})


@sequence_bp.route("/addNote", methods=["POST"])
def addnote():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    participant = data["participant"]
    placement = data["placement"]
    text = data["text"]
    y_position = data["yPosition"]
    second_participant = data.get("secondParticipant")
    return jsonify(
        {
            "plantuml": add_note(
                puml, svg, participant, placement, text, y_position, second_participant
            )
        }
    )


@sequence_bp.route("/getSeqNoteText", methods=["POST"])
def getseqnotetext():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    return jsonify({"text": get_note_text(puml, svg, svgelement)})


@sequence_bp.route("/editSeqNote", methods=["POST"])
def editseqnote():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    text = data["text"]
    return jsonify({"plantuml": edit_note(puml, svg, svgelement, text)})


@sequence_bp.route("/deleteSeqNote", methods=["POST"])
def deleteseqnote():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    svgelement = data["svgelement"]
    return jsonify({"plantuml": delete_note(puml, svg, svgelement)})
