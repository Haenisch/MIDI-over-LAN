# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

# Written by Christoph Hänisch.
# Version 1
# Last changed on 2025-05-01.

"""MIDI over LAN library for Python.

The MIDI over LAN protocol allows sending MIDI messages over a local area
network to control MIDI devices remotely. The messages are sent as multicast
packets to all hosts in the network; interested hosts simply listen for these
packets. The protocol has very little overhead and is suitable for real-time
communication. Along with the actual MIDI message, the packets contain the name
of the MIDI device that sent the message which allows the receiving host to
filter or to route accordingly (e.g., it can pass the MIDI message to a
particular local MIDI input port).

The protocol supports a simple discovery mechanism where hosts can announce
their presence in the network by sending a 'Hello' packet. Moreover, other hosts
can respond to this packet with a 'Hello Reply' packet which in turn allows to
determine the round-trip time between the hosts. Also, the hello packets may
contain the names of the MIDI devices connected to the host.

Technical details:

    The packets are sent as UDP packets to the multicast address '239.0.3.250'
    on port '56129'. The packet structure is as follows:

    +------------------+---------------------------+
    | Header (6 Bytes) | Payload (variable length) |
    +------------------+---------------------------+

    The header consists of three fields:

    +-----------------------+------------------+----------------------+
    | Header Mark (4 bytes) | Version (1 byte) | Packet Type (1 byte) |
    +-----------------------+------------------+----------------------+

    The header mark is the ASCII string "MIDI". The version is currently 1. The
    packet type can be one of the following values (as defined in the
    'PacketType' enumeration):

        - '0': MIDI Message
        - '1': Hello Message
        - '2': Hello Reply Message

    The payload of the 'MIDI Message' packet contains the device name and the
    actual MIDI message data. The device name is a UTF-8 encoded Pascal like
    string with a maximum length of 64 bytes. That is, it is prepended by a
    1-byte length field which gives the number of bytes in the device name
    (excluding the length field itself).The MIDI message data is a
    variable-length field that contains the actual MIDI message (remaining
    bytes of the packet).

    +-----------------------------+-----------------------------+-----------------------------+
    | Device Name Length (1 byte) | Device Name (max. 64 bytes) | MIDI Data (variable length) |
    +-----------------------------+-----------------------------+-----------------------------+

    'Hello' packets start with a numeric ID field (a 4-byte integer). Each time
    a 'Hello' packet is sent, the ID is incremented; note, each host has its own
    ID counter that is incremented independently of the other hosts. Once a host
    receives a 'Hello' packet, it must send a 'Hello Reply' packet back to the
    sender of the 'Hello' packet. As all messages are mulitcasted to all hosts
    in the network, the 'Hello Reply' packet must contain the IP address of the
    original sender of the 'Hello' packet. In addition, the 'Hello Reply' packet
    must contain the ID of the previous 'Hello' packet in order to allow the
    sender to match the 'Hello' and 'Hello Reply' packets correctly, even in the
    event of packet loss.
    
    As 'Hello' and 'Hello Reply' packets may contain a list of device names of
    the hosts that sent the packet, the number of device names is stored in the
    second field as a 1-byte integer. This field is mandatory and must be
    present even if the number of device names is zero. Then, the respective
    device names are stored in a sequence of fields. Each device name is
    prepended by a 1-byte length field which gives the number of bytes in the
    device name (excluding the length field itself).

    The packet structure is as follows:

    Hello Packet:

    +--------------+---------------------------------+-----------------------------+-----------------------------+-----+
    | ID (4 bytes) | Number of Device Names (1 byte) | Device Name Length (1 byte) | Device Name (max. 64 bytes) | ... |
    +--------------+---------------------------------+-----------------------------+-----------------------------+-----+

    Hello Reply Packet:

    +--------------+----------------------+---------------------------------+-----------------------------+-----------------------------+-----+
    | ID (4 bytes) | IP Adresss (4 Bytes) | Number of Device Names (1 byte) | Device Name Length (1 byte) | Device Name (max. 64 bytes) | ... |
    +--------------+----------------------+---------------------------------+-----------------------------+-----------------------------+-----+

    In summery, the packet 'MIDI Message' packet structure is as follows:

        1. Header (4 bytes): The ASCII string "MIDI".
        2. Version (1 byte): The protocol version, currently 1.
        3. Packet Type (1 byte): The type of the packet, as defined in the
           'PacketType' enumeration.
        4. Device Name Length (1 byte): The length of the device name.
        5. Device Name (variable length): The UTF-8 encoded name of the MIDI
           device that sent the message.
        5. MIDI Data (variable length): The actual MIDI message data.
    
    The 'Hello' packet structure is as follows:

        1. Header (4 bytes): The ASCII string "MIDI".
        2. Version (1 byte): The protocol version, currently 1.
        3. Packet Type (1 byte): The type of the packet, as defined in the
           'PacketType' enumeration.
        4. ID (4 bytes): A numeric ID that is incremented each time a 'Hello'
           packet is sent.
        5. Number of Device Names (1 byte): The number of device names.

        If present:
        6. Device Name Length (1 byte): The length of the device name.
        7. Device Name (variable length): The UTF-8 encoded name of the MIDI
           device that sent the message.
        8. Repeat steps 6 and 7 for each device name.
    
    The 'Hello Reply' packet structure is as follows:

        1. Header (4 bytes): The ASCII string "MIDI".
        2. Version (1 byte): The protocol version, currently 1.
        3. Packet Type (1 byte): The type of the packet, as defined in the
           'PacketType' enumeration.
        4. ID (4 bytes): The numeric ID from the correponding 'Hello' packet.
        5. IP Address (4 bytes): The IP address of the original sender of the
           'Hello' packet (the recipient of the 'Hello Reply' packet).
        6. Number of Device Names (1 byte): The number of device names.

        If present:
        7. Device Name Length (1 byte): The length of the device name.
        8. Device Name (variable length): The UTF-8 encoded name of the MIDI
           device that sent the message.
        9. Repeat steps 6 and 7 for each device name.
    
    A last note: UDP datagrams should be smaller than the maximum transmission
    unit (MTU) of the network to avoid fragmentation. The MTU is typically 1500
    bytes for Ethernet networks. However, in theory a UDP packet may be as large
    as 65507 bytes.
"""

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long

