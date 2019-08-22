#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Standard library
import sys
import time
# Additional imports
import pyads
from PyQt5 import QtCore, QtGui, QtWidgets

# ADS configuration.
global AMS_NET_ID
global AMS_NET_PORT
AMS_NET_ID = '192.168.19.1.1.1'
AMS_NET_PORT = 851

class ReadTimer(QtCore.QThread):
    """ Trigger the read process. """
    # Signal must be defined at the same level as the methods.
    timer_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def run(self):
        """ Executed automatically when the thread starts. """
        while True:
            self.timer_signal.emit('') # send a signal
            time.sleep(0.3) # 300 ms

class DeviceNotification(QtCore.QThread):
    """ Receive a notification when the PLC variable changes its state. """
    # A signal which is sent when the PLC variable changes its state.
    notification_signal = QtCore.pyqtSignal('PyQt_PyObject') 

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.signal_sent = False
    
    def run(self):
        """ Executed automatically when the thread starts. """
        # Create and open a connection.
        plc = pyads.Connection(AMS_NET_ID, AMS_NET_PORT)
        plc.open()

        @plc.notification(pyads.PLCTYPE_BOOL)
        def callback(handle, name, timestamp, value):
            """ Executed when the variable changes its state. """
            data = {'name': name, 'value': value}
            self.notification_signal.emit(data) # send data

        # Create device notifications.
        attr = pyads.NotificationAttrib(1)
        plc.add_device_notification('MAIN.qCyl1toMinus', attr, callback)
        plc.add_device_notification('MAIN.qCyl1toPlus', attr, callback)
        plc.add_device_notification('MAIN.qCyl2toMinus', attr, callback)
        plc.add_device_notification('MAIN.qCyl2toPlus', attr, callback)
        plc.add_device_notification('MAIN.qCyl3toMinus', attr, callback)
        plc.add_device_notification('MAIN.qCyl3toPlus', attr, callback)
        plc.add_device_notification('MAIN.qCyl4toMinus', attr, callback)
        plc.add_device_notification('MAIN.qCyl4toPlus', attr, callback)
        plc.add_device_notification('MAIN.qMot1start', attr, callback)
        plc.add_device_notification('MAIN.qMot2start', attr, callback)
        plc.add_device_notification('MAIN.qMot3start', attr, callback)
        plc.add_device_notification('MAIN.qMot4start', attr, callback)

class MoveCylinder(QtCore.QThread):
    """ Move the cylinder to minus/plus position. """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
    
    def animate_movement(self, cylinder, x1, x2, y):
        """ Animate the cylinder's movement. """
        self.animation = QtCore.QPropertyAnimation(cylinder, b'pos')
        self.animation.setDuration(1500) # 1.5 seconds
        self.animation.setStartValue(QtCore.QPoint(x1, y))
        self.animation.setEndValue(QtCore.QPoint(x2, y))
        self.animation.start()

class MoveMotors(QtCore.QThread):
    """ Move the motor left or right """
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def move_right(self, motor, yc):
        """ Turn the motor ON by moving it to the right. """
        self.anim_right = QtCore.QPropertyAnimation(motor, b'pos')
        self.anim_right.setDuration(3000)
        self.anim_right.setStartValue(QtCore.QPoint(380, yc))
        self.anim_right.setEndValue(QtCore.QPoint(400, yc))
        self.anim_right.start()

    def move_left(self, motor, yc):
        """ Turn the motor OFF by moving it the left. """
        self.anim_left = QtCore.QPropertyAnimation(motor, b'pos')
        self.anim_left.setDuration(3000)
        self.anim_left.setStartValue(QtCore.QPoint(400, yc))
        self.anim_left.setEndValue(QtCore.QPoint(380, yc))
        self.anim_left.start()

