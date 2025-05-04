# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Settings dialog of the main window."""

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
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QTextEdit


logger=logging.getLogger('midi_over_lan')  # pylint: disable=invalid-name


class DebugMessagesDialog(QDialog):
    """Debug message window for the GUI."""

    def __init__(self, parent: QWidget = None):
        """Initialize the debug message window."""
        super().__init__(parent=parent)
        self.setWindowTitle("Debug Messages")
        self.setGeometry(0, 0, 1000, 800)
        self.layout = QVBoxLayout(self)
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.append("Debug messages:\n")
        self.layout.addWidget(self.textEdit)
        self.setLayout(self.layout)

    def add_message(self, message: str):
        """Add a message to the debug message window."""
        self.textEdit.append(message)
        # self.textEdit.verticalScrollBar().setValue(self.textEdit.verticalScrollBar().maximum())


class LoggingHandler(logging.Handler):
    """A custom logging handler that sends all log messages to the debug message dialog."""

    def __init__(self, debug_messages_dialog: DebugMessagesDialog):
        """Initialize the handler with the given Qt widget."""
        super().__init__()
        self.debug_messages_dialog = debug_messages_dialog

    def emit(self, record):
        """Emit a log record to the Qt widget."""
        log_entry = self.format(record)
        if record.levelno < 10:  # NOTSET
            text_color = "black"
        elif record.levelno < 20:  # DEBUG
            text_color = "blue"
        elif record.levelno < 30:  # INFO
            text_color = "green"
        elif record.levelno < 40:  # WARNING
            text_color = "orange"
        elif record.levelno < 50:  # ERROR
            text_color = "red"
        else:  # CRITICAL
            text_color = "purple"
        log_entry = f'<font color="{text_color}">{record.asctime} - {record.levelname} - {record.module} - line {record.lineno} - {record.message}</font>'
        self.debug_messages_dialog.add_message(log_entry)
