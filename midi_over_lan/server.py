#!/usr/bin/env python3

# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Simple console server.

This is a simple console server that listens to one or more local MIDI ports and
sends the MIDI data as 'MIDI over LAN' packets. The local MIDI ports are
selected by the user from a list of available MIDI input ports. The packets are
sent to the multicast address '239.0.3.250' on port '56129'. The server can be
terminated by pressing 'Ctrl+C'.

Enter 'python -m midi_over_lan.server -h' to run the script. Add the '-h' option
to see the help message.
"""

VERSION_NUMBER = "1.0"


# pylint: disable=line-too-long

import argparse
import re
import signal
import socket
import sys
import time

from typing import List

try:
    import mido
    mido.set_backend('mido.backends.rtmidi', load=True)
except Exception:  # pylint: disable=broad-except
    print("Please install the required dependencies by running 'pip install python-rtmidi mido[ports-rtmidi]' in your shell.")
    sys.exit(1)

from midi_over_lan import (MULTICAST_GROUP_ADDRESS,
                           MULTICAST_PORT_NUMBER,
                           MidiMessagePacket)


#############################################################################
# Helper classes and functions
#############################################################################

class DelayedKeyboardInterrupt:
    """Context manager to delay KeyboardInterrupt."""
    # https://stackoverflow.com/a/21919644

    def __init__(self):
        self.signal_received = False
        self.old_handler = None

    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        """SIGINT received. Delaying KeyboardInterrupt."""
        self.signal_received = (sig, frame)

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


#############################################################################
# Main functions
#############################################################################

def is_port_open(port_name: str) -> bool:  # pylint: disable=redefined-outer-name
    """Check if a MIDI input port is already open."""
    try:
        with mido.open_input(port_name):  # pylint: disable=no-member
            return False  # if the port can be opened, it is not open
    except IOError:
        # in case of an IOError, the port is probably already open
        return True


def parse_arguments():
    """Parse the command line arguments.
    
    If no arguments are provided, the program will use the default interface for
    network communication. Also, loopback for multicast packets is disabled.
    """
    parser = argparse.ArgumentParser(
        prog='server.py',
        description='Simple MIDI over LAN console server.',
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=50),
        add_help=False,

        epilog='Examples:\n'
               '  $ python -m midi_over_lan.server\n'
               '  $ python -m midi_over_lan.server -i localhost\n'
               '  $ python -m midi_over_lan.server -i 192.168.0.15\n'
               '  $ python -m midi_over_lan.server -l\n')

    parser.add_argument('-h', '--help',
                        action='help',
                        help='Show this help message and exit.')
    parser.add_argument("-v", "--version",
                        action="version",
                        version=f"Simple MIDI over LAN console server\nVersion {VERSION_NUMBER}",
                        help="Show the version number and exit.")
    parser.add_argument("-V", "--verbose",
                        action="count",
                        default=0,
                        help="Print status and debug messages to the console. "
                             "Use multiple times for more verbosity.")
    parser.add_argument('-i', '--interface-ip',
                        type=str,
                        default='',
                        help='IP address of the network interface to be used. If not specified, the default interface is used.')
    parser.add_argument('-l', '--enable-multicast-loop',
                        action='store_true',
                        help='Enable loopback for multicast packets.')
    parser.add_argument('-c', '--ignore-clock',
                        action='store_true',
                        help='Ignore MIDI clock messages.')

    return parser.parse_args()

def select_input_port() -> List[str]:
    """Returns a list of MIDI input port names.

    A list of available MIDI devices is shown to the user from which one or more
    devices are selected. The device names are then returned.
    
    If no input ports are available, an error message is put out and the
    programm is terminated with error code -1.
    """

    available_input_ports = mido.get_input_names()  # pylint: disable=no-member
    number_input_ports = len(available_input_ports)

    if number_input_ports == 0:
        print("No MIDI input devices available.")
        sys.exit(-1)

    print("Available MIDI devices:\n")
    for i, input_port_name in enumerate(available_input_ports):
        print(f"{i}. {input_port_name.split(':')[0]}")
    print()
    while True:
        try:
            input_str = input("Select MIDI devices by entering a list of numbers: ")
            if not input_str or input_str in ('q', 'quit', 'exit'):
                print("Terminated.")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\nTerminated.")
            sys.exit(0)
        numbers = re.findall(r'\d+', input_str)  # extract numbers from user input
        numbers = [int(number) for number in numbers]  # convert to integers
        numbers = list(dict.fromkeys(numbers))  # remove duplicates
        # Remove numbers from the list that are out of range or whose corresponding port is already open.
        for number in list(numbers):
            if number < 0 or number >= number_input_ports:
                print(f"Ignored number {number}.")
                numbers.remove(number)
                continue
            if is_port_open(available_input_ports[number]):
                print(f"Port '{available_input_ports[number]}' is already in use!")
                numbers.remove(number)
                continue
        if not numbers:
            continue
        break
    return [available_input_ports[number] for number in numbers]


def send_midi_messages(input_port_names: str,
                       interface_ip: str = None,
                       enable_multicast_loop: bool = False,
                       ignore_clock: bool = False,
                       verbosity_level: int = 0) -> None:
    """Send MIDI messages from the input ports to the multicast address of the given interface.
    
    Parameters:
      - input_port_names: List of MIDI input port names.
      - interface_ip: IP address of the network interface to be used. If None or
        '', the default interface is used.
      - enable_multicast_loop: Enable loopback for multicast packets.
      - verbosity_level: Verbosity level for debug messages. The higher the
        number, the more verbose the output.
    """

    print("\nStarting MIDI over LAN console server...")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        if enable_multicast_loop:  # If loopback is enabled, a local client can receive the multicast packets
            if verbosity_level > 1:
                print("Loopback for multicast packets is enabled.")
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        else:
            if verbosity_level > 1:
                print("Loopback for multicast packets is disabled.")
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        if interface_ip:
            try:
                interface_ip = socket.gethostbyname(interface_ip)
                print(f"Using network interface with IP address '{interface_ip}'.")
            except socket.gaierror:
                print(f"Could not resolve IP address '{interface_ip}'. Closing the server.")
                sys.exit(-1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(interface_ip))
        else:
            print("Using the default network interface.")

        # Start listening to the MIDI input ports
        # The loop is terminated by pressing 'Ctrl+C'
        print()
        try:
            input_ports = [mido.open_input(port_name) for port_name in input_port_names]
            while True:
                # For each MIDI input port...
                for input_port in input_ports:
                    input_port_name = input_port.name.split(':')[0]
                    # ... poll the port and send the message(s) to the multicast address
                    for message in input_port.iter_pending():
                        if ignore_clock and message.type == 'clock':
                            continue
                        if verbosity_level > 0:
                            print(f"{input_port_name}: {message}")
                        packet = MidiMessagePacket(device_name=input_port_name, midi_data=bytes(message.bytes()))
                        with DelayedKeyboardInterrupt():
                            sock.sendto(packet.to_bytes(), (MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER))
                    # time.sleep(0.001)
        except OSError as os_error:
            print(f"OSError: {os_error}")
            print("Please check the network interface and the multicast address.")
            print("Terminated.")
            sys.exit(-1)
        except KeyboardInterrupt:
            pass

    print("Terminated.")
    sys.exit(0)


if __name__ == "__main__":
    args = parse_arguments()
    port_names = select_input_port()
    send_midi_messages(port_names,
                       interface_ip=args.interface_ip,
                       enable_multicast_loop=args.enable_multicast_loop,
                       ignore_clock=args.ignore_clock,
                       verbosity_level=args.verbose)

