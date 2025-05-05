# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'debug_messages_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGroupBox,
    QHBoxLayout, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_DebugMessages(object):
    def setupUi(self, DebugMessages):
        if not DebugMessages.objectName():
            DebugMessages.setObjectName(u"DebugMessages")
        DebugMessages.resize(1200, 800)
        self.verticalLayout = QVBoxLayout(DebugMessages)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.groupBox_DebugLevel = QGroupBox(DebugMessages)
        self.groupBox_DebugLevel.setObjectName(u"groupBox_DebugLevel")
        self.horizontalLayout = QHBoxLayout(self.groupBox_DebugLevel)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.radioButton_Debug = QRadioButton(self.groupBox_DebugLevel)
        self.radioButton_Debug.setObjectName(u"radioButton_Debug")
        self.radioButton_Debug.setChecked(False)

        self.horizontalLayout.addWidget(self.radioButton_Debug)

        self.radioButton_Info = QRadioButton(self.groupBox_DebugLevel)
        self.radioButton_Info.setObjectName(u"radioButton_Info")
        self.radioButton_Info.setChecked(True)

        self.horizontalLayout.addWidget(self.radioButton_Info)

        self.radioButton_Warning = QRadioButton(self.groupBox_DebugLevel)
        self.radioButton_Warning.setObjectName(u"radioButton_Warning")

        self.horizontalLayout.addWidget(self.radioButton_Warning)

        self.radioButton_Error = QRadioButton(self.groupBox_DebugLevel)
        self.radioButton_Error.setObjectName(u"radioButton_Error")

        self.horizontalLayout.addWidget(self.radioButton_Error)

        self.radioButton_Critical = QRadioButton(self.groupBox_DebugLevel)
        self.radioButton_Critical.setObjectName(u"radioButton_Critical")

        self.horizontalLayout.addWidget(self.radioButton_Critical)


        self.horizontalLayout_3.addWidget(self.groupBox_DebugLevel)

        self.groupBox_ScrollToBottom = QGroupBox(DebugMessages)
        self.groupBox_ScrollToBottom.setObjectName(u"groupBox_ScrollToBottom")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_ScrollToBottom)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBox_ScrollToBottom = QCheckBox(self.groupBox_ScrollToBottom)
        self.checkBox_ScrollToBottom.setObjectName(u"checkBox_ScrollToBottom")
        self.checkBox_ScrollToBottom.setChecked(True)

        self.horizontalLayout_2.addWidget(self.checkBox_ScrollToBottom)


        self.horizontalLayout_3.addWidget(self.groupBox_ScrollToBottom)

        self.horizontalSpacer = QSpacerItem(276, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButton_ClearAllMessages = QPushButton(DebugMessages)
        self.pushButton_ClearAllMessages.setObjectName(u"pushButton_ClearAllMessages")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_ClearAllMessages.sizePolicy().hasHeightForWidth())
        self.pushButton_ClearAllMessages.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.pushButton_ClearAllMessages)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.textEdit_DebugMessages = QTextEdit(DebugMessages)
        self.textEdit_DebugMessages.setObjectName(u"textEdit_DebugMessages")
        self.textEdit_DebugMessages.setReadOnly(True)

        self.verticalLayout.addWidget(self.textEdit_DebugMessages)


        self.retranslateUi(DebugMessages)
        self.pushButton_ClearAllMessages.clicked.connect(self.textEdit_DebugMessages.clear)

        QMetaObject.connectSlotsByName(DebugMessages)
    # setupUi

    def retranslateUi(self, DebugMessages):
        DebugMessages.setWindowTitle(QCoreApplication.translate("DebugMessages", u"Debug Messages", None))
        self.groupBox_DebugLevel.setTitle("")
        self.radioButton_Debug.setText(QCoreApplication.translate("DebugMessages", u"Debug", None))
        self.radioButton_Info.setText(QCoreApplication.translate("DebugMessages", u"Info", None))
        self.radioButton_Warning.setText(QCoreApplication.translate("DebugMessages", u"Warning", None))
        self.radioButton_Error.setText(QCoreApplication.translate("DebugMessages", u"Error", None))
        self.radioButton_Critical.setText(QCoreApplication.translate("DebugMessages", u"Critical", None))
        self.groupBox_ScrollToBottom.setTitle("")
        self.checkBox_ScrollToBottom.setText(QCoreApplication.translate("DebugMessages", u"Scroll to Bottom", None))
        self.pushButton_ClearAllMessages.setText(QCoreApplication.translate("DebugMessages", u"  Clear All Messages  ", None))
    # retranslateUi

