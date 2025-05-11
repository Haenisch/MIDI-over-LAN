# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

# TODO: Send warning and error messages to the GUI client

"""Worker process for sending MIDI over LAN data (MIDI messages, hello packets, etc.)."""

import logging
import multiprocessing
import queue
import re
import time
from socket import (gaierror,
                    gethostbyname,
                    inet_aton,
                    AF_INET,
                    IP_MULTICAST_IF,
                    IP_MULTICAST_LOOP,
                    IPPROTO_IP,
                    IPPROTO_UDP,
                    SOCK_DGRAM,
                    socket)
from typing import List, Tuple

import mido
from mido.ports import BasePort

from midi_over_lan.logging_setup  import init_logger
from midi_over_lan.protocol import (MULTICAST_GROUP_ADDRESS,
                                    MULTICAST_PORT_NUMBER,
                                    MidiMessagePacket,
                                    HelloPacket,
                                    HelloReplyPacket)
from midi_over_lan.worker_messages import Command, CommandMessage, Information, InfoMessage

# pylint: disable=line-too-long
# pylint: disable=no-member
# pylint: disable=logging-fstring-interpolation

logger = None  # must be setup by calling init_logger() in the run() method


def is_list_of_pairs(data) -> bool:
    """Check if the data is a list of 2-tuples."""
    # Check if data is a list
    if not isinstance(data, list):
        return False

    # Check if each element is a tuple and if each tuple has two elements
    for item in data:
        if not isinstance(item, tuple) or len(item) != 2:
            return False

    return True


