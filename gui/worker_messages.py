# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Collection of messages sent between the GUI and the worker processes."""

from abc import ABC
from dataclasses import dataclass
from enum import Enum


class Command(Enum):
    """Command enumeration.

    Available commands:

        PAUSE
            objective: Pause the worker process.
            data: None

        RESUME:
            objective: Resume the worker process.
            data: None

        STOP:
            objective: Stop the worker process.
            data: None

        SET_MIDI_INPUT_PORTS:
            objective: Set the list of MIDI input ports to be sent.
            data: list of tuples (active, device_name, network_name)

        SET_MIDI_OUTPUT_PORTS:
            objective: Set the list of MIDI output ports to be processed.
            data: list of tuples (network_name, device_name)

        SET_NETWORK_INTERFACE:
            objective: Set the network interface for sending multicast packets.
            data: str (IPv4 address or hostname)

        SET_ENABLE_LOOPBACK_INTERFACE:
            objective: Enable or disable the loopback interface.
            data: bool

        SET_IGNORE_MIDI_CLOCK:
            objective: Ignore or process MIDI clock messages.
            data: bool

        SET_SAVE_CPU_TIME:
            objective: If enabled, save CPU time with the trade-off of a higher latency.
            data: bool
    
    Note:
    
        - The set of MIDI input ports is a list of tuples, where each tuple
            contains the actual device name and its user-defined network name as
            well as a flag indicating whether the port is active. With each call
            of SET_MIDI_INPUT_PORTS, the internal list of MIDI input ports is
            replaced.

        - The set of MIDI output ports is a list of tuples, where each tuple
            contains the network name (MIDI input ports from the network) and
            the local MIDI output port name to which the input port is bind
            (i.e., to which the MIDI messages should be sent). With each call of
            SET_MIDI_OUTPUT_PORTS, the internal list of MIDI output ports is
            replaced.
    """
    PAUSE = 1
    RESUME = 2
    STOP = 3
    SET_MIDI_INPUT_PORTS = 4
    SET_MIDI_OUTPUT_PORTS = 5
    SET_NETWORK_INTERFACE = 6
    SET_ENABLE_LOOPBACK_INTERFACE = 7
    SET_IGNORE_MIDI_CLOCK = 8
    SET_SAVE_CPU_TIME = 9


class WorkerMessage(ABC):
    """Base class for worker messages."""


@dataclass
class CommandMessage(WorkerMessage):
    """Command message."""
    command: Command
    data: any = None


@dataclass
class ResultMessage(WorkerMessage):
    """Result message."""
    result: any
