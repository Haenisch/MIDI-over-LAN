#!/usr/bin/env python3

# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""MIDI over LAN GUI client.

The GUI client is a simple "MIDI over LAN" application that allows you to
select the MIDI input ports that you want to send over the network and the
MIDI input ports that you want to receive from the network.

The GUI has four sections:

    1. Outgoing Traffic: A list of local MIDI input ports that you want to send
       over the network.

    2. Incoming Traffic: A list of MIDI input ports that you received from the
       network and bind to local MIDI output ports.

    3. Statistics: Round-trip time statistics between various hosts.

    4. About: Information about the application.

By default, the device names shown on the network are the same as the device
names on the local machine. However, you can change the network name to
something more meaningful.
"""

VERSION = "1.0"

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=no-member
# pylint: disable=c-extension-no-member
# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=logging-fstring-interpolation

# The GUI is implemented using the PySide6 library, which is a Python binding, and
# uses the Qt Designer to design the layout of the application.
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

import logging
import multiprocessing
import os.path
import re
import socket
import sys
import threading
import time
from typing import List, Tuple

import mido
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QDialog, QHeaderView, QLabel, QMainWindow, QMessageBox, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget
import midi_over_lan.logging_setup
from midi_over_lan.midi_sender import MidiSender
from midi_over_lan.midi_receiver import MidiReceiver
from midi_over_lan.worker_messages import Command, CommandMessage, ResultMessage

# To generate the python file from the ui file, run either of the following commands:
# pyside6-uic .\MainWindow.ui -o MainWindow.py
# poetry run pyside6-uic .\MainWindow.ui -o MainWindow.py
from MainWindow import Ui_MainWindow
from SettingsDialog import Ui_Settings


# Create queues for communication between the GUI and the worker processes
sender_queue = multiprocessing.Queue()  # Queue for sending commands to the sender process
receiver_queue = multiprocessing.Queue()  # Queue for sending commands to the receiver process
result_queue = multiprocessing.Queue()  # Queue for receiving results from the sender and receiver processes


# Setup the logger

class JsonLinesFormatter(logging.Formatter):
    """A custom JSON line formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON line."""
        # From record.filename, extract only the file name without the path.
        filename = os.path.basename(record.filename)
        message = record.getMessage().replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        output_string = f'{{"asctime": "{self.formatTime(record, self.datefmt)}",' \
                        f'"filename": "{filename}",' \
                        f'"funcName": "{record.funcName}",' \
                        f'"levelname": "{record.levelname}",' \
                        f'"levelno": "{record.levelno}",' \
                        f'"lineno": "{record.lineno}",' \
                        f'"message": "{message}",' \
                        f'"module": "{record.module}",' \
                        f'"msecs": "{record.msecs}",' \
                        f'"name": "{record.name}",' \
                        f'"process": "{record.process}",' \
                        f'"processName": "{record.processName}",' \
                        f'"thread": "{record.thread}",' \
                        f'"threadName": "{record.threadName}",' \
                        f'"taskName": "{record.taskName}"}}'
                        # f'"pathname": "{record.pathname}",' \
        return output_string


jsonl_handler = logging.handlers.RotatingFileHandler("log messages.jsonl", encoding="utf-8", maxBytes=1000000, backupCount=5)
jsonl_handler.setFormatter(JsonLinesFormatter())
jsonl_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(levelname)s  %(module)-15s  line %(lineno)-4d  %(message)s')

# root = logging.getLogger()
# root.addHandler(jsonl_handler)

logger = logging.getLogger("MIDI over LAN GUI")
logger.setLevel(logging.DEBUG)


# Create a queue for the log messages. The log_queue has a maximum size of 1000
# messages. If the queue is full, the worker processes will block until the main
# process has processed some log messages. Thus, the logger_thread should be
# created as early as possible.
log_queue = multiprocessing.Queue(maxsize=1000)


def is_input_port_in_use(port_name: str) -> bool:
    """Check if a MIDI input port is already open."""
    try:
        with mido.open_input(port_name):  # pylint: disable=no-member
            return False  # if the port can be opened, it is not open
    except IOError:
        # in case of an IOError, the port is probably already open
        return True


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main widget for the GUI."""

    def __init__(self):
        """Initialize the main widget."""
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("MIDI over LAN")
        self.menubar.hide()
        self.input_ports: List[Tuple[bool, str, str]] = []  # List of tuples (active, device_name, network_name)
        self.sender = MidiSender(sender_queue, receiver_queue, result_queue, log_queue)
        self.sender_paused = False
        self.receiver = MidiReceiver(sender_queue, receiver_queue, result_queue, log_queue)
        self.run_sending_process()
        self.run_receiving_process()

        # Set up the table widget.
        self.tableWidget_LocalInputPorts.clearSelection()
        self.tableWidget_LocalInputPorts.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_LocalInputPorts.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget_LocalInputPorts.setSortingEnabled(False)
        self.tableWidget_LocalInputPorts.itemClicked.connect(self.toggle_active_input_port)
        self.tableWidget_LocalInputPorts.itemChanged.connect(self.update_network_names)

        # Connect the GUI elements to the functions.
        self.pushButton_LocalInputPorts_SelectAll.clicked.connect(self.select_all_input_ports)
        self.pushButton_LocalInputPorts_UnselectAll.clicked.connect(self.unselect_all_input_ports)
        self.pushButton_LocalInputPorts_Refresh.clicked.connect(self.refresh_input_ports)
        self.pushButton_OutgoingTraffic_Restart.clicked.connect(self.restart_sending_process)
        self.pushButton_OutgoingTraffic_PauseResume.clicked.connect(self.pause_and_resume_sending_process)
        self.checkBox_OutgoingTraffic_IgnoreMidiClock.stateChanged.connect(self.update_midi_clock_handling)

        # Set up the dialogs (preferences, help, etc.) now, as they are referenced below.
        self.setup_dialogs()

        ## Set up the menu bar.
        self.action_Quit.triggered.connect(self.close)
        self.action_Preferences.triggered.connect(self.show_settings_dialog)
        self.action_About.triggered.connect(lambda: QMessageBox.information(self, "About", f"MIDI over LAN\nVersion {VERSION}\n(c) 2025 Christoph Hänisch"))

        # Add global shortcuts.
        self.shortcut_Quit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_Quit.activated.connect(self.close)
        self.shortcut_Help = QShortcut(QKeySequence("F1"), self)
        self.shortcut_Help.activated.connect(lambda: QMessageBox.information(self, "About", f"MIDI over LAN\nVersion {VERSION}\n(c) 2025 Christoph Hänisch"))
        self.shortcut_Preferences = QShortcut(QKeySequence("Ctrl+P"), self)
        self.shortcut_Preferences.activated.connect(self.settings_dialog.show)

        # Add the input ports to the list.
        self.refresh_input_ports()

        # Initialization finished.
        self.statusbar.addWidget(QLabel("   Ready   "))


    def __del__(self):
        """Delete the main widget."""
        # Stop the worker processes and wait for them to finish
        sender_queue.put(CommandMessage(Command.STOP))
        self.sender.join()
        receiver_queue.put(CommandMessage(Command.STOP))
        self.receiver.join()


    def add_input_port(self, active: bool, device_name: str, network_name: str):
        """Add the given input port to the table widget and to the internal list of input ports."""
        logger.debug(f"Add input port: {device_name} ({network_name})")
        # Skip if the port is already in the list.
        for port in self.input_ports:
            if port[1] == device_name:
                return
        self.input_ports.append((active, device_name, network_name))
        self.tableWidget_LocalInputPorts.setRowCount(len(self.input_ports))
        row = len(self.input_ports) - 1
        item = QTableWidgetItem(device_name)
        item.setCheckState(Qt.Checked if active else Qt.Unchecked)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
        self.tableWidget_LocalInputPorts.setItem(row, 0, item)
        self.tableWidget_LocalInputPorts.setItem(row, 1, QTableWidgetItem(network_name))
        if is_input_port_in_use(device_name):
            logger.debug(f"Port {device_name} is already in use.")
            item.setForeground(Qt.red)
            item.setToolTip("The input port is already in use by another application.")


    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        """Handle key press events. In particular, show the menu bar when the Alt key is pressed."""
        if event.key() == Qt.Key_Alt:
            self.menubar.show()


    def keyReleaseEvent(self, event):  # pylint: disable=invalid-name
        """Handle key release events. In particular, hide the menu bar when the Alt key is released."""
        if event.key() == Qt.Key_Alt:
            self.menubar.hide()


    def pause_sending_process(self):
        """Pause the sending process."""
        logger.debug('Pause the sending process.')
        sender_queue.put(CommandMessage(Command.PAUSE))
        # Set the style sheet of the label to indicate that the server is paused.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: red;\nborder: 1px solid gray;\nborder-radius: 10px;")


    def pause_and_resume_sending_process(self):
        """Pause or resume the sending process."""
        logger.debug('Pause or resume the sending process.')
        if self.sender_paused:
            self.resume_sending_process()
            self.sender_paused = False
        else:
            self.pause_sending_process()
            self.sender_paused = True


    def refresh_input_ports(self):
        """Refresh the list of internal input ports."""
        logger.debug('Refresh the list of input ports.')
        self.tableWidget_LocalInputPorts.clearContents()
        self.input_ports = []
        for input_port in mido.get_input_names():
            input_port = input_port.split(':')[0]
            self.add_input_port(False, input_port, input_port)


    def restart_sending_process(self):
        """Restart the processing loop of the sending process."""
        logger.debug('Restart the sending process.')
        # Set the style sheet of the label to indicate that the server is shut down.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: red;\nborder: 1px solid gray;\nborder-radius: 10px;")
        self.repaint()
        sender_queue.put(CommandMessage(Command.RESTART))
        time.sleep(1)
        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: green;\nborder: 1px solid gray;\nborder-radius: 10px;")


    def resume_sending_process(self):
        """Resume the sending process."""
        logger.debug('Resume the sending process.')
        sender_queue.put(CommandMessage(Command.RESUME))
        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: green;\nborder: 1px solid gray;\nborder-radius: 10px;")


    def run_receiving_process(self):
        """Start the sending process."""
        logger.debug('Start the receiving process.')
        self.receiver.start()


    def run_sending_process(self):
        """Start the sending process."""
        logger.debug('Start the sending process.')
        self.sender.start()
        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: green;\nborder: 1px solid gray;\nborder-radius: 10px;")


    def show_settings_dialog(self):
        """Show the settings dialog."""
        logger.debug('Show settings dialog.')
        self.settings_dialog.show()
        self.settings_dialog.raise_()


    def send_input_ports_to_worker_process(self):
        """Send the list of active input ports to the sender process."""
        logger.debug('Send input ports to the worker process.')
        # The worker process expects a list of tuples (device_name, network_name).
        # Note, that the active state is not used here (cf. the definition of
        # self.input_ports). Thus, we filter the list accordingly and send only
        # the desired format.
        active_input_ports = [(item[1], item[2]) for item in self.input_ports if item[0]]
        sender_queue.put(CommandMessage(Command.SET_MIDI_INPUT_PORTS, active_input_ports))


    def select_all_input_ports(self):
        """Select all input ports."""
        logger.debug('Select all input ports.')
        for row in range(self.tableWidget_LocalInputPorts.rowCount()):
            item = self.tableWidget_LocalInputPorts.item(row, 0)
            self.input_ports[row] = (True, self.input_ports[row][1], self.input_ports[row][2])
            item.setCheckState(Qt.Checked)
        self.send_input_ports_to_worker_process()


    def setup_dialogs(self):
        """Setup the settings dialog and the help/about dialog."""
        logger.debug('Setup the dialogs.')
        self.settings_dialog = SettingsDialog(parent=self)
        # self.help_dialog = HelpDialog(parent=self)
        # self.about_dialog = AboutDialog(parent=self)
        

    def stop_sending_process(self):
        """Stop the sending process."""
        logger.debug('Stop the sending process.')
        sender_queue.put(CommandMessage(Command.STOP))
        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: red;\nborder: 1px solid gray;\nborder-radius: 10px;")


    def toggle_active_input_port(self, item: QTableWidgetItem):
        """Toggle the active state of the input port."""
        logger.debug('Toggle active input port.')
        row = item.row()
        column = item.column()
        if column == 0:
            device_name = self.input_ports[row][1]
            network_name = self.input_ports[row][2]
            item = self.tableWidget_LocalInputPorts.item(row, 0)
            if item.checkState() == Qt.Checked:
                self.input_ports[row] = (False, device_name, network_name)
                item.setCheckState(Qt.Unchecked)
            else:
                self.input_ports[row] = (True, device_name, network_name)
                item.setCheckState(Qt.Checked)
            self.send_input_ports_to_worker_process()


    def unselect_all_input_ports(self):
        """Unselect all input ports."""
        logger.debug('Unselect all input ports.')
        for row in range(self.tableWidget_LocalInputPorts.rowCount()):
            self.input_ports[row] = (False, self.input_ports[row][1], self.input_ports[row][2])
            item = self.tableWidget_LocalInputPorts.item(row, 0)
            item.setCheckState(Qt.Unchecked)
        self.send_input_ports_to_worker_process()


    def update_midi_clock_handling(self, state: int):
        """Update the ignore MIDI clock state."""
        logger.debug('Update MIDI clock handling.')
        # The state is either of type 'int' and 0 (unchecked) or 2 (checked),
        # or of type Qt.CheckState and Qt.Unchecked or Qt.Checked.
        if isinstance(state, int):
            state = bool(state)
        else:
            state = state == Qt.Checked
        sender_queue.put(CommandMessage(Command.SET_IGNORE_MIDI_CLOCK, state))


    def update_network_names(self, item: QTableWidgetItem):
        """Update the device name alias / network name of the input port."""
        logger.debug('Update network names of the input ports.')
        row = item.row()
        column = item.column()
        if column == 1:
            active = self.input_ports[row][0]
            device_name = self.input_ports[row][1]
            network_name = item.text()
            self.input_ports[row] = (active, device_name, network_name)
            self.send_input_ports_to_worker_process()


