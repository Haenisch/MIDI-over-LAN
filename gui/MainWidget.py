# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableWidget, QTableWidgetItem, QTextEdit, QWidget)

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        if not MainWidget.objectName():
            MainWidget.setObjectName(u"MainWidget")
        MainWidget.resize(586, 392)
        MainWidget.setMinimumSize(QSize(0, 0))
        self.gridLayout_2 = QGridLayout(MainWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(MainWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_OutgoingTraffic = QWidget()
        self.tab_OutgoingTraffic.setObjectName(u"tab_OutgoingTraffic")
        self.gridLayout_3 = QGridLayout(self.tab_OutgoingTraffic)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.groupBox_LocalOutputPorts = QGroupBox(self.tab_OutgoingTraffic)
        self.groupBox_LocalOutputPorts.setObjectName(u"groupBox_LocalOutputPorts")
        self.gridLayout = QGridLayout(self.groupBox_LocalOutputPorts)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tableWidget_LocalOutputPorts = QTableWidget(self.groupBox_LocalOutputPorts)
        if (self.tableWidget_LocalOutputPorts.columnCount() < 2):
            self.tableWidget_LocalOutputPorts.setColumnCount(2)
        font = QFont()
        font.setBold(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem.setFont(font);
        self.tableWidget_LocalOutputPorts.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem1.setFont(font);
        self.tableWidget_LocalOutputPorts.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableWidget_LocalOutputPorts.setObjectName(u"tableWidget_LocalOutputPorts")
        palette = QPalette()
        brush = QBrush(QColor(0, 218, 105, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush)
        palette.setBrush(QPalette.Active, QPalette.Accent, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Accent, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Accent, brush)
        self.tableWidget_LocalOutputPorts.setPalette(palette)
        self.tableWidget_LocalOutputPorts.setEditTriggers(QAbstractItemView.EditTrigger.CurrentChanged|QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed|QAbstractItemView.EditTrigger.SelectedClicked)
        self.tableWidget_LocalOutputPorts.horizontalHeader().setVisible(True)
        self.tableWidget_LocalOutputPorts.horizontalHeader().setMinimumSectionSize(100)
        self.tableWidget_LocalOutputPorts.horizontalHeader().setDefaultSectionSize(250)
        self.tableWidget_LocalOutputPorts.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_LocalOutputPorts.verticalHeader().setVisible(False)
        self.tableWidget_LocalOutputPorts.verticalHeader().setHighlightSections(False)
        self.tableWidget_LocalOutputPorts.verticalHeader().setStretchLastSection(False)

        self.gridLayout.addWidget(self.tableWidget_LocalOutputPorts, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_LocalOutputPorts_SelectAll = QPushButton(self.groupBox_LocalOutputPorts)
        self.pushButton_LocalOutputPorts_SelectAll.setObjectName(u"pushButton_LocalOutputPorts_SelectAll")

        self.horizontalLayout.addWidget(self.pushButton_LocalOutputPorts_SelectAll)

        self.pushButton_LocalOutputPorts_UnselectAll = QPushButton(self.groupBox_LocalOutputPorts)
        self.pushButton_LocalOutputPorts_UnselectAll.setObjectName(u"pushButton_LocalOutputPorts_UnselectAll")

        self.horizontalLayout.addWidget(self.pushButton_LocalOutputPorts_UnselectAll)

        self.pushButton_LocalOutputPorts_Refresh = QPushButton(self.groupBox_LocalOutputPorts)
        self.pushButton_LocalOutputPorts_Refresh.setObjectName(u"pushButton_LocalOutputPorts_Refresh")

        self.horizontalLayout.addWidget(self.pushButton_LocalOutputPorts_Refresh)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_LocalOutputPorts_Run = QPushButton(self.groupBox_LocalOutputPorts)
        self.pushButton_LocalOutputPorts_Run.setObjectName(u"pushButton_LocalOutputPorts_Run")

        self.horizontalLayout.addWidget(self.pushButton_LocalOutputPorts_Run)

        self.pushButton_LocalOutputPorts_Stop = QPushButton(self.groupBox_LocalOutputPorts)
        self.pushButton_LocalOutputPorts_Stop.setObjectName(u"pushButton_LocalOutputPorts_Stop")

        self.horizontalLayout.addWidget(self.pushButton_LocalOutputPorts_Stop)

        self.radioButton = QRadioButton(self.groupBox_LocalOutputPorts)
        self.radioButton.setObjectName(u"radioButton")

        self.horizontalLayout.addWidget(self.radioButton)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox_LocalOutputPorts, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_OutgoingTraffic, "")
        self.tab_IncomingTraffic = QWidget()
        self.tab_IncomingTraffic.setObjectName(u"tab_IncomingTraffic")
        self.tabWidget.addTab(self.tab_IncomingTraffic, "")
        self.tab_Statistics = QWidget()
        self.tab_Statistics.setObjectName(u"tab_Statistics")
        self.gridLayout_4 = QGridLayout(self.tab_Statistics)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_RTT = QGroupBox(self.tab_Statistics)
        self.groupBox_RTT.setObjectName(u"groupBox_RTT")
        self.gridLayout_5 = QGridLayout(self.groupBox_RTT)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.tableWidget_RTT = QTableWidget(self.groupBox_RTT)
        if (self.tableWidget_RTT.columnCount() < 5):
            self.tableWidget_RTT.setColumnCount(5)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem2.setFont(font);
        self.tableWidget_RTT.setHorizontalHeaderItem(0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem3.setFont(font);
        self.tableWidget_RTT.setHorizontalHeaderItem(1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem4.setFont(font);
        self.tableWidget_RTT.setHorizontalHeaderItem(2, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem5.setFont(font);
        self.tableWidget_RTT.setHorizontalHeaderItem(3, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem6.setFont(font);
        self.tableWidget_RTT.setHorizontalHeaderItem(4, __qtablewidgetitem6)
        if (self.tableWidget_RTT.rowCount() < 1):
            self.tableWidget_RTT.setRowCount(1)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_RTT.setVerticalHeaderItem(0, __qtablewidgetitem7)
        self.tableWidget_RTT.setObjectName(u"tableWidget_RTT")
        self.tableWidget_RTT.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_RTT.verticalHeader().setVisible(False)

        self.gridLayout_5.addWidget(self.tableWidget_RTT, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_RTT, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_Statistics, "")
        self.tab_About = QWidget()
        self.tab_About.setObjectName(u"tab_About")
        self.gridLayout_6 = QGridLayout(self.tab_About)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.textEdit_About = QTextEdit(self.tab_About)
        self.textEdit_About.setObjectName(u"textEdit_About")
        self.textEdit_About.setFrameShape(QFrame.Shape.NoFrame)
        self.textEdit_About.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textEdit_About, 1, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_2, 1, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_6.addItem(self.verticalSpacer_2, 2, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_6.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(10, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_3, 1, 2, 1, 1)

        self.tabWidget.addTab(self.tab_About, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        QWidget.setTabOrder(self.tabWidget, self.tableWidget_LocalOutputPorts)
        QWidget.setTabOrder(self.tableWidget_LocalOutputPorts, self.pushButton_LocalOutputPorts_SelectAll)
        QWidget.setTabOrder(self.pushButton_LocalOutputPorts_SelectAll, self.pushButton_LocalOutputPorts_UnselectAll)

        self.retranslateUi(MainWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWidget)
    # setupUi

    def retranslateUi(self, MainWidget):
        MainWidget.setWindowTitle(QCoreApplication.translate("MainWidget", u"MIDI over LAN", None))
        self.groupBox_LocalOutputPorts.setTitle(QCoreApplication.translate("MainWidget", u"Local Output Ports", None))
        ___qtablewidgetitem = self.tableWidget_LocalOutputPorts.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWidget", u"Device Name", None));
        ___qtablewidgetitem1 = self.tableWidget_LocalOutputPorts.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWidget", u"Network Name", None));
        self.pushButton_LocalOutputPorts_SelectAll.setText(QCoreApplication.translate("MainWidget", u"Select &All", None))
        self.pushButton_LocalOutputPorts_UnselectAll.setText(QCoreApplication.translate("MainWidget", u"&Unselect All", None))
#if QT_CONFIG(tooltip)
        self.pushButton_LocalOutputPorts_Refresh.setToolTip(QCoreApplication.translate("MainWidget", u"<html><head/><body><p>Refresh the list of output ports in case a new device is connected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_LocalOutputPorts_Refresh.setText(QCoreApplication.translate("MainWidget", u"Re&fresh", None))
        self.pushButton_LocalOutputPorts_Run.setText(QCoreApplication.translate("MainWidget", u"&Run", None))
        self.pushButton_LocalOutputPorts_Stop.setText(QCoreApplication.translate("MainWidget", u"&Stop", None))
        self.radioButton.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_OutgoingTraffic), QCoreApplication.translate("MainWidget", u"Outgoing Traffic", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_IncomingTraffic), QCoreApplication.translate("MainWidget", u"Incoming Traffic", None))
        self.groupBox_RTT.setTitle(QCoreApplication.translate("MainWidget", u"Round-Trip Times", None))
        ___qtablewidgetitem2 = self.tableWidget_RTT.horizontalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWidget", u"Hostname", None));
        ___qtablewidgetitem3 = self.tableWidget_RTT.horizontalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWidget", u"Minimum RTT", None));
        ___qtablewidgetitem4 = self.tableWidget_RTT.horizontalHeaderItem(2)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWidget", u"Maximum RTT", None));
        ___qtablewidgetitem5 = self.tableWidget_RTT.horizontalHeaderItem(3)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWidget", u"Average RTT", None));
        ___qtablewidgetitem6 = self.tableWidget_RTT.horizontalHeaderItem(4)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWidget", u"Lost Packets", None));
        ___qtablewidgetitem7 = self.tableWidget_RTT.verticalHeaderItem(0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWidget", u"0", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Statistics), QCoreApplication.translate("MainWidget", u"Statitstics", None))
        self.textEdit_About.setHtml(QCoreApplication.translate("MainWidget", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:700;\">MIDI Over LAN</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent"
                        ":0px;\">Version 1.0</p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Copyright \u00a9 2025 Christoph H\u00e4nisch</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:700;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This program is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.</p>\n"
""
                        "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.</p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">You should have received a copy of the GNU Lesser General Public License along with this program; if not, write to the Free Software Foundation,"
                        " Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA</p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_About), QCoreApplication.translate("MainWidget", u"About", None))
    # retranslateUi

