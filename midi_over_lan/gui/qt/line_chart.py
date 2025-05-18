# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""LineChart class for displaying a line chart using PySide6 only."""

# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# pylint: disable=invalid-name

from typing import List, Tuple

from PySide6.QtCharts import QChart, QChartView, QSplineSeries
from PySide6.QtCore import QMargins, QPointF, Qt
from PySide6.QtGui import QColor, QPen, QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout


class LineChart(QWidget):
    """Display a line chart from a given list of 2D points.

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

        # Create the chart (show only the graph/spline and nothing else)
        self.chart = QChart()
        self.series = QSplineSeries()
        self.chart.addSeries(self.series)
        self.chart.legend().hide()
        self.chart.createDefaultAxes()
        self.chart.axisX().setVisible(False)
        self.chart.axisY().setVisible(False)
        self.chart.setMargins(QMargins(0, 0, 0, 0))  # remove chart margins
        self.chart_view = QChartView(self.chart)
        self.chart_view.setStyleSheet("background: transparent; border: 0px;")
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        layout.setContentsMargins(0, 0, 0, 0)  # remove layout margins
        self.setLayout(layout)

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
        self.series.clear()

        if not self.points:
            return

        pen = QPen(self.line_color)
        pen.setWidth(self.line_width)
        self.series.setPen(pen)
        self.chart.setBackgroundBrush(self.background_color)
        self.chart.setBackgroundRoundness(0)
        min_x = min(x for x, _ in self.points)
        max_x = max(x for x, _ in self.points)
        min_y = min(y for _, y in self.points)
        max_y = max(y for _, y in self.points)
        y_range = max_y - min_y if max_y != min_y else 1
        self.chart.axisX().setRange(min_x, max_x)
        self.chart.axisY().setRange(-0.2, 1.2)
        for (x, y) in self.points:
            self.series.append(QPointF(x, (y - min_y) / y_range))


def main():
    """Main function for testing the LineChart class."""

    # pylint: disable=import-outside-toplevel
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    chart = LineChart()
    chart.set_points([(0, 2), (1, 7), (2, 6), (3, 7), (4, 3), (5, 7), (6, 5)])
    chart.set_line_color(QColor(255, 255, 255))  # white
    chart.set_line_width(2)
    chart.set_background_color(QColor(100, 100, 255))  # light blue
    chart.add_point(5, 15)
    chart.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