import re
from enum import IntEnum
from typing import ClassVar

try:
    from pydantic import validate_call
    from pydantic.dataclasses import dataclass
    from pydantic.fields import Field as field
except ImportError:
    from dataclasses import dataclass
    from dataclasses import field
    def validate_call(func):
        return func

try:
    from icecream import ic
    ic.disable()
except ImportError:  # Graceful fallback if IceCream isn't installed.
    def ic(*args):
        return None if not args else (args[0] if len(args) == 1 else args)


###############################################################################
# Helper functions
###############################################################################

def to_byte_string(string: str, maximum_length: int, encoding='utf-8') -> bytes:
    """Convert a string to a byte string with a maximum length."""
    # First, encode the string to bytes using the given encoding (default is
    # UTF-8) and truncate it to the desired length. This might result in a
    # string whose last character is a partial character and thus invalid. To
    # handle this, decode the bytes back to a string while ignoring any encoding
    # errors. This will just drop the invalid partial character. The result is
    # then encoded back to bytes.
    return string.encode(encoding)[:maximum_length].decode(encoding=encoding, errors='ignore').encode()

def to_fixed_length_byte_string(string: str, length: int, padding_character=b'\x00', encoding='utf-8') -> bytes:
    """Convert a string to a fixed-length byte string."""
    # First, encode the string to bytes using the given encoding (default is
    # UTF-8) and truncate it to the desired length. This might result in a
    # string whose last character is a partial character and thus invalid. To
    # handle this, decode the bytes back to a string while ignoring any encoding
    # errors. This will just drop the invalid partial character. The result is
    # then encoded back to bytes and padded with the padding character if
    # necessary.
    return string.encode()[:length].decode(encoding=encoding, errors='ignore').encode().ljust(length, padding_character)


###############################################################################
# MIDI over LAN packet definitions
###############################################################################

VERSION_NUMBER = 1  # version number of the MIDI over LAN protocol
MULTICAST_GROUP_ADDRESS = '239.0.3.250'  # MIDI over LAN multicast address
MULTICAST_PORT_NUMBER = 56129  # MIDI over LAN port number

# The below indices are used to access the fields of the MIDI over LAN packets
# and are derived from the packet structure described in the module docstring.
_HEADER_LENGTH = 6
_HEADER_MARK_INDEX = 0
_VERSION_FIELD_INDEX = 4
_PACKET_TYPE_INDEX = 5
_MIDI_MESSAGE_PACKET__DEVICE_NAME_LENGTH_INDEX = 6
_MIDI_MESSAGE_PACKET__DEVICE_NAME_INDEX = 7
_HELLO_PACKET__NUMBER_OF_DEVICE_NAMES_INDEX = 10
_HELLO_PACKET__FIRST_DEVICE_NAME_INDEX = 11  # includes the length field
_HELLO_REPLY_PACKET__IP_ADDRESS_INDEX = 10
_HELLO_REPLY_PACKET__NUMBER_OF_DEVICE_NAMES_INDEX = 14
_HELLO_REPLY_PACKET__FIRST_DEVICE_NAME_INDEX = 15  # includes the length field


