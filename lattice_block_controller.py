import sys, os
import serial
from serial.tools import list_ports
from PySide2 import QtCore, QtWidgets
from maestro import *

class lattice_block_gui(QtWidgets.QMainWindow):
    chan = 0
    direct_pos = 1500*4
    nothing_pos = 1094*4
    indirect_pos = 611*4
    max_spd = 15
    min_pos = 600*4
    max_pos = 1500*4

    def __init__(self, Parent=None):
        super(lattice_block_gui, self).__init__(Parent)
        self.setWindowTitle("Lattice Beam Block Controller")
        self.initialize()

    def initialize(self):
        # Select and initialize serial port
        ports = list_ports.comports()
        port_names = [p.name+": "+ p.description for p in ports]
        port, ok = QtWidgets.QInputDialog.getItem(self, "Select Maestro Port", "Select Maestro Port", port_names, 0, False)
        if not ok:
            sys.exit()
        try:
            self.controller = Controller('/dev/'+port.partition(":")[0])
        except Exception as e:
            print(e)
            msg = QtWidgets.QMessageBox()
            msg.setText("Could not connect! Sad.")
            msg.exec_()
            sys.exit()
        
        self.controller.setRange(self.chan, self.min_pos, self.max_pos)
        self.controller.setSpeed(self.chan, self.max_spd)
        self.controller.setTarget(self.chan, self.nothing_pos)

        main = QtWidgets.QHBoxLayout()

        self.dir_button = QtWidgets.QPushButton()
        self.dir_button.setText("Block direct")
        self.dir_button.pressed.connect(self.direct)
        main.addWidget(self.dir_button)

        self.indir_button = QtWidgets.QPushButton()
        self.indir_button.setText("Block indirect")
        self.indir_button.pressed.connect(self.indirect)
        main.addWidget(self.indir_button)

        self.none_button = QtWidgets.QPushButton()
        self.none_button.setText("Block nothing")
        self.none_button.pressed.connect(self.nothing)
        self.none_button.setEnabled(False)
        main.addWidget(self.none_button)
        
        mainWidget = QtWidgets.QWidget()
        mainWidget.setLayout(main)
        self.setCentralWidget(mainWidget)

    def direct(self):
        print("blocking direct!")
        self.controller.setTarget(self.chan, self.direct_pos)
        self.none_button.setEnabled(True)
        self.dir_button.setEnabled(False)
        self.indir_button.setEnabled(True)

    def indirect(self):
        print("blocking indirect!")
        self.controller.setTarget(self.chan, self.indirect_pos)
        self.none_button.setEnabled(True)
        self.dir_button.setEnabled(True)
        self.indir_button.setEnabled(False)

    def nothing(self):
        print("blocking nothing!")
        self.controller.setTarget(self.chan, self.nothing_pos)
        self.none_button.setEnabled(False)
        self.dir_button.setEnabled(True)
        self.indir_button.setEnabled(True)

    def status(self):
        pass
        # print(self.controller.getPosition(self.chan))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Set up window
    w = lattice_block_gui()
    # w.setGeometry(100, 100, 1200, 380)
    w.show()

    # Call Python every 100 ms and print the position so Ctrl-c works
    timer = QtCore.QTimer()
    timer.timeout.connect(w.status)
    timer.start(100)

    # Run event loop
    ret = app.exec_()
    if w.controller is not None:
        w.controller.close()
    sys.exit(ret)
