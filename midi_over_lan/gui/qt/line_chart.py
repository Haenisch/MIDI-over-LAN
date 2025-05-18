# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""LineChart class for displaying a line chart using PySide6 only."""

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=invalid-name

from typing import List, Tuple

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem


class LineChart(QGraphicsView):
    """LineChart class for displaying a line chart using PySide6 only.

    Points are added to the chart using the add_point method, and the chart is
    updated automatically. Alternatively, all points can be set at once using the
    set_points method. None values are ignored.

    The background color can be set using the set_background_color method (default
    is transparent), the line color can be set using the set_line_color method
    (default is black), and the line width can be set using the set_line_width
    method (default is 1). The chart is always scaled to fit the current view. The
    chart can be cleared using the clear method.
    """

    def __init__(self, parent=None):
        """Initialize the LineChart class."""
        super().__init__(parent)

        self.points: List[Tuple[float, float]] = []
        self.line_color = QColor(0, 0, 0)  # black
        self.line_width = 1
        self.background_color = QColor("transparent")

        self.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor("transparent"))
        self.setScene(QGraphicsScene(self))
        self.scene().views()[0].scale(1, -1)  # flip the view's y-axis

        self.set_background_color(self.background_color)
        self.set_line_color(self.line_color)
        self.set_line_width(self.line_width)


    def add_point(self, x: float = 0, y: float = 0):
        """Add a point to the chart. None values are ignored."""
        if x is None or y is None:
            return
        self.points.append((x, y))
        self.update_chart()


    def clear(self):
        """Clear the chart."""
        self.points = []
        self.update_chart()


    def set_background_color(self, color: QColor):
        """Set the background color of the chart."""
        self.background_color = color
        self.setBackgroundBrush(self.background_color)
        self.update_chart()


    def set_line_color(self, color: QColor):
        """Set the color of the line."""
        self.line_color = color
        self.update_chart()


    def set_line_width(self, width: float):
        """Set the width of the line."""
        self.line_width = width
        self.update_chart()


    def set_points(self, points: List[Tuple[float, float]]):
        """Set the points of the chart. None values are ignored."""
        self.points = [(x, y) for x, y in points if x is not None and y is not None]
        self.update_chart()


    def update_chart(self):
        """Update the chart with the current points."""
        self.scene().clear()

        if not self.points:
            return

        # Scale the y values to fit into the interval [0, 1]
        min_y = min(y for _, y in self.points)
        max_y = max(y for _, y in self.points)
        y_range = max_y - min_y
        if y_range == 0:
            y_range = 1
        for i, (x, y) in enumerate(self.points):
            y = (y - min_y) / y_range
            self.points[i] = (x, y)

        # Draw the line using QGraphicsPathItem
        path = QPainterPath()
        path.moveTo(QPointF(self.points[0][0], self.points[0][1]))
        for x, y in self.points[1:]:
            path.lineTo(QPointF(x, y))
        graphics_item = QGraphicsPathItem(path)
        graphics_item.setPen(QPen(self.line_color, self.line_width))
        graphics_item.setBrush(QColor("transparent"))
        self.scene().addItem(graphics_item)


    def resizeEvent(self, event):
        """Resize the chart to fit the view."""
        super().resizeEvent(event)
        self.fitInView(self.sceneRect())
        # self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)


def main():
    """Main function for testing the LineChart class."""

    # pylint: disable=import-outside-toplevel
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWidgets import QHBoxLayout, QWidget, QSpacerItem, QSizePolicy
    from PySide6.QtCore import Qt
    import sys

    app = QApplication(sys.argv)
    chart = LineChart()
    # chart.set_points([(0, 0), (1, 10), (2, 8), (3, 2), (4, 10)])
    chart.set_points([(0, 0.000), (1, 0.0010), (2, 0.0080), (3, 0.002), (4, 0.0010)])
    chart.set_line_color(QColor(255, 0, 0))  # red
    chart.set_line_width(0.1)
    chart.set_background_color(QColor(0, 0, 255))  # white
    chart.add_point(5, 15)
    chart.show()

    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.addWidget(chart)
    layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Preferred))
    layout.setAlignment(Qt.AlignLeft)
    layout.setContentsMargins(0, 0, 0, 0)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
