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

from .activity import (
    add_arrow_label,
    add_note_activity,
    break_activity,
    check_backward,
    delete_activity,
    detach_activity,
    edit_activity,
    find_full_bounds,
    find_text_bounds,
    index_of_clicked_activity,
    svgchunktotext,
    svgtochunklist,
)
from .add import add
from .arrow import (
    check_for_duplicate_arrow,
    delete_arrow,
    edit_arrow,
    get_arrow_line,
    get_arrow_type,
    svgtoarrowtext,
)
from .classes import Ellipse, PolyElement, RectElement
from .connector import (
    delete_connector,
    detach_connector,
    edit_connector_char,
    find_index_connector,
    get_connector_char,
    get_index_connector,
    svgtochunklistconnector,
)
from .ellipse import (
    delete_ellipse_element,
    get_index_ellipse,
    svgtochunklistellipse,
)
from .fork import (
    delete_fork2,
    deletefork,
    fork_again,
    fork_toggle,
    fork_toggle2,
    svgtochunklistfork,
)
from .group import delete_group, edit_group, get_group_line, get_group_text
from .if_statements import (
    add_backwards,
    check_if_repeat_has_backward,
    check_what_poly,
    deleteif,
    detach_if,
    edittextinternalif2,
    get_if_line,
    get_line_for_adding_into_if,
    polychunktotext,
    svgtochunklistpolygon,
    switch_again,
)
from .merge import get_index_merge
from .note import (
    delete_note,
    edit_note,
    get_note_line,
    get_note_text,
    note_toggle,
)
from .title import (
    add_title,
    delete_title,
    edit_title_text,
    find_title_bounds,
    get_title_text,
)
from .whilepoly import (
    delete_while,
    editwhile,
    find_index_break,
    find_index_loop,
    get_while_line,
    whiletotext,
)

activity_bp = Blueprint("activity", __name__)


@activity_bp.route("/editText", methods=["POST"])
def edittext():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    newname = data["newname"]
    clickedsvg = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedsvg)
    return edit_activity(puml, svg, clickedelement, newname)


@activity_bp.route("/getText", methods=["POST"])
def gettext():
    data = request.get_json()
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)
    svgchunklist = svgtochunklist(svg)

    return svgchunktotext(svgchunklist, clickedelement)


@activity_bp.route("/deleteActivity", methods=["POST"])
def deleteactivity():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)

    return delete_activity(puml, svg, clickedelement)


@activity_bp.route("/addNoteActivity", methods=["POST"])
def addnoteactivity():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)

    return add_note_activity(puml, svg, clickedelement)


@activity_bp.route("/addToActivity", methods=["POST"])
def addtoactivity():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    type = data["type"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)
    start, end = find_full_bounds(puml, svg, clickedelement)
    return add(puml, end + 1, type)


@activity_bp.route("/detachActivity", methods=["POST"])
def detachactivity():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)
    return detach_activity(puml, svg, clickedelement)


@activity_bp.route("/breakActivity", methods=["POST"])
def breakactivity():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)
    return break_activity(puml, svg, clickedelement)


@activity_bp.route("/checkBackward", methods=["POST"])
def checkbackward():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)
    return check_backward(puml, svg, clickedelement)


@activity_bp.route("/getActivityLine", methods=["POST"])
def getactivityline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)
    count = index_of_clicked_activity(svg, clickedelement)
    lines = puml.splitlines()
    result = find_text_bounds(lines, count)
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/addArrowLabel", methods=["POST"])
def addarrowlabel():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    where = data["where"]
    clickedelement = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedelement)
    return add_arrow_label(puml, svg, where, clickedelement)


@activity_bp.route("/checkWhatPoly", methods=["POST"])
def checkwhatpoly():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]

    svgchunklist = svgtochunklistpolygon(svg)
    clickedelement = PolyElement.from_svg(clickedsvg)
    return check_what_poly(puml, svgchunklist, clickedelement)


@activity_bp.route("/checkIfRepeatHasBackward", methods=["POST"])
def checkifrepeathasbackward():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]

    svgchunklist = svgtochunklistpolygon(svg)
    clickedelement = PolyElement.from_svg(clickedsvg)
    return check_if_repeat_has_backward(puml, svgchunklist, clickedelement)


@activity_bp.route("/addBackwards", methods=["POST"])
def addbackwards():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]

    svgchunklist = svgtochunklistpolygon(svg)
    clickedelement = PolyElement.from_svg(clickedsvg)
    return add_backwards(puml, svgchunklist, clickedelement)


@activity_bp.route("/editTextIf", methods=["POST"])
def edittextif():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    statement = data["statement"]
    branch1 = data["branch1"]
    branch2 = data["branch2"]
    clickedsvg = data["svgelement"]

    svgchunklist = svgtochunklistpolygon(svg)
    clickedelement = PolyElement.from_svg(clickedsvg)
    return edittextinternalif2(
        puml, svgchunklist, statement, branch1, branch2, clickedelement
    )


