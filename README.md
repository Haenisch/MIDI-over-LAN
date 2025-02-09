# MIDI-over-LAN

MIDI over LAN (protocol, Python library, GUI client, ...)



## Overview

MIDI-over-LAN is a Python library that defines and implements a protocol for sending MIDI messages over a network. The project includes sample programs to demonstrate its usage.



## Features

- Sends MIDI messages over the network using UDP packets (connectionless protocol).
- Includes raw MIDI data, sending host information, and original MIDI device names in the packets.
- Allows for computing round trip times between hosts using hello packages.
- Allows for filtering MIDI data based on device names.
- GUI client for selecting MIDI devices and output ports (planned feature).



## Installation

To install the library, use pip:

```bash
pip install midi-over-lan
```

**TODO:** The package still needs to be uploaded to the Python Package Index (PyPI). 



## Usage

Here is an example of how to use the library.

Server:

```python
#!/usr/bin/env python3

"""Minimal example of a MIDI over LAN server."""

interface_ip = '192.168.0.50' # Change this to the IP address of the network interface to be used.

import socket
import time
import mido
from midi_over_lan import MidiMessagePacket, MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(interface_ip))
    message = mido.Message('note_on', note=60, velocity=64)
    while True:
        packet = MidiMessagePacket()
        packet.device_name='example script'
        packet.midi_data=bytes(message.bytes())
        sock.sendto(packet.to_bytes(), (MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER))
        time.sleep(3)
```

Client:

```python
#!/usr/bin/env python3

"""Minimal example of a MIDI over LAN client."""

import socket
import struct
import mido
from midi_over_lan import Packet, MidiMessagePacket, MULTICAST_GROUP_ADDRESS, MULTICAST_PORT_NUMBER

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
```

Possible console output:

```
$ python minimal_example_client.py
note_on channel=0 note=60 velocity=64 time=0
note_on channel=0 note=60 velocity=64 time=0
note_on channel=0 note=60 velocity=64 time=0
note_on channel=0 note=60 velocity=64 time=0
note_on channel=0 note=60 velocity=64 time=0
note_on channel=0 note=60 velocity=64 time=0
...
```


## Sample Programs

The repository includes sample programs to help you get started with using the library.



## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.



## License

This project is licensed under the GNU Lesser General public license.
