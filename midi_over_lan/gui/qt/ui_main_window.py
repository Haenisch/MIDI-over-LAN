# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

from rotated_label import RotatedLabel
from routing_matrix import RoutingMatrix

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(668, 522)
        self.action_Quit = QAction(MainWindow)
        self.action_Quit.setObjectName(u"action_Quit")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        self.action_Quit.setIcon(icon)
        self.action_Quit.setMenuRole(QAction.MenuRole.QuitRole)
        self.action_About = QAction(MainWindow)
        self.action_About.setObjectName(u"action_About")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.action_About.setIcon(icon1)
        self.action_About.setMenuRole(QAction.MenuRole.AboutRole)
        self.action_Preferences = QAction(MainWindow)
        self.action_Preferences.setObjectName(u"action_Preferences")
        icon2 = QIcon(QIcon.fromTheme(u"preferences-other"))
        self.action_Preferences.setIcon(icon2)
        self.action_Preferences.setMenuRole(QAction.MenuRole.PreferencesRole)
        self.actionShow_Debug_Messages = QAction(MainWindow)
        self.actionShow_Debug_Messages.setObjectName(u"actionShow_Debug_Messages")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_11 = QGridLayout(self.centralwidget)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_OutgoingTraffic = QWidget()
        self.tab_OutgoingTraffic.setObjectName(u"tab_OutgoingTraffic")
        self.verticalLayout_3 = QVBoxLayout(self.tab_OutgoingTraffic)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_LocalInputDevices = QGroupBox(self.tab_OutgoingTraffic)
        self.groupBox_LocalInputDevices.setObjectName(u"groupBox_LocalInputDevices")
        self.gridLayout_2 = QGridLayout(self.groupBox_LocalInputDevices)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tableWidget_LocalInputPorts = QTableWidget(self.groupBox_LocalInputDevices)
        if (self.tableWidget_LocalInputPorts.columnCount() < 2):
            self.tableWidget_LocalInputPorts.setColumnCount(2)
        font = QFont()
        font.setBold(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem.setFont(font);
        self.tableWidget_LocalInputPorts.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem1.setFont(font);
        self.tableWidget_LocalInputPorts.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableWidget_LocalInputPorts.setObjectName(u"tableWidget_LocalInputPorts")
        palette = QPalette()
        brush = QBrush(QColor(0, 218, 105, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, brush)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent, brush)
#endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, brush)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Accent, brush)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Accent, brush)
#endif
        self.tableWidget_LocalInputPorts.setPalette(palette)
        self.tableWidget_LocalInputPorts.setEditTriggers(QAbstractItemView.EditTrigger.CurrentChanged|QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed|QAbstractItemView.EditTrigger.SelectedClicked)
        self.tableWidget_LocalInputPorts.horizontalHeader().setVisible(True)
        self.tableWidget_LocalInputPorts.horizontalHeader().setMinimumSectionSize(100)
        self.tableWidget_LocalInputPorts.horizontalHeader().setDefaultSectionSize(250)
        self.tableWidget_LocalInputPorts.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_LocalInputPorts.verticalHeader().setVisible(False)
        self.tableWidget_LocalInputPorts.verticalHeader().setHighlightSections(False)
        self.tableWidget_LocalInputPorts.verticalHeader().setStretchLastSection(False)

        self.gridLayout_2.addWidget(self.tableWidget_LocalInputPorts, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_LocalInputPorts_SelectAll = QPushButton(self.groupBox_LocalInputDevices)
        self.pushButton_LocalInputPorts_SelectAll.setObjectName(u"pushButton_LocalInputPorts_SelectAll")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_LocalInputPorts_SelectAll.sizePolicy().hasHeightForWidth())
        self.pushButton_LocalInputPorts_SelectAll.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.pushButton_LocalInputPorts_SelectAll)

        self.pushButton_LocalInputPorts_UnselectAll = QPushButton(self.groupBox_LocalInputDevices)
        self.pushButton_LocalInputPorts_UnselectAll.setObjectName(u"pushButton_LocalInputPorts_UnselectAll")
        sizePolicy.setHeightForWidth(self.pushButton_LocalInputPorts_UnselectAll.sizePolicy().hasHeightForWidth())
        self.pushButton_LocalInputPorts_UnselectAll.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.pushButton_LocalInputPorts_UnselectAll)

        self.pushButton_LocalInputPorts_Refresh = QPushButton(self.groupBox_LocalInputDevices)
        self.pushButton_LocalInputPorts_Refresh.setObjectName(u"pushButton_LocalInputPorts_Refresh")
        sizePolicy.setHeightForWidth(self.pushButton_LocalInputPorts_Refresh.sizePolicy().hasHeightForWidth())
        self.pushButton_LocalInputPorts_Refresh.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.pushButton_LocalInputPorts_Refresh)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_LocalInputDevices)

        self.groupBox_Server_OutgoingTraffic = QGroupBox(self.tab_OutgoingTraffic)
        self.groupBox_Server_OutgoingTraffic.setObjectName(u"groupBox_Server_OutgoingTraffic")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_Server_OutgoingTraffic)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.checkBox_OutgoingTraffic_IgnoreMidiClock = QCheckBox(self.groupBox_Server_OutgoingTraffic)
        self.checkBox_OutgoingTraffic_IgnoreMidiClock.setObjectName(u"checkBox_OutgoingTraffic_IgnoreMidiClock")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.checkBox_OutgoingTraffic_IgnoreMidiClock.sizePolicy().hasHeightForWidth())
        self.checkBox_OutgoingTraffic_IgnoreMidiClock.setSizePolicy(sizePolicy1)
        self.checkBox_OutgoingTraffic_IgnoreMidiClock.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_OutgoingTraffic_IgnoreMidiClock, 0, 0, 1, 1)

        self.label_OutgoingTraffic_IgnoreMidiClock = QLabel(self.groupBox_Server_OutgoingTraffic)
        self.label_OutgoingTraffic_IgnoreMidiClock.setObjectName(u"label_OutgoingTraffic_IgnoreMidiClock")
        self.label_OutgoingTraffic_IgnoreMidiClock.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_OutgoingTraffic_IgnoreMidiClock, 0, 1, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 13, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_OutgoingTraffic_Restart = QPushButton(self.groupBox_Server_OutgoingTraffic)
        self.pushButton_OutgoingTraffic_Restart.setObjectName(u"pushButton_OutgoingTraffic_Restart")
        sizePolicy.setHeightForWidth(self.pushButton_OutgoingTraffic_Restart.sizePolicy().hasHeightForWidth())
        self.pushButton_OutgoingTraffic_Restart.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.pushButton_OutgoingTraffic_Restart)

        self.pushButton_OutgoingTraffic_PauseResume = QPushButton(self.groupBox_Server_OutgoingTraffic)
        self.pushButton_OutgoingTraffic_PauseResume.setObjectName(u"pushButton_OutgoingTraffic_PauseResume")
        sizePolicy.setHeightForWidth(self.pushButton_OutgoingTraffic_PauseResume.sizePolicy().hasHeightForWidth())
        self.pushButton_OutgoingTraffic_PauseResume.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.pushButton_OutgoingTraffic_PauseResume)

        self.horizontalSpacer_2 = QSpacerItem(3, 19, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.label_OutgoingTraffic_ServerStatus = QLabel(self.groupBox_Server_OutgoingTraffic)
        self.label_OutgoingTraffic_ServerStatus.setObjectName(u"label_OutgoingTraffic_ServerStatus")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_OutgoingTraffic_ServerStatus.sizePolicy().hasHeightForWidth())
        self.label_OutgoingTraffic_ServerStatus.setSizePolicy(sizePolicy2)
        self.label_OutgoingTraffic_ServerStatus.setMinimumSize(QSize(20, 20))
        self.label_OutgoingTraffic_ServerStatus.setMaximumSize(QSize(20, 20))
        self.label_OutgoingTraffic_ServerStatus.setStyleSheet(u"background-color: green;\n"
"border: 1px solid gray;\n"
"border-radius: 10px;")

        self.horizontalLayout_2.addWidget(self.label_OutgoingTraffic_ServerStatus)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)


        self.verticalLayout_3.addWidget(self.groupBox_Server_OutgoingTraffic)

        self.tabWidget.addTab(self.tab_OutgoingTraffic, "")
        self.tab_IncomingTraffic = QWidget()
        self.tab_IncomingTraffic.setObjectName(u"tab_IncomingTraffic")
        self.verticalLayout_2 = QVBoxLayout(self.tab_IncomingTraffic)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_RoutingMatrix = QGroupBox(self.tab_IncomingTraffic)
        self.groupBox_RoutingMatrix.setObjectName(u"groupBox_RoutingMatrix")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_RoutingMatrix)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.frame_HorizontalHeader = QFrame(self.groupBox_RoutingMatrix)
        self.frame_HorizontalHeader.setObjectName(u"frame_HorizontalHeader")
        self.frame_HorizontalHeader.setMaximumSize(QSize(16777215, 36))
        self.frame_HorizontalHeader.setStyleSheet(u"background-color: rgba(240, 240, 240, 128);")
        self.frame_HorizontalHeader.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_HorizontalHeader.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_HorizontalHeader.setLineWidth(0)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_HorizontalHeader)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_4 = QSpacerItem(218, 13, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.label_RoutingMatrix_NetworkDevices = QLabel(self.frame_HorizontalHeader)
        self.label_RoutingMatrix_NetworkDevices.setObjectName(u"label_RoutingMatrix_NetworkDevices")
        self.label_RoutingMatrix_NetworkDevices.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_4.addWidget(self.label_RoutingMatrix_NetworkDevices)

        self.horizontalSpacer_5 = QSpacerItem(217, 13, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)


        self.gridLayout_3.addWidget(self.frame_HorizontalHeader, 0, 1, 1, 1)

        self.frame_VerticalHeader = QFrame(self.groupBox_RoutingMatrix)
        self.frame_VerticalHeader.setObjectName(u"frame_VerticalHeader")
        self.frame_VerticalHeader.setMaximumSize(QSize(36, 16777215))
        self.frame_VerticalHeader.setStyleSheet(u"background-color: rgba(240, 240, 240, 128);")
        self.frame_VerticalHeader.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_VerticalHeader.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_VerticalHeader.setLineWidth(0)
        self.verticalLayout = QVBoxLayout(self.frame_VerticalHeader)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_RoutingMatrix_LocalMidiDevices = RotatedLabel(self.frame_VerticalHeader)
        self.label_RoutingMatrix_LocalMidiDevices.setObjectName(u"label_RoutingMatrix_LocalMidiDevices")
        self.label_RoutingMatrix_LocalMidiDevices.setMinimumSize(QSize(250, 20))
        self.label_RoutingMatrix_LocalMidiDevices.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_RoutingMatrix_LocalMidiDevices)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_3)


        self.gridLayout_3.addWidget(self.frame_VerticalHeader, 1, 0, 1, 1)

        self.tableWidget_RoutingMatrix = RoutingMatrix(self.groupBox_RoutingMatrix)
        self.tableWidget_RoutingMatrix.setObjectName(u"tableWidget_RoutingMatrix")

        self.gridLayout_3.addWidget(self.tableWidget_RoutingMatrix, 1, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton_RoutingMatrix_SelectAll = QPushButton(self.groupBox_RoutingMatrix)
        self.pushButton_RoutingMatrix_SelectAll.setObjectName(u"pushButton_RoutingMatrix_SelectAll")

        self.horizontalLayout_3.addWidget(self.pushButton_RoutingMatrix_SelectAll)

        self.pushButton_RoutingMatrix_UnselectAll = QPushButton(self.groupBox_RoutingMatrix)
        self.pushButton_RoutingMatrix_UnselectAll.setObjectName(u"pushButton_RoutingMatrix_UnselectAll")

        self.horizontalLayout_3.addWidget(self.pushButton_RoutingMatrix_UnselectAll)

        self.pushButton_RoutingMatrix_Refresh = QPushButton(self.groupBox_RoutingMatrix)
        self.pushButton_RoutingMatrix_Refresh.setObjectName(u"pushButton_RoutingMatrix_Refresh")

        self.horizontalLayout_3.addWidget(self.pushButton_RoutingMatrix_Refresh)

        self.pushButton_RoutingMatrix_Clear = QPushButton(self.groupBox_RoutingMatrix)
        self.pushButton_RoutingMatrix_Clear.setObjectName(u"pushButton_RoutingMatrix_Clear")

        self.horizontalLayout_3.addWidget(self.pushButton_RoutingMatrix_Clear)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addWidget(self.groupBox_RoutingMatrix)

        self.tabWidget.addTab(self.tab_IncomingTraffic, "")
        self.tab_Statistics = QWidget()
        self.tab_Statistics.setObjectName(u"tab_Statistics")
        self.gridLayout_8 = QGridLayout(self.tab_Statistics)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.groupBox_RTT = QGroupBox(self.tab_Statistics)
        self.groupBox_RTT.setObjectName(u"groupBox_RTT")
        self.gridLayout_9 = QGridLayout(self.groupBox_RTT)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.tableWidget_RTT = QTableWidget(self.groupBox_RTT)
        if (self.tableWidget_RTT.columnCount() < 6):
            self.tableWidget_RTT.setColumnCount(6)
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
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem7.setFont(font);
        self.tableWidget_RTT.setHorizontalHeaderItem(5, __qtablewidgetitem7)
        self.tableWidget_RTT.setObjectName(u"tableWidget_RTT")
        self.tableWidget_RTT.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_RTT.verticalHeader().setVisible(False)

        self.gridLayout_9.addWidget(self.tableWidget_RTT, 0, 0, 1, 1)


        self.gridLayout_8.addWidget(self.groupBox_RTT, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_Statistics, "")

        self.gridLayout_11.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 668, 33))
        self.menu_File = QMenu(self.menubar)
        self.menu_File.setObjectName(u"menu_File")
        self.menu_Help = QMenu(self.menubar)
        self.menu_Help.setObjectName(u"menu_Help")
        self.menu_Settings = QMenu(self.menubar)
        self.menu_Settings.setObjectName(u"menu_Settings")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.label_OutgoingTraffic_IgnoreMidiClock.setBuddy(self.checkBox_OutgoingTraffic_IgnoreMidiClock)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.tableWidget_LocalInputPorts, self.pushButton_LocalInputPorts_SelectAll)
        QWidget.setTabOrder(self.pushButton_LocalInputPorts_SelectAll, self.pushButton_LocalInputPorts_UnselectAll)
        QWidget.setTabOrder(self.pushButton_LocalInputPorts_UnselectAll, self.pushButton_LocalInputPorts_Refresh)
        QWidget.setTabOrder(self.pushButton_LocalInputPorts_Refresh, self.checkBox_OutgoingTraffic_IgnoreMidiClock)
        QWidget.setTabOrder(self.checkBox_OutgoingTraffic_IgnoreMidiClock, self.pushButton_OutgoingTraffic_Restart)
        QWidget.setTabOrder(self.pushButton_OutgoingTraffic_Restart, self.pushButton_OutgoingTraffic_PauseResume)
        QWidget.setTabOrder(self.pushButton_OutgoingTraffic_PauseResume, self.tabWidget)
        QWidget.setTabOrder(self.tabWidget, self.tableWidget_RoutingMatrix)
        QWidget.setTabOrder(self.tableWidget_RoutingMatrix, self.pushButton_RoutingMatrix_SelectAll)
        QWidget.setTabOrder(self.pushButton_RoutingMatrix_SelectAll, self.pushButton_RoutingMatrix_UnselectAll)
        QWidget.setTabOrder(self.pushButton_RoutingMatrix_UnselectAll, self.pushButton_RoutingMatrix_Refresh)
        QWidget.setTabOrder(self.pushButton_RoutingMatrix_Refresh, self.pushButton_RoutingMatrix_Clear)
        QWidget.setTabOrder(self.pushButton_RoutingMatrix_Clear, self.tableWidget_RTT)

        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Settings.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.menu_File.addAction(self.action_Quit)
        self.menu_Help.addAction(self.action_About)
        self.menu_Settings.addAction(self.action_Preferences)
        self.menu_Settings.addAction(self.actionShow_Debug_Messages)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MIDI over LAN", None))
        self.action_Quit.setText(QCoreApplication.translate("MainWindow", u"&Quit", None))
        self.action_About.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.action_Preferences.setText(QCoreApplication.translate("MainWindow", u"&Preferences", None))
