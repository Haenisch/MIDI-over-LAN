"""Small test script to receive MIDI messages from a pad controller using mido."""

import time
import mido


def test():
    inputs = mido.get_input_names()
    pad_name = inputs[1]  # does only work in my test setup
    print(f"Using MIDI input: {pad_name}")
    pad = mido.open_input(pad_name)

    while True:
        try:
            # Attempt to receive a message without blocking
            # This will raise BlockingIOError if no message is available
            # and allow us to handle it gracefully
            try:
                msg = pad.receive(block=False)
            except mido.BlockingIOError:
                continue

            if msg is None:
                time.sleep(0.01)  # Prevent busy waiting
                continue

            if msg.type == 'note_on':
                print(f"Note On: {msg.note} Velocity: {msg.velocity}")
            elif msg.type == 'note_off':
                print(f"Note Off: {msg.note} Velocity: {msg.velocity}")
            elif msg.type == 'control_change':
                print(f"Control Change: {msg.control} Value: {msg.value}")
            elif msg.type == 'program_change':
                print(f"Program Change: {msg.program}")
            elif msg.type == 'pitchwheel':
                print(f"Pitch Wheel: {msg.pitch}")
            elif msg.type == 'sysex':
                print(f"SysEx: {msg.data}")
            elif msg.type == 'clock':
                print("Clock received")
            elif msg.type == 'start':
                print("Start received")
            elif msg.type == 'stop':
                print("Stop received")
            elif msg.type == 'continue':
                print("Continue received")
            else:
                print(f"Unknown message type: {msg.type}")

            time.sleep(0.01)  # Prevent busy waiting

        except KeyboardInterrupt:
            print("Exiting...")
            break


if __name__ == "__main__":
    test()