class PacketType(IntEnum):
    """Enumeration for the different types of MIDI packets."""
    MIDI_MESSAGE = 0
    HELLO = 1
    HELLO_REPLY = 2


@dataclass
class Packet():
    """Common structure of a MIDI over LAN packet."""
    header_mark: bytes = b'MIDI'
    version: int = VERSION_NUMBER
    packet_type: int = PacketType.MIDI_MESSAGE.value

    MIDI_MESSAGE_PACKET_HEADER = b'MIDI\x01\x00'
    HELLO_PACKET_HEADER = b'MIDI\x01\x01'
    HELLO_REPLY_PACKET_HEADER = b'MIDI\x01\x02'


    @staticmethod
    @validate_call
    def from_bytes(data: bytes):
        """Create a 'MIDI over LAN' packet object from a byte string.

        The input byte string may be interpreted as one of the following types:

            - MIDI over LAN: the first 4 bytes are 'MIDI' and the byte string is
              greater than or equal to 6 bytes. The packet type field is checked
              to determine the packet type. In case of a 'Hello' or 'Hello
              Reply' packet, a 'HelloPacket' or 'HelloReplyPacket' object is
              created. Possible trailing bytes are ignored. In case of a 'MIDI
              Message' packet, a 'MidiMessagePacket' object is created.

            - Raw MIDI data: if 'data' does not meet the above criteria, it is
              assumed to be raw MIDI data and a 'MidiMessagePacket' is created.

        Exceptions:
            - ValueError: if the packet header is invalid, the packet version is
              not 1, the packet type is unknown, or the packet is too short.

        Example:
            # note on, channel 0, middle C, velocity 64
            packet = Packet.from_bytes(b'MIDI\x01\x00\x90\x3C\x40')
        """

        # Handle raw MIDI data
        if len(data) < _HEADER_LENGTH:
            return MidiMessagePacket(device_name='unknown', midi_data=data)
        if not data.startswith(b'MIDI'):
            return MidiMessagePacket(device_name='unknown', midi_data=data)

        # Handle MIDI over LAN packets
        if data[_VERSION_FIELD_INDEX] != VERSION_NUMBER:
            raise ValueError("Invalid MIDI over LAN packet version")
        match data[_PACKET_TYPE_INDEX]:
            case PacketType.HELLO:
                return HelloPacket.from_bytes(data)
            case PacketType.HELLO_REPLY:
                return HelloReplyPacket.from_bytes(data)
            case PacketType.MIDI_MESSAGE:
                return MidiMessagePacket.from_bytes(data)
            case _:
                ic('Invalid data.', data)
                raise ValueError("Unknown MIDI over LAN packet type")


@dataclass
class MidiMessagePacket(Packet):
    """A MIDI message packet consists of a device name and the actual MIDI data."""
    packet_type: int = PacketType.MIDI_MESSAGE.value
    device_name: str = ''  # name of the MIDI device that sent the message
    midi_data: bytes = b''
    header: bytes = Packet.MIDI_MESSAGE_PACKET_HEADER  # header without the device name


    def __str__(self):
        """Return a string representation of the MIDI message packet."""
        output_string = f"MidiMessagePacket\n" \
                        f"  Device name: {self.device_name}\n" \
                        f"  MIDI data: "
        for byte in self.midi_data:
            output_string += f"{byte:02X} "
        output_string += "\n"
        return output_string


    @staticmethod
    @validate_call
    def from_bytes(data: bytes):
        """Create a MIDI message packet object from a byte string.
        
        If the data does not start with the MIDI message packet header, it is
        assumed that the data is solely the payload of the packet (MIDI data)
        and a MIDI message packet object is created from this data.
        """
        ic(data)

        if not data.startswith(Packet.MIDI_MESSAGE_PACKET_HEADER):
            return MidiMessagePacket(device_name='unknown', midi_data=data)

        device_name_length = data[_MIDI_MESSAGE_PACKET__DEVICE_NAME_LENGTH_INDEX]
        minimum_packet_length = _HEADER_LENGTH + 1 + device_name_length + 1  # header + device name length + device name + 1 byte of MIDI data
        if len(data) < minimum_packet_length:
            raise ValueError("MIDI over LAN packet is too short")
        packet = MidiMessagePacket()
        start = _MIDI_MESSAGE_PACKET__DEVICE_NAME_INDEX
        end = start + device_name_length
        packet.device_name = data[start:end].decode('utf-8').strip('\x00')
        packet.midi_data = data[end:]
        return packet


    def to_bytes(self):
        """Return the MIDI message packet as a byte string (e.g., for using it in a UDP packet)."""
        device_name = to_byte_string(self.device_name, 64)
        return self.header + len(device_name).to_bytes() + device_name + self.midi_data


