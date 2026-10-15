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

"""Tests for diagram title creation, editing, and deletion."""

from flask import json


class TestAppRoutesTitle:
    def test_edittitle_remove_title(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
endtitle
:Activity 1;
@enduml""",
            "title": "",
        }
        with client:
            response = client.post(
                "/editTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addtitle_there_already_is_one(self, client):
        test_data = {
            "plantuml": """@startuml
title
This is a title
endtitle
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/addTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
title
This is a title
endtitle
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addtitle(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/addTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
title
Placeholder Title
endtitle
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_edittitle(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
endtitle
:Activity 1;
@enduml""",
            "title": "Hej",
        }
        with client:
            response = client.post(
                "/editTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
title
Hej
endtitle
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletetitle(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
Hello
endtitle
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/deleteTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_gettitle(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
Hello
endtitle
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/getTextTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """Placeholder Title
Hello"""
            assert response.data.decode("utf-8") == expected_result


class TestTitleResponsesArePlainText:
    """Title routes echo puml text, so they must never be served as HTML."""

    def test_title_routes_return_text_plain(self, client):
        payload = {"plantuml": "@startuml\ntitle\n<b>x</b>\nendtitle\n@enduml"}
        calls = {
            "/addTitle": payload,
            "/getTextTitle": payload,
            "/editTitle": {**payload, "title": "<script>alert(1)</script>"},
            "/deleteTitle": payload,
        }
        for url, data in calls.items():
            response = client.post(
                url, data=json.dumps(data), content_type="application/json"
            )
            assert response.status_code == 200, url
            assert response.mimetype == "text/plain", url