class MidiSender(multiprocessing.Process):
    """Worker process for sending MIDI over LAN data (MIDI messages, hello packets, etc.)."""

    def __init__(self, sender_queue, receiver_queue, result_queue, log_queue):
        """Initialize the MidiSender."""
        super().__init__(args=(log_queue,), daemon=True)
        self.sender_queue = sender_queue
        self.receiver_queue = receiver_queue
        self.result_queue = result_queue
        self.log_queue = log_queue
        self.sock = None  # created in the run() method
        self.network_interface = "127.0.0.1"
        self.enable_multicast_loop = True
        self.restart = True
        self.running = True
        self.paused = False
        self.midi_input_ports: List[Tuple[str, str]]  = []  # List of tuples (input port name, network name)
        self.opened_input_ports: List[Tuple[BasePort, str]] = []   # List of tuples (mido port, network name)
        self.ignore_midi_clock = True
        self.save_cpu_time = True
        self.timestamp_of_last_hello = None  # time when the last hello packet was sent


    def resume_sending_midi_messages(self):
        """Resume sending MIDI messages."""
        self.paused = False
        # Remove all pending MIDI messages
        i = 0
        for port, _ in self.opened_input_ports:
            for _ in port.iter_pending():
                i += 1
        logger.info(f"Skipped {i} pending MIDI messages.")


    def run(self):
        """Process the commands and send the MIDI messages."""

        global logger  # pylint: disable=global-statement
        logger = init_logger(self.log_queue, name="midi_over_lan.sender", level=logging.DEBUG)

        while self.restart:
            self.restart = False  # Flag can be set via the RESTART command
            with socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) as self.sock:
                self.setup_socket()
                self.running = True  # Flag is set via the STOP and RESTART command
                while self.running:
                    try:
                        item = self.sender_queue.get_nowait()  # Check for new commands
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
                                    self.resume_sending_midi_messages()  # Skip all pending MIDI messages
                                case Command.STOP:
                                    logger.debug("Stopping.")
                                    self.running = False
                                case Command.SET_MIDI_INPUT_PORTS:
                                    logger.debug(f"Setting MIDI input ports '{item.data}'.")
                                    self.set_midi_input_ports(item)
                                case Command.SET_NETWORK_INTERFACE:
                                    logger.debug(f"Setting network interface '{item.data}'.")
                                    self.set_network_interface(item)
                                case Command.SET_ENABLE_LOOPBACK_INTERFACE:
                                    self.set_enable_loopback_interface(item)
                                case Command.SET_IGNORE_MIDI_CLOCK:
                                    self.set_ignore_midi_clock(item)
                                case Command.SET_SAVE_CPU_TIME:
                                    self.set_save_cpu_time(item)
                        elif isinstance(item, InfoMessage):
                            match item.info:
                                case Information.RECEIVED_HELLO_PACKET:
                                    self.send_hello_reply_packet(item)
                        else:
                            logger.warning(f"Invalid command '{item}'.")
                            continue
                    except queue.Empty:
                        pass

                    self.send_hello_packet()

                    if self.paused:
                        time.sleep(0.1)
                        continue

                    self.send_midi_messages()

                    # Save CPU time with the trade-off of a higher latency
                    if self.save_cpu_time:
                        time.sleep(0.001)


    def send_hello_packet(self):
        """Send every 10 seconds a hello packet to the multicast group."""
        now = time.time()
        timestamp = self.timestamp_of_last_hello
        if (timestamp is None) or (now - timestamp >= 10):
            logger.debug("Sending 'Hello' packet.")
            self.timestamp_of_last_hello = now
            # A 'Hello' packet may contain a list of active device names / input
            # ports. Send the entire list of active input ports (network names)
            # to the multicast group. Thus a receiving client can display the
            # available input ports.
            device_names = [network_name for _, network_name in self.opened_input_ports]
            packet = HelloPacket(device_names=device_names)
            message = InfoMessage(Information.HELLO_PACKET_INFO, (packet.id, time.perf_counter()))
            self.receiver_queue.put(message)  # Inform the receiver about the sent hello packet
            try:
                self.sock.sendto(packet.to_bytes(), (MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER))
            except OSError as error:
                logger.error(f"Could not send 'Hello' packet: {error}")


    def send_hello_reply_packet(self, item: InfoMessage):
        """Send a hello reply packet to the multicast group."""
        remote_ip, hello_packet_id, _ = item.data
        logger.debug(f"Sending 'Hello Reply' packet, answering {remote_ip}.")
        packet = HelloReplyPacket(id=hello_packet_id, remote_ip=remote_ip)
        try:
            self.sock.sendto(packet.to_bytes(), (MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER))
        except OSError as error:
            logger.error(f"Could not send 'Hello Reply' packet: {error}")
        except Exception:  # pylint: disable=broad-except
            logger.error("Could not send 'Hello Reply' packet. (UNKNOWN ERROR)")


    def send_midi_messages(self):
        """Poll the MIDI input ports and send the message(s) to the multicast address."""
        for port, network_name in self.opened_input_ports:
            for message in port.iter_pending():
                if self.ignore_midi_clock and message.type == 'clock':
                    continue
                logger.debug(f"Sending MIDI message ({message}).")
                packet = MidiMessagePacket(device_name=network_name, midi_data=bytes(message.bytes()))
                logger.debug(packet)
                try:
                    self.sock.sendto(packet.to_bytes(), (MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER))
                except OSError as error:
                    logger.error(f"Could not send MIDI message: {error}")


    def set_enable_loopback_interface(self, item: CommandMessage):
        """Enable or disable the loopback interface."""
        if item.data:
            logger.debug("Enable loopback interface.")
            self.enable_multicast_loop = True
        else:
            logger.debug("Disable loopback interface.")
            self.enable_multicast_loop = False

        # Restart the loop to apply the new setting
        self.restart = True
        self.running = False


    def set_ignore_midi_clock(self, item: CommandMessage):
        """Ignore or handle MIDI clock messages."""
        if item.data:
            logger.debug("Ignore MIDI clock messages.")
            self.ignore_midi_clock = True
        else:
            logger.debug("Do not ignore MIDI clock messages.")
            self.ignore_midi_clock = False

        # Restart the loop to apply the new setting
        self.restart = True
        self.running = False


    def set_midi_input_ports(self, item: CommandMessage):
        """Set the list of MIDI input ports to be sent."""

        # Check the format of the data
        # From worker_messages.py (SET_MIDI_INPUT_PORTS):
        # data: list of tuples (input port name, network name)

        if not is_list_of_pairs(item.data):
            logger.error(f"Invalid data format '{item.data}'.")
            return

        self.midi_input_ports = item.data

        # Before setting the MIDI input ports, close the currently opened ports
        for port, network_name in self.opened_input_ports:
            port.close()

        # Open the new MIDI input ports
        self.opened_input_ports = []
        for input_port_name, network_name in self.midi_input_ports:
            try:
                port = mido.open_input(input_port_name)
                self.opened_input_ports.append((port, network_name))
            except OSError as error:
                logger.error(f"Could not open MIDI input port '{input_port_name}': {error}")
                # TODO: Send error message to the GUI client


    def set_network_interface(self, item: CommandMessage):
        """Set the network interface for sending multicast packets.
        
        The network interface must be given as an IPv4 address. If the address is
        not valid, the default interface (loopback address) is used.
         
        Note, a call to this method will not setup the socket for sending multicast
        packets. The socket must be setup by calling the setup_socket() method or
        by restarting the loop in the run() method.
        """
        self.network_interface = item.data

        # Check if the network interface is a valid IPv4 address.
        if isinstance(self.network_interface, str) and re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", self.network_interface.strip()):
            pass
        else:
            logger.error(f"Invalid network interface '{self.network_interface}'. Using default interface.")
            self.network_interface = "127.0.0.0"

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
        """Setup the socket for sending multicast packets."""
        if not self.sock:
            return

        # Check if the network interface is a valid IPv4 address.
        if isinstance(self.network_interface, str) and re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", self.network_interface.strip()):
            pass
        else:
            logger.error(f"Invalid network interface '{self.network_interface}'. Using default interface.")
            self.network_interface = "127.0.0.0"

        # If loopback is enabled, a local client can receive the multicast packets
        if self.enable_multicast_loop:
            self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)
        else:
            self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 0)

        # Set the network interface for sending multicast packets
        try:
            self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_IF, inet_aton(self.network_interface))
        except OSError as error:
            logger.error(f"Could not set network interface '{self.network_interface}': {error}")
            self.network_interface = "127.0.0.0"
            return
