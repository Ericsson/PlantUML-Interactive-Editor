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

    def test_gettitleline(self, client):
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
                "/getTitleLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_result = [1, 4]

            # Assert the result value is as expected
            assert result_value == expected_result

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
