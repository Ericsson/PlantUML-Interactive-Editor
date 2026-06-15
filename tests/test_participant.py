# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2025 Ericsson

from plantuml_gui.participant import find_closest_participant
from plantuml_gui.sequence_classes import Participant


def test_find_closest_participant_accepts_float_coordinate():
    participants = [
        Participant(name="Alice", cx=10.0, cy=0.0, index=0),
        Participant(name="Bob", cx=30.0, cy=0.0, index=1),
    ]

    closest = find_closest_participant(participants, 29.5)

    assert closest == participants[1]
