# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Main Window of the GUI."""

# The main window is based on the Qt Designer file 'main_window.ui'.
# The file is generated from the Qt Designer file using either of the commands:
#   pyside6-uic .\main_window.ui -o ui_main_window.py
#   poetry run pyside6-uic .\main_window.ui -o ui_main_window.py

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=no-member
# pylint: disable=c-extension-no-member
# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=logging-fstring-interpolation
# pylint: disable=invalid-name

import logging
import multiprocessing
import time
from typing import List, Tuple

import mido
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHeaderView, QLabel, QMainWindow, QMessageBox, QTableWidgetItem

from midi_over_lan.worker_messages import Command, CommandMessage
from ui_main_window import Ui_MainWindow
from settings_dialog import SettingsDialog
from debug_messages_dialog import DebugMessagesDialog, LoggingHandler
from version import VERSION


logger=logging.getLogger('midi_over_lan')  # pylint: disable=invalid-name


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

    def __init__(self, sender_queue: multiprocessing.Queue, receiver_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
        """Initialize the main widget."""
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("MIDI over LAN")
        self.menubar.hide()
        self.sender_queue = sender_queue
        self.receiver_queue = receiver_queue
        self.result_queue = result_queue
        self.sender_paused = False
        self.receiver_paused = False
        self.input_ports: List[Tuple[bool, str, str]] = []  # List of tuples (active, device_name, network_name)

        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: green;\nborder: 1px solid gray;\nborder-radius: 10px;")

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

        # Set up the dialogs (preferences, debug messages dialog, etc.) now, as they are referenced below.
        self.setup_dialogs()

        ## Set up the menu bar.
        self.action_Quit.triggered.connect(self.close)
        self.action_Preferences.triggered.connect(self.show_settings_dialog)
        self.actionShow_Debug_Messages.triggered.connect(self.show_debug_messages_dialog)
        self.action_About.triggered.connect(lambda: QMessageBox.information(self, "About", f"MIDI over LAN\nVersion {VERSION}\n(c) 2025 Christoph Hänisch"))

        # Add global shortcuts.
        self.shortcut_Quit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_Quit.activated.connect(self.close)
        self.shortcut_Help = QShortcut(QKeySequence("F1"), self)
        self.shortcut_Help.activated.connect(lambda: QMessageBox.information(self, "About", f"MIDI over LAN\nVersion {VERSION}\n(c) 2025 Christoph Hänisch"))
        self.shortcut_Preferences = QShortcut(QKeySequence("Ctrl+P"), self)
        self.shortcut_Preferences.activated.connect(self.show_settings_dialog)
        self.shortcut_DebugMessagesDialog = QShortcut(QKeySequence("Ctrl+SHIFT+D"), self)
        self.shortcut_DebugMessagesDialog.activated.connect(self.show_debug_messages_dialog)

        # Add the input ports to the list.
        self.refresh_input_ports()

        # Initialization finished.
        self.statusbar.addWidget(QLabel("   Ready   "))



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
        self.sender_queue.put(CommandMessage(Command.PAUSE))
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
        self.sender_queue.put(CommandMessage(Command.RESTART))
        time.sleep(1)
        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: green;\nborder: 1px solid gray;\nborder-radius: 10px;")


    def resume_sending_process(self):
        """Resume the sending process."""
        logger.debug('Resume the sending process.')
        self.sender_queue.put(CommandMessage(Command.RESUME))
        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: green;\nborder: 1px solid gray;\nborder-radius: 10px;")


    def show_debug_messages_dialog(self):
        """Show the debug messages dialog."""
        logger.debug('Show debug messages dialog.')
        self.debug_messages_dialog.show()
        self.debug_messages_dialog.raise_()


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
        self.sender_queue.put(CommandMessage(Command.SET_MIDI_INPUT_PORTS, active_input_ports))


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

        # Set up the settings dialog
        self.settings_dialog = SettingsDialog(self.sender_queue, self.receiver_queue, self.result_queue, parent=self)
        self.settings_dialog.hide()

        # Set up the debug messages dialog
        self.debug_messages_dialog = DebugMessagesDialog()
        self.debug_messages_logging_handler = LoggingHandler(self.debug_messages_dialog)
        self.debug_messages_logging_handler.setLevel(logging.DEBUG)
        root = logging.getLogger()
        root.addHandler(self.debug_messages_logging_handler)



    def stop_sending_process(self):
        """Stop the sending process."""
        logger.debug('Stop the sending process.')
        self.sender_queue.put(CommandMessage(Command.STOP))
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
        self.sender_queue.put(CommandMessage(Command.SET_IGNORE_MIDI_CLOCK, state))


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
