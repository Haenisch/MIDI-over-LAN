# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
    QLabel, QLineEdit, QSizePolicy, QTabWidget,
    QWidget)

class Ui_Settings(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName(u"Settings")
        Settings.resize(332, 163)
        Settings.setModal(True)
        self.gridLayout = QGridLayout(Settings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(Settings)
        self.tabWidget.setObjectName(u"tabWidget")
        self.Network = QWidget()
        self.Network.setObjectName(u"Network")
        self.gridLayout_2 = QGridLayout(self.Network)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_NetworkInterface = QLabel(self.Network)
        self.label_NetworkInterface.setObjectName(u"label_NetworkInterface")
        self.label_NetworkInterface.setMinimumSize(QSize(0, 0))
        self.label_NetworkInterface.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_NetworkInterface, 0, 0, 1, 1)

        self.lineEdit_NetworkInterface = QLineEdit(self.Network)
        self.lineEdit_NetworkInterface.setObjectName(u"lineEdit_NetworkInterface")
        self.lineEdit_NetworkInterface.setMinimumSize(QSize(150, 0))

        self.gridLayout_2.addWidget(self.lineEdit_NetworkInterface, 0, 1, 1, 1)

        self.label_MulticastGroupAddress = QLabel(self.Network)
        self.label_MulticastGroupAddress.setObjectName(u"label_MulticastGroupAddress")
        self.label_MulticastGroupAddress.setMinimumSize(QSize(0, 0))
        self.label_MulticastGroupAddress.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_MulticastGroupAddress, 1, 0, 1, 1)

        self.lineEdit_MulticastGroupAddress = QLineEdit(self.Network)
        self.lineEdit_MulticastGroupAddress.setObjectName(u"lineEdit_MulticastGroupAddress")
        self.lineEdit_MulticastGroupAddress.setEnabled(False)
        self.lineEdit_MulticastGroupAddress.setMinimumSize(QSize(150, 0))

        self.gridLayout_2.addWidget(self.lineEdit_MulticastGroupAddress, 1, 1, 1, 1)

        self.label_MulticastPortNumber = QLabel(self.Network)
        self.label_MulticastPortNumber.setObjectName(u"label_MulticastPortNumber")
        self.label_MulticastPortNumber.setMinimumSize(QSize(0, 0))
        self.label_MulticastPortNumber.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_MulticastPortNumber, 2, 0, 1, 1)

        self.lineEdit_MulticastPortNumber = QLineEdit(self.Network)
        self.lineEdit_MulticastPortNumber.setObjectName(u"lineEdit_MulticastPortNumber")
        self.lineEdit_MulticastPortNumber.setEnabled(False)
        self.lineEdit_MulticastPortNumber.setMinimumSize(QSize(150, 0))

        self.gridLayout_2.addWidget(self.lineEdit_MulticastPortNumber, 2, 1, 1, 1)

        self.label_EnableLoopback = QLabel(self.Network)
        self.label_EnableLoopback.setObjectName(u"label_EnableLoopback")
        self.label_EnableLoopback.setMinimumSize(QSize(0, 0))
        self.label_EnableLoopback.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_EnableLoopback, 3, 0, 1, 1)

        self.checkBox_EnableLoopback = QCheckBox(self.Network)
        self.checkBox_EnableLoopback.setObjectName(u"checkBox_EnableLoopback")

        self.gridLayout_2.addWidget(self.checkBox_EnableLoopback, 3, 1, 1, 1)

        self.tabWidget.addTab(self.Network, "")
        self.WorkerThreads = QWidget()
        self.WorkerThreads.setObjectName(u"WorkerThreads")
        self.gridLayout_3 = QGridLayout(self.WorkerThreads)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_SaveCpuTime = QLabel(self.WorkerThreads)
        self.label_SaveCpuTime.setObjectName(u"label_SaveCpuTime")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_SaveCpuTime.sizePolicy().hasHeightForWidth())
        self.label_SaveCpuTime.setSizePolicy(sizePolicy)
        self.label_SaveCpuTime.setMinimumSize(QSize(0, 0))
        self.label_SaveCpuTime.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_SaveCpuTime, 0, 0, 1, 1)

        self.checkBox_SaveCpuTime = QCheckBox(self.WorkerThreads)
        self.checkBox_SaveCpuTime.setObjectName(u"checkBox_SaveCpuTime")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.checkBox_SaveCpuTime.sizePolicy().hasHeightForWidth())
        self.checkBox_SaveCpuTime.setSizePolicy(sizePolicy1)
        self.checkBox_SaveCpuTime.setMinimumSize(QSize(0, 0))
        self.checkBox_SaveCpuTime.setChecked(True)

        self.gridLayout_3.addWidget(self.checkBox_SaveCpuTime, 0, 1, 1, 1)

        self.tabWidget.addTab(self.WorkerThreads, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

#if QT_CONFIG(shortcut)
        self.label_NetworkInterface.setBuddy(self.lineEdit_NetworkInterface)
        self.label_MulticastGroupAddress.setBuddy(self.lineEdit_MulticastGroupAddress)
        self.label_MulticastPortNumber.setBuddy(self.lineEdit_MulticastPortNumber)
        self.label_EnableLoopback.setBuddy(self.checkBox_EnableLoopback)
        self.label_SaveCpuTime.setBuddy(self.checkBox_SaveCpuTime)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(Settings)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Settings)
    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", u"Settings", None))
