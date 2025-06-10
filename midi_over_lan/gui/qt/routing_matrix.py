# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""This module implements a routing matrix for the MIDI over LAN GUI."""

# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=no-name-in-module


import logging
from math import hypot, degrees, radians, acos, sin, sqrt

from PySide6.QtCore import Qt, QRect, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QTransform
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QHeaderView, QLabel, QSizePolicy, QStackedWidget, QTableWidget, QWidget


logger = logging.getLogger("midi_over_lan.gui.routing_matrix")


class AngledHeader(QHeaderView):
    """This class implements a custom header for the routing table. The header
    is angled by 45 degrees to make the column labels more readable. The row
    labels are not angled, but they are bold and centered. The header is
    implemented using a QHeaderView, which is a part of the Qt framework. The
    header is painted using a QPainter, which allows for custom drawing of the
    header. The header is also clickable, allowing the end-user to select
    individual columns. The header is implemented using a custom class that
    inherits from QHeaderView.
    
    Courtesy of: https://stackoverflow.com/questions/57340852
    """

    borderPen = QColor(227, 227, 227)
    labelBrush = QColor("transparent")
    # labelBrush = QColor(254, 254, 254)


    def __init__(self, parent=None):
        """Initializes the AngledHeader class.
        
        The header is set to be clickable, and the default section size is set
        to the height of the font metrics. The maximum height of the header is
        set to 100 pixels. The font metrics are used to compute the size of the
        ellipsis, which is used to truncate the text in the header labels. The
        angle of the header is set to 45 degrees, and the shear transform is
        applied to the header to create the angled effect. The shear transform
        is applied using a QTransform, which allows for custom transformations
        of the header.
        """
        QHeaderView.__init__(self, Qt.Horizontal, parent)
        # self.setSectionResizeMode(self.ResizeMode.Fixed)
        self.setDefaultSectionSize(sqrt((self.fontMetrics().height() + 4)**2 *2))
        self.setSectionsClickable(True)
        self.setDefaultSectionSize(int(sqrt((self.fontMetrics().height() + 4)**2 *2)))
        self.setMaximumHeight(110)
        # compute the ellipsis size according to the angle; remember that:
        # 1. if the angle is not 45 degrees, you'll need to compute this value 
        #    using trigonometric functions according to the angle;
        # 2. we assume ellipsis is done with three period characters, so we can 
        #    "half" its size as (usually) they're painted on the bottom line and 
        #    they are large enough, allowing us to show as much as text is possible
        self.fontEllipsisSize = int(hypot(*[self.fontMetrics().height()] * 2) * .5)


    def sizeHint(self):
        """Computes the size hint for the header."""
        # compute the minimum height using the maximum header label "hypotenuse"'s
        hint = QHeaderView.sizeHint(self)
        count = self.count()
        if not count:
            return hint
        fm = self.fontMetrics()
        width = minSize = self.defaultSectionSize()
        # set the minimum width to ("hypotenuse" * sectionCount) + minimumHeight
        # at least, ensuring minimal horizontal scroll bar interaction
        hint.setWidth(width * count + self.minimumHeight())
        maxDiag = maxWidth = maxHeight = 1
        for s in range(count):
            if self.isSectionHidden(s):
                continue
            # compute the diagonal of the text's bounding rect, shift
            # its angle by 45° to get the minimum required height
            rect = fm.boundingRect(str(self.model().headerData(s, Qt.Horizontal)) + '    ')
            # avoid math domain errors for empty header labels
            diag = max(1, hypot(rect.width(), rect.height()))
            if diag > maxDiag:
                maxDiag = diag
                maxWidth = max(1, rect.width())
                maxHeight = max(1, rect.height())
        # get the angle of the largest boundingRect using the "Law of cosines":
        # https://en.wikipedia.org/wiki/Law_of_cosines
        angle = degrees(acos((maxDiag ** 2 + maxWidth ** 2 - maxHeight ** 2) / (2. * maxDiag * maxWidth)))
        # compute the minimum required height using the angle found above
        minSize = max(minSize, sin(radians(angle + 45)) * maxDiag)
        hint.setHeight(min(self.maximumHeight(), minSize))
        return hint


    def mousePressEvent(self, event):
        """Handles the mouse press event for the header."""
        width = self.defaultSectionSize()
        start = self.sectionViewportPosition(0)
        rect = QRect(0, 0, width, -self.height())
        transform = QTransform().translate(0, self.height()).shear(-1, 0)
        for s in range(self.count()):
            if self.isSectionHidden(s):
                continue
            if transform.mapToPolygon(rect.translated(s * width + start, 0)).containsPoint(event.position().toPoint(), Qt.WindingFill):
                self.sectionPressed.emit(s)
                return


    def paintEvent(self, event):
        """Handles the paint event for the header."""
        qp = QPainter(self.viewport())
        qp.setRenderHints(qp.RenderHint.Antialiasing)
        width = self.defaultSectionSize()
        delta = self.height()
        # add offset if the view is horizontally scrolled
        qp.translate(self.sectionViewportPosition(0) - .5, -.5)
        fmDelta = (self.fontMetrics().height() - self.fontMetrics().descent()) * .5
        # create a reference rectangle (note that the negative height)
        rect = QRectF(0, 0, width, -delta)
        diagonal = hypot(delta, delta)
        for s in range(self.count()):
            if self.isSectionHidden(s):
                continue
            qp.save()
            qp.save()
            qp.setPen(self.borderPen)
            # apply a "shear" transform making the rectangle a parallelogram;
            # since the transformation is applied top to bottom
            # we translate vertically to the bottom of the view
            # and draw the "negative height" rectangle
            qp.setTransform(qp.transform().translate(s * width, delta).shear(-1, 0))
            qp.drawRect(rect)
            qp.setPen(Qt.NoPen)
            qp.setBrush(self.labelBrush)
            qp.drawRect(rect)
            qp.restore()

            qp.translate(s * width + width, delta)
            qp.rotate(-45)
            label = str(self.model().headerData(s, Qt.Horizontal))
            elidedLabel = self.fontMetrics().elidedText(label, Qt.ElideRight, diagonal - self.fontEllipsisSize)
            qp.drawText(0, -fmDelta, elidedLabel)
            qp.restore()


