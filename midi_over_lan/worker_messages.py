# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Collection of messages sent between the GUI and the worker processes."""

from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class Command(Enum):
    """Command enumeration.

    Available commands:

        RESTART:
            objective:  Restart the worker process.
                 data:  None

        PAUSE:
            objective:  Pause the worker process.
                 data:  None

        RESUME:
            objective:  Resume the worker process.
                 data:  None

        STOP:
            objective:  Stop the worker process.
                 data:  None

        SET_MIDI_INPUT_PORTS:
            objective:  Set the list of MIDI input ports to be sent.
                 data:  list of tuples (input port name, network name)

        SET_MIDI_OUTPUT_PORTS:
            objective:  Set the list of MIDI output ports to be bound.
                 data:  list of tuples (network name, output port name)

        SET_NETWORK_INTERFACE:
            objective:  Set the network interface to be used in the worker
                        processes.
                 data:  str or None. See below for more information.

        SET_ENABLE_LOOPBACK_INTERFACE:
            objective:  Enable or disable the loopback interface.
                 data:  bool

        SET_IGNORE_MIDI_CLOCK:
            objective:  Ignore MIDI clock messages (if data is set to True).
                 data:  bool

        SET_SAVE_CPU_TIME:
            objective:  If enabled, save CPU time with the trade-off of a higher
                        latency.
                 data:  bool

    Note:
    
        - The set of MIDI input ports is a list of tuples, where each tuple
          contains the actual MIDI input port name as well as its user-defined
          network name. With each call of SET_MIDI_INPUT_PORTS, the internal
          list of MIDI input ports is replaced.

        - The set of MIDI output ports is a list of tuples, where each tuple
          contains the network name (remote MIDI device) and the local MIDI
          output port name to which the input port is bound (i.e., to which the
          MIDI messages should be sent). With each call of
          SET_MIDI_OUTPUT_PORTS, the internal list of MIDI output ports is
          replaced.

        - The network interface must be a valid IPv4 address in dot-decimal
          notation. The receiving worker process may also receive a None value
          for the network interface. In this case, the worker process binds to
          all available network interfaces.
    """
    RESTART = auto()
    PAUSE = auto()
    RESUME = auto()
    STOP = auto()
    SET_MIDI_INPUT_PORTS = auto()
    SET_MIDI_OUTPUT_PORTS = auto()
    SET_NETWORK_INTERFACE = auto()
    SET_ENABLE_LOOPBACK_INTERFACE = auto()
    SET_IGNORE_MIDI_CLOCK = auto()
    SET_SAVE_CPU_TIME = auto()


class Information(Enum):
    """Enumeration for information messages.

    Available commands:

        HELLO_PACKET_INFO:
            objective:  Provide information about the recently sent hello packet.
                        The hello packet has been created by the sending worker
                        process and has been sent to the network.
                 data:  tuple (packet id, timestamp as provided by perf_counter)

        RECEIVED_HELLO_PACKET:
            objective:  Provide information about a just received hello reply
                        packet (received from the network by the receiving
                        worker process). The information is passed to the
                        sending worker process in order to create and send a
                        corresponding hello reply packet.
                 data:  tuple (IP address of remote host, packet id, timestamp
                        as provided by perf_counter)

        REMOTE_MIDI_DEVICES:
            objective:  Provide information about the remote MIDI devices
                        discovered by the receiving worker process.
                 data:  dict[str, set[str]] where the key is the IP address or
                        hostname of the remote host and the values are the
                        network names of the remote MIDI devices.

        ROUND_TRIP_TIMES:
            objective:  Provide information about the round trip times between
                        the local host and the various remote hosts. The round
                        trip time is the time between sending a hello packet and
                        receiving the corresponding hello reply packet.
                 data:  dict[str, deque[float]] where the key is the IP address
                        of the remote host and the value is a deque of round
                        trip times (in seconds) for the last 100 hello packets
                        sent to the remote host.


        ROUTING_INFORMATION:
            objective:  Provide information about which remote MIDI device shall
                        be mapped to which local MIDI output port.
                 data:  dict[str, set[str]] where the key is the network name
                        of the remote MIDI device and the value is a set of
                        local MIDI output port names to which the remote MIDI
                        device is bound.
"""

    HELLO_PACKET_INFO = auto()
    RECEIVED_HELLO_PACKET = auto()
    REMOTE_MIDI_DEVICES = auto()
    ROUND_TRIP_TIMES = auto()
    ROUTING_INFORMATION = auto()


@dataclass
class CommandMessage:
    """Command message.
    
    Attributes:
        command: The command to be executed.
        data: Optional data associated with the command.
    
    Example:
        ```python
        CommandMessage(Command.SET_NETWORK_INTERFACE, data="192.168.0.50")
        ```
    
    See the `Command` enumeration for available commands and their expected
    data types.
    """
    command: Command
    data: Any = None


@dataclass
class InfoMessage:
    """Info message.
    
    Attributes:
        info: The information to be conveyed.
        data: Optional data associated with the information.

    Example:
        ```python
        packet_id = 12
        timestamp = time.perf_counter()
        InfoMessage(Information.HELLO_PACKET_INFO, data=(packet_id, timestamp))
        ```

    See the `Information` enumeration for available information types and their
    expected data types.
    """
    info: Information
    data: Any = None
