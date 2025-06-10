# MIDI over LAN

MIDI over LAN (protocol, Python library, GUI client, ...)



## Overview

MIDI-over-LAN is a Python library that defines and implements a protocol for sending MIDI messages over a network. The project includes sample programs to demonstrate its usage as well as a fully-fledged GUI client.



## Features

### Protocol

- Sends MIDI messages over the network using UDP packets (connectionless
  protocol).
- Low latency protocol and thus real-time capable.
- Zero-configuration on the end-user side.
- Round-trip times less than a millisecond are possible (even in Python). Higher
  round-trip times measured in the current implementation often stem from the
  limitation of the thread scheduler of the underlying operating system. Modern
  operating systems often have resolutions in the range of 1 ms (Linux, Windows
  11) but the resolution can be up to 10 ms - 15 ms (Windows 10).
- Hosts see all MIDI messages of every MIDI over LAN client; filtering is
  done in the application (see GUI client).
- The network MIDI messages include the raw MIDI data, the sending host, and the
  MIDI device names which allows for easy filtering.
- The protocol support computing round-trip times between hosts using hello
  packets.


### GUI-Client

- Auto-discovery of MIDI network devices (according to the MIDI over LAN
  protocol).
- Only user-selected local MIDI devices are sent into the network.
- Routing matrix for mapping network MIDI devices to local MIDI output ports.
- Loopback network interfaces are supported which allows to route local MIDI
  devices (i.e., local MIDI input ports to local MIDI output ports).
- Statistics of round-trip times along with a graphical representation.
- Debug console.

<img src="./pics/GUI 01.png" alt="MIDI over LAN GUI - Outgoing Traffic" width="500">
<img src="./pics/GUI 02.png" alt="MIDI over LAN GUI - Routing Matrix" width="500">
<img src="./pics/GUI 03.png" alt="MIDI over LAN GUI - Statistics" width="500">
<img src="./pics/GUI 06.png" alt="MIDI over LAN GUI - Debug Console" width="500">



## Installation

To install the library, use pip:

```bash
pip install midi-over-lan
```

**TODO:** The package still needs to be uploaded to the Python Package Index (PyPI). 

#### Current installation:

Installation of `pipx` and `poetry` using Python 3.12:

```shell
py.exe -3.12 -m pip install --upgrade pip
py.exe -3.12 -m pip install --user pipx
py.exe -3.12 -m pipx install poetry
```

You might want to put `pipx` in your search path for executable: `pipx ensure path`.

Note, `poetry` might be installed in `C:\Users\<user name>\pipx\venvs\poetry\Scripts\`.


Installation of `MIDI-over-LAN`:

```shell
git clone https://github.com/Haenisch/MIDI-over-LAN.git
cd MIDI-over-LAN
poetry config virtualenvs.in-project true
poetry env use 3.12
poetry install
```

If `poetry env use 3.12` fails, you might want to try `poetry env use C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe` or similar with a hard-coded path to the Python 3.12 installation.

Run the GUI client:

```shell
poetry run python .\midi_over_lan\gui\qt\main.py
```



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
