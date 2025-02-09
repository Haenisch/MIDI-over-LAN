#!/usr/bin/env python3

# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Simple console client for MIDI over LAN.

This script listens to MIDI messages and prints them to the console. If desired,
the messages can also be sent to a user-selected MIDI output port.

Enter

  $ python -m midi_over_lan.client

to run the script. Add the '-h' option to see the help message.
"""

# pylint: disable=line-too-long
# pylint: disable=redefined-outer-name

import argparse
import signal
import socket
import struct
import sys

try:
    import mido
    mido.set_backend('mido.backends.rtmidi', load=True)
except Exception:  # pylint: disable=broad-except
    print("Please install the required dependencies by running 'pip install python-rtmidi mido[ports-rtmidi]' in your shell.")
    sys.exit(1)

from midi_over_lan import MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER, MidiMessagePacket, Packet


VERSION_NUMBER = "1.0"


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


def is_output_port_open(port_name: str) -> bool:
    """Check if a MIDI port is already open."""
    try:
        with mido.open_output(port_name):  # pylint: disable=no-member
            return False  # if the port can be opened, it is not open
    except IOError:
        # in case of an IOError, the port is probably already open
        return True


def main_loop(interface_ip: str = '',
              midi_output_port: str = None,
              suppress_console_output: bool = False,
              ignore_clock: bool = False) -> None:
    """Main loop for receiving and sending MIDI messages."""
    printv(1, "Setting up MIDI over LAN client...")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow multiple sockets to use the same port
        if not interface_ip:
            # Bind to all interfaces
            sock.bind(('', MULTICAST_PORT_NUMBER))
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP_ADDRESS), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            # Resolve the IP address of the network interface if given as a hostname
            try:
                interface_ip = socket.gethostbyname(interface_ip)
                printv(1, f"Using network interface with IP address '{interface_ip}'.")
            except socket.gaierror:
                print(f"Could not resolve IP address '{interface_ip}'. Closing the server.")
                sys.exit(-1)
            # Bind to the specific interface
            sock.bind((interface_ip, MULTICAST_PORT_NUMBER))
            mreq = struct.pack("4s4s", socket.inet_aton(MULTICAST_GROUP_ADDRESS), socket.inet_aton(interface_ip))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setblocking(False)

        # Receive/respond loop
        print(f"Listening for MIDI messages on {MULTICAST_GROUP_ADDRESS}:{MULTICAST_PORT_NUMBER}")
        port = mido.open_output(midi_output_port) if midi_output_port else None
        try:
            if port:
                print(f"Sending MIDI messages to {port.name.split(':')[0]}")
            while True:
                with DelayedKeyboardInterrupt():  # prevents KeyboardInterrupt from being raised while receiving data
                    try:
                        data, addr = sock.recvfrom(1024)  # buffer size of 1024 bytes
                    except BlockingIOError:
                        continue  # no data received
                    try:
                        packet = Packet.from_bytes(data)
                    except ValueError:
                        printv(2, f"Received invalid packet from {addr}")
                        continue
                    printv(2, f"Received packet from {addr} of type {type(packet)}")
                    if isinstance(packet, MidiMessagePacket):  # got some MIDI data
                        midi_msg = mido.parse(packet.midi_data)
                        if ignore_clock and midi_msg.type == 'clock':
                            continue
                        if not suppress_console_output:
                            print(f"From {addr}: {packet.device_name}: {midi_msg}")
                        if port:
                            port.send(midi_msg)
        except KeyboardInterrupt:
            print("Program aborted by user.")

        # Clean up
        if port:
            port.close()
        printv(1, "Leaving multicast group.")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)


def parse_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        prog='server.py',
        description='Simple MIDI over LAN console client.',
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=50),
        add_help=False,

        epilog='Examples:\n'
               '  $ python -m midi_over_lan.server\n'
               '  $ python -m midi_over_lan.server -i localhost\n'
               '  $ python -m midi_over_lan.server -i 192.168.0.15\n'
               '  $ python -m midi_over_lan.server -i 192.168.0.15 -o\n')

    parser.add_argument('-h', '--help',
                        action='help',
                        help='Show this help message and exit.')
    parser.add_argument("-v", "--version",
                        action="version",
                        version=f"Simple MIDI over LAN console client\nVersion {VERSION_NUMBER}",
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
    parser.add_argument('-o', '--select-output-port',
                        action='store_true',
                        help='Send MIDI messages to the user-selected output port.')
    parser.add_argument("-s", "--suppress-console-output",
                        action="store_true",
                        help="Suppress console output.")
    parser.add_argument('-c', '--ignore-clock',
                        action='store_true',
                        help='Ignore MIDI clock messages.')

    return parser.parse_args()


def select_output_port() -> str:
    """Returns a MIDI output port name.

    A list of available MIDI devices is shown to the user from which one device
    can be selected. The device name is then returned. If the user just presses
    return without selecting a device, an empty string is returned. Also, if no
    devices are available, an empty string is returned.
    """

    available_output_ports = mido.get_output_names()  # pylint: disable=no-member
    number_output_ports = len(available_output_ports)

    if number_output_ports == 0:
        print("No MIDI output ports available.")
        return ""

    print("\nSelect one of the following MIDI output ports:\n")
    for i, port_name in enumerate(available_output_ports):
        print(f"{i}. {port_name.split(':')[0]}")
    print()
    while True:
        try:
            user_input = input("Enter a number and press return (just return to skip): ")
            if not user_input:
                return ""
            number = int(user_input)
        except:  # pylint: disable=bare-except
            continue
        if number < 0 or number >= number_output_ports:
            print("Number out of range!")
            continue
        break
    return available_output_ports[number]


def printv(level: int, *args, **kwargs):
    """Print a message if the verbosity level is high enough."""
    global verbosity_level  # pylint: disable=global-variable-not-assigned
    if verbosity_level >= level:
        print(*args, **kwargs)

if __name__ == "__main__":
    args = parse_arguments()
    verbosity_level = args.verbose
    print(f"Simple MIDI over LAN console client (v{VERSION_NUMBER})")
    output_port = select_output_port() if args.select_output_port else None
    main_loop(interface_ip=args.interface_ip,
              midi_output_port=output_port,
              suppress_console_output=args.suppress_console_output,
              ignore_clock=args.ignore_clock)
