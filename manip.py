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
from threading import *
import re
import pickle
from functools import partial
import pygame
import socket
import select
import collections

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
from manipulator import Ui_MainWindow
#from internal_ipkernel import InternalIPKernel

#sm5lock = Lock()

#################################################################
class manipulatorControl(QMainWindow, Ui_MainWindow, Thread):
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
        self.setGeometry(10, 30,537,971)
        #
        #self.create_status_bar()
        # 
        self.connectSignals()
        
        # read settings file if it exists
        #try :
        #	h5Settings = pickle.load(open('.h5Settings.p','rb'))
        #except IOError:
        #	print 'No settings fils found.'
        #	setExits = False
        #else:

        self.rowHeight = 16

        self.homeLocs = {}
        self.nHomeItem = 0
        self.rowHomeC = 4
        self.homeLocationsTable.setRowCount(self.rowHomeC)
        for i in range(self.rowHomeC):
            self.homeLocationsTable.setRowHeight(i,self.rowHeight)
        self.homeLocationsTable.setSelectionMode(self.homeLocationsTable.ContiguousSelection)
        self.homeLocationsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.homeLocationsTable.setColumnWidth(0,30)
        self.homeLocationsTable.setColumnWidth(1,100)
        self.homeLocationsTable.setColumnWidth(2,100)
        self.homeLocationsTable.setColumnWidth(3,100)
        
        self.cells = {}
        self.nItem = 0
        self.rowC = 6
        
        self.cellListTable.setRowCount(self.rowC)
        for i in range(self.rowC):
            self.cellListTable.setRowHeight(i,self.rowHeight)
        self.cellListTable.setSelectionMode(self.cellListTable.ContiguousSelection)
        self.cellListTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # parameters for socket connection
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a socket object
        host = '172.20.61.89' #socket.gethostname() #Get the local machine name
        port = 5555 # Reserve a port for your service
        self.s.bind((host,port)) #Bind to the port
        
        # precision of values to show and store
        self.precision = 1
        self.locationDiscrepancy = 0.1
        # angles of the manipulators with respect to a vertical line
        self.alphaDev1 = 30.
        self.alphaDev2 = 30.
        self.manip1MoveStep = 2.
        self.manip2MoveStep = 2.
        
        self.axes         = np.array(['x','y','z'])
        self.stageAxes    = collections.OrderedDict([('x',2),('y',1),('z',3)])
        self.stageNumbers = collections.OrderedDict([(0,self.stageAxes['x']),(1,self.stageAxes['y']),(2,self.stageAxes['z'])])
        
        self.defaultPosition = np.array([12000.,12000.,6000.])
        
        # movement parameters
        self.stepWidths = collections.OrderedDict([('fine',1.),('small',10.),('medium',100.),('coarse',1000.)])
        #self.fineStep = 1.
        #self.smallStep = 10.
        #self.mediumStep = 100.
        #self.coarseStep = 1000.
        
        self.speeds = collections.OrderedDict([('fine',0.01),('small',0.05),('medium',0.2),('coarse',1.5)])
        
        self.defaultMoveSpeed = 'fine'
        #self.fineSpeed =  np.array([0.01,0.01,0.01])
        #self.smallSpeed =  np.array([0.05,0.05,0.05])
        #self.mediumSpeed = np.array([0.5,0.5,0.5])
        #self.coarseSpeed = np.array([1.5,1.5,2.])
        
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        
        #if setExits:
        #    DDir = h5Settings['dataDirectory']
        #    if os.path.isdir(DDir):
        #        self.dataDirectory = DDir
        #        self.fillOutFileList()
        
        # configure column widths in cellListTable
        self.cellListTable.setColumnWidth(0,30)
        self.cellListTable.setColumnWidth(1,38)
        self.cellListTable.setColumnWidth(2,30)
        self.cellListTable.setColumnWidth(3,58)
        self.cellListTable.setColumnWidth(4,150)
        
        self.activate = Thread(target=self.controlerInput)
        
        self.autoUpdateManipulatorLocations = Thread(target=self.autoUpdateManip)
        self.sm5Lock = Lock()
        
        self.listenThread = Thread(target=self.socketListening)
        self.c843Lock = Lock()
        
        self.disableAndEnableBtns(False)
        self.enableDiableControllerBtns(False)
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
    # connect signals to actions
    def connectSignals(self):
        
        ################################################
        # Connection panel 
        self.connectBtn.clicked.connect(self.connectSM5_c843)
        self.C843XYPowerBtn.clicked.connect(partial(self.switchOnOffC843Motors,'xy'))
        self.C843ZPowerBtn.clicked.connect(partial(self.switchOnOffC843Motors,'z'))
        self.SM5Dev1PowerBtn.clicked.connect(partial(self.switchOnOffSM5Motors,1))
        self.SM5Dev2PowerBtn.clicked.connect(partial(self.switchOnOffSM5Motors,2))
        
        #self.yzPowerBtn.clicked.connect(self.yzPower)
        #self.xPowerBtn.clicked.connect(self.xPower)
        #self.x1PosStepBtn.clicked.connect(self.x1PosStep)
        #self.x1NegStepBtn.clicked.connect(self.x1NegStep)
        #self.x2PosStepBtn.clicked.connect(self.x2PosStep)
        #self.x2NegStepBtn.clicked.connect(self.x2NegStep)
        
        self.refChoseLocationBtn.clicked.connect(self.referenceChoseLocations)
        self.refSavedLocationBtn.clicked.connect(partial(self.referenceStage,False))
        self.refNegativeBtn.clicked.connect(partial(self.referenceStage,True))
        
        ################################################
        # Move panel
        self.controllerActivateBtn.clicked.connect(self.activateController)
        self.listenToSocketBtn.clicked.connect(self.listenToSocket)
        
        self.fineBtn.clicked.connect(partial(self.setMovementValues,'fine'))
        self.smallBtn.clicked.connect(partial(self.setMovementValues,'small'))
        self.mediumBtn.clicked.connect(partial(self.setMovementValues,'medium'))
        self.coarseBtn.clicked.connect(partial(self.setMovementValues,'coarse'))
        self.stepLineEdit.editingFinished.connect(self.getStepValue)
        self.speedLineEdit.editingFinished.connect(self.getSpeedValue)
        
        self.device1StepLE.editingFinished.connect(self.setManiplatorStep)
        self.device2StepLE.editingFinished.connect(self.setManiplatorStep)
        
        self.device1SpeedLE.editingFinished.connect(partial(self.setManiplatorSpeed,1))
        self.device2SpeedLE.editingFinished.connect(partial(self.setManiplatorSpeed,2))
        
        ################################################
        # Location panel 
        self.electrode1MLIBtn.clicked.connect(partial(self.recordCell,1,'MLI'))
        self.electrode1PCBtn.clicked.connect(partial(self.recordCell,1,'PC'))
        self.electrode2MLIBtn.clicked.connect(partial(self.recordCell,2,'MLI'))
        self.electrode2PCBtn.clicked.connect(partial(self.recordCell,2,'PC'))
        
        self.moveToItemBtn.clicked.connect(self.moveToLocation)
        self.updateItemLocationBtn.clicked.connect(self.updateLocation)
        self.recordDepthBtn.clicked.connect(self.recordDepth)
        self.removeItemBtn.clicked.connect(self.removeLocation)
        self.saveLocationsBtn.clicked.connect(self.saveLocations)
        self.loadLocationsBtn.clicked.connect(self.loadLocations)
        
        self.recordHomeLocationBtn.clicked.connect(self.recordHomeLocation)
        self.updateHomeLocationBtn.clicked.connect(self.updateHomeLocation)
        self.moveToHomeLocationBtn.clicked.connect(self.moveToHomeLocation)
        self.removeHomeLocationBtn.clicked.connect(self.removeHomeLocation)
        
                
    #################################################################################################
    def connectSM5_c843(self):
        
        self.setStatusMessage('initializing stages')
        ############################################
        # c843
        try :
            self.c843
        except AttributeError:
            self.c843 = c843_class.c843_class()
            self.c843.init_stage(self.stageAxes['x'])
            self.c843.init_stage(self.stageAxes['y'])
            self.c843.init_stage(self.stageAxes['z'])
            self.isStage = np.zeros(3)
            self.setStage = np.zeros(3)
            #self.switchOnOffC843Motors('xy')
            #self.switchOnOffC843Motors('z')
            #self.connectBtn.setChecked(True)
            self.C843XYPowerBtn.setChecked(True)
            self.C843ZPowerBtn.setChecked(True)
            self.SM5Dev1PowerBtn.setChecked(True)
            self.SM5Dev2PowerBtn.setChecked(True)
            #self.connectBtn.setText('Disconnect SM-5 and C-843')
            self.enableReferencePowerBtns()
        else:
            if self.activate.is_alive():
                self.controllerActivateBtn.setChecked(False)
                self.listenToSocketBtn.setChecked(False)
                self.controllerActivateBtn.setText('Activate Controller')
                self.listenToSocketBtn.setText('Listen to Socket')
                self.done=True
                self.listen = False
                self.activate = Thread(target=self.controlerInput)
                self.listenThread = Thread(target=self.socketListening)
                #self.activate = Thread(ThreadStart(self.controlerInput))
                print 'controller deactive'
            del self.c843
            #self.connectBtn.setChecked(False)
            self.C843XYPowerBtn.setChecked(False)
            self.C843ZPowerBtn.setChecked(False)
            self.SM5Dev1PowerBtn.setChecked(False)
            self.SM5Dev2PowerBtn.setChecked(False)
            #self.connectBtn.setText('Connect SM-5 and C-843')
            self.disableAndEnableBtns(False)
        
        # SM5
        try :
            self.luigsNeumann
        except AttributeError:
            self.luigsNeumann = LandNSM5.LandNSM5()
            if self.luigsNeumann.connected:
                self.autoUpdateManipulatorLocations.start()
            else:
                reply = QMessageBox.warning(self, 'Warning','Switch on Luigs & Neumann SM5 controller.',  QMessageBox.Ok )
            #self.switchOnOffSM5Motors(1)
            #self.switchOnOffSM5Motors(2)
        else:
            if self.autoUpdateManipulatorLocations.is_alive():
                self.updateDone=True
                self.autoUpdateManipulatorLocations.join()
                self.autoUpdateManipulatorLocations = Thread(target=self.autoUpdateManip)
            del self.luigsNeumann
            #self.switchOnOffSM5Motors(1)
            #self.switchOnOffSM5Motors(2)
        
        #
        self.unSetStatusMessage('initializing stages')

    #################################################################################################
    def switchOnOffC843Motors(self,axes):
        # if active : deactivate controler first
        if self.activate.is_alive():
            self.activateController()
        # switch on or off motors
        if axes == 'xy':
            self.c843.switch_servo_on_off(self.stageAxes['x'])
            self.c843.switch_servo_on_off(self.stageAxes['y'])
            #if self.C843XYPowerBtn.isChecked():
            #    self.C843XYPowerBtn.setText('Switch Off XY')
            #else:
            #    self.C843XYPowerBtn.setText('Switch On XY')
        #
        elif axes=='z':
            self.c843.switch_servo_on_off(self.stageAxes['z'])
            #if self.C843ZPowerBtn.isChecked():
            #    self.C843ZPowerBtn.setText('Switch Off Z')
            #else:
            #    self.C843ZPowerBtn.setText('Switch On Z')
    #################################################################################################
    def switchOnOffSM5Motors(self,device):
        if self.SM5Dev1PowerBtn.isChecked():
            self.luigsNeumann.switchOnAxis(1,'x')
            self.luigsNeumann.switchOnAxis(1,'y')
            self.luigsNeumann.switchOnAxis(1,'z')
            #self.SM5Dev1PowerBtn.setText('Switch Off XYZ of Dev1')
        elif not self.SM5Dev1PowerBtn.isChecked():
            self.luigsNeumann.switchOffAxis(1,'x')
            self.luigsNeumann.switchOffAxis(1,'y')
            self.luigsNeumann.switchOffAxis(1,'z')
            #self.SM5Dev1PowerBtn.setText('Switch On XYZ of Dev1')
        
        if self.SM5Dev2PowerBtn.isChecked():
            self.luigsNeumann.switchOnAxis(2,'x')
            self.luigsNeumann.switchOnAxis(2,'y')
            self.luigsNeumann.switchOnAxis(2,'z')
            #self.SM5Dev2PowerBtn.setText('Switch Off XYZ of Dev2')
        elif not self.SM5Dev2PowerBtn.isChecked():
            self.luigsNeumann.switchOffAxis(2,'x')
            self.luigsNeumann.switchOffAxis(2,'y')
            self.luigsNeumann.switchOffAxis(2,'z')
            #self.SM5Dev2PowerBtn.setText('Switch On XYZ of Dev2')
    #################################################################################################
    def referenceChoseLocations(self):
        #
        fileName = QFileDialog.getOpenFileName(self, 'Choose C843 stage location file', 'C:\\Users\\2-photon\\experiments\\ManipulatorControl\\','Python object file (*.p)')
            
        if len(fileName)>0:
                self.c843.openReferenceFile(fileName)
                self.referenceStage(False)
    
    #################################################################################################
    def referenceStage(self,moveStage=False):
        #
        self.setStatusMessage('referencing axes')
        #
        ref1 = self.c843.reference_stage(self.stageAxes['x'],moveStage)
        ref2 = self.c843.reference_stage(self.stageAxes['y'],moveStage)
        ref3 = self.c843.reference_stage(self.stageAxes['z'],moveStage)
        # move stage to default location
        if moveStage:
            for i in range(3):
                self.c843.move_to_absolute_position(self.stageNumbers[i],self.defaultPosition[i])
            
        if not all((ref1,ref2,ref3)):
            reply = QMessageBox.warning(self, 'Warning','Reference failed.',  QMessageBox.Ok )
            #break
        else:
            self.refChoseLocationBtn.setEnabled(False)
            self.refSavedLocationBtn.setEnabled(False)
            self.refNegativeBtn.setEnabled(False)
            self.updateStageLocations()
            self.initializeSetLocations()
            self.getMinMaxOfStage()
            self.setMovementValues(self.defaultMoveSpeed)
            with self.sm5Lock:
                self.initializeManipulatorSpeed()
        #
        self.disableAndEnableBtns(True)
        self.unSetStatusMessage('referencing axes')

    #################################################################################################
    def activateController(self):
        #
        if self.activate.is_alive():
            self.controllerActivateBtn.setText('Activate controller')
            self.controllerActivateBtn.setStyleSheet('background-color:None')
            self.done=True
            self.activate = Thread(target=self.controlerInput)
            self.enableDiableControllerBtns(False)
            print 'controler deactive'
        else:
            self.controllerActivateBtn.setText('Deactivate Controller')
            self.controllerActivateBtn.setStyleSheet('background-color:red')
            self.enableDiableControllerBtns(True)
            self.activate.start()
            print 'controler active'

    #################################################################################################
    def listenToSocket(self):
        #
        if self.listenThread.is_alive():
            self.listenToSocketBtn.setText('Listen to Socket')
            self.listenToSocketBtn.setStyleSheet('background-color:None')
            self.listen=False
            #self.activate._stop()
            self.listenThread = Thread(target=self.socketListening)
            #self.enableDiableControllerBtns(False)
            #self.activate = Thread(ThreadStart(self.controlerInput))
            print 'socket deactive'
        else:
            self.listenToSocketBtn.setText('Stop listening to Socket')
            self.listenToSocketBtn.setStyleSheet('background-color:red')
            #self.enableDiableControllerBtns(True)
            self.listenThread.start()
            print 'socket active'
    #################################################################################################        
    def autoUpdateManip(self):
        #self.sm5Lock = Lock()
        self.updateDone=False
        while self.updateDone==False:
            with self.sm5Lock:
                self.updateManipulatorLocations()
            time.sleep(1)
    #################################################################################################  
    def socketListening(self):
        self.listen = True
        self.s.listen(1)
        self.c,addr = self.s.accept()
        #self.c.settimeout(1)
        while self.listen:
            do_read = False
            try:
                #print 'waiting for for connection to be established'
                #self.c,addr = self.s.accept() #Establish a connection with the client
                #print 'select select'
                r, _, _ = select.select([self.c], [], [])
                #data = self.c.recv(1024)
                #print r
                do_read = bool(r)
            except socket.error:
                pass
            if do_read:
                try:
                    #print 'before recv'
                    data = self.c.recv(1024)
                    if data == 'disconnect':
                        self.c.send('OK..'+data)
                        self.listen = False
                        self.listenThread = Thread(target=self.socketListening)
                        break
                    #print "Got data: ", data, 'from', addr[0],':',addr[1]
                    res = self.performRemoteInstructions(data)
                    self.c.send(str(res)+'...'+data)
                except socket.error:
                    self.listenToSocketBtn.setChecked(False)
                    self.listenToSocketBtn.setText('Listen to Socket')
                    self.listenToSocketBtn.setStyleSheet('background-color:None')
                    self.listen = False
                    self.listenThread = Thread(target=self.socketListening)
                    break
                #self.c.close()
        self.c.close()
        self.listenToSocketBtn.setChecked(False)
        self.listenToSocketBtn.setText('Listen to Socket')
        self.listenToSocketBtn.setStyleSheet('background-color:None')
        print 'thread ended by remote host'
            #print do_read
            #time.sleep(0.1)
            
            #self.c,addr = self.s.accept() #Establish a connection with the client
            #print "Got connection from", addr
            #rawDataReceived =  self.c.recv(1024)
            
            #print rawDataReceived
            #self.c.send('successful')
            #self.c.close()
            #time.sleep(0.5)
        
    #################################################################################################
    def performRemoteInstructions(self,rawData):
        data = rawData.split(',')
        #
        if data[0] == 'getPos':
            with self.c843Lock:
                self.updateStageLocations()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'relativeMoveTo':
            moveStep = float(data[2])
            with self.c843Lock:
                self.choseRightSpeed(abs(moveStep))
                self.moveStageToNewLocation(np.where(self.axes==data[1])[0][0],moveStep)
                self.moveSpeed = self.moveSpeedBefore
                self.propagateSpeeds()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'absoluteMoveTo':
            moveStep = float(data[2])
            with self.c843Lock:
                self.choseRightSpeed(abs(moveStep-self.isStage[np.where(self.axes==data[1])[0][0]]))
                self.moveStageToNewLocation(np.where(self.axes==data[1])[0][0],moveStep,moveType='absolute')
                self.moveSpeed = self.moveSpeedBefore
                self.propagateSpeeds()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'checkMovement':
            isXMoving = self.c843.check_for_movement(self.stageAxes['x'])
            isYMoving = self.c843.check_for_movement(self.stageAxes['y'])
            isZMoving = self.c843.check_for_movement(self.stageAxes['z'])
            if any((isXMoving,isYMoving,isZMoving)):
                return 1
            else:
                return 0
        elif data[0] == 'stop':
            self.switchOnOffC843Motors('z')
            self.switchOnOffC843Motors('xy')
            return 1
        else:
            return 0
    #################################################################################################
    def choseRightSpeed(self,stepSize):
        self.moveSpeedBefore = self.moveSpeed
        for key, value in self.stepWidths.iteritems():
            if stepSize >= value:
                self.moveSpeed = self.speeds[key]
            else :
                break
        print stepSize, self.moveSpeed
        self.propagateSpeeds()
            
    
    #################################################################################################
    def controlerInput(self):
        # Initialize the joysticks
        pygame.init()
        pygame.joystick.init()
        
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        
        self.done = False
        while self.done==False:
            #self.manip1MoveStep = float(self.device1StepLE.text())
            #self.manip2MoveStep = float(self.device2StepLE.text())
            print '1'
            for event in pygame.event.get(): # User did something
                #	# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                if event.type == pygame.JOYBUTTONDOWN:
                    pass
                    #print ("Joystick button pressed.")
                if event.type == pygame.JOYBUTTONUP:
                    pass
                    #print ("Joystick button released.")
            #
            print '2'
            #print 'test'
            xAxis = joystick.get_axis( 0 )
            yAxis = joystick.get_axis( 1 )
            #print xAxis, yAxis
            # x-Axis
            if abs(xAxis) > 0.5 :
                with self.c843Lock:
                    self.moveStageToNewLocation(0,-self.moveStep*np.sign(xAxis))
            # y-Axis
            if abs(yAxis) > 0.5 :
                with self.c843Lock:
                    self.moveStageToNewLocation(1,-self.moveStep*np.sign(yAxis))
            print '3'
            # z-Axis up and down is button 4 and 6
            setZ = self.setStage[2]
            if joystick.get_button( 4 ):
                with self.c843Lock:
                    setZ -= self.moveStep
                    print '3.1'
                    self.moveStageToNewLocation(2,-self.moveStep)
            print '3.2'
            if joystick.get_button( 6 ) :
                with self.c843Lock:
                    setZ += self.moveStep
                    print '3.3'
                    self.moveStageToNewLocation(2,self.moveStep)
            print '4'
            # change speed settings
            if joystick.get_button( 0 ):
                self.setMovementValues('fine')
            if joystick.get_button( 1 ):
                self.setMovementValues('small')
            if joystick.get_button( 2 ):
                self.setMovementValues('medium')
            if joystick.get_button( 3 ):
                self.setMovementValues('coarse')
            print '5'
            # chose which manipulator to move
            if joystick.get_button( 8 ):
                self.activateDev1.setChecked(True)
            if joystick.get_button( 9 ):
                self.activateDev2.setChecked(True)
            print '6'
            # manipulator steps
            if joystick.get_button( 7 ):
                if self.activateDev1.isChecked():
                    self.setXDev1+= self.manip1MoveStep
                    #self.luigsNeumann.goVariableFastToRelativePosition(1,'x',-2.)
                    time.sleep(0.2)
                if self.activateDev2.isChecked():
                    self.setXDev2+= self.manip2MoveStep
                    #self.luigsNeumann.goVariableFastToRelativePosition(2,'x',-2.)
                    time.sleep(0.2)
                #self.updateManipulatorLocations('x')
            if joystick.get_button( 5 ):
                if self.activateDev1.isChecked():
                    self.setXDev1-= self.manip1MoveStep
                    #self.luigsNeumann.goVariableFastToRelativePosition(1,'x',2.)
                    time.sleep(0.2)
                if self.activateDev2.isChecked():
                    self.setXDev2-= self.manip2MoveStep
                    #self.luigsNeumann.goVariableFastToRelativePosition(2,'x',2.)
                    time.sleep(0.2)
                #self.updateManipulatorLocations('x')
            print '7'
            # Dev 1
            if self.activateDev1.isChecked() and self.trackStageZMovementDev1Btn.isChecked():
                mov = self.oldSetZ - setZ
                if mov:
                    self.setZDev1-= mov
                    #self.goVariableFastToRelativePosition(1,'z',mov)
                    #self.updateManipulatorLocations('z')
            elif self.activateDev1.isChecked() and self.trackStageXMovementDev1Btn.isChecked():
                mov = (self.oldSetZ - setZ)/np.cos(self.alphaDev1*np.pi/180.)
                if mov:
                    self.setXDev1-= mov
                    #self.goVariableFastToRelativePosition(1,'x',mov)
                    #self.updateManipulatorLocations('x')
            # Dev 2
            if self.activateDev2.isChecked() and self.trackStageZMovementDev2Btn.isChecked():
                mov = self.oldSetZ - setZ
                if mov:
                    self.setZDev2-= mov
                    #self.goVariableFastToRelativePosition(2,'z',mov)
                    #self.updateManipulatorLocations('z')
            elif self.activateDev2.isChecked() and self.trackStageXMovementDev2Btn.isChecked():
                mov = (self.oldSetZ - setZ)/np.cos(self.alphaDev2*np.pi/180.)
                if mov:
                    self.setXDev2-= mov
                    #self.goVariableFastToRelativePosition(2,'x',mov)
                    #self.updateManipulatorLocations('x')
            self.oldSetZ = self.setStage[2]
            print '8'
            # Limit to 10 frames per second
            self.clock.tick(10)
            print '9'
            self.xSetPosDev1LE.setText(str(round(self.setXDev1,self.precision)))
            self.ySetPosDev1LE.setText(str(round(self.setYDev1,self.precision)))
            self.zSetPosDev1LE.setText(str(round(self.setZDev1,self.precision)))
            
            self.xSetPosDev2LE.setText(str(round(self.setXDev2,self.precision)))
            self.ySetPosDev2LE.setText(str(round(self.setYDev2,self.precision)))
            self.zSetPosDev2LE.setText(str(round(self.setZDev2,self.precision)))
            
            #
            if abs(self.setXDev1)>self.locationDiscrepancy:
                print 'difference : ', abs(self.setXDev1), self.setXDev1, self.isXDev1
                self.moveManipulatorToNewLocation(1,'x',self.setXDev1)
                self.setXDev1 = 0.
            if abs(self.setXDev2)>self.locationDiscrepancy:
                self.moveManipulatorToNewLocation(2,'x',self.setXDev2)
                self.setXDev2 = 0.
            if abs(self.setZDev1)>self.locationDiscrepancy:
                self.moveManipulatorToNewLocation(1,'z',self.setZDev1)
                self.setZDev1 = 0.
            if abs(self.setZDev2)>self.locationDiscrepancy:
                self.moveManipulatorToNewLocation(2,'z',self.setZDev2)
                self.setZDev2 = 0.
            print '10'
    #################################################################################################
    def moveStageToNewLocation(self,axis,moveDistance,moveType='relative'):
        
        print 'mSTNL 1'
        # define movement length
        if moveType == 'relative':
            self.setStage[axis] += moveDistance
        if moveType == 'absolute':
            self.setStage[axis] = moveDistance
        # check if limits are reached
        print 'mSTNL 2'
        if self.setStage[axis] < self.minStage[axis]:
            self.setStage[axis] = self.minStage[axis]
        elif self.setStage[axis] > self.maxStage[axis]:
            self.setStage[axis] = self.maxStage[axis]
        print 'mSTNL 3'
        # update set locations
        #if axis==0:
        #    self.setXLocationLineEdit.setText(str(round(self.setStage[axis],self.precision)))
        #elif axis==1:
        #    self.setYLocationLineEdit.setText(str(round(self.setStage[axis],self.precision)))
        #elif axis==2:
        #    self.setZLocationLineEdit.setText(str(round(self.setStage[axis],self.precision)))
        print 'mSTNL 4'
        if any(abs(self.isStage - self.setStage)> self.locationDiscrepancy):
            wait = True
            while wait:
                isMoving = self.c843.check_for_movement(self.stageNumbers[axis])
                if not isMoving: 
                    wait = False
            print 'mSTNL 5', isMoving
            self.c843.move_to_absolute_position(self.stageNumbers[axis],self.setStage[axis])
            print 'mSTNL 6'
            self.updateStageLocations()

    
    #################################################################################################
    def moveManipulatorToNewLocation(self,dev,axis,move):
        #exec("loc = self.set%sDev%s" % (axis.upper(),dev)) 
        #print self.loc
        if 'z' in axis:
            mult = 1.
        else:
            mult = -1.
        # stop update thread here
        with self.sm5Lock : #.acquire()
            self.luigsNeumann.goVariableFastToRelativePosition(dev,axis,float(move*mult))
            self.updateManipulatorLocations(axis)
            # release update thread here
        #self.sm5Lock.release()
        self.initializeSetLocations()
        
    #################################################################################################
    def updateStageLocations(self):
        # C843
        for i in range(3):
            self.isStage[i] = self.c843.get_position(self.stageNumbers[i])
        #
        #self.isXLocationValueLabel.setText(str(round(self.isStage[0],self.precision)))
        #self.isYLocationValueLabel.setText(str(round(self.isStage[1],self.precision)))
        #self.isZLocationValueLabel.setText(str(round(self.isStage[2],self.precision)))
        
        self.updateHomeTable()
        #
    #################################################################################################
    def updateManipulatorLocations(self,axis=None):
        
        if axis is None:
            # SM5 : Dev1
            self.isXDev1 = self.luigsNeumann.getPosition(1,'x')
            self.isYDev1 = self.luigsNeumann.getPosition(1,'y')
            self.isZDev1 = self.luigsNeumann.getPosition(1,'z')
            # SM5 : Dev2
            self.isXDev2 = self.luigsNeumann.getPosition(2,'x')
            self.isYDev2 = self.luigsNeumann.getPosition(2,'y')
            self.isZDev2 = self.luigsNeumann.getPosition(2,'z')
        else:
            if 'x' in axis:
                self.isXDev1 = self.luigsNeumann.getPosition(1,'x')
                self.isXDev2 = self.luigsNeumann.getPosition(2,'x')
            if 'y' in axis:
                self.isYDev1 = self.luigsNeumann.getPosition(1,'y')
                self.isYDev2 = self.luigsNeumann.getPosition(2,'y')
            if 'z' in axis:
                self.isZDev1 = self.luigsNeumann.getPosition(1,'z')
                self.isZDev2 = self.luigsNeumann.getPosition(2,'z')
        #
        self.xIsPosDev1LE.setText(str(round(self.isXDev1,self.precision)))
        self.yIsPosDev1LE.setText(str(round(self.isYDev1,self.precision)))
        self.zIsPosDev1LE.setText(str(round(self.isZDev1,self.precision)))
        
        self.xIsPosDev2LE.setText(str(round(self.isXDev2,self.precision)))
        self.yIsPosDev2LE.setText(str(round(self.isYDev2,self.precision)))
        self.zIsPosDev2LE.setText(str(round(self.isZDev2,self.precision)))
        
    #################################################################################################
    def initializeSetLocations(self):
        for i in range(3):
            self.setStage[i] = self.isStage[i]
            if i == 0:
                self.setXLocationLineEdit.setText(str(round(self.setStage[0],self.precision)))
            elif i == 1:
                self.setYLocationLineEdit.setText(str(round(self.setStage[1],self.precision)))
            elif i == 2:
                self.setZLocationLineEdit.setText(str(round(self.setStage[2],self.precision)))

        self.oldSetZ = self.setStage[2]
        
        self.setXDev1 = 0. #self.isXDev1
        self.setYDev1 = 0. #self.isYDev1
        self.setZDev1 = 0. #self.isZDev1
        
        self.setXDev2 = 0. #self.isXDev2
        self.setYDev2 = 0. #self.isYDev2
        self.setZDev2 = 0. #self.isZDev2
        
        self.xSetPosDev1LE.setText(str(round(self.setXDev1,self.precision)))
        self.ySetPosDev1LE.setText(str(round(self.setYDev1,self.precision)))
        self.zSetPosDev1LE.setText(str(round(self.setZDev1,self.precision)))
        
        self.xSetPosDev2LE.setText(str(round(self.setXDev2,self.precision)))
        self.ySetPosDev2LE.setText(str(round(self.setYDev2,self.precision)))
        self.zSetPosDev2LE.setText(str(round(self.setZDev2,self.precision)))
        
        self.device1StepLE.setText(str(self.manip1MoveStep))
        self.device2StepLE.setText(str(self.manip2MoveStep))
        
        #if self.isHomeSet :
        #    self.homeXLocationValue.setText(str(round(self.isX-self.homeP[0],self.precision)))
        #    self.homeYLocationValue.setText(str(round(self.isY-self.homeP[1],self.precision)))
        #    self.homeZLocationValue.setText(str(round(self.isZ-self.homeP[2],self.precision)))
        
    #################################################################################################
    def getMinMaxOfStage(self):
        # read maximal and minimal values
        self.minStage = np.zeros(3)
        self.maxStage = np.zeros(3)
        
        for i in range(3):
            (self.minStage[i],self.maxStage[i]) = self.c843.get_min_max_travel_range(self.stageNumbers[i])
            #(self.yMin,self.yMax) = self.c843.get_min_max_travel_range(2)
            #(self.zMin,self.zMax) = self.c843.get_min_max_travel_range(3)
        
        self.minMaxXLocationValueLabel.setText(str(round(self.maxStage[0],self.precision)))
        self.minMaxYLocationValueLabel.setText(str(round(self.maxStage[0],self.precision)))
        self.minMaxZLocationValueLabel.setText(str(round(self.maxStage[0],self.precision)))
        
    #################################################################################################
    def initializeManipulatorSpeed(self):
        # Manipulator Speed
        self.velDev1 = self.luigsNeumann.getPositioningVelocityFast(1,'x')
        self.device1SpeedLE.setText(str(self.velDev1))
        self.velDev2 = self.luigsNeumann.getPositioningVelocityFast(2,'x')
        self.device2SpeedLE.setText(str(self.velDev2))
        
        #self.enableButtons()
    #################################################################################################
    def setManiplatorSpeed(self,dev):
        if dev == 1:
            self.velDev1 = float(self.device1SpeedLE.text())
            with self.sm5Lock:
                self.luigsNeumann.setPositioningVelocityFast(1,'x',self.velDev1)
        elif dev == 2:
            self.velDev2 = float(self.device2SpeedLE.text())
            with self.sm5Lock:
                self.luigsNeumann.setPositioningVelocityFast(2,'x',self.velDev2)
    #################################################################################################
    def setManiplatorStep(self):
        self.manip1MoveStep = float(self.device1StepLE.text())
        self.manip2MoveStep = float(self.device2StepLE.text())
    #################################################################################################
    def setMovementValues(self,moveSize):
        if moveSize == 'fine':
            self.fineBtn.setChecked(True)
        elif moveSize == 'small':
            self.smallBtn.setChecked(True)
        elif moveSize == 'medium':
            self.mediumBtn.setChecked(True)
        elif moveSize == 'coarse':
            self.coarseBtn.setChecked(True)
        #
        self.moveStep = self.stepWidths[moveSize]
        self.moveSpeed = self.speeds[moveSize]
        self.stepLineEdit.setText(str(self.moveStep))
        self.speedLineEdit.setText(str(self.moveSpeed))
        self.propagateSpeeds()
        #self.propagateSpeeds()
    #################################################################################################
    def getStepValue(self):
        self.moveStep = float(self.stepLineEdit.text())

    #################################################################################################
    def getSpeedValue(self):
        self.moveSpeed = float(self.speedLineEdit.text())
        print "new speed :", self.moveSpeed
        self.propagateSpeeds()

    #################################################################################################
    def propagateSpeeds(self):
        for i in range(3):
            self.c843.set_velocity(self.stageNumbers[i],self.moveSpeed)

    #################################################################################################
    def recordCell(self,nElectrode,identity):
        #self.cellListTable.insertRow(3)
        xyzU = self.c843.get_all_positions((self.stageNumbers[0],self.stageNumbers[1],self.stageNumbers[2]))
        nC = len(self.cells)
        
        self.cells[nC] = {}
        self.cells[nC]['number'] = self.nItem
        self.cells[nC]['type'] = identity # 'MLI'
        self.cells[nC]['electrode'] = nElectrode
        self.cells[nC]['location'] = np.array([round(xyzU[0],self.precision),round(xyzU[1],self.precision),round(xyzU[2],self.precision)])
        self.cells[nC]['depth'] = 0.
        
        self.updateTable()
        print 'added ',str(nC),'item'	
        self.nItem+=1
        self.repaint()
    
    #################################################################################################
    def updateTable(self):
        print len(self.cells), self.rowC
        # add row if table gets filled up
        #if (len(self.cells)+1) == (self.rowC):
        #    self.cellListTable.insertRow(self.rowC)
        #    self.cellListTable.setRowHeight(self.rowC,self.rowHeight)
        #    self.rowC+=1
        
        # expand table when list is loaded directly from file
        while (len(self.cells)+1) > (self.rowC):
            self.cellListTable.insertRow(self.rowC)
            self.cellListTable.setRowHeight(self.rowC,self.rowHeight)
            self.rowC+=1
            
        
        #if self.surfaceRecorded:
        #	for r in range(len(self.cells)):
        #		if self.cells[r]['type']=='surface':
        #			zSurface = self.cells[r]['location'][2]
        
        for r in range(len(self.cells)):
            for c in range(5):
                if c==0:
                    self.cellListTable.setItem(r, c, QTableWidgetItem(str(self.cells[r]['number'])))
                elif c==1:
                    if self.cells[r]['type']=='PC':
                        self.cellListTable.setItem(r, c, QTableWidgetItem('PC'))
                    elif  self.cells[r]['type']=='MLI':
                        self.cellListTable.setItem(r, c, QTableWidgetItem('MLI'))
                    #elif  self.cells[r]['type']=='surface':
                    #	self.cellListTable.setItem(r, c, QtGui.QTableWidgetItem('S'))
                elif c==2:
                    self.cellListTable.setItem(r, c, QTableWidgetItem(str(self.cells[r]['electrode'])))
                elif c==3:
                    if not self.cells[r]['depth'] == 0.:
                        depth = self.cells[r]['depth']
                        self.cellListTable.setItem(r, c, QTableWidgetItem(str(depth)))
                    #pass
                elif c==4:
                    loc = str(self.cells[r]['location'][0])+','+str(self.cells[r]['location'][1])+','+str(self.cells[r]['location'][2])
                    self.cellListTable.setItem(r, c, QTableWidgetItem(loc))
    #################################################################################################
    def moveToLocation(self):
        
        self.setStatusMessage('moving stage to cell')

        r = self.cellListTable.selectionModel().selectedRows()
        nR = 0
        for index in sorted(r):
            row = index.row()
            nR+=1
        print 'row: ',row
        xyz = ([self.cells[row]['location'][0],self.cells[row]['location'][1],self.cells[row]['location'][2]])
        print xyz
        
        for i in range(3):
            self.setStage[i] = self.cells[row]['location'][i]
            self.moveStageToNewLocation(i,self.setStage[i],moveType='absolute')

        self.unSetStatusMessage('moving stage to cell')
    #################################################################################################
    def updateLocation(self):
        r = self.cellListTable.selectionModel().selectedRows()
        nR = 0
        for index in sorted(r):
            row = index.row()
            nR +=1
        xyz = self.c843.get_all_positions((self.stageNumbers[0],self.stageNumbers[1],self.stageNumbers[2]))
        self.cells[row]['location'] = np.array([round(xyz[0],self.precision),round(xyz[1],self.precision),round(xyz[2],self.precision)])
        self.updateTable()
        self.repaint()
    
    #################################################################################################
    def removeLocation(self):
        #print self.cells
        r = self.cellListTable.selectionModel().selectedRows()
        nR = 0
        for index in sorted(r):
            row = index.row()
            nR +=1
        
        nCells = len(self.cells)
        print nCells, row

        del self.cells[row]
        if (nCells-1) != row:
            for i in range(row,(nCells-1)):
                self.cells[i] = self.cells[i+1]
            del self.cells[(nCells-1)]
        #print self.cells
        self.updateTable()
        self.cellListTable.removeRow((nCells-1))
        self.cellListTable.insertRow((nCells-1))
        self.cellListTable.setRowHeight((nCells-1),self.rowHeight)
        self.repaint()
        #self.rowC-=1
        #self.nItem-=1
    #################################################################################################
    def recordDepth(self):
        
        r = self.cellListTable.selectionModel().selectedRows()
        nR = 0
        for index in sorted(r):
            row = index.row()
            nR+=1
        
        xyzU = self.c843.get_all_positions((self.stageNumbers[0],self.stageNumbers[1],self.stageNumbers[2]))
        
        self.cells[row]['depth'] = (self.cells[row]['location'][2] - round(xyzU[2],self.precision))

        self.updateTable()
        print 'recorded depth of cell # ',str(self.cells[row]['number'])        
      
    #################################################################################################
    def saveLocations(self):
        print self.today_date
        saveDir = 'C:\\Users\\2-photon\\experiments\\ManipulatorControl\\locations_'+self.today_date+'.p'
        #saveDir = 'C:\\Users\\reyesadmin\\experiments\\in_vivo_data_mg\\140410\\misc\\locations.p'
        filename = QFileDialog.getSaveFileName(self, 'Save File',saveDir, '.p')
        print str(filename),filename
        if filename:
            programData = {}
            programData['cells'] = self.cells
            programData['homeLocations'] = self.homeLocs
            pickle.dump(programData,open(filename,"wb"))
            self.fileSaved = True
    #################################################################################################
    def loadLocations(self):
        filename = QFileDialog.getOpenFileName(self, 'Choose cell location file', 'C:\\Users\\2-photon\\experiments\\ManipulatorControl\\','Python object file (*.p)')
            
        if len(filename)>0:
            programData = pickle.load(open(filename))
            self.cells = programData['cells']
            self.homeLocs = programData['homeLocations']
            
            nItems = len(self.cells)
            self.nItem = self.cells[(nItems-1)]['number'] + 1
            self.updateTable()
            print 'loaded ',str(nItems),'items'
            
            nHome = len(self.homeLocs)
            self.nHomeItem = self.homeLocs[(nHome-1)]['number'] + 1
            self.updateHomeTable()
            print 'loaded', str(nHome), 'home locations'
            
            self.repaint()
                
    #################################################################################################
    def updateHomeTable(self):
        #print len(self.homeLocs), self.rowHomeC
        # add row if table gets filled up
        #if (len(self.homeLocs)+1) == (self.rowHomeC):
        #    self.homeLocationsTable.insertRow(self.rowHomeC)
        #    self.homeLocationsTable.setRowHeight(self.rowHomeC,self.rowHeight)
        #    self.rowHomeC+=1
        
        # expand table when list is loaded directly from file
        while (len(self.homeLocs)+1) > (self.rowHomeC):
            self.homeLocationsTable.insertRow(self.rowHomeC)
            self.homeLocationsTable.setRowHeight(self.rowHomeC,self.rowHeight)
            self.rowHomeC+=1
            
        
        #if self.surfaceRecorded:
        #       for r in range(len(self.homeLocs)):
        #               if self.homeLocs[r]['type']=='surface':
        #                       zSurface = self.homeLocs[r]['location'][2]
        
        for r in range(len(self.homeLocs)):
            for c in range(4):
                if c==0:
                    self.homeLocationsTable.setItem(r, c, QTableWidgetItem(str(self.homeLocs[r]['number'])))
                elif c==1:
                    self.homeLocationsTable.setItem(r, c, QTableWidgetItem(str(round(self.isStage[0]-self.homeLocs[r]['x'],self.precision))))
                elif c==2:
                    self.homeLocationsTable.setItem(r, c, QTableWidgetItem(str(round(self.isStage[1]-self.homeLocs[r]['y'],self.precision))))
                elif c==3:
                    self.homeLocationsTable.setItem(r, c, QTableWidgetItem(str(round(self.isStage[2]-self.homeLocs[r]['z'],self.precision))))
    #################################################################################################
    def recordHomeLocation(self):
        #self.cellListTable.insertRow(3)
        xyzU = self.c843.get_all_positions((self.stageNumbers[0],self.stageNumbers[1],self.stageNumbers[2]))
        nC = len(self.homeLocs)
        
        self.homeLocs[nC] = {}
        self.homeLocs[nC]['number'] = self.nHomeItem
        
        self.homeLocs[nC]['x'] = round(xyzU[0],self.precision)
        self.homeLocs[nC]['y'] = round(xyzU[1],self.precision)
        self.homeLocs[nC]['z'] = round(xyzU[2],self.precision) 
        
        self.updateHomeTable()
        print 'added ',str(nC),'home item'   
        self.nHomeItem+=1
        self.repaint()
    #################################################################################################
    def updateHomeLocation(self):
        r = self.homeLocationsTable.selectionModel().selectedRows()
        for index in sorted(r):
            row = index.row()

        xyz = self.c843.get_all_positions((self.stageNumbers[0],self.stageNumbers[1],self.stageNumbers[2]))
        self.homeLocs[row]['x'] = round(xyz[0],self.precision) 
        self.homeLocs[row]['y'] = round(xyz[1],self.precision) 
        self.homeLocs[row]['z'] = round(xyz[2],self.precision)
        self.updateHomeTable()
        self.repaint()
    #################################################################################################
    def removeHomeLocation(self):
        #print self.cells
        r = self.homeLocationsTable.selectionModel().selectedRows()
        for index in sorted(r):
            row = index.row()

        nLocations = len(self.homeLocs)
        #print nCells, row

        del self.homeLocs[row]
        if (nLocations-1) != row:
            for i in range(row,(nLocations-1)):
                self.homeLocs[i] = self.homeLocs[i+1]
            del self.homeLocs[(nLocations-1)]
        #print self.cells
        self.updateHomeTable()
        self.homeLocationsTable.removeRow((nLocations-1))
        self.homeLocationsTable.insertRow((nLocations-1))
        self.homeLocationsTable.setRowHeight((nLocations-1),self.rowHeight)
        self.repaint()
        #self.rowC-=1
        #self.nItem-=1
    #################################################################################################
    def moveToHomeLocation(self):
        
        self.setStatusMessage('moving stage to home location')

        r = self.homeLocationsTable.selectionModel().selectedRows()
        for index in sorted(r):
            row = index.row()

        print 'row: ',row
        xyz = ([self.homeLocs[row]['x'],self.homeLocs[row]['y'],self.homeLocs[row]['z']])
        print xyz
        
        for i in range(3):
            self.setStage[i] = self.homeLocs[row][self.axes[i]]
            self.moveStageToNewLocation(i,self.setStage[i],moveType='absolute')
        
        self.unSetStatusMessage('moving stage to home location')
    #################################################################################################
    def setStatusMessage(self,statusText):
        self.statusbar.showMessage(statusText+' ...')
        self.statusbar.setStyleSheet('color: red')
        #self.statusbar.repaint()
    #################################################################################################
    def unSetStatusMessage(self,statusText):
        self.statusbar.showMessage(statusText+' ... done')
        self.statusbar.setStyleSheet('color: black')
        #self.statusValue.repaint()
    #################################################################################################
    def enableReferencePowerBtns(self):
        self.C843XYPowerBtn.setEnabled(True)
        self.C843ZPowerBtn.setEnabled(True)
        self.SM5Dev1PowerBtn.setEnabled(True)
        self.SM5Dev2PowerBtn.setEnabled(True)
        self.refChoseLocationBtn.setEnabled(True)
        self.refSavedLocationBtn.setEnabled(True)
        self.refNegativeBtn.setEnabled(True)
    #################################################################################################
    def disableAndEnableBtns(self,newSetting):
        # connection panel
        self.C843XYPowerBtn.setEnabled(newSetting)
        self.C843ZPowerBtn.setEnabled(newSetting)
        self.SM5Dev1PowerBtn.setEnabled(newSetting)
        self.SM5Dev2PowerBtn.setEnabled(newSetting)
        self.refChoseLocationBtn.setEnabled(newSetting)
        self.refSavedLocationBtn.setEnabled(newSetting)
        self.refNegativeBtn.setEnabled(newSetting)
        # Move panel
        self.controllerActivateBtn.setEnabled(newSetting)
        self.listenToSocketBtn.setEnabled(newSetting)
        # recorded locations
        self.electrode1MLIBtn.setEnabled(newSetting)
        self.electrode1PCBtn.setEnabled(newSetting)
        self.electrode2MLIBtn.setEnabled(newSetting)
        self.electrode2PCBtn.setEnabled(newSetting)
        
        self.recordHomeLocationBtn.setEnabled(newSetting)
        self.updateHomeLocationBtn.setEnabled(newSetting)
        self.moveToHomeLocationBtn.setEnabled(newSetting)
        self.removeHomeLocationBtn.setEnabled(newSetting)
        
        self.moveToItemBtn.setEnabled(newSetting)
        self.recordDepthBtn.setEnabled(newSetting)
        self.saveLocationsBtn.setEnabled(newSetting)
        self.updateItemLocationBtn.setEnabled(newSetting)
        self.removeItemBtn.setEnabled(newSetting)
        self.loadLocationsBtn.setEnabled(newSetting)
    ###################################################################################################
    def enableDiableControllerBtns(self, newSetting):
        self.fineBtn.setEnabled(newSetting)
        self.smallBtn.setEnabled(newSetting)
        self.mediumBtn.setEnabled(newSetting)
        self.coarseBtn.setEnabled(newSetting)
        
        self.activateDev1.setEnabled(newSetting)
        self.activateDev2.setEnabled(newSetting)
        
        self.trackStageZMovementDev1Btn.setEnabled(newSetting)
        self.trackStageXMovementDev1Btn.setEnabled(newSetting)
        self.trackStageZMovementDev2Btn.setEnabled(newSetting)
        self.trackStageXMovementDev2Btn.setEnabled(newSetting)
    #########################################################################################
    def closeEvent(self, event):
        self.done = True
        self.updateDone = True
        self.listen = False
        self.s.close()
        # delete class istances
        try :
            self.c843
        except AttributeError:
            pass
        else:
            del self.c843

        #####################################################
        try :
            self.luigsNeumann
        except AttributeError:
            pass
        else:
            del self.luigsNeumann
        
        # save locations and dispaly quitting dialog
        #if not self.fileSaved and self.nItem>0:
                #reply = QtGui.QMessageBox.question(self, 'Message',"Do you want to save locations before quitting?",  QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                #if reply == QtGui.QMessageBox.Yes:
                        #self.saveLocations()
                        #event.accept()
                #elif reply == QtGui.QMessageBox.No:
                        #event.accept()
                #else:
                        #event.ignore()    
        #else:
                   #reply = QtGui.QMessageBox.question(self, 'Message',"Do you want to quit?",  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                   #if reply == QtGui.QMessageBox.Yes:
                           #event.accept()
                   #else:
                            #event.ignore()    
        
        
##########################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = manipulatorControl()
    form.show()
    app.exec_()
    
    