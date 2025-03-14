# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Module for handling incoming MIDI over LAN data."""

import logging
import multiprocessing
import queue
import re
import struct
import time
from collections import deque
from socket import (gaierror,
                    gethostbyname,
                    gethostname,
                    inet_aton,
                    AF_INET,
                    INADDR_ANY,
                    IPPROTO_IP,
                    IP_ADD_MEMBERSHIP,
                    IPPROTO_UDP,
                    SOCK_DGRAM,
                    SOL_SOCKET,
                    SO_REUSEADDR,
                    socket)
from typing import List, Tuple

import mido

from midi_over_lan.midi_over_lan import (MULTICAST_GROUP_ADDRESS,
                                         MULTICAST_PORT_NUMBER,
                                         Packet, MidiMessagePacket,
                                         HelloPacket,
                                         HelloReplyPacket)
from midi_over_lan.worker_messages import Command, CommandMessage, Information, InfoMessage

# pylint: disable=line-too-long
# pylint: disable=no-member
# pylint: disable=logging-fstring-interpolation


logger = logging.getLogger("midi_over_lan")
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)


def is_output_port_in_use(port_name: str) -> bool:
    """Check if a MIDI output port is already open."""
    try:
        with mido.open_output(port_name):  # pylint: disable=no-member
            return False  # if the port can be opened, it is not open
    except IOError:
        # in case of an IOError, the port is probably already open
        return True