#if QT_CONFIG(tooltip)
        self.action_Preferences.setToolTip(QCoreApplication.translate("MainWindow", u"Preferences", None))
#endif // QT_CONFIG(tooltip)
        self.actionShow_Debug_Messages.setText(QCoreApplication.translate("MainWindow", u"Show &Debug Messages", None))
        self.groupBox_LocalInputDevices.setTitle(QCoreApplication.translate("MainWindow", u"Local Input Devices", None))
        ___qtablewidgetitem = self.tableWidget_LocalInputPorts.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Device Name", None));
        ___qtablewidgetitem1 = self.tableWidget_LocalInputPorts.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Network Name", None));
        self.pushButton_LocalInputPorts_SelectAll.setText(QCoreApplication.translate("MainWindow", u"Select &All", None))
        self.pushButton_LocalInputPorts_UnselectAll.setText(QCoreApplication.translate("MainWindow", u"&Unselect All", None))
#if QT_CONFIG(tooltip)
        self.pushButton_LocalInputPorts_Refresh.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Refresh the list of input ports in case a new device is connected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_LocalInputPorts_Refresh.setText(QCoreApplication.translate("MainWindow", u"R&efresh", None))
        self.groupBox_Server_OutgoingTraffic.setTitle(QCoreApplication.translate("MainWindow", u"Server", None))
