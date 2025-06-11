#!/usr/bin/env python3

# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""MIDI over LAN GUI client.

The GUI client is a simple "MIDI over LAN" application that allows you to select
the local MIDI ports that you want to send over the network and the remote MIDI
ports that you want to bind to your local MIDI ports. The remote MIDI ports are
provided by other MIDI over LAN applications running on the same network and
automatically discovered by the GUI client.
"""

# The GUI is implemented using PySide6. The wirdgets/dialogs are created using
# Qt Designer and the generated code is used in the application.
#
# There are two worker processes that run in the background:
#
#     1. The sender process sends MIDI messages over the network to the listening
#        hosts.
#
#     2. The receiver process receives MIDI messages from the network and sends
#        them to the specified local MIDI output ports.
#
# The sender and receiver processes are implemented using the multiprocessing
# library. The entire communication between the sender and receiver processes is
# done using the multiprocessing.Queue class. For possible commands and results,
# see the documentation of the sender and receiver classes and the
# worker_messages.py module, respectively.
#
# Logging is done using the standard Python logging module. The log messages
# are sent to a log queue, which is processed in a separate thread, thus allowing
# the worker processes to log messages much quicker and to reduce the latency.

# Note: All multiprocessing-related code -- including the creation of
#       multiprocessing.Queue() objects -- must be created in the main function
#       which is guarded by the "if __name__ == '__main__'" block. This is
#       necessary when packaging the application with PyInstaller or similar
#       tools, as it ensures that the multiprocessing module can correctly
#       spawn new processes.


# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=line-too-long


# Ensure that the multiprocessing module is initialized correctly when using
# PyInstaller or similar tools. This is necessary to avoid issues with process
# spawning on Windows and macOS.
import multiprocessing
multiprocessing.freeze_support()

import logging
import sys

from PySide6.QtWidgets import QApplication  # pylint: disable=no-name-in-module

from midi_over_lan.midi_sender import MidiSender
from midi_over_lan.midi_receiver import MidiReceiver
from midi_over_lan.worker_messages import Command, CommandMessage
from logging_setup import start_logger_thread, stop_logger_thread
from main_window import MainWindow

try:
    import mido
    import mido.backends.rtmidi  # pylint: disable=unused-import
    mido.set_backend('mido.backends.rtmidi', load=True)
except Exception:  # pylint: disable=broad-except
    print("Please install the required dependencies by running 'pip install python-rtmidi mido[ports-rtmidi]' in your shell.")
    sys.exit(1)


def main():
    """Main function."""

    # Create a queue for the log messages. The log_queue has a maximum size of
    # 10000 messages. If the queue is full, the worker processes will block
    # until the main process has processed some log messages. Thus, the
    # logger_thread should be created as early as possible.
    log_queue = multiprocessing.Queue(maxsize=10000)

    # Set up the logging system
    start_logger_thread(log_queue)
    logger = logging.getLogger('midi_over_lan')
    logger.setLevel(logging.DEBUG)

    # Create queues for communication between the GUI and the worker processes.
    sender_queue = multiprocessing.Queue()
    receiver_queue = multiprocessing.Queue()
    gui_queue = multiprocessing.Queue()

    # Start the sender and receiver processes
    logger.debug('Start the sending process.')
    sender = MidiSender(sender_queue, receiver_queue, gui_queue, log_queue)
    sender.start()
    logger.debug('Start the receiving process.')
    receiver = MidiReceiver(sender_queue, receiver_queue, gui_queue, log_queue)
    receiver.start()

    # Start the main GUI
    logger.debug('Start the GUI.')
    app = QApplication(sys.argv)
    window = MainWindow(sender_queue, receiver_queue, gui_queue)
    window.show()
    app.exec()

    # Stop all processes and the logger thread
    logger.debug('Waiting for the sender and receiver processes to finish.')
    sender_queue.put(CommandMessage(Command.STOP))
    receiver_queue.put(CommandMessage(Command.STOP))
    sender.join()
    receiver.join()
    stop_logger_thread(log_queue)


if __name__ == '__main__':
    main()
