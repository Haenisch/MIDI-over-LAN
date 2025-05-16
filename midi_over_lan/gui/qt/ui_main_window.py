# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(640, 515)
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
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush)
        palette.setBrush(QPalette.Active, QPalette.Accent, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Accent, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Accent, brush)
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
        self.menubar.setGeometry(QRect(0, 0, 640, 33))
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
        self.pushButton_LocalInputPorts_Refresh.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Refresh the list of output ports in case a new device is connected.</p></body></html>", None))
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
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_IncomingTraffic), QCoreApplication.translate("MainWindow", u"&Incoming Traffic", None))
        self.groupBox_RTT.setTitle(QCoreApplication.translate("MainWindow", u"Round-Trip Times", None))
        ___qtablewidgetitem2 = self.tableWidget_RTT.horizontalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Hostname", None));
        ___qtablewidgetitem3 = self.tableWidget_RTT.horizontalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Minimum RTT", None));
        ___qtablewidgetitem4 = self.tableWidget_RTT.horizontalHeaderItem(2)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Maximum RTT", None));
        ___qtablewidgetitem5 = self.tableWidget_RTT.horizontalHeaderItem(3)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Average RTT", None));
        ___qtablewidgetitem6 = self.tableWidget_RTT.horizontalHeaderItem(4)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Graph", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Statistics), QCoreApplication.translate("MainWindow", u"Sta&tistics", None))
        self.menu_File.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_Help.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.menu_Settings.setTitle(QCoreApplication.translate("MainWindow", u"&Settings", None))
    # retranslateUi