@activity_bp.route("/getTextPoly", methods=["POST"])
def gettextpoly():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedelement)
    svgchunklist = svgtochunklistpolygon(svg)
    return polychunktotext(puml, svgchunklist, clickedelement)


@activity_bp.route("/delIf", methods=["POST"])
def delif():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedsvg)
    svgchunklist = svgtochunklistpolygon(svg)
    return deleteif(puml, svgchunklist, clickedelement)


@activity_bp.route("/switchAgain", methods=["POST"])
def switchagain():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedsvg)
    svgchunklist = svgtochunklistpolygon(svg)
    return switch_again(puml, svgchunklist, clickedelement)


@activity_bp.route("/getIfLine", methods=["POST"])
def getifline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedelement)
    svgchunklist = svgtochunklistpolygon(svg)
    result = get_if_line(puml, svgchunklist, clickedelement)
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/addToIf", methods=["POST"])
def addtoif():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    where = data["where"]
    type = data["type"]
    clickedelement = PolyElement.from_svg(clickedsvg)
    index = get_line_for_adding_into_if(puml, svg, clickedelement, where)
    return add(puml, index, type)


@activity_bp.route("/detachIf", methods=["POST"])
def detachif():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedsvg)
    svgchunklist = svgtochunklistpolygon(svg)
    return detach_if(puml, svgchunklist, clickedelement)


@activity_bp.route("/addToEllipse", methods=["POST"])
def addtoellipse():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    where = data["where"]
    type = data["type"]
    clickedsvg = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistellipse(svg)
    index = get_index_ellipse(puml, svgchunklist, clickedelement, where)
    return add(puml, index, type)


@activity_bp.route("/deleteEllipse", methods=["POST"])
def deleteellipse():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistellipse(svg)
    return delete_ellipse_element(puml, svgchunklist, clickedelement)


@activity_bp.route("/getEllipseLine", methods=["POST"])
def getellipseline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedelement)
    svgchunklist = svgtochunklistellipse(svg)
    result = get_index_ellipse(puml, svgchunklist, clickedelement, "where")
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/addTitle", methods=["POST"])
def addtitle():
    data = request.get_json()
    puml = data["plantuml"]
    return add_title(puml)


@activity_bp.route("/getTextTitle", methods=["POST"])
def gettexttile():
    data = request.get_json()
    puml = data["plantuml"]
    return get_title_text(puml)


@activity_bp.route("/editTitle", methods=["POST"])
def edittitle():
    data = request.get_json()
    puml = data["plantuml"]
    title = data["title"]
    return edit_title_text(puml, title)


@activity_bp.route("/getTitleLine", methods=["POST"])
def gettitle():
    data = request.get_json()
    puml = data["plantuml"]
    lines = puml.splitlines()
    result = find_title_bounds(lines)
    return jsonify({"result": result})


@activity_bp.route("/deleteTitle", methods=["POST"])
def deletetitle():
    data = request.get_json()
    puml = data["plantuml"]
    return delete_title(puml)


@activity_bp.route("/deleteFork", methods=["POST"])
def delfork():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedsvg)
    svgchunklist = svgtochunklistfork(svg)
    return deletefork(puml, svgchunklist, clickedelement)


@activity_bp.route("/forkAgain", methods=["POST"])
def forkagain():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedsvg)
    svgchunklist = svgtochunklistfork(svg)
    return fork_again(puml, svgchunklist, clickedelement)


@activity_bp.route("/forkToggle", methods=["POST"])
def forktoggle():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = RectElement.from_svg(clickedsvg)
    svgchunklist = svgtochunklistfork(svg)
    return fork_toggle(puml, svgchunklist, clickedelement)


@activity_bp.route("/forkToggle2", methods=["POST"])
def forktoggle2():
    data = request.get_json()
    puml = data["plantuml"]
    index = data["line"]
    return fork_toggle2(puml, index)


@activity_bp.route("/deleteFork2", methods=["POST"])
def deletefork2():
    data = request.get_json()
    puml = data["plantuml"]
    index = data["line"]
    return delete_fork2(puml, index)


@activity_bp.route("/addToFork", methods=["POST"])
def addtofork():
    data = request.get_json()
    puml = data["plantuml"]
    index = data["line"]
    type = data["type"]
    return add(puml, index + 1, type)


@activity_bp.route("/getNoteText", methods=["POST"])
def getnotetext():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    return get_note_text(puml, svg, clickedelement)


@activity_bp.route("/editNote", methods=["POST"])
def editnote():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    text = data["text"]
    clickedelement = data["svgelement"]
    return edit_note(puml, svg, clickedelement, text)


@activity_bp.route("/deleteNote", methods=["POST"])
def deletenote():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    return delete_note(puml, svg, clickedelement)


@activity_bp.route("/noteToggle", methods=["POST"])
def notetoggle():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    return note_toggle(puml, svg, clickedelement)