@dataclass
class HelloPacket(Packet):
    """Data class for a Hello packet."""
    packet_type: int = PacketType.HELLO.value
    id: int = field(init=False)
    number_of_device_names: int = 0
    device_names: list[str] = field(default_factory=list)
    header: bytes = Packet.HELLO_PACKET_HEADER  # header without the device name

    _counter: ClassVar[int] = 0

    def __post_init__(self):
        """Set the ever increasing ID of the Hello packet."""
        self.id = HelloPacket._counter
        HelloPacket._counter += 1


    def __str__(self):
        """Return a string representation of the Hello packet."""
        if len(self.device_names) == 0:
            return f"HelloPacket (id = {self.id}) (no device names included)"
        else:
            output_string = f"HelloPacket (id = {self.id})"
            for device_name in self.device_names:
                output_string += f"\n  Device name: {device_name}"
            return output_string


    def add_device_name(self, device_name: str):
        """Add a device name to the list of device names."""
        self.device_names.append(device_name)
        self.number_of_device_names = len(self.device_names)


    def clear_device_names(self):
        """Clear the list of device names."""
        self.device_names.clear()
        self.number_of_device_names = 0


    @staticmethod
    @validate_call
    def from_bytes(data: bytes):
        """Create a Hello packet object from a byte string.
        
        The data must contain a valid Hello packet structure (see module
        docstring for details), otherwise an exception is raised.
        """
        ic(data)

        if not data.startswith(Packet.HELLO_PACKET_HEADER):
            raise ValueError("Invalid MIDI over LAN packet header")
        if len(data) < 11:  # header + ID + number of device names + 1 byte for the first device name
            raise ValueError("Expected at least 5 bytes for the Hello packet")
        if data[_VERSION_FIELD_INDEX] != VERSION_NUMBER:
            raise ValueError("Invalid MIDI over LAN packet version")
        if data[_PACKET_TYPE_INDEX] != PacketType.HELLO:
            raise ValueError("Invalid MIDI over LAN packet type")
        if data[_HELLO_PACKET__NUMBER_OF_DEVICE_NAMES_INDEX] > 0 and len(data) < 12:
            raise ValueError("Expected at least 12 bytes for the Hello packet with device names")

        packet = HelloPacket()
        packet.id = int.from_bytes(data[_HEADER_LENGTH:_HEADER_LENGTH + 4], 'big')
        n = data[_HELLO_PACKET__NUMBER_OF_DEVICE_NAMES_INDEX]  # number of subsequent device names
        if n == 0:
            return packet
        offset = _HELLO_PACKET__FIRST_DEVICE_NAME_INDEX  # includes the 1 byte long length field
        for _ in range(n):
            try:
                string_length = data[offset]
            except IndexError as error:
                raise ValueError("Invalid MIDI over LAN 'Hello' packet length") from error
            if string_length > 64:
                raise ValueError("Device name length exceeds maximum length of 64 bytes")
            if string_length == 0:
                raise ValueError("Device name length is zero")
            if len(data) < offset + 1 + string_length:
                raise ValueError("Invalid MIDI over LAN packet length; device name length suggests a longer packet")
            start = offset + 1  # index to the start of the device name
            end = start + string_length
            device_name = data[start:end].decode('utf-8').strip('\x00')
            packet.add_device_name(device_name)
            offset = end
        return packet


    def to_bytes(self):
        """Return the Hello packet as a byte string (e.g., for using it in a UDP packet)."""
        data = self.header + self.id.to_bytes(4, 'big') + len(self.device_names).to_bytes(1, 'big')
        for device_name in self.device_names:
            device_name = to_byte_string(device_name, 64)
            data += len(device_name).to_bytes(1, 'big') + device_name
        return data