#if QT_CONFIG(tooltip)
        self.checkBox_OutgoingTraffic_IgnoreMidiClock.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.checkBox_OutgoingTraffic_IgnoreMidiClock.setText("")
        self.label_OutgoingTraffic_IgnoreMidiClock.setText(QCoreApplication.translate("MainWindow", u"Ignore MIDI &Clock Data", None))
#if QT_CONFIG(tooltip)
        self.pushButton_OutgoingTraffic_Restart.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Shut down the worker process for outgoing messages and restart it afterwards.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_OutgoingTraffic_Restart.setText(QCoreApplication.translate("MainWindow", u"&Restart", None))
#if QT_CONFIG(tooltip)
        self.pushButton_OutgoingTraffic_PauseResume.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Pause or resume the worker process for outgoing messages. If the worker is paused, any MIDI messages from local input ports are discarded.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_OutgoingTraffic_PauseResume.setText(QCoreApplication.translate("MainWindow", u"&Pause/Resume", None))
        self.label_OutgoingTraffic_ServerStatus.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_OutgoingTraffic), QCoreApplication.translate("MainWindow", u"&Outgoing Traffic", None))
        self.groupBox_RoutingMatrix.setTitle(QCoreApplication.translate("MainWindow", u"Routing Matrix", None))
        self.label_RoutingMatrix_NetworkDevices.setText(QCoreApplication.translate("MainWindow", u"Network Devices", None))
        self.label_RoutingMatrix_LocalMidiDevices.setText(QCoreApplication.translate("MainWindow", u"Local MIDI Devices", None))
        self.pushButton_RoutingMatrix_SelectAll.setText(QCoreApplication.translate("MainWindow", u"Select &All", None))
        self.pushButton_RoutingMatrix_UnselectAll.setText(QCoreApplication.translate("MainWindow", u"&Unselect All", None))