@activity_bp.route("/getNoteLine", methods=["POST"])
def getnoteline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    result = get_note_line(puml, svg, clickedelement)
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/getGroupText", methods=["POST"])
def getgrouptext():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    return get_group_text(puml, svg, clickedelement)


@activity_bp.route("/getGroupLine", methods=["POST"])
def getgroupline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    result = get_group_line(puml, svg, clickedelement)
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/editGroup", methods=["POST"])
def editgroup():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    text = data["text"]
    return edit_group(puml, svg, clickedelement, text)


@activity_bp.route("/deleteGroup", methods=["POST"])
def deletegroup():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    return delete_group(puml, svg, clickedelement)


@activity_bp.route("/getMergeLine", methods=["POST"])
def getmergeline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    result = get_index_merge(puml, svg, clickedelement)
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/addToMerge", methods=["POST"])
def addtomerge():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    type = data["type"]
    index = get_index_merge(puml, svg, clickedelement)
    print(index)
    return add(puml, index + 1, type)


@activity_bp.route("/getTextWhile", methods=["POST"])
def gettextwhile():
    data = request.get_json()
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedelement)
    svgchunklist = svgtochunklistpolygon(svg)
    return whiletotext(svgchunklist, clickedelement)


@activity_bp.route("/editTextWhile", methods=["POST"])
def edittextwhile():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedelement)
    svgchunklist = svgtochunklistpolygon(svg)
    whilestatement = data["whilestatement"]
    breakstatement = data["break"]
    loop = data["loop"]
    return editwhile(
        puml, svgchunklist, whilestatement, breakstatement, loop, clickedelement
    )


@activity_bp.route("/delWhile", methods=["POST"])
def delwhile():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedelement)
    svgchunklist = svgtochunklistpolygon(svg)
    return delete_while(puml, svgchunklist, clickedelement)


@activity_bp.route("/addToWhile", methods=["POST"])
def addactivitywhile():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedelement)
    type = data["type"]
    where = data["where"]
    svgchunklist = svgtochunklistpolygon(svg)
    if where == "loop":
        index = find_index_loop(puml, svgchunklist, clickedelement)
    else:
        index = find_index_break(puml, svgchunklist, clickedelement)
    return add(puml, index, type)


@activity_bp.route("/getWhileLine", methods=["POST"])
def getwhileline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    clickedelement = PolyElement.from_svg(clickedelement)
    svgchunklist = svgtochunklistpolygon(svg)
    result = get_while_line(puml, svgchunklist, clickedelement)
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/editCharConnector", methods=["POST"])
def editcharconnector():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    text = data["text"]
    clickedsvg = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistconnector(svg)
    return edit_connector_char(puml, svgchunklist, clickedelement, text)


@activity_bp.route("/getCharConnector", methods=["POST"])
def getcharconnector():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistconnector(svg)
    return get_connector_char(puml, svgchunklist, clickedelement)


@activity_bp.route("/connectorDelete", methods=["POST"])
def connectordelete():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistconnector(svg)
    return delete_connector(puml, svgchunklist, clickedelement)


@activity_bp.route("/getConnectorLine", methods=["POST"])
def getconnectorline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistconnector(svg)
    result = find_index_connector(puml, svgchunklist, clickedelement)
    return jsonify({"result": result})  # int is not accepted by flask


@activity_bp.route("/detachConnector", methods=["POST"])
def detachconnector():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistconnector(svg)
    return detach_connector(puml, svgchunklist, clickedelement)


@activity_bp.route("/addToConnector", methods=["POST"])
def addtoconnector():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedsvg = data["svgelement"]
    where = data["where"]
    type = data["type"]
    clickedelement = Ellipse.from_svg(clickedsvg)
    svgchunklist = svgtochunklistconnector(svg)
    start, end = get_index_connector(puml, svgchunklist, clickedelement, where)
    return add(puml, end + 1, type)


@activity_bp.route("/delArrow", methods=["POST"])
def delarrow():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    return delete_arrow(puml, svg, clickedelement)


@activity_bp.route("/checkDuplicateArrow", methods=["POST"])
def checkdupearrow():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    result = check_for_duplicate_arrow(puml, svg, clickedelement)
    arrow_type = get_arrow_type(puml, svg, clickedelement)
    return jsonify({"result": result, "type": arrow_type})


@activity_bp.route("/getArrowText", methods=["POST"])
def getarrowtext():
    data = request.get_json()
    svg = data["svg"]
    clickedelement = data["svgelement"]
    return svgtoarrowtext(svg, clickedelement)


@activity_bp.route("/editArrow", methods=["POST"])
def editarrow():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    text = data["text"]
    clickedelement = data["svgelement"]
    return edit_arrow(puml, svg, text, clickedelement)


@activity_bp.route("/getArrowLine", methods=["POST"])
def getarrowline():
    data = request.get_json()
    puml = data["plantuml"]
    svg = data["svg"]
    clickedelement = data["svgelement"]
    result = get_arrow_line(puml, svg, clickedelement)
    return jsonify({"result": result})  # int is not accepted by flask
