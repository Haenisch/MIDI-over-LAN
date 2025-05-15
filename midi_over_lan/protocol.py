# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

# Written by Christoph Hänisch.
# Version 1
# Last changed on 2025-05-10.

"""MIDI over LAN library for Python.

The MIDI over LAN protocol enables the transmission of MIDI messages over a
local area network, allowing remote control of MIDI devices. Messages are
multicast to all hosts on the network, and interested hosts simply listen for
these packets. The protocol is efficient with minimal overhead, making it
suitable for real-time communication. Each packet includes the originating MIDI
device's name, enabling the receiving host to filter or route messages
appropriately (e.g., directing the MIDI message to a specific local MIDI input
port).

The protocol includes a simple discovery mechanism where hosts announce their
presence by sending a 'Hello' packet. Other hosts can respond with a 'Hello
Reply' packet, which helps determine the round-trip time between hosts. 'Hello'
packets can also contain the names of MIDI devices connected to the host.

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

        - Header mark: The ASCII string "MIDI".
        - Version: Currently 1.
        - Packet type: Defined in the 'PacketType' enumeration.
            - '0': MIDI Message
            - '1': Hello Message
            - '2': Hello Reply Message

    The 'MIDI Message' packet's payload includes the device name and MIDI
    message data. The device name is a UTF-8 encoded Pascal-like string with a
    maximum length of 64 bytes, preceded by a 1-byte length field. The MIDI
    message data follows, with variable length.

    +-----------------------------+-----------------------------+-----------------------------+
    | Device Name Length (1 byte) | Device Name (max. 64 bytes) | MIDI Data (variable length) |
    +-----------------------------+-----------------------------+-----------------------------+

    'Hello' packets start with a 4-byte numeric ID, incremented each time a
    packet is sent. Each host has its own independent ID counter. The ID is
    followed by the hostname, with a 1-byte length field and a UTF-8 encoded
    hostname (max 64 bytes). 'Hello' packets may also list MIDI device names,
    with the number of names specified in a mandatory 1-byte field. Each device
    name field is preceded by a 1-byte length field.

    When a host receives a 'Hello' packet, it must send a 'Hello Reply' packet
    back to the sender. Since all messages are multicast, the 'Hello Reply'
    packet must include the original sender's IP address and the ID of the
    previous 'Hello' packet. This ensures the original sender can match 'Hello'
    and 'Hello Reply' packets correctly, even if packets are lost, and helps
    determine round-trip time. Again, the 'Hello Reply' packet may include a
    list of MIDI device names. 

    The packet structure is as follows:

    Hello Packet:

    +--------------+--------------------------+--------------------------+---------------------------------+-----------------------------+-----------------------------+-----+
    | ID (4 bytes) | Hostname Length (1 byte) | Hostname (max. 64 bytes) | Number of Device Names (1 byte) | Device Name Length (1 byte) | Device Name (max. 64 bytes) | ... |
    +--------------+--------------------------+--------------------------+---------------------------------+-----------------------------+-----------------------------+-----+

    Hello Reply Packet:

    +--------------+----------------------+--------------------------+--------------------------+---------------------------------+-----------------------------+-----------------------------+-----+
    | ID (4 bytes) | IP Adresss (4 Bytes) | Hostname Length (1 byte) | Hostname (max. 64 bytes) | Number of Device Names (1 byte) | Device Name Length (1 byte) | Device Name (max. 64 bytes) | ... |
    +--------------+----------------------+--------------------------+--------------------------+---------------------------------+-----------------------------+-----------------------------+-----+

    In summery, the packet 'MIDI Message' packet structure is as follows:

        1. Header (4 bytes): The ASCII string "MIDI".
        2. Version (1 byte): The protocol version, currently 1.
        3. Packet Type (1 byte): Defined in the 'PacketType' enumeration.
        4. Device Name Length (1 byte): Length of the device name.
        5. Device Name (variable length): UTF-8 encoded name of the MIDI device.
        5. MIDI Data (variable length): Actual MIDI message data.
    
    The 'Hello' packet structure is as follows:

        1. Header (4 bytes): The ASCII string "MIDI".
        2. Version (1 byte): The protocol version, currently 1.
        3. Packet Type (1 byte): Defined in the 'PacketType' enumeration.
        4. ID (4 bytes): Numeric ID, incremented with each 'Hello' packet sent.
        5. Hostname Length (1 byte): Length of the hostname.
        6. Hostname (variable length): The UTF-8 encoded hostname.
        7. Number of Device Names (1 byte): The number of device names.

        If present:
        8.  Device Name Length (1 byte): Length of the device name.
        9.  Device Name (variable length): UTF-8 encoded name of the MIDI device.
        10. Repeat steps 8 and 9 for each device name.
    
    The 'Hello Reply' packet structure is as follows:

        1. Header (4 bytes): The ASCII string "MIDI".
        2. Version (1 byte): The protocol version, currently 1.
        3. Packet Type (1 byte): Defined in the 'PacketType' enumeration.
        4. ID (4 bytes): Numeric ID from the correponding 'Hello' packet.
        5. IP Address (4 bytes): IP address of the original sender of the 'Hello' packet.
        6. Hostname Length (1 byte): Length of the hostname.
        7. Hostname (variable length): The UTF-8 encoded hostname.
        8. Number of Device Names (1 byte): The number of device names.

        If present:
        9.  Device Name Length (1 byte): Length of the device name.
        10. Device Name (variable length): UTF-8 encoded name of the MIDI device.
        11. Repeat steps 9 and 10 for each device name.

    Note: UDP datagrams should be smaller than the network's maximum
    transmission unit (MTU) to avoid fragmentation. The typical MTU for Ethernet
    networks is 1500 bytes, although a UDP packet can theoretically be as large
    as 65507 bytes.
"""

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation

