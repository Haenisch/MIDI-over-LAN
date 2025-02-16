# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Worker process for sending MIDI over LAN data (MIDI messages, hello packets, etc.)."""

import multiprocessing
import queue
import re
import time
from socket import gaierror, gethostbyname, inet_aton, socket, AF_INET, IP_MULTICAST_IF, IP_MULTICAST_LOOP, IPPROTO_IP, IPPROTO_UDP, SOCK_DGRAM
from typing import List, Tuple
from warnings import warn

import mido
from mido.ports import BasePort

from midi_over_lan import MidiMessagePacket, MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER
from worker_messages import Command, CommandMessage

# pylint: disable=line-too-long
# pylint: disable=no-member


def debug_print(message):
    """Print the message if the debug flag is set."""
    if __debug__:
        print(message)


def is_list_of_tuples(data) -> bool:
    """Check if the data is a list of tuples with two strings."""
    # Check if data is a list
    if not isinstance(data, list):
        return False

    # Check if each element is a tuple and if each tuple has two strings
    for item in data:
        if not isinstance(item, tuple) or len(item) != 2:
            return False
        if not all(isinstance(element, str) for element in item):
            return False

    return True


class MidiSender(multiprocessing.Process):
    """Worker process for sending MIDI over LAN data (MIDI messages, hello packets, etc.)."""

    def __init__(self, command_queue, result_queue):
        """Initialize the MidiSender."""
        super().__init__()
        self.sock = None
        self.network_interface = None
        self.enable_multicast_loop = False
        self.command_queue = command_queue
        self.result_queue = result_queue
        self.running = True
        self.paused = False
        self.midi_input_ports: List[Tuple[str, str]]  = []  # List of tuples (device_name, network_name)
        self.opened_input_ports: List[Tuple[BasePort, str]] = []   # List of tuples (mido port, network_name)
        self.ignore_midi_clock = False


    def run(self):
        """Process the commands and send the MIDI messages."""
        with socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) as self.sock:
            self.setup_socket()

            while self.running:
                try:
                    item = self.command_queue.get_nowait()  # Check for new commands
                    if not isinstance(item, CommandMessage):
                        warn(f"MidiSender: Invalid command '{item}'.")
                        continue
                    match item.command:
                        case Command.PAUSE:
                            debug_print("MidiSender: Pausing...")
                            self.paused = True
                        case Command.RESUME:
                            debug_print("MidiSender: Resuming...")
                            self.paused = False
                        case Command.STOP:
                            debug_print("MidiSender: Stopping...")
                            self.running = False
                        case Command.SET_MIDI_INPUT_PORTS:
                            debug_print(f"MidiSender: Setting MIDI input ports '{item.data}'...")
                            self.set_midi_input_ports(item)
                        case Command.SET_NETWORK_INTERFACE:
                            debug_print(f"MidiSender: Setting network interface '{item.data}'...")
                            self.set_network_interface(item)
                        case Command.SET_ENABLE_LOOPBACK_INTERFACE:
                            debug_print(f"MidiSender: Enable loopback interface ({bool(item.data)})...")
                            self.enable_multicast_loop = bool(item.data)
                        case Command.SET_IGNORE_MIDI_CLOCK:
                            debug_print(f"MidiSender: Ignoring MIDI clock messages ({bool(item.data)})...")
                            self.ignore_midi_clock = bool(item.data)
                except queue.Empty:
                    pass

                if self.paused:
                    time.sleep(0.1)
                    continue

                self.send_midi_messages()


    def send_midi_messages(self):
        """Poll the MIDI input ports and send the message(s) to the multicast address."""
        for port, network_name in self.opened_input_ports:
            for message in port.iter_pending():
                if self.ignore_midi_clock and message.type == 'clock':
                    continue
                debug_print(f"MidiSender: Sending MIDI message ({message})...")
                packet = MidiMessagePacket(device_name=network_name, midi_data=bytes(message.bytes()))
                debug_print(packet)
                self.sock.sendto(packet.to_bytes(), (MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER))


    def set_midi_input_ports(self, item: CommandMessage):
        """Set the list of MIDI input ports to be sent."""

        # Check the format of the data
        if not is_list_of_tuples(item.data):
            warn(f"MidiSender (SET_MIDI_INPUT_PORTS): Invalid data format '{item.data}'.")
            return

        # Before setting the MIDI input ports, close the currently opened ports
        for port, network_name in self.opened_input_ports:
            port.close()
        self.midi_input_ports = item.data

        # Open the new MIDI input ports
        self.opened_input_ports = []
        for device_name, network_name in self.midi_input_ports:
            try:
                port = mido.open_input(device_name)
                self.opened_input_ports.append((port, network_name))
            except OSError as error:
                warn(f"MidiSender: Could not open MIDI input port '{device_name}': {error}")


    def set_network_interface(self, item: CommandMessage):
        """Set the network interface for sending multicast packets.
        
        The network interface can be given as an IPv4 address or a hostname.
        More detailed type checking is done in the setup_socket() function.
        Thus the network_interface attribute is set directly here as long
        as the data is a non-empty string.
        """
        network_interface = item.data
        if isinstance(network_interface, str):
            network_interface = network_interface.strip()
            if not network_interface or network_interface.lower() == "default":
                self.network_interface = None
            else:
                self.network_interface = network_interface
            self.setup_socket()
        else:
            warn(f"MidiSender (SET_NETWORK_INTERFACE): Expected string, got '{item.data}'.")


    def setup_socket(self):
        """Setup the socket for sending multicast packets."""
        if not self.sock:
            return

        # If loopback is enabled, a local client can receive the multicast packets
        if self.enable_multicast_loop:
            self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)
        else:
            self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 0)

        # Set the network interface
        if self.network_interface:
            # Is the network interface given as an IPv4 address?
            if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", self.network_interface):
                pass
            else:
                # The network interface must be given as a hostname; try to resolve it
                try:
                    self.network_interface = gethostbyname(self.network_interface)
                except gaierror:
                    warn(f"Could not resolve hostname '{self.network_interface}'. Using the default interface.")
                    self.network_interface = None
                    return
            self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_IF, inet_aton(self.network_interface))
