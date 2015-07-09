#! python
import os
import sys
from os.path import join, dirname, isdir
import glob
import h5py
import pdb
import time
import numpy as np
import platform
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import Slider, RadioButtons
import re
import pickle
from functools import partial
import pygame

from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from shapely.geometry import MultiPolygon, Polygon
#from shapely.topology import TopologicalError
#from skimage import transform as tf
#import itertools as it
#from random import shuffle
#import warnings as wa

import c843_class
import LandNSM5

# files
from manipulator.py import Ui_MainWindow
#from internal_ipkernel import InternalIPKernel


#################################################################
class manipulatorControl(QMainWindow, Ui_MainWindow):
    """Instance of the hdf5 Data Manager Qt interface."""
    def __init__(self):
        
        self.today_date = time.strftime("%Y%m%d")[2:]
        """
        Initialize the application
        """
        # initialize the UI and parent class
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle('Manipulator Control')
        #
        self.create_status_bar()
        # 
        self.connectSignals()
        
        # read settings file if it exists
        #try :
        #	h5Settings = pickle.load(open('.h5Settings.p','rb'))
        #except IOError:
        #	print 'No settings fils found.'
        #	setExits = False
        #else:
        #	setExits = True
        self.cells = {}
        # precision of values to show and store
        self.precision = 1
        
        # movement parameters
        self.stepWidths = {'fine':1.,'small':10.,'medium':100.,'coarse':1000.}
        #self.fineStep = 1.
        #self.smallStep = 10.
        #self.mediumStep = 100.
        #self.coarseStep = 1000.
        
        self.speeds = {'fine':0.01,'small':0.05,'medium':0.2,'coarse':1.5}
        
        self.defaultMoveSpeed = 'fine'
        #self.fineSpeed =  np.array([0.01,0.01,0.01])
        #self.smallSpeed =  np.array([0.05,0.05,0.05])
        #self.mediumSpeed = np.array([0.5,0.5,0.5])
        #self.coarseSpeed = np.array([1.5,1.5,2.])
        
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        
        if setExits:
            DDir = h5Settings['dataDirectory']
            if os.path.isdir(DDir):
                self.dataDirectory = DDir
                self.fillOutFileList()
        
        # configure column widths in cellListTable
        self.cellListTable.setColumnWidth(0,30)
        self.cellListTable.setColumnWidth(1,38)
        self.cellListTable.setColumnWidth(2,30)
        self.cellListTable.setColumnWidth(3,58)
        self.cellListTable.setColumnWidth(4,150)
        
        #self.saveAttributeChangeBtn.setEnabled(False)
        #self.restoreAttributesBtn.setEnabled(False)
        
        #self.saveNotesBtn.setEnabled(False)
        #self.restoreNotesBtn.setEnabled(False)
    
    #################################################################################################
    # destroy class instances
    def __del__(self):
        # sutter class
        try: 
            self.c843
        except AttributeError:
            pass
        else:
            del self.c843
        # tdt class
        try: 
            self.luigsNeumann
        except AttributeError:
            pass
        else:
            del self.luigsNeumann
    
    ####################################################
    # set status bar
    def create_status_bar(self):
        self.statusBar().addWidget(QLabel("Ready"), 1)
        
    ####################################################
    # connect signals to actions
    def connectSignals(self):
        
        ################################################
        # Connection panel 
        self.connectBtn.clicked.connect(self.connectSM5_c843)
        self.C843XYPowerBtn.clicked.connect(partial(self.switchOnOffC843Motors,'xy'))
        self.C843ZPowerBtn.clicked.connect(partial(self.switchOnOffC843Motors,'z'))
        self.SM5_1PowerBtn.clicked.connect(partial(self.switchOnOffSM5Motors,1))
        self.SM5_2PowerBtn.clicked.connect(partial(self.switchOnOffSM5Motors,2))
        
        #self.yzPowerBtn.clicked.connect(self.yzPower)
        #self.xPowerBtn.clicked.connect(self.xPower)
        #self.x1PosStepBtn.clicked.connect(self.x1PosStep)
        #self.x1NegStepBtn.clicked.connect(self.x1NegStep)
        #self.x2PosStepBtn.clicked.connect(self.x2PosStep)
        #self.x2NegStepBtn.clicked.connect(self.x2NegStep)
        
        self.refLocationBtn.clicked.connect(self.referenceLocations)
        self.refPositiveBtn.clicked.connect(self.referencePositiveMove)
        self.refNegativeBtn.clicked.connect(self.referenceNegativeMove)
        
        ################################################
        # Move panel
        self.controlerActivateBtn.clicked.connect(self.activateControler)
        
        self.fineBtn.clicked.connect(partial(self.setMovementValues,'fine'))
        self.smallBtn.clicked.connect(partial(self.setMovementValues,'small'))
        self.mediumBtn.clicked.connect(partial(self.setMovementValues,'medium'))
        self.coarseBtn.clicked.connect(partial(self.setMovementValues,'coarse'))
        self.stepLineEdit.textChanged.connect(self.getMovementValues)
        self.speedLineEdit.textChanged.connect(self.getMovementValues)
        
    #################################################################################################
    def connectSM5_c843(self):
        
        self.setStatusMessage('initializing stages')
        ############################################
        # c843
        try :
            self.c843
        except AttributeError:
            self.c843 = c843_class.c843_class()
            self.c843.init_stage(1)
            self.c843.init_stage(2)
            self.c843.init_stage(3)
            self.switchOnOffC843Motors('xy')
            self.switchOnOffC843Motors('z')
            #self.connectBtn.setChecked(True)
            self.connectBtn.setText('Disconnect SM-5 and C-843')
            self.enableReferenceButtons()
        else:
            if self.activate.is_alive():
                self.controlerActivateBtn.setChecked(False)
                self.controlerActivateBtn.setText('Activate Controller')
                self.done=True
                #self.activate._stop()
                self.activate = Thread(target=self.controlerInput)
                #self.activate = Thread(ThreadStart(self.controlerInput))
                print 'controller deactive'
            del self.c843
            #self.connectBtn.setChecked(False)
            self.connectBtn.setText('Connect SM-5 and C-843')
            self.switchOnOffC843Motors('xy')
            self.switchOnOffC843Motors('z')
            #self.disableButtons()
            #self.motorPowerBtn.setEnabled(False)
        
        # SM5
        try :
            self.luigsNeumann
        except AttributeError:
            self.luigsNeumann = LandNSM5.LandNSM5()
            self.switchOnOffSM5Motors(1)
            self.switchOnOffSM5Motors(2)
        else:
            del self.luigsNeumann
            self.switchOnOffSM5Motors(1)
            self.switchOnOffSM5Motors(2)
        #
        self.unSetStatusMessage('initializing stages')

    #################################################################################################
    def switchOnOffC843Motors(self,axes):
        # if active : deactivate controler first
        if self.activate.is_alive():
            self.activateControler()
        # switch on or off motors
        if axes == 'xy':
            self.c843.switch_servo_on_off(2)
            self.c843.switch_servo_on_off(1)
            if C843XYPowerBtn.isChecked():
                self.C843XYPowerBtn.setText('Switch Off XY')
            else:
                self.C843XYPowerBtn.setText('Switch On XY')
        #
        elif axes=='z':
            self.c843.switch_servo_on_off(3)
            if C843ZPowerBtn.isChecked():
                self.C843XYPowerBtn.setText('Switch Off Z')
            else:
                self.C843XYPowerBtn.setText('Switch On Z')
    #################################################################################################
    def switchOnOffSM5Motors(self,device):
        if SM5_1PowerBtn.isChecked():
            self.luigsNeumann.switchOnAxis(1,'x')
            self.luigsNeumann.switchOnAxis(1,'y')
            self.luigsNeumann.switchOnAxis(1,'z')
        elif not SM5_1PowerBtn.isChecked():
            self.luigsNeumann.switchOffAxis(1,'x')
            self.luigsNeumann.switchOffAxis(1,'y')
            self.luigsNeumann.switchOffAxis(1,'z')
        
        if SM5_2PowerBtn.isChecked():
            self.luigsNeumann.switchOnAxis(2,'x')
            self.luigsNeumann.switchOnAxis(2,'y')
            self.luigsNeumann.switchOnAxis(2,'z')
        elif not SM5_2PowerBtn.isChecked():
            self.luigsNeumann.switchOffAxis(2,'x')
            self.luigsNeumann.switchOffAxis(2,'y')
            self.luigsNeumann.switchOffAxis(2,'z')
    #################################################################################################
    def referenceLocations(self):
        #
        self.setStatusMessage('referencing axes using location')
        #
        ref1 = self.c843.reference_stage(1,False,'neg')
        ref2 = self.c843.reference_stage(2,False,'neg')
        ref3 = self.c843.reference_stage(3,False,'neg')
        if not all((ref1,ref2,ref3)):
            reply = QtGui.QMessageBox.warning(self, 'Warning','Reference with saved locations failed.',  QtGui.QMessageBox.Ok )
            #break
        else:
            #self.refLabel.setText('xyz referenced')
            self.refLocationBtn.setEnabled(False)
            #self.refPositiveBtn.setEnabled(False)
            #self.refNegativeBtn.setEnabled(False)
            self.updateStageLocations()
            self.initializeStageSpeed()
        #
        self.unSetStatusMessage('referencing axes using location')

    #################################################################################################
    def referencePositiveMove(self):
        #
        self.setStatusMessage('referencing axes to pos. limit')
        #
        ref1 = self.c843.reference_stage(1,True,'pos')
        ref2 = self.c843.reference_stage(2,True,'pos')
        ref3 = self.c843.reference_stage(3,True,'pos')
        if not all((ref1,ref2,ref3)):
            reply = QtGui.QMessageBox.warning(self, 'Warning','Reference at pos. limit failed.',  QtGui.QMessageBox.Ok )
        else:
            #self.refLabel.setText('xyz referenced')
            self.refLocationBtn.setEnabled(False)
            self.refPositiveBtn.setEnabled(False)
            self.refNegativeBtn.setEnabled(False)
            self.updateStageLocations()
            self.initializeStageSpeed()
        #
        self.unSetStatusMessage('referencing axes to pos. limit')
        #
    #################################################################################################
    def referenceNegativeMove(self):
        #
        self.setStatusMessage('referencing axes to neg. limit')
        #
        ref1 = self.c843.reference_stage(1,True,'neg')
        ref2 = self.c843.reference_stage(2,True,'neg')
        ref3 = self.c843.reference_stage(3,True,'neg')
        if not all((ref1,ref2,ref3)):
            reply = QtGui.QMessageBox.warning(self, 'Warning','Reference at neg. limit failed.',  QtGui.QMessageBox.Ok )
        else:
            #self.refLabel.setText('xyz referenced')
            self.refLocationBtn.setEnabled(False)
            self.refPositiveBtn.setEnabled(False)
            self.refNegativeBtn.setEnabled(False)
            self.updateStageLocations()
            self.initializeStageSpeed()
        #
        self.unSetStatusMessage('referencing axes to neg. limit')
    
    #################################################################################################
    def updateStageLocations(self):
        #
        self.isX = self.c843.get_position(1)
        self.isY = self.c843.get_position(2)
        self.isZ = self.c843.get_position(3)
        #
        self.isXLocationValueLabel.setText(str(round(self.isX,self.precision)))
        self.isYLocationValueLabel.setText(str(round(self.isY,self.precision)))
        self.isZLocationValueLabel.setText(str(round(self.isZ,self.precision)))
        
        self.setX = self.isX
        self.setY = self.isY
        self.setZ = self.isZ
        self.setXLocationLineEdit.setText(str(round(self.setX,self.precision)))
        self.setYLocationLineEdit.setText(str(round(self.setY,self.precision)))
        self.setZLocationLineEdit.setText(str(round(self.setY,self.precision)))
        
        if self.isHomeSet :
            self.homeXLocationValue.setText(str(round(self.isX-self.homeP[0],self.precision)))
            self.homeYLocationValue.setText(str(round(self.isY-self.homeP[1],self.precision)))
            self.homeZLocationValue.setText(str(round(self.isZ-self.homeP[2],self.precision)))
        
    #################################################################################################
    def initializeStageSpeed(self):
        # read maximal and minimal values
        (self.xMin,self.xMax) = self.c843.get_min_max_travel_range(1)
        (self.yMin,self.yMax) = self.c843.get_min_max_travel_range(2)
        (self.zMin,self.zMax) = self.c843.get_min_max_travel_range(3)
        
        self.minMaxXLocationValueLabel.setText(str(round(self.xMax,self.precision)))
        self.minMaxYLocationValueLabel.setText(str(round(self.yMax,self.precision)))
        self.minMaxZLocationValueLabel.setText(str(round(self.zMax,self.precision)))
        
        # set default move and speed
        self.setMovements(self.defaultMoveSpeed)

        #self.enableButtons()
    #################################################################################################
    def setMovementValues(self,moveSize):
        self.moveStep = self.stepWidths[moveSize]
        self.moveSpeed = self.speeds[moveSize]
        self.stepLineEdit.setText(str(self.moveStep))
        self.speedLineEdit.setText(str(self.moveSpeed))
        self.propagateSpeeds()
    #################################################################################################
    def getMovementValues(self,moveSize):
        self.moveStep = float(self.stepLineEdit.text())
        self.moveSpeed = float(self.speedLineEdit.text())
        self.propagateSpeeds()
    #################################################################################################
    def propagateSpeeds(self):
        self.c843.set_velocity(1,self.moveSpeed)
        self.c843.set_velocity(2,self.moveSpeed)
        self.c843.set_velocity(3,self.moveSpeed)
        # change color according to selection
        #self.fineBtn.setChecked(True)
        #self.smallBtn.setChecked(False)
        #self.mediumBtn.setChecked(False)
        #self.coarseBtn.setChecked(False)
        #self.fineBtn.repaint()
        #self.mediumBtn.repaint()
        #self.coarseBtn.repaint()
    #################################################################################################
    def setStatusMessage(self,statusText):
        self.statusValue.setText(statusText+' ...')
        self.statusValue.setStyleSheet('color: red')
        self.statusValue.repaint()
    #################################################################################################
    def unSetStatusMessage(self,statusText):
        self.statusValue.setText(statusText+' ... done')
        self.statusValue.setStyleSheet('color: black')
    #self.statusValue.repaint()


##########################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = manipulatorControl()
    form.show()
    app.exec_()
    
    