class SettingsDialog(QDialog, Ui_Settings):
    """Settings dialog for the GUI."""

    def __init__(self, parent: QWidget = None):
        """Initialize the settings dialog."""
        super().__init__(parent=parent)
        self.setupUi(self)
        self.lineEdit_NetworkInterface.editingFinished.connect(self.update_network_interface)
        self.checkBox_EnableLoopback.stateChanged.connect(self.update_loopback)
        self.checkBox_SaveCpuTime.stateChanged.connect(self.update_save_cpu_time)
        self.lineEdit_NetworkInterface.setText(socket.gethostname())
        self.hide()


    def update_loopback(self, state: int):
        """Update the loopback state."""
        logger.debug('Update loopback.')
        # The state is either of type 'int' and 0 (unchecked) or 2 (checked),
        # or of type Qt.CheckState and Qt.Unchecked or Qt.Checked.
        if isinstance(state, int):
            state = bool(state)
        else:
            state = state == Qt.Checked
        sender_queue.put(CommandMessage(Command.SET_ENABLE_LOOPBACK_INTERFACE, state))


    def update_network_interface(self):
        """Update the network interface."""
        logger.debug('Update network interface.')
        text = self.lineEdit_NetworkInterface.text()
        # Check if the text is a valid hostname or a valid IPv4 address in dot-decimal notation.
        try:
            ip_address = socket.gethostbyname(text)
        except socket.gaierror:
            # If the hostname cannot be resolved, try to get the IP address of the local host.
            try:
                ip_address = socket.gethostbyname(socket.gethostname())
            except socket.gaierror:
                ip_address = '127.0.0.1'  # fallback to localhost
            logger.warning(f"Invalid network interface: {text} Use {ip_address} instead.")
            QMessageBox.warning(self, "Invalid network interface", "Invalid network interface: {text}")
            self.lineEdit_NetworkInterface.setText(ip_address)
        # Set the ip address used in the worker processes.
        sender_queue.put(CommandMessage(Command.SET_NETWORK_INTERFACE, ip_address))
        receiver_queue.put(CommandMessage(Command.SET_NETWORK_INTERFACE, ip_address))


    def update_save_cpu_time(self, state: int):
        """Update the save CPU time state."""
        logger.debug('Update save CPU time.')
        # The state is either of type 'int' and 0 (unchecked) or 2 (checked),
        # or of type Qt.CheckState and Qt.Unchecked or Qt.Checked.
        if isinstance(state, int):
            state = bool(state)
        else:
            state = state == Qt.Checked
        sender_queue.put(CommandMessage(Command.SET_SAVE_CPU_TIME, state))
        receiver_queue.put(CommandMessage(Command.SET_SAVE_CPU_TIME, state))