class RoutingTable(QTableWidget):
    """A routing table that enables the end-user to select which output port is
    connected to which input port.

    This routing table is implemented using a QTableWidget, where each row
    represents an input port and each column represents an output port. The
    end-user can select multiple cells in the grid to indicate connections
    between outputs and inputs. Users of this class must provide the inputs and
    outputs as lists of strings, with each string representing the name of an
    input or output port.

    Whenever the end-user selects a cell, a `connections_changed()` signal is
    emitted. Connections are stored in dictionaries, where the keys can either
    be input ports or output ports, and the values are sets of the corresponding
    connected ports. Two dictionaries (`dict[str, set[str]]`) are passed along
    with the `connections_changed()` signal:

        - `outputs_to_inputs`:  Keys are output ports, and values are sets of
                                input ports connected to each specific output
                                port (i.e., connections from output ports to
                                input ports from the perspective of the output
                                ports).

        - `inputs_to_outputs`:  Keys are input ports, and values are sets of
                                output ports connected to each specific input
                                port (i.e., connections from output ports to
                                input ports from the perspective of the input
                                ports).

    It is guaranteed that a port name is a valid key in both dictionaries,
    yielding a set of connected ports. If a port has no connections, the set
    will be empty.

    The routing table is automatically updated when the list of input ports or
    output ports is changed. The class maintains the current connections,
    ensuring that connections are preserved even when the input or output port
    lists are modified.

    Public API:
    ===========

    Available methods:

        - `clear()`: Remove input and output port names (for the internal bookkeeping see function description).
        - `select_all()`: Select all checkboxes in the routing table.
        - `unselect_all()`: Unselect all checkboxes in the routing table.
        - `set_input_ports(names: List[str])`: Set the names of the input ports.
        - `set_output_ports(names: List[str])`: Set the names of the output ports.

    Available signals:
        - `connections_changed(outputs_to_inputs: dict[str, list[str]], inputs_to_outputs: dict[str, list[str]])`: 
            Emitted when the connections are changed (as described above).
    """

    connections_changed = Signal(dict, dict)  # Signal to notify about connection changes


    def __init__(self, parent=None, output_port_names:list[str]|None=None, input_port_names:list[str]|None=None):
        """Initialize the RoutingMatrix class.
        Args:
            parent: The parent widget for the routing table.
            output_port_names: A list of names for the output ports.
            input_port_names: A list of names for the input ports.
        """
        super().__init__(parent)
        self.output_port_names = [] if output_port_names is None else output_port_names
        self.input_port_names = [] if input_port_names is None else input_port_names
        self.outputs_to_inputs: dict[str, set[str]] = {}
        self.inputs_to_outputs: dict[str, set[str]] = {}
        self.connections_bookkeeping: dict[str, set[str]] = {}  # used to restore formerly deleted connections; dict is never cleared, keys may be updated
        self.clear_bookkeeping_and_setup_dictionaries()

        # Set up the table widget
        self.setHorizontalHeader(AngledHeader(self))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignRight)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.rebuild_table()


    def clear(self, keep_internal_bookkeeping:bool=True):
        """Remove input and output port names.
        
        If `keep_internal_bookkeeping` is True, the internal bookkeeping
        dictionary is not cleared, allowing the restoration of previously
        established connections. If False, the internal bookkeeping is cleared
        and the routing table is reset to an empty state.

        The `connections_changed` signal is emitted with the current state of
        the `outputs_to_inputs` and `inputs_to_outputs` dictionaries, which will
        be empty after clearing the routing table.
        """

        logger.debug("Clearing the routing table")

        if keep_internal_bookkeeping:
            # Clear the output and input port names, but keep the bookkeeping
            self.output_port_names.clear()
            self.input_port_names.clear()
            self.rebuild_table()
        else:
            # Clear the output and input port names, and also clear the bookkeeping
            self.clear_bookkeeping_and_setup_dictionaries()
            self.output_port_names.clear()
            self.input_port_names.clear()
            self.rebuild_table()

        self.connections_changed.emit(self.outputs_to_inputs, self.inputs_to_outputs)


    def clear_bookkeeping_and_setup_dictionaries(self):
        """Clear the bookkeeping dictionary and set up the dictionaries storing the connections."""
        self.outputs_to_inputs.clear()
        self.inputs_to_outputs.clear()
        for output_port in self.output_port_names:
            self.outputs_to_inputs[output_port] = set()
            if output_port not in self.connections_bookkeeping:
                self.connections_bookkeeping[output_port] = set()
        for input_port in self.input_port_names:
            self.inputs_to_outputs[input_port] = set()
        logger.debug("Cleared connections and set up dictionaries")
        # logger.debug("  outputs_to_inputs: %s", self.outputs_to_inputs)
        # logger.debug("  inputs_to_outputs: %s", self.inputs_to_outputs)


    def handle_checkbox_state_change(self, row, col, state):
        """Handle the state change of a checkbox in the routing table.
        
        This method updates the connections based on the state of the checkbox
        at the specified row and column. It emits the `connections_changed`
        signal with the updated connections.
        
        Args:
            row: The row index of the checkbox.
            col: The column index of the checkbox.
            state: The new state of the checkbox (checked, unchecked, or indeterminate).
        """

        logger.debug("Checkbox state changed at row %d, col %d: %s", row, col, state)

        input_port = self.input_port_names[row]
        output_port = self.output_port_names[col]

        if state == Qt.CheckState.Checked:
            # Add connection
            self.outputs_to_inputs[output_port].add(input_port)
            self.inputs_to_outputs[input_port].add(output_port)
            self.connections_bookkeeping[output_port].add(input_port)
        else:
            # Remove connection
            self.outputs_to_inputs[output_port].remove(input_port)
            self.inputs_to_outputs[input_port].remove(output_port)
            self.connections_bookkeeping[output_port].remove(input_port)

        # Emit signal with updated connections
        self.connections_changed.emit(self.outputs_to_inputs, self.inputs_to_outputs)

        logger.debug("Updated connections")
        # logger.debug("  outputs_to_inputs: %s", self.outputs_to_inputs)
        # logger.debug("  inputs_to_outputs: %s", self.inputs_to_outputs)


    def rebuild_table(self):
        """Build up the routing table (i.e., the table with the header labels and checkboxes)."""
        logger.debug("Rebuilding routing table with %d input ports and %d output ports", len(self.input_port_names), len(self.output_port_names))

        super().clear()
        num_rows = len(self.input_port_names)
        num_cols = len(self.output_port_names)
        self.setRowCount(num_rows)
        self.setColumnCount(num_cols)
        for r in range(num_rows):
            for c in range(num_cols):
                checkbox = QCheckBox()
                checkbox.setTristate(False)
                checkbox.setChecked(False)
                checkbox.setStyleSheet("QCheckBox::indicator {width: 16px; height: 16px}")
                checkbox.checkStateChanged.connect(lambda state, row=r, col=c: self.handle_checkbox_state_change(row, col, state))
                cell_widget = QWidget()
                cell_widget.setMinimumWidth(32)  # or a bit more than indicator size
                layout = QHBoxLayout(cell_widget)
                layout.addWidget(checkbox)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(layout)
                self.setCellWidget(r, c, cell_widget)

        self.setHorizontalHeaderLabels(self.output_port_names)
        self.setVerticalHeaderLabels(self.input_port_names)

        self.restore_connections()


    def restore_connections(self):
        """Restore the connections from the bookkeeping dictionary."""
        logger.debug("Restoring connections from bookkeeping dictionary")

        # Update the outputs_to_inputs and inputs_to_outputs dictionaries
        for output_port, input_ports in self.connections_bookkeeping.items():
            if output_port not in self.outputs_to_inputs:
                continue  # Skip if the output port is not in the current output ports
            for input_port in input_ports:
                if input_port not in self.inputs_to_outputs:
                    continue  # Skip if the input port is not in the current input ports
                # Add the connection to both dictionaries
                self.outputs_to_inputs[output_port].add(input_port)
                self.inputs_to_outputs[input_port].add(output_port)

        # Update checkboxes based on restored connections
        for r, input_port in enumerate(self.input_port_names):
            for c, output_port in enumerate(self.output_port_names):
                checkbox = self.cellWidget(r, c).findChild(QCheckBox)
                if checkbox:
                    checkbox.blockSignals(True)
                    if output_port in self.outputs_to_inputs and input_port in self.outputs_to_inputs[output_port]:
                        checkbox.setChecked(True)
                    else:
                        checkbox.setChecked(False)
                    checkbox.blockSignals(False)


    def select_all(self):
        """Select all checkboxes in the routing table.

        The connections_changed signal is emitted with the current state of the
        outputs_to_inputs and inputs_to_outputs dictionaries, which will be
        populated with all connections after selecting all checkboxes.
        """
        logger.debug("Selecting all checkboxes")
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                checkbox = self.cellWidget(r, c).findChild(QCheckBox)
                if checkbox:
                    checkbox.blockSignals(True)
                    checkbox.setChecked(True)
                    checkbox.blockSignals(False)
        # Emit signal with updated connections
        self.connections_changed.emit(self.outputs_to_inputs, self.inputs_to_outputs)


    def set_input_ports(self, names:list[str], emit_signal:bool=True):
        """Set the names of the input ports.
        
        By default, the `emit_signal` parameter is set to True, which means that
        the `connections_changed` signal will be emitted after setting the input
        ports. If `emit_signal` is set to False, the signal will not be emitted.
        """
        if not isinstance(names, list):
            raise TypeError("Input ports must be a list of strings.")
        self.input_port_names = sorted(names)
        logger.debug("Input ports set to: %s", self.input_port_names)
        self.clear_bookkeeping_and_setup_dictionaries()
        self.rebuild_table()
        if emit_signal:
            self.connections_changed.emit(self.outputs_to_inputs, self.inputs_to_outputs)


    def set_output_ports(self, names:list[str], emit_signal:bool=True):
        """Set the names of the output ports.
        
        By default, the `emit_signal` parameter is set to True, which means that
        the `connections_changed` signal will be emitted after setting the output
        ports. If `emit_signal` is set to False, the signal will not be emitted.
        """
        if not isinstance(names, list):
            raise TypeError("Output ports must be a list of strings.")
        self.output_port_names = sorted(names)
        logger.debug("Output ports set to: %s", self.output_port_names)
        self.clear_bookkeeping_and_setup_dictionaries()
        self.rebuild_table()
        if emit_signal:
            self.connections_changed.emit(self.outputs_to_inputs, self.inputs_to_outputs)


    def unselect_all(self):
        """Unselect all checkboxes in the routing table.

        The connections_changed signal is emitted with the current state of the
        outputs_to_inputs and inputs_to_outputs dictionaries, which will be
        empty after unselecting all checkboxes.
        """
        logger.debug("Unselecting all checkboxes")
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                checkbox = self.cellWidget(r, c).findChild(QCheckBox)
                if checkbox:
                    checkbox.blockSignals(True)
                    checkbox.setChecked(False)
                    checkbox.blockSignals(False)
        # Emit signal with updated connections
        self.connections_changed.emit(self.outputs_to_inputs, self.inputs_to_outputs)


