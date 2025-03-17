#!/usr/bin/env python3

# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Minimal example of a MIDI over LAN server."""

import socket
import time
import mido
from midi_over_lan.protocol import MidiMessagePacket, MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER

INTERFACE_IP = '192.168.0.50' # Change this to the IP address of the network interface to be used.

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(INTERFACE_IP))
    message = mido.Message('note_on', note=60, velocity=64)
    while True:
        packet = MidiMessagePacket()
        packet.device_name='example script'
        packet.midi_data=bytes(message.bytes())
        sock.sendto(packet.to_bytes(), (MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER))
        time.sleep(3)