class DebugMessagesWindow(QDialog):
    """Debug message window for the GUI."""

    def __init__(self, parent: QWidget = None):
        """Initialize the debug message window."""
        super().__init__(parent=parent)
        self.setWindowTitle("Debug Messages")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout(self)
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setGeometry(0, 0, 800, 600)
        self.textEdit.append("Debug messages:\n")
        self.layout.addWidget(self.textEdit)
        self.setLayout(self.layout)

    def add_message(self, message: str):
        """Add a message to the debug message window."""
        self.textEdit.append(message)
        self.textEdit.verticalScrollBar().setValue(self.textEdit.verticalScrollBar().maximum())


class DebugMessagesWindow_LoggingHandler(logging.Handler):
    """A custom logging handler that sends log messages to a Qt widget."""

    def __init__(self, debug_messages_window: DebugMessagesWindow):
        """Initialize the handler with the given Qt widget."""
        super().__init__()
        self.debug_messages_window = debug_messages_window

    def emit(self, record):
        """Emit a log record to the Qt widget."""
        log_entry = self.format(record)
        if record.levelno < 10:
            text_color = "black"
        elif record.levelno < 20:
            text_color = "blue"
        elif record.levelno < 30:
            text_color = "green"
        elif record.levelno < 40:
            text_color = "orange"
        elif record.levelno < 50:
            text_color = "red"
        else:
            text_color = "purple"
        log_entry = f'<font color="{text_color}">{record.asctime} - {record.levelname} - {record.module} - line {record.lineno} - {record.message}</font>'
        self.debug_messages_window.add_message(log_entry)


def main():
    """Main function."""
    logger_thread = threading.Thread(target=midi_over_lan.logging_setup.logger_thread, args=(log_queue,))
    logger_thread.start()

    app = QApplication(sys.argv)

    debug_messages_window = DebugMessagesWindow()
    debug_messages_window.show()
    debug_messages_window_logging_handler = DebugMessagesWindow_LoggingHandler(debug_messages_window)
    debug_messages_window_logging_handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(debug_messages_window_logging_handler)

    window = MainWindow()
    window.show()
    app.exec()

    log_queue.put(None)
    logger_thread.join()


if __name__ == "__main__":
    main()
