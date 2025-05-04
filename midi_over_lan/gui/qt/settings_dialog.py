# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Settings dialog of the main window."""

# The settings dialog is based on the Qt Designer file 'settings_dialog.ui'.
# The file is generated from the Qt Designer file using either of the commands:
#   pyside6-uic .\settings_dialog.ui -o ui_settings_dialog.py
#   poetry run pyside6-uic .\settings_dialog.ui -o ui_settings_dialog.py

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=no-member
# pylint: disable=c-extension-no-member
# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=logging-fstring-interpolation

import logging
import multiprocessing
import socket

from PySide6.QtWidgets import QDialog, QWidget, QMessageBox
from PySide6.QtCore import Qt

from midi_over_lan.worker_messages import Command, CommandMessage
from ui_settings_dialog import Ui_Settings


logger=logging.getLogger('midi_over_lan')  # pylint: disable=invalid-name


class SettingsDialog(QDialog, Ui_Settings):
    """Settings dialog for the GUI."""

    def __init__(self,
                 sender_queue: multiprocessing.Queue,
                 receiver_queue: multiprocessing.Queue,
                 result_queue: multiprocessing.Queue,
                 parent: QWidget = None):
        """Initialize the settings dialog."""
        super().__init__(parent=parent)
        self.setupUi(self)
        # self.setWindowTitle("Settings")
        self.sender_queue = sender_queue
        self.receiver_queue = receiver_queue
        self.result_queue = result_queue
        self.lineEdit_NetworkInterface.editingFinished.connect(self.update_network_interface)
        self.checkBox_EnableLoopback.stateChanged.connect(self.update_loopback)
        self.checkBox_SaveCpuTime.stateChanged.connect(self.update_save_cpu_time)
        self.lineEdit_NetworkInterface.setText(socket.gethostname())
        self.update_network_interface()


    def update_loopback(self, state: int):
        """Update the loopback state."""
        logger.debug('Update loopback.')
        # The state is either of type 'int' and 0 (unchecked) or 2 (checked),
        # or of type Qt.CheckState and Qt.Unchecked or Qt.Checked.
        if isinstance(state, int):
            state = bool(state)
        else:
            state = state == Qt.Checked
        self.sender_queue.put(CommandMessage(Command.SET_ENABLE_LOOPBACK_INTERFACE, state))


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
        self.sender_queue.put(CommandMessage(Command.SET_NETWORK_INTERFACE, ip_address))
        self.receiver_queue.put(CommandMessage(Command.SET_NETWORK_INTERFACE, ip_address))


    def update_save_cpu_time(self, state: int):
        """Update the save CPU time state."""
        logger.debug('Update save CPU time.')
        # The state is either of type 'int' and 0 (unchecked) or 2 (checked),
        # or of type Qt.CheckState and Qt.Unchecked or Qt.Checked.
        if isinstance(state, int):
            state = bool(state)
        else:
            state = state == Qt.Checked
        self.sender_queue.put(CommandMessage(Command.SET_SAVE_CPU_TIME, state))
        self.receiver_queue.put(CommandMessage(Command.SET_SAVE_CPU_TIME, state))
