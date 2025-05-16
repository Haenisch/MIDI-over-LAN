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

from midi_over_lan.logging_setup  import init_logger
from midi_over_lan.protocol import (MULTICAST_GROUP_ADDRESS,
                                    MULTICAST_PORT_NUMBER,
                                    Packet,
                                    MidiMessagePacket,
                                    HelloPacket,
                                    HelloReplyPacket,
                                    packet_type_to_string)
from midi_over_lan.worker_messages import Command, CommandMessage, Information, InfoMessage

# pylint: disable=line-too-long
# pylint: disable=no-member
# pylint: disable=logging-fstring-interpolation

logger = None  # must be setup by calling init_logger() in the run() method


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


    def __init__(self, sender_queue, receiver_queue, ui_queue, log_queue):
        """Initialize the MidiReceiver."""
        super().__init__(args=(log_queue,), daemon=True)
        self.sender_queue = sender_queue
        self.receiver_queue = receiver_queue
        self.ui_queue = ui_queue
        self.log_queue = log_queue
        self.sock = None  # create the socket in the run() method
        self.network_interface = None  # default: bind to all interfaces
        self.restart = True
        self.running = True
        self.paused = False
        self.save_cpu_time = True
        self.remote_midi_devices: List[Tuple[str, str]] = []  # List of tuples (device_name, remote ip address)
        self.midi_output_ports: List[bool, str] = []  # List of tuples (available, port_name)
        self.received_midi_messages: deque[Tuple[MidiMessagePacket, str]] = deque()  # (packet, remote ip address)
        self.received_hello_packets: deque[Tuple[HelloPacket, str]] = deque()  # (packet, remote ip address)
        self.received_hello_reply_packets: deque[Tuple[HelloReplyPacket, str]] = deque()  # (packet, remote ip address [sender of the hello reply packet])
        self.sent_hello_packets_timestamps: dict[int, float] = {}  # entries of the form {packet_id: perf_counter timestamp}
        self.round_trip_times: dict[str, deque[float]] = {}  # round trip times for the various ip addresses; limit to 100 entries

    def run(self):
        """Process incoming MIDI over LAN data."""

        global logger  # pylint: disable=global-statement
        logger = init_logger(self.log_queue, name='midi_over_lan.receiver', level=logging.DEBUG)

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
                                    logger.debug("Resuming.   *** NOT YET IMPLEMENTED ***")
                                case Command.STOP:
                                    logger.debug("Stopping.")
                                    self.running = False
                                case Command.SET_MIDI_OUTPUT_PORTS:
                                    logger.debug(f"Setting MIDI input ports '{item.data}'.   *** NOT YET IMPLEMENTED ***")
                                    # self.set_midi_output_ports(item)  # TODO
                                case Command.SET_NETWORK_INTERFACE:
                                    logger.debug(f"Setting network interface '{item.data}'.")
                                    self.set_network_interface(item)
                                case Command.SET_SAVE_CPU_TIME:
                                    self.set_save_cpu_time(item)
                        elif isinstance(item, InfoMessage):
                            match item.info:
                                case Information.HELLO_PACKET_INFO:
                                    logger.debug("Received internal 'Hello Packet' information.")
                                    self.store_internal_hello_packet_info(item)
                        else:
                            logger.warning(f"Invalid command '{item}'.")
                            continue
                    except queue.Empty:
                        pass

                    self.check_and_store_incoming_packets()
                    self.process_hello_packets()
                    self.process_hello_reply_packets()
                    self.process_other_packets()

                    if self.paused:
                        time.sleep(0.1)
                        continue

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
            logger.debug(f"Received packet from {remote_ip} of type '{packet_type_to_string.get(packet.packet_type)}'.")
        except ValueError:
            logger.warning(f"Received invalid packet from {remote_ip}.")
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
            if packet.hostname == 'unknown':
                packet.hostname = remote_ip
            # Inform the sending process about the received hello packet
            self.sender_queue.put(InfoMessage(Information.RECEIVED_HELLO_PACKET, (remote_ip, packet.id, time.perf_counter())))
            logger.debug("Received hello packet. Informing sender process.")
            # TODO: Inform main process about available network MIDI devices

        # Delete hello packets information that is older than 5 minutes
        self.sent_hello_packets_timestamps = {packet_id: timestamp for packet_id, timestamp in self.sent_hello_packets_timestamps.items() if time.perf_counter() - timestamp < 300}


    def process_hello_reply_packets(self):
        """Process incoming 'Hello Reply' packets."""
        while self.received_hello_reply_packets:
            packet, remote_ip = self.received_hello_reply_packets.popleft()  # remote_ip is the sender of the hello reply packet
            origin_ip = packet.remote_ip  # the ip address of the original sender of the hello packet
            if origin_ip != self.network_interface:
                logger.debug(f"Local IP address {self.network_interface} and origin IP address {origin_ip} do not match. Skipping packet.")
                continue
            if packet.hostname == 'unknown':
                packet.hostname = remote_ip
            if packet.id not in self.sent_hello_packets_timestamps:
                logger.warning(f"Received 'Hello Reply' packet from {remote_ip}, but no corresponding 'Hello' packet was sent!?")
                logger.warning("Ignoring 'Hello Reply' packet.")
                continue
            send_off_timestamp = self.sent_hello_packets_timestamps.get(packet.id)
            receive_timestamp = time.perf_counter()
            round_trip_time = receive_timestamp - send_off_timestamp
            logger.info(f"Received 'Hello Reply' packet from {remote_ip}: {packet}")
            logger.info(f"Round trip time: {round_trip_time * 1000:.2f} milliseconds")
            # Store the round trip time for the remote ip address
            if remote_ip not in self.round_trip_times:
                self.round_trip_times[remote_ip] = deque(maxlen=100)
            self.round_trip_times[remote_ip].append(round_trip_time)
            # Inform the main process about the round trip times
            self.ui_queue.put(InfoMessage(Information.ROUND_TRIP_TIMES, self.round_trip_times))


    def process_other_packets(self):
        """Process incoming MIDI message packets."""
        while self.received_midi_messages:
            packet, addr = self.received_midi_messages.popleft()
            midi_msg = mido.parse(packet.midi_data)
            logger.debug(f"Received MIDI message from {addr}: {midi_msg}")


    def set_network_interface(self, item: CommandMessage):
        """Set the network interface for receiving multicast packets.
        
        The network interface must be a valid IPv4 address in dot-decimal
        notation or None. In the latter case, the worker process binds to
        all available network interfaces.

        Note, a call to this method will not setup the socket. It must be either
        setup by calling the setup_socket() method or by restarting the loop in
        the run() method.
        """
        self.network_interface = item.data

        if self.network_interface is None:
            logger.debug("Binding to all network interfaces.")
        else:
            # Check if the network interface is a valid IPv4 address.
            if isinstance(self.network_interface, str) and re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", self.network_interface.strip()):
                pass
            else:
                logger.error(f"Invalid network interface '{self.network_interface}'. Binding to all interfaces.")
                self.network_interface = None

        # Restart the loop to apply the new setting
        self.running = False
        self.restart = True


    def set_save_cpu_time(self, item: CommandMessage):
        """Save CPU time with the trade-off of a higher latency."""
        if item.data:
            logger.debug("Save CPU time.")
            self.save_cpu_time = True
        else:
            logger.debug("Do not save CPU time.")
            self.save_cpu_time = False


    def setup_socket(self):
        """Setup the socket for receiving MIDI data."""
        if not self.sock:
            return

        # Allow multiple sockets to use the same port
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        if not self.network_interface:
            # Bind to all interfaces
            logger.debug("Binding to all network interfaces.")
            self.sock.bind(('', MULTICAST_PORT_NUMBER))
            mreq = struct.pack("4sl", inet_aton(MULTICAST_GROUP_ADDRESS), INADDR_ANY)
            self.sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
        else:
            # Bind to the specific interface
            try:
                logger.debug(f"Binding to network interface '{self.network_interface}'.")
                self.sock.bind((self.network_interface, MULTICAST_PORT_NUMBER))
                mreq = struct.pack("4s4s", inet_aton(MULTICAST_GROUP_ADDRESS), inet_aton(self.network_interface))
                self.sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
            except (gaierror, OSError) as error:
                logger.error(f"Failed to bind to network interface '{self.network_interface}': {error}")
                logger.error("Binding to all interfaces.")
                self.network_interface = None
                self.sock.bind(('', MULTICAST_PORT_NUMBER))
                mreq = struct.pack("4sl", inet_aton(MULTICAST_GROUP_ADDRESS), INADDR_ANY)
                self.sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

        # Set the socket to non-blocking mode
        self.sock.setblocking(False)


    def store_internal_hello_packet_info(self, message: InfoMessage):
        """Store the information for the sent hello packet provided by the sender process."""
        packet_id = message.data[0]
        timestamp = message.data[1]
        self.sent_hello_packets_timestamps[packet_id] = timestamp
        logger.debug(f"Hello packet information (id = {packet_id}, timestamp = {timestamp}).")
