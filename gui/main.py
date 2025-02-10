"""Test the Packet and MidiMessagePacket classes."""

import mido
from midi_over_lan import Packet, HelloPacket, HelloReplyPacket, MidiMessagePacket

print('Test 1')
packet = Packet.from_bytes(b'MIDI\x01\x00' + b'test' + b'\x00'*60 + b'\x90\x3C\x40')
print(packet)
print()

print('Test 2')
packet = Packet.from_bytes(b'\x90\x3C\x40')
packet.device_name = 'test'
print(packet)
print()

print('Test 3')
packet = MidiMessagePacket.from_bytes(b'\x90\x3C\x40')
packet.device_name = 'test'
print(packet)
print()

print('Test 4')
message = mido.Message('note_on', note=60, velocity=64)
packet = MidiMessagePacket(device_name='test', midi_data=bytes(message.bytes()))
print(packet)
print()

print('Test 5')
print(packet.to_bytes())
print()

print('Test 6')
print(MidiMessagePacket.from_bytes(packet.to_bytes()))
print()

print('Test 7')
print(MidiMessagePacket.from_bytes(b'\x90\x3C\x40'))
print()

print('Test 8')
print(MidiMessagePacket.from_bytes(b'MIDI\x01\x00\x90\x3C\x40'))
print()

print('Test 9')
print(MidiMessagePacket())
print()

print('Test 10')
print(HelloPacket())
print()

print('Test 11')
print(HelloReplyPacket())
print()