import logging
import re
import socket
from enum import IntEnum
from functools import cache
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


logger = logging.getLogger('midi_over_lan.protocol')
logger.setLevel(logging.CRITICAL)


###############################################################################
# Helper functions and classes
###############################################################################

@cache
def get_hostname() -> str:
    """Get the hostname of the local machine."""
    try:
        hostname = socket.gethostname()
    except OSError as error:
        logger.error(f'Error getting hostname: {error}')
        hostname = 'unknown'
    return hostname


@cache
def ip_address_to_bytes(ip_address: str) -> bytes:
    """Convert an IP address string to a byte string.
    
    Exceptions:
        - ValueError: if the IP address is invalid.
    """
    # Check if the IP address is valid
    regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    if not re.match(regex, ip_address):
        raise ValueError("Invalid IP address")

    # Do the actual conversion
    try:
        # Split the IP address into its components and convert each component to a byte
        return b''.join(int(octet).to_bytes(length=1, byteorder='big') for octet in ip_address.split('.'))
    except ValueError as error:
        logger.error(f"Invalid IP address: {ip_address}")
        raise ValueError("Invalid IP address") from error
    except Exception as error:
        logger.error(f"Error converting IP address to bytes: {error}")
        raise ValueError("Error converting IP address to bytes") from error


def to_byte_string(string: str, maximum_length: int, encoding='utf-8') -> bytes:
    """Convert a string to a byte string with a maximum length."""
    # Encode the string to bytes using the specified encoding (default is UTF-8)
    # and truncate it to the maximum length. This might result in an invalid
    # string if the last character is partially encoded. To address this, decode
    # the bytes back to a string, ignoring any encoding errors, which will drop
    # the invalid partial character. Finally, re-encode the result back to bytes.
    return string.encode(encoding)[:maximum_length].decode(encoding=encoding, errors='ignore').encode()


def to_fixed_length_byte_string(string: str, length: int, padding_character=b'\x00', encoding='utf-8') -> bytes:
    """Convert a string to a fixed-length byte string."""
    # Encode the string to bytes using the specified encoding (default is UTF-8)
    # and truncate it to the desired length. This might result in an invalid
    # string if the last character is partially encoded. To address this, decode
    # the bytes back to a string, ignoring any encoding errors, which will drop
    # the invalid partial character. Re-encode the result back to bytes and pad
    # it with the specified padding character to reach the fixed length if needed.
    return string.encode()[:length].decode(encoding=encoding, errors='ignore').encode().ljust(length, padding_character)


def to_pascal_like_byte_string(string: str) -> bytes:
    """Convert a UTF-8 string to a Pascal-like byte string.
    
    It is assumed that the input string is a UTF-8 encoded Pascal-like string
    with a maximum length of 64 bytes.
    """
    byte_string = to_byte_string(string, 64, encoding='utf-8')
    return len(byte_string).to_bytes(length=1, byteorder='big') + byte_string


