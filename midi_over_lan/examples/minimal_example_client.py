#!/usr/bin/env python3

# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Minimal example of a MIDI over LAN client."""

import socket
import struct
import mido
from midi_over_lan.protocol import Packet, MidiMessagePacket, MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER

INTERFACE_IP = '192.168.0.50' # Change this to the IP address of the network interface to be used.

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((INTERFACE_IP, MULTICAST_PORT_NUMBER))
    mreq = struct.pack("4s4s", socket.inet_aton(MULTICAST_GROUP_ADDRESS), socket.inet_aton(INTERFACE_IP))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setblocking(False)

    while True:
        try:
            data, addr = sock.recvfrom(1024)  # buffer size of 1024 bytes
        except BlockingIOError:
            continue  # no data received
        try:
            # Depending on the received data a MidiMessagePacket object, a
            # HelloPacket object, or a HelloReplyPacket object is created.
            packet = Packet.from_bytes(data)
        except ValueError:
            print(f"Received invalid packet from {addr}")
            continue
        if isinstance(packet, MidiMessagePacket):  # got some MIDI data
            midi_msg = mido.parse(packet.midi_data)
            print(midi_msg)