#if QT_CONFIG(tooltip)
        self.label_NetworkInterface.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>IPv4 address of the network interface to be used. If not specified, the default interface is used. Alternatively, you can specify a hostname such as 'computer' or 'computer.domain.name', or an alias like 'localhost'.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_NetworkInterface.setText(QCoreApplication.translate("Settings", u"&Network Interface:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_NetworkInterface.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>IPv4 address of the network interface to be used. If not specified, the default interface is used. Alternatively, you can specify a hostname such as 'computer' or 'computer.domain.name', or an alias like 'localhost'.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_NetworkInterface.setText(QCoreApplication.translate("Settings", u"default", None))
        self.label_MulticastGroupAddress.setText(QCoreApplication.translate("Settings", u"Multicast Group Address:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_MulticastGroupAddress.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>IPv4 address of the network interface to be used. If not specified, the default interface is used. Alternatively, you can specify a hostname such as 'computer' or 'computer.domain.name', or an alias like 'localhost'.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_MulticastGroupAddress.setText(QCoreApplication.translate("Settings", u"239.0.3.250", None))
        self.label_MulticastPortNumber.setText(QCoreApplication.translate("Settings", u"Multicast Port Number:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_MulticastPortNumber.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>IPv4 address of the network interface to be used. If not specified, the default interface is used. Alternatively, you can specify a hostname such as 'computer' or 'computer.domain.name', or an alias like 'localhost'.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_MulticastPortNumber.setText(QCoreApplication.translate("Settings", u"56129", None))
#if QT_CONFIG(tooltip)
        self.label_EnableLoopback.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>If loopback is enabled, a local client can receive the multicast packets.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_EnableLoopback.setText(QCoreApplication.translate("Settings", u"Enable &Loopback:", None))
#if QT_CONFIG(tooltip)
        self.checkBox_EnableLoopback.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>If loopback is enabled, a local client can receive the multicast packets.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_EnableLoopback.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Network), QCoreApplication.translate("Settings", u"Network", None))
#if QT_CONFIG(tooltip)
        self.label_SaveCpuTime.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>When enabled, the worker thread pauses briefly at the end of each loop iteration, significantly reducing CPU load. However, this may introduce some latency.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_SaveCpuTime.setText(QCoreApplication.translate("Settings", u"Save CPU &time:", None))
#if QT_CONFIG(tooltip)
        self.checkBox_SaveCpuTime.setToolTip(QCoreApplication.translate("Settings", u"<html><head/><body><p>When enabled, the worker thread pauses briefly at the end of each loop iteration, significantly reducing CPU load. However, this may introduce some latency.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_SaveCpuTime.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.WorkerThreads), QCoreApplication.translate("Settings", u"Worker Threads", None))
    # retranslateUi

