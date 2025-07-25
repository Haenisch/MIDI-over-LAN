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
import platform
import time
from collections import deque
from functools import cache
from socket import gethostbyaddr, gethostname
from statistics import median
from typing import List, Tuple

import mido
from PySide6.QtCore import Qt, QTimerEvent
from PySide6.QtGui import QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import QHeaderView, QLabel, QMainWindow, QMessageBox, QTableWidgetItem

from midi_over_lan.worker_messages import Command, CommandMessage, Information, InfoMessage
from ui_main_window import Ui_MainWindow
from line_chart import LineChart
from version import VERSION
from debug_messages_dialog import DebugMessagesDialog, LoggingHandler
from settings_dialog import SettingsDialog


logger=logging.getLogger('midi_over_lan.gui')  # pylint: disable=invalid-name


##################################################################################################
# Helper functions
##################################################################################################

@cache
def get_hostname(string: str) -> str:
    """Get the hostname for the given string.

    The string can be either a hostname or an IPv4 address.
    """
    try:
        name = gethostbyaddr(string)[0]
    except Exception:  # pylint: disable=broad-except
        try:
            name = gethostname()
        except Exception:  # pylint: disable=broad-except
            name = 'unknown'
    return name


def is_input_port_in_use(port_name: str) -> bool:
    """Check if a MIDI input port is already open."""
    try:
        with mido.open_input(port_name):  # pylint: disable=no-member
            return False  # if the port can be opened, it is not open
    except IOError:
        # in case of an IOError, the port is probably already open
        return True


##################################################################################################
# Main Window
##################################################################################################