#if QT_CONFIG(tooltip)
        self.pushButton_RoutingMatrix_Refresh.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Refresh the list of local output ports in case a new device is connected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_RoutingMatrix_Refresh.setText(QCoreApplication.translate("MainWindow", u"&Refresh", None))
#if QT_CONFIG(tooltip)
        self.pushButton_RoutingMatrix_Clear.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Remove all entries. The routing matrix will remain empty until some network devices are detected.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_RoutingMatrix_Clear.setText(QCoreApplication.translate("MainWindow", u"&Clear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_IncomingTraffic), QCoreApplication.translate("MainWindow", u"&Incoming Traffic", None))
        self.groupBox_RTT.setTitle(QCoreApplication.translate("MainWindow", u"Round-Trip Times (in milliseconds)", None))
        ___qtablewidgetitem2 = self.tableWidget_RTT.horizontalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Hostname", None));
        ___qtablewidgetitem3 = self.tableWidget_RTT.horizontalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Minimum", None));
        ___qtablewidgetitem4 = self.tableWidget_RTT.horizontalHeaderItem(2)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Maximum", None));
        ___qtablewidgetitem5 = self.tableWidget_RTT.horizontalHeaderItem(3)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Median", None));
        ___qtablewidgetitem6 = self.tableWidget_RTT.horizontalHeaderItem(4)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Average", None));
        ___qtablewidgetitem7 = self.tableWidget_RTT.horizontalHeaderItem(5)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Graph", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Statistics), QCoreApplication.translate("MainWindow", u"Sta&tistics", None))
        self.menu_File.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_Help.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.menu_Settings.setTitle(QCoreApplication.translate("MainWindow", u"&Settings", None))
    # retranslateUi