class RoutingMatrix(QStackedWidget):
    """The routing matrix is a table that enables the end-user to select which
    output ports are connected to which input ports.

    This widget is a simple wrapper around the `RoutingTable` class, providing
    a convenient way to display and manage MIDI routing connections in a GUI.
    The main difference from the `RoutingTable` is that it shows a message
    when there are no input or output ports available, instead of displaying an
    empty table. In addition, the class can be used as a toplevel widget as it
    inherits from `QStackedWidget`.

    Each row in the table represents an input port and each column represents an
    output port. The end-user can select multiple cells in the grid to indicate
    connections between outputs and inputs. The names of the input and output
    ports are provided as lists of strings when initializing the `RoutingMatrix`
    or by calling the `set_input_ports()` and `set_output_ports()` methods.

    Whenever the end-user selects a cell, a `connections_changed()` signal is
    emitted. Connections are stored in dictionaries, where the keys can either
    be input ports or output ports, and the values are sets of the corresponding
    connected ports. Two dictionaries (`dict[str, set[str]]`) are passed along
    with the `connections_changed()` signal:

        - `outputs_to_inputs`:  Keys are output ports, and values are sets of
                                input ports connected to each specific output
                                port (i.e., connections from output ports to
                                input ports from the perspective of the output
                                ports).

        - `inputs_to_outputs`:  Keys are input ports, and values are sets of
                                output ports connected to each specific input
                                port (i.e., connections from output ports to
                                input ports from the perspective of the input
                                ports).

    It is guaranteed that a port name is a valid key in both dictionaries,
    yielding a set of connected ports. If a port has no connections, the set
    will be empty.

    The routing matrix is automatically updated when the list of input ports or
    output ports is changed. The class maintains the current connections,
    ensuring that connections are preserved even when the input or output port
    lists are modified.

    Public API:
    ===========

    Available methods:

        - `clear()`: Remove input and output port names (for the internal bookkeeping see function description).
        - `select_all()`: Select all checkboxes in the routing table.
        - `unselect_all()`: Unselect all checkboxes in the routing table.
        - `set_input_ports(names: List[str])`: Set the names of the input ports.
        - `set_output_ports(names: List[str])`: Set the names of the output ports.

    Available signals:
        - `connections_changed(outputs_to_inputs: dict[str, list[str]], inputs_to_outputs: dict[str, list[str]])`: 
            Emitted when the connections are changed (as described above).
    """

    connections_changed = Signal(dict, dict)  # Signal to notify about connection changes

    def __init__(self, parent=None, output_port_names:list[str]|None=None, input_port_names:list[str]|None=None):
        """Initialize the RoutingMatrix class."""
        super().__init__(parent)

        # First widget is the routing table
        self.routing_table = RoutingTable(output_port_names=output_port_names, input_port_names=input_port_names)
        self.routing_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(self.routing_table)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.routing_table.connections_changed.connect(self.handle_connections_changed)

        # Second widget is a label indicating no input/output ports
        self.ports_missing_label = QLabel("No input and/or output ports available.")
        self.ports_missing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ports_missing_widget = QWidget()
        self.ports_missing_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ports_missing_widget.setLayout(QHBoxLayout())
        self.ports_missing_widget.layout().addWidget(self.ports_missing_label)
        self.ports_missing_widget.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addWidget(self.ports_missing_widget)

        self._update_displayed_widget()


    def _update_displayed_widget(self):
        """Show the table or the label based on the current input and output ports."""
        num_input_ports = len(self.routing_table.input_port_names)
        num_output_ports = len(self.routing_table.output_port_names)
        if num_input_ports > 0 and num_output_ports > 0:
            self.setCurrentWidget(self.routing_table)
        else:
            if num_input_ports > 0 and num_output_ports == 0:
                self.ports_missing_label.setText(
                    "No network devices (output ports) available.\n" \
                    "It may take a few seconds to discover any devices.\n\n\n" \
                    "Note: If you select local MIDI devices in the `Outgoing Traffic`\n" \
                    "tab and activate the loopback option in the settings, these\n" \
                    "devices will be listed as network devices in the routing matrix."
                )
            elif num_input_ports == 0 and num_output_ports > 0:
                self.ports_missing_label.setText(
                    "No local MIDI devices (input ports) available.\n" \
                    "Are any MIDI devices connected to your computer?"
                )
            else:
                self.ports_missing_label.setText(
                    "No input and/or output ports available.\n" \
                    "It may take a few seconds to discover any devices.\n\n\n" \
                    "Note: If you select local MIDI devices in the `Outgoing Traffic`\n" \
                    "tab and activate the loopback option in the settings, these\n" \
                    "devices will be listed as network devices in the routing matrix."
                )
            self.setCurrentWidget(self.ports_missing_widget)


    def clear(self, keep_internal_bookkeeping:bool=True):
        """Clear the routing matrix.
        
        If `keep_internal_bookkeeping` is True, the internal bookkeeping
        dictionary is not cleared, allowing the restoration of previously
        established connections. If False, the internal bookkeeping is cleared
        and the routing matrix is reset to an empty state.

        The `connections_changed` signal is emitted with the current state of
        the `outputs_to_inputs` and `inputs_to_outputs` dictionaries, which will
        be empty after clearing the routing table.
        """
        logger.debug("Clearing RoutingMatrix")
        self.routing_table.clear(keep_internal_bookkeeping)
        self._update_displayed_widget()


    def handle_connections_changed(self, outputs_to_inputs, inputs_to_outputs):
        """Handle the connections changed signal from the routing table."""
        logger.debug("Connections changed in RoutingMatrix")
        self.connections_changed.emit(outputs_to_inputs, inputs_to_outputs)


    def select_all(self):
        """Select all checkboxes in the routing table."""
        logger.debug("Selecting all checkboxes in RoutingMatrix")
        self.routing_table.select_all()


    def set_input_ports(self, names:list[str], emit_signal:bool=True):
        """Set the names of the input ports in the routing table.
        
        By default, the `emit_signal` parameter is set to True, which means that
        the `connections_changed` signal will be emitted after setting the input
        ports. If `emit_signal` is set to False, the signal will not be emitted.
        """
        logger.debug("Setting input ports in RoutingMatrix: %s", names)
        self.routing_table.set_input_ports(names, emit_signal)
        self._update_displayed_widget()


    def set_output_ports(self, names:list[str], emit_signal:bool=True):
        """Set the names of the output ports in the routing table.
        
        By default, the `emit_signal` parameter is set to True, which means that
        the `connections_changed` signal will be emitted after setting the output
        ports. If `emit_signal` is set to False, the signal will not be emitted.
        """
        logger.debug("Setting output ports in RoutingMatrix: %s", names)
        self.routing_table.set_output_ports(names, emit_signal)
        self._update_displayed_widget()


    def unselect_all(self):
        """Unselect all checkboxes in the routing table."""
        logger.debug("Unselecting all checkboxes in RoutingMatrix")
        self.routing_table.unselect_all()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QPushButton
    from PySide6.QtWidgets import QGridLayout, QSpacerItem, QFrame

    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    widget = QWidget()
    widget.setWindowTitle("RoutingTable Example")
    output_port_names = ['Output 1', 'Output 2', 'Output 3', 'Output 4']
    input_port_names = ['Input 1', 'Input 2', 'Input 3']
    routing_table = RoutingTable(output_port_names=output_port_names, input_port_names=input_port_names)
    routing_table.connections_changed.connect(
        lambda outputs, inputs: logger.debug("Connections changed:\n  Outputs to Inputs: %s\n  Inputs to Outputs: %s", outputs, inputs)
    )
    # routing_matrix.show()
    l = QHBoxLayout()
    l.addWidget(routing_table)
    l.setContentsMargins(0, 0, 0, 0)
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.Box)
    frame.setLayout(l)
    spacer_top = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
    spacer_bottom = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
    spacer_left = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
    spacer_right = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
    layout = QGridLayout(widget)
    layout.addItem(spacer_top, 0, 1, 1, 1)
    layout.addItem(spacer_bottom, 2, 1, 1, 1)
    layout.addItem(spacer_left, 1, 0, 1, 1)
    layout.addItem(spacer_right, 1, 2, 1, 1)
    layout.addWidget(frame, 1, 1, 1, 1)
    button = QPushButton("Configuration 1")
    button.clicked.connect(lambda: routing_table.set_output_ports(['Output 1', 'Output *']))
    layout.addWidget(button, 3, 1, 1, 1)
    button = QPushButton("Configuration 2")
    button.clicked.connect(lambda: routing_table.set_output_ports(['Output 1', 'Output 2', 'Output 3', 'Output 4']))
    layout.addWidget(button, 4, 1, 1, 1)
    widget.setLayout(layout)
    widget.resize(800, 600)
    widget.show()

    m = RoutingMatrix(input_port_names=['Input 1', 'Input 2', 'Input 3'], output_port_names=[])
    m.show()

    routing_matrix = RoutingMatrix(output_port_names=output_port_names, input_port_names=input_port_names)
    routing_matrix.setWindowTitle("Routing Matrix Example")
    routing_matrix.connections_changed.connect(
        lambda outputs, inputs: logger.debug("Routing Matrix Connections changed:\n  Outputs to Inputs: %s\n  Inputs to Outputs: %s", outputs, inputs)
    )
    routing_matrix.show()

    sys.exit(app.exec())