class MainWindow(QMainWindow, Ui_MainWindow):
    """Main widget for the GUI."""

    def __init__(self, sender_queue: multiprocessing.Queue, receiver_queue: multiprocessing.Queue, ui_queue: multiprocessing.Queue):
        """Initialize the main widget."""
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("MIDI over LAN")
        self.menubar.hide()
        self.sender_queue = sender_queue
        self.receiver_queue = receiver_queue
        self.ui_queue = ui_queue
        self.sender_paused = False
        self.receiver_paused = False
        self.input_ports: List[Tuple[bool, str, str]] = []  # List of tuples (active, device_name, network_name)
        self.local_output_ports: List[str] = []
        self.remote_midi_devices: dict[str, set[str]] = {}  # key is remote ip address or hostname; values are the user-defined network names of the remote MIDI devices
        self.routing_connections: dict[str, set[str]] = {}  # key is the network name of the MIDI device; values are the local output port names to which the MIDI data should be sent

        # Set the style sheet of the label to indicate that the server is running.
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet("background-color: green;\nborder: 1px solid gray;\nborder-radius: 10px;")

        # Set up the table widget.
        self.tableWidget_LocalInputPorts.clearSelection()
        self.tableWidget_LocalInputPorts.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_LocalInputPorts.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget_LocalInputPorts.itemClicked.connect(self.toggle_active_input_port)
        self.tableWidget_LocalInputPorts.setSortingEnabled(False)
        self.tableWidget_LocalInputPorts.itemChanged.connect(self.update_network_names)

        # Connect the GUI elements in the `Outgoing Traffic` tab to the functions.
        self.pushButton_LocalInputPorts_SelectAll.clicked.connect(self.select_all_input_ports)
        self.pushButton_LocalInputPorts_UnselectAll.clicked.connect(self.unselect_all_input_ports)
        self.pushButton_LocalInputPorts_Refresh.clicked.connect(self.refresh_input_ports)
        self.pushButton_OutgoingTraffic_Restart.clicked.connect(self.restart_sending_process)
        self.pushButton_OutgoingTraffic_PauseResume.clicked.connect(self.pause_and_resume_sending_process)
        self.checkBox_OutgoingTraffic_IgnoreMidiClock.stateChanged.connect(self.update_midi_clock_handling)

        # Set up routing matrix.
        self.stackedWidget_RoutingMatrix.connections_changed.connect(self.routing_matrix_connections_changed)

        # Connect the GUI elements in the `Incoming Traffic` tab to the functions.
        self.pushButton_RoutingMatrix_Clear.clicked.connect(self.clear_routing_matrix)
        self.pushButton_RoutingMatrix_SelectAll.clicked.connect(self.stackedWidget_RoutingMatrix.select_all)
        self.pushButton_RoutingMatrix_UnselectAll.clicked.connect(self.stackedWidget_RoutingMatrix.unselect_all)
        self.pushButton_RoutingMatrix_Refresh.clicked.connect(self.refresh_routing_matrix)

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

        # Determine input and output ports.
        self.refresh_input_ports()
        self.refresh_output_ports()
        self.refresh_routing_matrix()

        # Process the UI message queue every second.
        self.timer = self.startTimer(1000)  # 1000 ms
        self.timerEvent = self.process_ui_message_queue

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
            logger.info(f"Port {device_name} is already in use.")
            item.setForeground(Qt.red)
            item.setToolTip("The input port is already in use by another application.")


    def clear_routing_matrix(self):
        """Clear the routing matrix."""
        logger.debug('Clearing the routing matrix.')
        self.receiver_queue.put(CommandMessage(Command.CLEAR_STORED_REMOTE_MIDI_DEVICES))
        self.remote_midi_devices.clear()
        self.stackedWidget_RoutingMatrix.clear()
        self.refresh_routing_matrix()


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


    def process_ui_message_queue(self, event: QTimerEvent):
        """Process the UI message queue every second."""
        while not self.ui_queue.empty():
            message = self.ui_queue.get()
            if isinstance(message, InfoMessage):
                if message.info == Information.ROUND_TRIP_TIMES:
                    logger.debug('Got a message update for the round trip times.')
                    self.update_round_trip_times(message.data)
                    continue
                if message.info == Information.REMOTE_MIDI_DEVICES:
                    logger.debug('Got a message update for the remote MIDI devices.')
                    self.remote_midi_devices |= message.data  # merge the new remote MIDI devices with the existing ones
                    logger.debug(f"Remote MIDI devices: {self.remote_midi_devices}")
                    self.refresh_routing_matrix()
                    continue
            else:
                logger.warning(f"Unexpected or unknown message: {message}")


    def refresh_input_ports(self):
        """Refresh the list of internal input ports."""
        logger.debug('Refresh the list of input ports.')
        self.tableWidget_LocalInputPorts.clearContents()
        self.input_ports = []
        for input_port in mido.get_input_names():
            if platform.system() == 'Windows':
                input_port = input_port.split(':')[0]
            self.add_input_port(False, input_port, input_port)


    def refresh_output_ports(self):
        """Refresh the list of internal output ports."""
        logger.debug('Refresh the list of output ports.')
        self.local_output_ports.clear()
        for output_port in mido.get_output_names():
            self.local_output_ports.append(output_port.split(':')[0])


    def refresh_routing_matrix(self):
        """Update/refresh the routing matrix."""
        logger.debug('Refresh/update the routing matrix.')
        # Set up the routing matrix.
        # Note: Outputs are routed (i.e., sent) to inputs:
        #       (1) routing matrix's output port = remote/network device
        #       (2) routing matrix's input port = local output device / local output port

        # (1)
        remote_device_names = set()
        for device_names in self.remote_midi_devices.values():
            for device_name in device_names:
                remote_device_names.add(device_name)
        self.stackedWidget_RoutingMatrix.set_output_ports(list(remote_device_names))

        # (2)
        self.refresh_output_ports()  # Ensure the local output ports are up to date.
        self.stackedWidget_RoutingMatrix.set_input_ports(self.local_output_ports)


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


    def routing_matrix_connections_changed(self, outputs: dict[str, set[str]], inputs: dict[str, set[str]]):
        """Handle the connections changed signal from the routing matrix."""
        logger.debug(f'Routing matrix connections changed: {outputs}')
        self.routing_connections = outputs  # Update the routing connections.
        self.receiver_queue.put(InfoMessage(Information.ROUTING_INFORMATION, self.routing_connections))


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
        self.settings_dialog = SettingsDialog(self.sender_queue, self.receiver_queue, self.ui_queue, parent=self)
        self.settings_dialog.hide()

        # Set up the debug messages dialog
        self.debug_messages_dialog = DebugMessagesDialog()
        self.debug_messages_logging_handler = LoggingHandler(self.debug_messages_dialog)
        self.debug_messages_logging_handler.setLevel(logging.DEBUG)
        self.debug_messages_logging_handler.logRecordReceived.signal.connect(self.debug_messages_dialog.add_message, Qt.QueuedConnection)
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


    def update_round_trip_times(self, round_trip_times: dict[str, deque[float]]):
        """Update the round trip times in the table widget."""

        logger.debug('Update round trip times.')

        for ip_address, rtt in round_trip_times.items():
            hostname = get_hostname(ip_address)

            # Check if the hostname is already in the table widget.
            found = False
            for row in range(self.tableWidget_RTT.rowCount()):
                item = self.tableWidget_RTT.item(row, 0)
                if item is not None and item.text() == hostname:
                    found = True
                    break

            if not found:
                # Add a new row to the table widget.
                self.tableWidget_RTT.setRowCount(self.tableWidget_RTT.rowCount() + 1)
                row = self.tableWidget_RTT.rowCount() - 1
                self.tableWidget_RTT.setItem(row, 0, QTableWidgetItem(hostname))
                self.tableWidget_RTT.setItem(row, 1, QTableWidgetItem(""))
                self.tableWidget_RTT.setItem(row, 2, QTableWidgetItem(""))
                self.tableWidget_RTT.setItem(row, 3, QTableWidgetItem(""))
                self.tableWidget_RTT.setItem(row, 4, QTableWidgetItem(""))
                self.tableWidget_RTT.setItem(row, 5, QTableWidgetItem("Collecting data..."))

            # Update the existing row.
            minimum_value = min(rtt) * 1000
            maximum_value = max(rtt) * 1000
            median_value = median(rtt) * 1000
            average_value = sum(rtt) / len(rtt) * 1000
            item = self.tableWidget_RTT.item(row, 1)
            item.setText(f"{minimum_value:.2f}")
            item = self.tableWidget_RTT.item(row, 2)
            item.setText(f"{maximum_value:.2f}")
            item = self.tableWidget_RTT.item(row, 3)
            item.setText(f"{median_value:.2f}")
            item = self.tableWidget_RTT.item(row, 4)
            item.setText(f"{average_value:.2f}")
            item = self.tableWidget_RTT.item(row, 5)
            item.setText("")

            # Update the line chart.
            if len(rtt) >= 3:
                chart = LineChart()
                chart.set_line_color(QColor(50, 50, 50))
                chart.set_line_width(1)
                chart.set_points(list(enumerate(rtt)))
                self.tableWidget_RTT.setCellWidget(row, 5, chart)