@dataclass
class HelloReplyPacket(Packet):
    """Data class for a Hello Reply packet.
    
    Example:

        # Create a Hello Reply packet
        packet = HelloReplyPacket(id = 37)  # ID of the corresponding 'Hello' packet
        packet.remote_ip = '192.168.0.71'  # IP address of the original sender of the 'Hello' packet
        packet.add_device_name('MIDI Keyboard')
        packet.add_device_name('MIDI Drum Kit')
        packet.add_device_name('MIDI Synthesizer')
        data = packet.to_bytes()
        print(data)
    """
    packet_type: int = PacketType.HELLO_REPLY.value
    id: int = -1 # ID of the corresponding 'Hello' packet
    remote_ip: str = ''  # IP address of the original sender of the 'Hello' packet
    number_of_device_names: int = 0
    device_names: list[str] = field(default_factory=list)
    header: bytes = Packet.HELLO_REPLY_PACKET_HEADER  # header without the device name


    def __str__(self):
        """Return a string representation of the Hello Reply packet."""
        output_string = f"HelloReplyPacket (id = {self.id}, recipient = {self.remote_ip})"
        if len(self.device_names) == 0:
            return output_string + " (no device names included)"
        else:
            for device_name in self.device_names:
                output_string += f"\n  Device name: {device_name}"
            return output_string


    def add_device_name(self, device_name: str):
        """Add a device name to the list of device names."""
        self.device_names.append(device_name)
        self.number_of_device_names = len(self.device_names)


    def clear_device_names(self):
        """Clear the list of device names."""
        self.device_names.clear()
        self.number_of_device_names = 0


    @staticmethod
    @validate_call
    def from_bytes(data: bytes):
        """Create a Hello Reply packet object from a byte string.
        
        The data must contain a valid Hello Reply packet structure (see module
        docstring for details), otherwise an exception is raised.
        """
        ic(data)

        if not data.startswith(Packet.HELLO_REPLY_PACKET_HEADER):
            raise ValueError("Invalid MIDI over LAN packet header")
        if len(data) < 15:  # header + ID + IP address + number of device names + 1 byte for the first device name
            raise ValueError("Expected at least 5 bytes for the Hello Reply packet")
        if data[_VERSION_FIELD_INDEX] != VERSION_NUMBER:
            raise ValueError("Invalid MIDI over LAN packet version")
        if data[_PACKET_TYPE_INDEX] != PacketType.HELLO_REPLY:
            raise ValueError("Invalid MIDI over LAN packet type")
        if data[_HELLO_REPLY_PACKET__NUMBER_OF_DEVICE_NAMES_INDEX] > 0 and len(data) < 16:
            raise ValueError("Expected at least 16 bytes for the Hello Reply packet with device names")

        packet = HelloReplyPacket()
        # ID is the first 4 bytes of the payload
        packet.id = int.from_bytes(data[_HEADER_LENGTH:_HEADER_LENGTH + 4], 'big')
        # The next 4 bytes are the IPv4 address of the original sender
        packet.remote_ip = '.'.join(str(byte) for byte in data[_HELLO_REPLY_PACKET__IP_ADDRESS_INDEX:_HELLO_REPLY_PACKET__IP_ADDRESS_INDEX + 4])
        n = data[_HELLO_REPLY_PACKET__NUMBER_OF_DEVICE_NAMES_INDEX]  # number of subsequent device names
        if n == 0:
            return packet
        offset = _HELLO_REPLY_PACKET__FIRST_DEVICE_NAME_INDEX  # includes the 1 byte long length field
        for _ in range(n):
            try:
                string_length = data[offset]
            except IndexError as error:
                raise ValueError("Invalid MIDI over LAN 'Hello Reply' packet length") from error
            if string_length > 64:
                raise ValueError("Device name length exceeds maximum length of 64 bytes")
            if string_length == 0:
                raise ValueError("Device name length is zero")
            if len(data) < offset + 1 + string_length:
                raise ValueError("Invalid MIDI over LAN packet length; device name length suggests a longer packet")
            start = offset + 1  # index to the start of the device name
            end = start + string_length
            device_name = data[start:end].decode('utf-8').strip('\x00')
            packet.add_device_name(device_name)
            offset = end
        return packet


    def to_bytes(self):
        """Return the Hello packet as a byte string (e.g., for using it in a UDP packet).
        
        Exceptions:
            - ValueError: if the IP address is invalid.
        """
        # Convert the IP address to a byte string
        regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        if not re.match(regex, self.remote_ip):
            raise ValueError("Invalid IP address")
        ip_bytes = b''.join(int(byte).to_bytes(1, 'big') for byte in map(int, self.remote_ip.split('.')))
        data = self.header + self.id.to_bytes(4, 'big') + ip_bytes + len(self.device_names).to_bytes(1, 'big')
        for device_name in self.device_names:
            device_name = to_byte_string(device_name, 64)
            data += len(device_name).to_bytes(1, 'big') + device_name
        return data
