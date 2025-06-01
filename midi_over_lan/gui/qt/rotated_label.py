# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""This module implements a label widget that is rotated by 90 degrees."""

# pylint: disable=invalid-name
# pylint: disable=no-name-in-module

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter


class RotatedLabel(QLabel):
    """A label that is rotated by 90 degrees anticlockwise."""

    def paintEvent(self, event):
        """Override the paint event to rotate the text."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(-90)  # Rotation um 90 Grad
        painter.translate(-self.height() / 2, -self.width() / 2)
        # Text im rotierten Rechteck zeichnen
        painter.drawText(0, 0, self.height(), self.width(), Qt.AlignLeft, self.text())


    def sizeHint(self):
        """Override the size hint to return the rotated size."""
        return self.size().transposed()


    def minimumSizeHint(self):
        """Override the minimum size hint to return the rotated size."""
        return self.sizeHint().transposed()