class UI_MainWindow(object):
    """ The user interface of the main window. """
  
    def init_ui(self, MainWindow):
        """ Initialize the user interface. """
        # Set the appearance of the window.
        MainWindow.setGeometry(QtCore.QRect(100, 100, 500, 640))
        MainWindow.setWindowIcon(QtGui.QIcon('icon.png'))
        MainWindow.setWindowTitle('Simulator')
        # Set font.
        self.font_arial = QtGui.QFont('Arial', 10)
        self.font_arial.setBold(True)
        # Pixmaps.
        self.cylinder = QtGui.QPixmap('cylinder.png')
        self.motor_off = QtGui.QPixmap('motor_off.png') # red
        self.motor_on = QtGui.QPixmap('motor_on.png') # green
        self.motor_ts = QtGui.QPixmap('motor_ts.png') # yellow (transition state)
        # Cylinders' minus and plus position.
        self.minus = 50
        self.plus = 200
        # Y-coordinates of the cylinders/motors.
        self.yc1 = 50
        self.yc2 = self.yc1 + 150
        self.yc3 = self.yc2 + 150
        self.yc4 = self.yc3 + 150
        # Input variables.
        self.iCyl1minus = False
        self.iCyl1plus = False
        self.iCyl2minus = False
        self.iCyl2plus = False
        self.iCyl3minus = False
        self.iCyl3plus = False
        self.iCyl4minus = False
        self.iCyl4plus = False
        self.iMot1running = False
        self.iMot2running = False
        self.iMot3running = False
        self.iMot4running = False
        # Output variables.
        self.qCyl1toMinus = False
        self.qCyl1toPlus = False
        self.qCyl2toMinus = False
        self.qCyl2toPlus = False
        self.qCyl3toMinus = False
        self.qCyl3toPlus = False
        self.qCyl4toMinus = False
        self.qCyl4toPlus = False
        self.qMot1start = False
        self.qMot2start = False
        self.qMot3start = False
        self.qMot4start = False
        # Create a centralwidget object.
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # Tabwidget configuration.
        self.tabwidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabwidget.setGeometry(QtCore.QRect(0, 0, 500, 620))
        # Setup the user interface of the tabs.
        self.setup_tab_1_ui()
        self.setup_tab_2_ui()
        # Display copyright information at the bottom of the window.
        self.lbl_footer = QtWidgets.QLabel(self.centralwidget)
        self.lbl_footer.setGeometry(QtCore.QRect(80, 620, 400, 20))
        self.lbl_footer.setText('Copyright (C) 2019 Seinäjoki University of Applied Sciences')
        # Set centralwidget.
        MainWindow.setCentralWidget(self.centralwidget)
        # Tab configuration.
        self.tabwidget.setCurrentIndex(0)
        self.tabwidget.setTabText(self.tabwidget.indexOf(self.tab_1), 'Simulation')
        self.tabwidget.setTabText(self.tabwidget.indexOf(self.tab_2), 'Settings')
        # Make sure that there is a working connection with the TwinCAT.
        self.check_connection_with_twincat()

    def check_connection_with_twincat(self):
        """ Check the connection with the TwinCAT message router. """
        try:
            self.connection = pyads.Connection(AMS_NET_ID, AMS_NET_PORT)
            self.connection.open()
            self.state = self.connection.read_state() # (adsState, deviceState)
        except pyads.pyads_ex.ADSError as error:
            # No connection.
            self.connection.close()
            self.open_messagebox_critical(error) # open a popup window
        else:
            if self.state[0] == 5:
                # Successfull connection.
                self.open_messagebox_information()
                self.start_threading()
                self.create_mover_instances()
            else:
                # Wrong port.
                self.connection.close()
                self.open_messagebox_critical('Wrong port number.')

    def open_messagebox_critical(self, error):
        """ Open a popup window which displays an error message. """
        title = 'ADS Connection Error'
        message = str(error) + '\nPlease, check AMS Net ID and AMS Net Port.'
        QtWidgets.QMessageBox.critical(self.centralwidget, title, message)
        # Open the 'Settings' tab when the user clicks 'OK'.
        if QtWidgets.QMessageBox.Ok:
            self.tabwidget.setCurrentIndex(1)

    def open_messagebox_information(self):
        """ Open a popup window, which displays an information message. """
        title = 'Information'
        message = 'Connected with the TwinCAT!'
        QtWidgets.QMessageBox.information(self.centralwidget, title, message)
        # Open the 'Simulation' tab when the user clicks 'OK'.
        if QtWidgets.QMessageBox.Ok:
            self.tabwidget.setCurrentIndex(0)

    def start_threading(self):
        """ Start the threads. """
        # Start a thread, which sends a signal periodically.
        self.timer = ReadTimer() # create an instance of the class
        self.timer.timer_signal.connect(self.actions_input) # connect the signal to the method
        self.timer.start() # start the thread
        # Start a thead, which sends a signal when the PLC variable changes its state.
        self.notification = DeviceNotification()
        self.notification.notification_signal.connect(self.actions_output)
        self.notification.start()

    def create_mover_instances(self):
        """ Create the instances for moving the elements on the window. """
        # Instances for moving the cylinders.
        self.mover_cyl1 = MoveCylinder()
        self.mover_cyl2 = MoveCylinder()
        self.mover_cyl3 = MoveCylinder()
        self.mover_cyl4 = MoveCylinder()
        # Instances for moving the motors.
        self.mover_mot1 = MoveMotors()
        self.mover_mot2 = MoveMotors()
        self.mover_mot3 = MoveMotors()
        self.mover_mot4 = MoveMotors()
    
    def button_clicked(self):
        """ Update ADS configuration. """
        if self.textbox_id.text():
            global AMS_NET_ID
            AMS_NET_ID = self.textbox_id.text() # read new Id from the textbox
            self.lbl_config_id.setText('AMS Net Id = ' + AMS_NET_ID) # update label text
        if self.textbox_port.text():
            global AMS_NET_PORT
            AMS_NET_PORT = int(self.textbox_port.text())
            self.lbl_config_port.setText('AMS Net Port = ' + str(AMS_NET_PORT))
        if self.textbox_id.text() or self.textbox_port.text():
            # Clear the textboxes.
            self.textbox_id.setText('')
            self.textbox_port.setText('')
            # Retry the connection with new value(s).
            self.check_connection_with_twincat()

    #-------------------------------------------------------------------------
    def setup_tab_1_ui(self):
        """ Setup the user interface on the first tab. """
        self.tab_1 = QtWidgets.QWidget()

        # Cylinder 1.
        self.lbl_c1 = QtWidgets.QLabel(self.tab_1)
        self.lbl_c1.setGeometry(QtCore.QRect(90, self.yc1 - 30, 80, 20))
        self.lbl_c1.setText('Cylinder 1')
        self.lbl_c1.setFont(self.font_arial)
        self.cylinder_1 = QtWidgets.QLabel(self.tab_1)
        self.cylinder_1.setGeometry(QtCore.QRect(self.minus, self.yc1, 150, 50))
        self.cylinder_1.setPixmap(self.cylinder)
        self.lbl_iCyl1minus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl1minus.setGeometry(QtCore.QRect(self.minus, self.yc1 + 50, 80, 20))
        self.lbl_iCyl1plus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl1plus.setGeometry(QtCore.QRect(self.plus, self.yc1 + 50, 80, 20))
        self.lbl_qCyl1toMinus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl1toMinus.setGeometry(QtCore.QRect(self.minus, self.yc1 + 70, 80, 20))
        self.lbl_qCyl1toPlus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl1toPlus.setGeometry(QtCore.QRect(self.plus, self.yc1 + 70, 80, 20))

        # Cylinder 2.
        self.lbl_c2 = QtWidgets.QLabel(self.tab_1)
        self.lbl_c2.setGeometry(QtCore.QRect(90, self.yc2 - 30, 80, 20))
        self.lbl_c2.setText('Cylinder 2')
        self.lbl_c2.setFont(self.font_arial)
        self.cylinder_2 = QtWidgets.QLabel(self.tab_1)
        self.cylinder_2.setGeometry(QtCore.QRect(self.minus, self.yc2, 150, 50))
        self.cylinder_2.setPixmap(self.cylinder)
        self.lbl_iCyl2minus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl2minus.setGeometry(QtCore.QRect(self.minus, self.yc2 + 50, 80, 20))
        self.lbl_iCyl2plus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl2plus.setGeometry(QtCore.QRect(self.plus, self.yc2 + 50, 80, 20))
        self.lbl_qCyl2toMinus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl2toMinus.setGeometry(QtCore.QRect(self.minus, self.yc2 + 70, 80, 20))
        self.lbl_qCyl2toPlus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl2toPlus.setGeometry(QtCore.QRect(self.plus, self.yc2 + 70, 80, 20))

        # Cylinder 3.
        self.lbl_c3 = QtWidgets.QLabel(self.tab_1)
        self.lbl_c3.setGeometry(QtCore.QRect(90, self.yc3 - 30, 80, 20))
        self.lbl_c3.setText('Cylinder 3')
        self.lbl_c3.setFont(self.font_arial)
        self.cylinder_3 = QtWidgets.QLabel(self.tab_1)
        self.cylinder_3.setGeometry(QtCore.QRect(self.minus, self.yc3, 150, 50))
        self.cylinder_3.setPixmap(self.cylinder)
        self.lbl_iCyl3minus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl3minus.setGeometry(QtCore.QRect(self.minus, self.yc3 + 50, 80, 20))
        self.lbl_iCyl3plus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl3plus.setGeometry(QtCore.QRect(self.plus, self.yc3 + 50, 80, 20))
        self.lbl_qCyl3toMinus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl3toMinus.setGeometry(QtCore.QRect(self.minus, self.yc3 + 70, 80, 20))
        self.lbl_qCyl3toPlus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl3toPlus.setGeometry(QtCore.QRect(self.plus, self.yc3 + 70, 80, 20))

        # Cylinder 4.
        self.lbl_c4 = QtWidgets.QLabel(self.tab_1)
        self.lbl_c4.setGeometry(QtCore.QRect(90, self.yc4 - 30, 80, 20))
        self.lbl_c4.setText('Cylinder 4')
        self.lbl_c4.setFont(self.font_arial)
        self.cylinder_4 = QtWidgets.QLabel(self.tab_1)
        self.cylinder_4.setGeometry(QtCore.QRect(self.minus, self.yc4, 150, 50))
        self.cylinder_4.setPixmap(self.cylinder)
        self.lbl_iCyl4minus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl4minus.setGeometry(QtCore.QRect(self.minus, self.yc4 + 50, 80, 20))
        self.lbl_iCyl4plus = QtWidgets.QLabel(self.tab_1)
        self.lbl_iCyl4plus.setGeometry(QtCore.QRect(self.plus, self.yc4 + 50, 80, 20))
        self.lbl_qCyl4toMinus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl4toMinus.setGeometry(QtCore.QRect(self.minus, self.yc4 + 70, 80, 20))
        self.lbl_qCyl4toPlus = QtWidgets.QLabel(self.tab_1)
        self.lbl_qCyl4toPlus.setGeometry(QtCore.QRect(self.plus, self.yc4 + 70, 80, 20))

        # Motor 1.
        self.lbl_m1 = QtWidgets.QLabel(self.tab_1)
        self.lbl_m1.setGeometry(QtCore.QRect(390, self.yc1 - 30, 80, 20))
        self.lbl_m1.setText('Motor 1')
        self.lbl_m1.setFont(self.font_arial)
        self.motor_1 = QtWidgets.QLabel(self.tab_1)
        self.motor_1.setGeometry(QtCore.QRect(380, self.yc1, 80, 50))
        self.motor_1.setPixmap(self.motor_off)
        self.lbl_iMot1running = QtWidgets.QLabel(self.tab_1)
        self.lbl_iMot1running.setGeometry(QtCore.QRect(380, self.yc1 + 50, 80, 20))
        self.lbl_qMot1start = QtWidgets.QLabel(self.tab_1)
        self.lbl_qMot1start.setGeometry(QtCore.QRect(380, self.yc1 + 70, 80, 20))

        # Motor 2.
        self.lbl_m2 = QtWidgets.QLabel(self.tab_1)
        self.lbl_m2.setGeometry(QtCore.QRect(390, self.yc2 - 30, 80, 20))
        self.lbl_m2.setText('Motor 2')
        self.lbl_m2.setFont(self.font_arial)
        self.motor_2 = QtWidgets.QLabel(self.tab_1)
        self.motor_2.setGeometry(QtCore.QRect(380, self.yc2, 80, 50))
        self.motor_2.setPixmap(self.motor_off)
        self.lbl_iMot2running = QtWidgets.QLabel(self.tab_1)
        self.lbl_iMot2running.setGeometry(QtCore.QRect(380, self.yc2 + 50, 80, 20))
        self.lbl_qMot2start = QtWidgets.QLabel(self.tab_1)
        self.lbl_qMot2start.setGeometry(QtCore.QRect(380, self.yc2 + 70, 80, 20))

        # Motor 3.
        self.lbl_m3 = QtWidgets.QLabel(self.tab_1)
        self.lbl_m3.setGeometry(QtCore.QRect(390, self.yc3 - 30, 80, 20))
        self.lbl_m3.setText('Motor 3')
        self.lbl_m3.setFont(self.font_arial)
        self.motor_3 = QtWidgets.QLabel(self.tab_1)
        self.motor_3.setGeometry(QtCore.QRect(380, self.yc3, 80, 50))
        self.motor_3.setPixmap(self.motor_off)
        self.lbl_iMot3running = QtWidgets.QLabel(self.tab_1)
        self.lbl_iMot3running.setGeometry(QtCore.QRect(380, self.yc3 + 50, 80, 20))
        self.lbl_qMot3start = QtWidgets.QLabel(self.tab_1)
        self.lbl_qMot3start.setGeometry(QtCore.QRect(380, self.yc3 + 70, 80, 20))

        # Motor 4.
        self.lbl_m4 = QtWidgets.QLabel(self.tab_1)
        self.lbl_m4.setGeometry(QtCore.QRect(390, self.yc4 - 30, 80, 20))
        self.lbl_m4.setText('Motor 4')
        self.lbl_m4.setFont(self.font_arial)
        self.motor_4 = QtWidgets.QLabel(self.tab_1)
        self.motor_4.setGeometry(QtCore.QRect(380, self.yc4, 80, 50))
        self.motor_4.setPixmap(self.motor_off)
        self.lbl_iMot4running = QtWidgets.QLabel(self.tab_1)
        self.lbl_iMot4running.setGeometry(QtCore.QRect(380, self.yc4 + 50, 80, 20))
        self.lbl_qMot4start = QtWidgets.QLabel(self.tab_1)
        self.lbl_qMot4start.setGeometry(QtCore.QRect(380, self.yc4 + 70, 80, 20))

        self.tabwidget.addTab(self.tab_1, '')
    
    #-------------------------------------------------------------------------
    def setup_tab_2_ui(self):
        """ Setup the user interface on the second tab. """
        self.tab_2 = QtWidgets.QWidget()

        self.lbl_info = QtWidgets.QLabel(self.tab_2)
        self.lbl_info.setGeometry(QtCore.QRect(20, 20, 150, 30))
        self.lbl_info.setText('Current configuration:')
        # Label showing the AMS Net Id currently in use.
        self.lbl_config_id = QtWidgets.QLabel(self.tab_2)
        self.lbl_config_id.setGeometry(QtCore.QRect(200, 20, 200, 30))
        self.lbl_config_id.setText('AMS Net Id = ' + AMS_NET_ID)
        # Label showing the AMS Net Port currently in use.
        self.lbl_config_port = QtWidgets.QLabel(self.tab_2)
        self.lbl_config_port.setGeometry(QtCore.QRect(200, 50, 200, 30))
        self.lbl_config_port.setText('AMS Net Port = ' + str(AMS_NET_PORT))

        self.lbl_update = QtWidgets.QLabel(self.tab_2)
        self.lbl_update.setGeometry(QtCore.QRect(20, 70, 150, 30))
        self.lbl_update.setText('Update values:')
        self.lbl_net_id = QtWidgets.QLabel(self.tab_2)
        self.lbl_net_id.setGeometry(QtCore.QRect(20, 110, 80, 30))
        self.lbl_net_id.setText('AMS Net Id')
        self.lbl_net_port = QtWidgets.QLabel(self.tab_2)
        self.lbl_net_port.setGeometry(QtCore.QRect(20, 150, 80, 30))
        self.lbl_net_port.setText('AMS Net Port')

        # Text input field for typing the AMS Net Id.
        self.textbox_id = QtWidgets.QLineEdit(self.tab_2)
        self.textbox_id.setGeometry(QtCore.QRect(120, 110, 150, 30))
        # Text input field for typing the AMS Net Port.
        self.textbox_port = QtWidgets.QLineEdit(self.tab_2)
        self.textbox_port.setGeometry(QtCore.QRect(120, 150, 150, 30))
        # Update Id/port when the button is clicked. 
        self.button = QtWidgets.QPushButton(self.tab_2)
        self.button.clicked.connect(self.button_clicked)
        self.button.setGeometry(QtCore.QRect(20, 200, 100, 30))
        self.button.setText('Update values')
        
        self.tabwidget.addTab(self.tab_2, '')

    #-------------------------------------------------------------------------
    def actions_input(self):
        """ Executed when the signal is received. """
        self.set_input_values()
        self.set_input_labels()
        self.set_motor_pixmaps()
        self.write_plc_inputs()

    def set_input_values(self):
        """ Set the inputs based on elements' location. """
        # Cylinders' minus position.
        self.iCyl1minus = True if self.cylinder_1.x() == self.minus else False
        self.iCyl2minus = True if self.cylinder_2.x() == self.minus else False
        self.iCyl3minus = True if self.cylinder_3.x() == self.minus else False
        self.iCyl4minus = True if self.cylinder_4.x() == self.minus else False
        # Cylinders' plus position.
        self.iCyl1plus = True if self.cylinder_1.x() == self.plus else False
        self.iCyl2plus = True if self.cylinder_2.x() == self.plus else False
        self.iCyl3plus = True if self.cylinder_3.x() == self.plus else False
        self.iCyl4plus = True if self.cylinder_4.x() == self.plus else False
        # Motors.
        if self.qMot1start and self.motor_1.x() == 400:
            self.iMot1running = True
        elif self.qMot1start is False and self.motor_1.x() == 380:
            self.iMot1running = False
        if self.qMot2start and self.motor_2.x() == 400:
            self.iMot2running = True
        elif self.qMot2start is False and self.motor_2.x() == 380:
            self.iMot2running = False
        if self.qMot3start and self.motor_3.x() == 400:
            self.iMot3running = True
        elif self.qMot3start is False and self.motor_3.x() == 380:
            self.iMot3running = False
        if self.qMot4start and self.motor_4.x() == 400:
            self.iMot4running = True
        elif self.qMot4start is False and self.motor_4.x() == 380:
            self.iMot4running = False

    def set_input_labels(self):
        """ Set the label texts of the PLC inputs. """
        self.lbl_iCyl1minus.setText('I0.0:' + str(self.iCyl1minus))
        self.lbl_iCyl1plus.setText('I0.1:' + str(self.iCyl1plus))
        self.lbl_iMot1running.setText('I0.2:' + str(self.iMot1running))

        self.lbl_iCyl2minus.setText('I0.3:' + str(self.iCyl2minus))
        self.lbl_iCyl2plus.setText('I0.4:' + str(self.iCyl2plus))
        self.lbl_iMot2running.setText('I0.5:' + str(self.iMot2running))

        self.lbl_iCyl3minus.setText('I1.0:' + str(self.iCyl3minus))
        self.lbl_iCyl3plus.setText('I1.1:' + str(self.iCyl3plus))
        self.lbl_iMot3running.setText('I1.2:' + str(self.iMot3running))

        self.lbl_iCyl4minus.setText('I1.3:' + str(self.iCyl4minus))
        self.lbl_iCyl4plus.setText('I1.4:' + str(self.iCyl4plus))
        self.lbl_iMot4running.setText('I1.5:' + str(self.iMot4running))

    def set_motor_pixmaps(self):
        """ Set motor's pixmap based on motor's location. """
        if self.motor_1.x() == 380:
            self.motor_1.setPixmap(self.motor_off) # red motor
        elif self.motor_1.x() == 400:
            self.motor_1.setPixmap(self.motor_on) # green motor
        else:
            self.motor_1.setPixmap(self.motor_ts) # yellow motor

        if self.motor_2.x() == 380:
            self.motor_2.setPixmap(self.motor_off)
        elif self.motor_2.x() == 400:
            self.motor_2.setPixmap(self.motor_on)
        else:
            self.motor_2.setPixmap(self.motor_ts)

        if self.motor_3.x() == 380:
            self.motor_3.setPixmap(self.motor_off)
        elif self.motor_3.x() == 400:
            self.motor_3.setPixmap(self.motor_on)
        else:
            self.motor_3.setPixmap(self.motor_ts)

        if self.motor_4.x() == 380:
            self.motor_4.setPixmap(self.motor_off)
        elif self.motor_4.x() == 400:
            self.motor_4.setPixmap(self.motor_on)
        else:
            self.motor_4.setPixmap(self.motor_ts)

    def write_plc_inputs(self):
        """ Write the PLC inputs. """
        # Cylinders.
        self.connection.write_by_name('MAIN.iCyl1minus', self.iCyl1minus, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iCyl1plus', self.iCyl1plus, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iCyl2minus', self.iCyl2minus, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iCyl2plus', self.iCyl2plus, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iCyl3minus', self.iCyl3minus, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iCyl3plus', self.iCyl3plus, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iCyl4minus', self.iCyl4minus, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iCyl4plus', self.iCyl4plus, pyads.PLCTYPE_BOOL)
        # Motors.
        self.connection.write_by_name('MAIN.iMot1running', self.iMot1running, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iMot2running', self.iMot2running, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iMot3running', self.iMot3running, pyads.PLCTYPE_BOOL)
        self.connection.write_by_name('MAIN.iMot4running', self.iMot4running, pyads.PLCTYPE_BOOL)

    #-------------------------------------------------------------------------
    def actions_output(self, received_notification_data):
        """ Executed when the signal is received from the thread. """
        self.set_output_values(received_notification_data)
        self.set_output_labels()
        self.move_cylinders()
        self.move_motors()

    def set_output_values(self, received_notification_data):
        """ Set the outputs based on PLC outputs. """
        # Read name and value of the PLC variable.
        name = received_notification_data['name']
        value = received_notification_data['value']
        # Cylinder outputs.
        if name == 'MAIN.qCyl1toMinus':
            self.qCyl1toMinus = value
        elif name == 'MAIN.qCyl1toPlus':
            self.qCyl1toPlus = value
        elif name == 'MAIN.qCyl2toMinus':
            self.qCyl2toMinus = value
        elif name == 'MAIN.qCyl2toPlus':
            self.qCyl2toPlus = value
        elif name == 'MAIN.qCyl3toMinus':
            self.qCyl3toMinus = value
        elif name == 'MAIN.qCyl3toPlus':
            self.qCyl3toPlus = value
        elif name == 'MAIN.qCyl4toMinus':
            self.qCyl4toMinus = value
        elif name == 'MAIN.qCyl4toPlus':
            self.qCyl4toPlus = value
        # Motor outputs.
        elif name == 'MAIN.qMot1start':
            self.qMot1start = value
        elif name == 'MAIN.qMot2start':
            self.qMot2start = value
        elif name == 'MAIN.qMot3start':
            self.qMot3start = value
        elif name == 'MAIN.qMot4start':
            self.qMot4start = value

    def set_output_labels(self):
        """ Set the label texts of the PLC outputs. """
        # Cylinders.
        self.lbl_qCyl1toMinus.setText('Q0.0:' + str(self.qCyl1toMinus))
        self.lbl_qCyl1toPlus.setText('Q0.1:' + str(self.qCyl1toPlus))
        self.lbl_qCyl2toMinus.setText('Q0.3:' + str(self.qCyl2toMinus))
        self.lbl_qCyl2toPlus.setText('Q0.4:' + str(self.qCyl2toPlus))
        self.lbl_qCyl3toMinus.setText('Q1.0:' + str(self.qCyl3toMinus))
        self.lbl_qCyl3toPlus.setText('Q1.1:' + str(self.qCyl3toPlus))
        self.lbl_qCyl4toMinus.setText('Q1.3:' + str(self.qCyl4toMinus))
        self.lbl_qCyl4toPlus.setText('Q1.4:' + str(self.qCyl4toPlus))
        # Motors.
        self.lbl_qMot1start.setText('Q0.2:' + str(self.qMot1start))
        self.lbl_qMot2start.setText('Q0.5:' + str(self.qMot2start))
        self.lbl_qMot3start.setText('Q1.2:' + str(self.qMot3start))
        self.lbl_qMot4start.setText('Q1.5:' + str(self.qMot4start))

    def move_cylinders(self):
        """ Move the cylinders based on PLC outputs. """
        if self.iCyl1plus and self.qCyl1toMinus:
            self.mover_cyl1.animate_movement(self.cylinder_1, self.plus, self.minus, self.yc1)
        if self.iCyl1minus and self.qCyl1toPlus:
            self.mover_cyl1.animate_movement(self.cylinder_1, self.minus, self.plus, self.yc1)
        if self.iCyl2plus and self.qCyl2toMinus:
            self.mover_cyl2.animate_movement(self.cylinder_2, self.plus, self.minus, self.yc2)
        if self.iCyl2minus and self.qCyl2toPlus:
            self.mover_cyl2.animate_movement(self.cylinder_2, self.minus, self.plus, self.yc2)
        if self.iCyl3plus and self.qCyl3toMinus:
            self.mover_cyl3.animate_movement(self.cylinder_3, self.plus, self.minus, self.yc3)
        if self.iCyl3minus and self.qCyl3toPlus:
            self.mover_cyl3.animate_movement(self.cylinder_3, self.minus, self.plus, self.yc3)
        if self.iCyl4plus and self.qCyl4toMinus:
            self.mover_cyl4.animate_movement(self.cylinder_4, self.plus, self.minus, self.yc4)
        if self.iCyl4minus and self.qCyl4toPlus:
            self.mover_cyl4.animate_movement(self.cylinder_4, self.minus, self.plus, self.yc4)

    def move_motors(self):
        """ Move the motors based on PLC outputs. """
        # Start the motor by moving it to the right.
        if self.iMot1running is False and self.qMot1start:
            self.mover_mot1.move_right(self.motor_1, self.yc1)
        if self.iMot2running is False and self.qMot2start:
            self.mover_mot2.move_right(self.motor_2, self.yc2)
        if self.iMot3running is False and self.qMot3start:
            self.mover_mot3.move_right(self.motor_3, self.yc3)
        if self.iMot4running is False and self.qMot4start:
            self.mover_mot4.move_right(self.motor_4, self.yc4)
        # Stop the motor by moving it to the left.
        if self.iMot1running and self.qMot1start is False:
            self.mover_mot1.move_left(self.motor_1, self.yc1)
        if self.iMot2running and self.qMot2start is False:
            self.mover_mot2.move_left(self.motor_2, self.yc2)
        if self.iMot3running and self.qMot3start is False:
            self.mover_mot3.move_left(self.motor_3, self.yc3)
        if self.iMot4running and self.qMot4start is False:
            self.mover_mot4.move_left(self.motor_4, self.yc4)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    window = UI_MainWindow()
    window.init_ui(main_window)
    main_window.show()
    sys.exit(app.exec_())