class Parser():
    """Parser for MIDI over LAN packets.

    This class is used to parse MIDI over LAN packets. It is not intended to be
    used directly by the user.

    First, the header is checked (header mark, version number, and packet type).
    If the header is invalid, a ValueError is raised.

    If the header is valid, the packet can be parsed using the following methods:

        - read(length: int) -> bytes
        - rear_id() -> int
        - read_ip_address() -> str
        - read_hostname() -> str
        - read_list_of_strings() -> list[str]
        - read_string() -> str

    Note, the methods must be called in the order the packet fields are defined
    in the packet structure. Internally, the methods keep track of the current
    position in the packet data. The methods will raise a ValueError if the
    packet is too short or if the packet header is invalid.

    Execptions:
        - ValueError: if the packet header is invalid, the packet version is
          not 1, the packet type is unknown, or the packet is too short.
    """

    def __init__(self, data: bytes):
        """Initialize the parser with the given data."""
        self.data = data
        self.position = 0
        self.packet_type = None
        self.check_header()


    def check_header(self):
        """Check the header of the MIDI over LAN packet."""
        if len(self.data) < _HEADER_LENGTH:
            raise ValueError("MIDI over LAN packet is too short")
        if not self.data.startswith(b'MIDI'):
            raise ValueError("Invalid MIDI over LAN packet header")
        if self.data[_VERSION_FIELD_INDEX] != VERSION_NUMBER:
            raise ValueError("Invalid MIDI over LAN packet version")
        self.packet_type = self.data[_PACKET_TYPE_INDEX]
        if self.packet_type not in (PacketType.MIDI_MESSAGE, PacketType.HELLO, PacketType.HELLO_REPLY):
            raise ValueError("Unknown MIDI over LAN packet type")
        self.position = 6


    def read(self, length: int) -> bytes:
        """Read a number of bytes from the data."""
        if self.position + length > len(self.data):
            raise ValueError("Error parsing MIDI over LAN packet: Not enough data to read")
        result = self.data[self.position:self.position + length]
        self.position += length
        return result


    def read_id(self) -> int:
        """Read a 4-byte ID from the data.
        
        The ID is read as a big-endian integer from the data. The position in the
        data is updated accordingly.
        """
        id_bytes = self.read(4)
        return int.from_bytes(id_bytes, 'big')


    def read_ip_address(self) -> str:
        """Read a 4-byte IP address from the data.
        
        The IP address is read as a 4-byte string from the data. The position in
        the data is updated accordingly. The IP address is returned as a string
        in the format 'x.x.x.x'.
        """
        ip_bytes = self.read(4)
        return '.'.join(str(byte) for byte in ip_bytes)


    def read_hostname(self) -> str:
        """Read a hostname from the data.
        
        The hostname is assumed to be a UTF-8 encoded Pascal-like string with a
        maximum length of 64 bytes, preceded by a 1-byte length field. The
        hostname is decoded and returned as a Python string. The length field is
        not included in the returned string.
        """
        string_length = int.from_bytes(self.read(1), byteorder='big')
        try:
            hostname = self.read(string_length).decode('utf-8').strip('\x00')
        except UnicodeDecodeError as error:
            logger.error(f"Error decoding hostname: {error}")
            raise ValueError("Invalid unicode string") from error
        return hostname


    def read_list_of_strings(self) -> list[str]:
        """Read a list of strings from the data.
        
        The list of strings is assumed to be a sequence of UTF-8 encoded
        Pascal-like strings with a maximum length of 64 bytes. Each strings is
        preceded by a 1-byte length field. The strings are decoded and returned
        as a list of Python strings. The length field is not included in the
        returned strings.
        """
        number_of_strings = int.from_bytes(self.read(1), byteorder='big')
        strings = []
        for _ in range(number_of_strings):
            strings.append(self.read_string())
        return strings


    def read_string(self) -> str:
        """Read a string from the data.
        
        The string is assumed to be a UTF-8 encoded Pascal-like string with a
        maximum length of 64 bytes, preceded by a 1-byte length field. The
        string is decoded and returned as a Python string. The length field is
        not included in the returned string.
        """
        string_length = int.from_bytes(self.read(1), byteorder='big')
        try:
            string =self.read(string_length).decode('utf-8').strip('\x00')
        except UnicodeDecodeError as error:
            logger.error(f"Error decoding string: {error}")
            raise ValueError("Invalid unicode string") from error
        return string


###############################################################################
# MIDI over LAN packet definitions
###############################################################################

VERSION_NUMBER = 1  # version number of the MIDI over LAN protocol
MULTICAST_GROUP_ADDRESS = '239.0.3.250'  # MIDI over LAN multicast address
MULTICAST_PORT_NUMBER = 56129  # MIDI over LAN port number

# The below indices are used to access the fields of the MIDI over LAN packets
# and are derived from the packet structure described in the module docstring.
_HEADER_LENGTH = 6
_VERSION_FIELD_INDEX = 4
_PACKET_TYPE_INDEX = 5
_MIDI_MESSAGE_PACKET__DEVICE_NAME_LENGTH_INDEX = 6
_MIDI_MESSAGE_PACKET__DEVICE_NAME_INDEX = 7