class MidiReceiver(multiprocessing.Process):
    """Worker process for handling incoming MIDI over LAN data."""


    def __init__(self, sender_queue, receiver_queue, result_queue):
        """Initialize the MidiReceiver."""
        super().__init__()
        self.sock = None  # create the socket in the run() method
        self.interface_ip = None
        self.network_interface = None
        self.sender_queue = sender_queue
        self.receiver_queue = receiver_queue
        self.result_queue = result_queue
        self.restart = True
        self.running = True
        self.paused = False
        self.save_cpu_time = True
        self.midi_devices: List[Tuple[str, str]] = []  # List of tuples (device_name, source ip address)
        self.midi_output_ports: List[bool, str] = []  # List of tuples (available, port_name)
        self.received_midi_messages: deque[Tuple[MidiMessagePacket, str]] = deque()  # (packet, source ip address)
        self.received_hello_packets: deque[Tuple[HelloPacket, str]] = deque()  # (packet, source ip address)
        self.received_hello_reply_packets: deque[Tuple[HelloReplyPacket, str]] = deque()  # (packet, address)
        self.sent_hello_packets: dict[id, float] = {}  # entries of the form {packet_id: perf_counter timestamp}
        self.network_interface_of_sender: None|str = None  # None, "", hostname, or an IPv4 address in dot-decimal notation
        self.resolve_network_interface_of_sender()

    def run(self):
        """Run the MidiReceiver."""
        while self.restart:
            self.restart = False  # Flag can be set via the RESTART command
            self.get_midi_output_ports()
            with socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) as self.sock:
                self.setup_socket()
                self.running = True  # Flag is set via the STOP and RESTART command
                while self.running:
                    try:
                        item = self.receiver_queue.get_nowait()  # Check for new commands
                        if isinstance(item, CommandMessage):
                            match item.command:
                                case Command.RESTART:
                                    logger.debug("Restarting.")
                                    self.running = False
                                    self.restart = True
                                    break
                                case Command.PAUSE:
                                    logger.debug("Pausing.")
                                    self.paused = True
                                case Command.RESUME:
                                    logger.debug("Resuming.")
                                    self.resume_sending_midi_messages()
                                case Command.STOP:
                                    logger.debug("Stopping.")
                                    self.running = False
                                case Command.SET_MIDI_OUTPUT_PORTS:
                                    logger.debug(f"Setting MIDI input ports '{item.data}'.")
                                    # self.set_midi_output_ports(item)  # TODO
                                case Command.SET_NETWORK_INTERFACE:
                                    logger.debug(f"Setting network interface '{item.data}'.")
                                    self.set_network_interface(item)
                                    # Restart the process to apply the new network interface
                                    self.running = False
                                    self.restart = True
                                    break
                                case Command.SET_SAVE_CPU_TIME:
                                    logger.debug(f"Save CPU time ({bool(item.data)}).")
                                    self.save_cpu_time = bool(item.data)
                        elif isinstance(item, InfoMessage):
                            match item.info:
                                case Information.HELLO_PACKET_INFO:
                                    logger.debug("Received internal hello packet information.")
                                    self.store_internal_hello_packet_info(item)
                                case Information.NETWORK_INTERFACE_OF_SENDING_WORKER:
                                    logger.debug("Received network interface of sending worker.")
                                    self.network_interface_of_sender = item.data
                                    self.resolve_network_interface_of_sender()
                        else:
                            logger.warning(f"Invalid command '{item}'.")
                            continue
                    except queue.Empty:
                        pass

                    self.check_and_store_incoming_packets()
                    self.process_hello_packets()
                    self.process_hello_reply_packets()

                    if self.paused:
                        time.sleep(0.1)
                        continue

                    self.process_other_packets()

                    # Save CPU time with the trade-off of a higher latency
                    if self.save_cpu_time:
                        time.sleep(0.001)


    def check_and_store_incoming_packets(self):
        """Check for incoming packets and store them."""
        try:
            data, (remote_ip, _) = self.sock.recvfrom(4096)  # buffer size of 4096 bytes
        except BlockingIOError:
            return  # no data received
        try:
            packet = Packet.from_bytes(data)
            logger.debug(f"Received packet from {remote_ip} of type {type(packet)}.")
        except ValueError:
            logger.debug(f"Received invalid packet from {remote_ip}.")
            return
        if isinstance(packet, MidiMessagePacket):
            self.received_midi_messages.append((packet, remote_ip))  # pylint: disable=no-value-for-parameter
        elif isinstance(packet, HelloPacket):
            self.received_hello_packets.append((packet, remote_ip))  # pylint: disable=no-value-for-parameter
        elif isinstance(packet, HelloReplyPacket):
            self.received_hello_reply_packets.append((packet, remote_ip))  # pylint: disable=no-value-for-parameter
        else:
            logger.warning(f"Received unknown packet format from {remote_ip} of type {type(packet)}.")


    def get_midi_output_ports(self):
        """Determine MIDI output ports on the host computer."""
        for port in mido.get_output_names():
            available = not is_output_port_in_use(port)
            self.midi_output_ports.append((available, port))
            logger.debug(f"MIDI output port '{port}' is {'available' if available else 'in use'}.")


    def process_hello_packets(self):
        """Process incoming hello packets."""
        while self.received_hello_packets:
            packet, remote_ip = self.received_hello_packets.popleft()
            # Inform the sending process about the received hello packet
            self.sender_queue.put(InfoMessage(Information.RECEIVED_HELLO_PACKET, (remote_ip, packet.id, time.perf_counter())))
            logger.debug("Received hello packet. Informing sender process.")
            # TODO: Inform main process about available network MIDI devices
        # Delete hello packets information that is older than 5 minutes
        self.sent_hello_packets = {packet_id: timestamp for packet_id, timestamp in self.sent_hello_packets.items() if time.perf_counter() - timestamp < 300}


    def process_hello_reply_packets(self):
        """Process incoming hello reply packets."""
        while self.received_hello_reply_packets:
            packet, remote_ip = self.received_hello_reply_packets.popleft()
            if packet.id not in self.sent_hello_packets:
                logger.debug(f"Received hello reply packet from {remote_ip}, but no corresponding hello packet was sent.")
                logger.debug("Ignoring hello reply packet.")
                continue
            if packet.remote_ip != self.network_interface_of_sender:
                logger.debug("Host ip address {self.network_interface_of_sender} and remote ip address {packet.remote_ip} do not match.")
                continue
            send_off_timestamp = self.sent_hello_packets.get(packet.id)
            receive_timestamp = time.perf_counter()
            round_trip_time = receive_timestamp - send_off_timestamp
            logger.debug(f"Received hello reply packet from {remote_ip}: {packet}")
            logger.debug(f"Round trip time: {round_trip_time * 1000:.2f} milliseconds")
            # TODO: Inform the main process about the round trip time
            # self.result_queue.put(InfoMessage(Information.ROUND_TRIP_TIME, (packet.id, round_trip_time)))


    def process_other_packets(self):
        """Process incoming MIDI message packets."""
        while self.received_midi_messages:
            packet, addr = self.received_midi_messages.popleft()
            midi_msg = mido.parse(packet.midi_data)
            logger.debug(f"Received MIDI message from {addr}: {midi_msg}")


    def setup_socket(self):
        """Setup the socket for receiving MIDI data."""
        if not self.sock:
            return

        # Allow multiple sockets to use the same port
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        if not self.interface_ip:
            # Bind to all interfaces
            self.sock.bind(('', MULTICAST_PORT_NUMBER))
            mreq = struct.pack("4sl", inet_aton(MULTICAST_GROUP_ADDRESS), INADDR_ANY)
            self.sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
        else:
            # Is the network interface given as an IPv4 address?
            if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", self.network_interface):
                pass
            else:
                # The network interface must be given as a hostname; try to resolve it
                try:
                    self.interface_ip = gethostbyname(self.interface_ip)
                except gaierror:
                    logger.warning(f"Could not resolve hostname '{self.network_interface}'. Using the default interface.")
                    self.network_interface = None
                    return
                # Bind to the specific interface
                self.sock.bind((interface_ip, MULTICAST_PORT_NUMBER))
                mreq = struct.pack("4s4s", socket.inet_aton(MULTICAST_GROUP_ADDRESS), inet_aton(interface_ip))
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.setblocking(False)


    def store_internal_hello_packet_info(self, message: InfoMessage):
        """Store the information for the sent hello packet provided by the sender process."""
        packet_id = message.data[0]
        timestamp = message.data[1]
        self.sent_hello_packets[packet_id] = timestamp
        logger.debug(f"Hello packet information (id = {packet_id}, timestamp = {timestamp}).")


    def resolve_network_interface_of_sender(self):
        """Update the network interface received from the sending worker process.
        
        An IPv4 address is kept as is, a hostname is resolved to an IPv4 address,
        None or an empty string is resolved to the default network interface.
        """
        if not self.network_interface_of_sender:
            self.network_interface_of_sender = gethostbyname(gethostname())
            return
        regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        if not re.match(regex, self.network_interface_of_sender):
            try:
                self.network_interface_of_sender = gethostbyname(self.network_interface_of_sender)
            except gaierror:
                logger.warning(f"Could not resolve hostname '{self.network_interface_of_sender}'. Using the default interface.")
                self.network_interface_of_sender = gethostbyname(gethostname())
            return
