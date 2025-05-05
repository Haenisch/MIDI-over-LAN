# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Dialog for displaying the debug messages."""

# The debug messages dialog is based on the Qt Designer file 'debug_messages_dialog.ui'.
# The file is generated from the Qt Designer file using either of the following commands:
#   pyside6-uic .\debug_messages_dialog.ui -o .\ui_debug_messages_dialog.py
#   poetry run pyside6-uic .\debug_messages_dialog.ui -o .\ui_debug_messages_dialog.py

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
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QDialog, QWidget
from ui_debug_messages_dialog import Ui_DebugMessages


logger=logging.getLogger('midi_over_lan')  # pylint: disable=invalid-name


class DebugMessagesDialog(QDialog, Ui_DebugMessages):
    """Debug message window for the GUI."""

    def __init__(self, parent: QWidget = None):
        """Initialize the debug message window."""
        super().__init__(parent=parent)
        self.setupUi(self)
        self.radioButton_Info.setChecked(True)  # Set the default log level to INFO
        self.displayed_log_level = logging.INFO
        self.scroll_to_bottom = True
        self.textEdit_DebugMessages.append("Debug messages:\n")

        # Connect the GUI elements to the functions.
        self.radioButton_Debug.clicked.connect(lambda: self.set_loglevel(logging.DEBUG))
        self.radioButton_Info.clicked.connect(lambda: self.set_loglevel(logging.INFO))
        self.radioButton_Warning.clicked.connect(lambda: self.set_loglevel(logging.WARNING))
        self.radioButton_Error.clicked.connect(lambda: self.set_loglevel(logging.ERROR))
        self.radioButton_Critical.clicked.connect(lambda: self.set_loglevel(logging.CRITICAL))
        self.checkBox_ScrollToBottom.stateChanged.connect(self.set_scroll_to_bottom)


    @Slot(str)
    def add_message(self, record: logging.LogRecord):
        """Add a log message to the debug message window."""

        # Check if the log level is below the displayed log level.
        if record.levelno < self.displayed_log_level:
            return

        # Format the log message and add it to the text edit widget.
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

        # Add the log entry to the text edit widget.
        self.textEdit_DebugMessages.append(log_entry)
        if self.scroll_to_bottom:
            self.textEdit_DebugMessages.verticalScrollBar().setValue(self.textEdit_DebugMessages.verticalScrollBar().maximum())


    def set_loglevel(self, loglevel: int):
        """Set the log level of the debug message window."""
        self.displayed_log_level = loglevel


    def set_scroll_to_bottom(self, state: int):
        """Set the scroll to bottom state of the debug message window."""
        # The state is either of type 'int' and 0 (unchecked) or 2 (checked),
        # or of type Qt.CheckState and Qt.Unchecked or Qt.Checked.
        if isinstance(state, int):
            state = bool(state)
        else:
            state = state == Qt.Checked
        self.scroll_to_bottom = state


class SignalProxy(QObject):
    """A proxy class that emits LogRecords with Qt's signals and slots mechanism.
    
    This class is used to emit signals from the below logging handler to the Qt
    GUI. It is necessary because a) there is a name clash with the emit method
    of the logging.Handler class and b) the logging handler runs in a different
    thread and updating the GUI from a different thread is not allowed in Qt.
    """
    signal = Signal(logging.LogRecord)


class LoggingHandler(logging.Handler):
    """A custom logging handler that emits log messages via Qt signals.
    
    Note, the signal proxy member is used to emit the log messages to the Qt GUI
    (see SignalProxy for more details). The logRecordReceived signal must be
    connected to the add_message slot of the DebugMessagesDialog class.
    """

    def __init__(self, debug_messages_dialog: DebugMessagesDialog):
        """Initialize the handler with the given Qt widget."""
        super().__init__()
        self.debug_messages_dialog = debug_messages_dialog
        self.logRecordReceived = SignalProxy()

    def emit(self, record: logging.LogRecord):
        """Emit a log record to the Qt widget."""
        self.logRecordReceived.signal.emit(record)