class PacketType(IntEnum):
    """Enumeration for the different types of MIDI packets."""
    MIDI_MESSAGE = 0
    HELLO = 1
    HELLO_REPLY = 2


packet_type_to_string = {
    PacketType.MIDI_MESSAGE: 'MIDI Message',
    PacketType.HELLO: 'Hello',
    PacketType.HELLO_REPLY: 'Hello Reply'
}


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
                logger.error(f"Invalid data: {data}")
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
        logger.debug(data)

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
        return self.header + len(device_name).to_bytes(length=1, byteorder='big') + device_name + self.midi_data


@dataclass
class HelloPacket(Packet):
    """Data class for a Hello packet.
    
    Public fields:
        - packet_type: The type of the packet (Hello).
        - id: The ID of the packet (incremented with each Hello packet sent).
        - hostname: The hostname of the local machine or 'unknown'.
        - number_of_device_names: The number of device names included in the packet.
        - device_names: A list of local MIDI devices whose data is broadcast.
        - header: The header of the packet (without the device name).
    """
    packet_type: int = PacketType.HELLO.value
    id: int = field(init=False)
    hostname: str = field(default_factory=get_hostname)  # hostname of the local machine
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
            return f"HelloPacket (id = {self.id}, host = {self.hostname}) (no device names included)"
        else:
            output_string = f"HelloPacket (id = {self.id}, host = {self.hostname})"
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
        logger.debug(data)

        parser = Parser(data)
        if parser.packet_type != PacketType.HELLO:
            raise ValueError("Invalid MIDI over LAN packet type (expected Hello packet)")

        packet = HelloPacket()
        packet.id = parser.read_id()
        packet.hostname = parser.read_hostname()
        packet.device_names = parser.read_list_of_strings()
        packet.number_of_device_names = len(packet.device_names)

        return packet


    def to_bytes(self):
        """Return the Hello packet as a byte string (e.g., for using it in a UDP packet)."""
        data = self.header + \
               self.id.to_bytes(4, 'big') + \
               to_pascal_like_byte_string(self.hostname) + \
               len(self.device_names).to_bytes(length=1, byteorder='big')
        for device_name in self.device_names:
            data += to_pascal_like_byte_string(device_name)
        return data


@dataclass
class HelloReplyPacket(Packet):
    """Data class for a Hello Reply packet.

    Public fields:
        - packet_type: The type of the packet (Hello Reply).
        - id: The ID of the corresponding Hello packet.
        - remote_ip: The IP address of the original sender of the Hello packet.
        - hostname: The hostname of the local machine or 'unknown'.
        - number_of_device_names: The number of device names included in the packet.
        - device_names: A list of local MIDI devices whose data is broadcast.
        - header: The header of the packet (without the device name).
    
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
    hostname: str = field(default_factory=get_hostname)  # hostname of the local machine
    number_of_device_names: int = 0
    device_names: list[str] = field(default_factory=list)
    header: bytes = Packet.HELLO_REPLY_PACKET_HEADER  # header without the device name


    def __str__(self):
        """Return a string representation of the Hello Reply packet."""
        output_string = f"HelloReplyPacket (id = {self.id}, host = {self.hostname}, recipient = {self.remote_ip})"
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
        logger.debug(data)

        parser = Parser(data)
        if parser.packet_type != PacketType.HELLO_REPLY:
            raise ValueError("Invalid MIDI over LAN packet type (expected Hello Reply packet)")

        packet = HelloReplyPacket()
        packet.id = parser.read_id()
        packet.remote_ip = parser.read_ip_address()
        packet.hostname = parser.read_hostname()
        packet.device_names = parser.read_list_of_strings()
        packet.number_of_device_names = len(packet.device_names)

        return packet


    def to_bytes(self):
        """Return the Hello packet as a byte string (e.g., for using it in a UDP packet).
        
        Exceptions:
            - ValueError: if the ID is not set.
            - ValueError: if the IP address is not set.
        """
        if self.id < 0:
            raise ValueError("ID is not set")
        if not self.remote_ip:
            raise ValueError("IP address is not set")
        data = self.header + \
               self.id.to_bytes(4, 'big') + \
               ip_address_to_bytes(self.remote_ip) + \
               to_pascal_like_byte_string(self.hostname) + \
               len(self.device_names).to_bytes(length=1, byteorder='big')
        for device_name in self.device_names:
            data += to_pascal_like_byte_string(device_name)
        return data
