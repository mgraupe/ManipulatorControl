import sys
import pygame
import select
import time
import pickle
import numpy as np
import socket
from threading import *
from functools import partial

from PyQt4 import QtCore, QtGui

import manipulatorTemplate 
#import manipulator


#################################################################
class manipulatorControlGui(QtGui.QMainWindow,manipulatorTemplate.Ui_MainWindow,Thread):
    
    listenControlerButtonChanged = QtCore.Signal(object)
    listenSocketButtonChanged = QtCore.Signal(object)
    
    def __init__(self,dev):
        
        self.today_date = time.strftime("%Y%m%d")[2:]
        
        self.dev = dev
        # initialize the UI and parent class
        QtGui.QMainWindow.__init__(self)
        self.ui = manipulatorTemplate.Ui_MainWindow()
        self.ui.setupUi(self)
        
        #
        self.connectSignals()
        
        self.rowHeight = 16

        self.homeLocs = {}
        self.nHomeItem = 0
        self.rowHomeC = 4
        
        self.ui.homeLocationsTable.setRowCount(self.rowHomeC)
        for i in range(self.rowHomeC):
            self.ui.homeLocationsTable.setRowHeight(i,self.rowHeight)
        self.ui.homeLocationsTable.setSelectionMode(self.ui.homeLocationsTable.ContiguousSelection)
        self.ui.homeLocationsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        self.ui.homeLocationsTable.setColumnWidth(0,30)
        self.ui.homeLocationsTable.setColumnWidth(1,100)
        self.ui.homeLocationsTable.setColumnWidth(2,100)
        self.ui.homeLocationsTable.setColumnWidth(3,100)
        
        self.axes = np.array(['x','y','z'])
        
        self.cells = {}
        self.nItem = 0
        self.rowC = 6
        
        self.ui.cellListTable.setRowCount(self.rowC)
        for i in range(self.rowC):
            self.ui.cellListTable.setRowHeight(i,self.rowHeight)
        self.ui.cellListTable.setSelectionMode(self.ui.cellListTable.ContiguousSelection)
        self.ui.cellListTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        
        # configure column widths in cellListTable
        self.ui.cellListTable.setColumnWidth(0,30)
        self.ui.cellListTable.setColumnWidth(1,38)
        self.ui.cellListTable.setColumnWidth(2,30)
        self.ui.cellListTable.setColumnWidth(3,58)
        self.ui.cellListTable.setColumnWidth(4,150)
        
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        
        self.SM5_ModLock = Lock()
        
        self.fileSaved = False
        
        self.disableAndEnableBtns(False)
        self.enableDisableControllerBtns(False)
        
        self.receiveControlerInput = Thread(target=self.controlerInput)
        self.autoUpdateManipulatorLocations = Thread(target=self.autoUpdateManip)
        self.socketListenThread = Thread(target=self.socketListening) # listenThread
        
    ####################################################
    # connect signals to actions
    def connectSignals(self):
        
        ################################################
        # Connection panel 
        self.ui.connectBtn.clicked.connect(self.connectSM5_c843)
        self.ui.C843XYPowerBtn.clicked.connect(partial(self.switchOnOffC843Motors,'xy'))
        self.ui.C843ZPowerBtn.clicked.connect(partial(self.switchOnOffC843Motors,'z'))
        self.ui.SM5Dev1PowerBtn.clicked.connect(self.switchOnOffSM5Dev1Motors)
        self.ui.SM5Dev2PowerBtn.clicked.connect(self.switchOnOffSM5Dev2Motors)
        
        self.ui.refChoseLocationBtn.clicked.connect(self.referenceChoseLocations)
        self.ui.refSavedLocationBtn.clicked.connect(partial(self.referenceStage,False))
        self.ui.refNegativeBtn.clicked.connect(partial(self.referenceStage,True))
        
        #################################################
        ## Move panel
        self.ui.controllerActivateBtn.clicked.connect(self.activateController)
        self.ui.listenToSocketBtn.clicked.connect(self.activateSocket)
        
        self.ui.fineBtn.clicked.connect(partial(self.setMovementValues,'fine'))
        self.ui.smallBtn.clicked.connect(partial(self.setMovementValues,'small'))
        self.ui.mediumBtn.clicked.connect(partial(self.setMovementValues,'medium'))
        self.ui.coarseBtn.clicked.connect(partial(self.setMovementValues,'coarse'))
        self.ui.stepLineEdit.editingFinished.connect(self.setC843StepValue)
        self.ui.speedLineEdit.editingFinished.connect(self.setC843SpeedValue)
        self.ui.precisionLineEdit.editingFinished.connect(self.setC843PrecisionValue)
        
        self.ui.device1StepLE.editingFinished.connect(self.setSM5Step)
        self.ui.device2StepLE.editingFinished.connect(self.setSM5Step)
        
        self.ui.device1SpeedLE.editingFinished.connect(partial(self.setSM5Speed,1))
        self.ui.device2SpeedLE.editingFinished.connect(partial(self.setSM5Speed,2))
        
        #################################################
        ## Location panel 
        self.ui.electrode1MLIBtn.clicked.connect(partial(self.recordCell,1,'MLI'))
        self.ui.electrode1PCBtn.clicked.connect(partial(self.recordCell,1,'PC'))
        self.ui.electrode2MLIBtn.clicked.connect(partial(self.recordCell,2,'MLI'))
        self.ui.electrode2PCBtn.clicked.connect(partial(self.recordCell,2,'PC'))
        
        self.ui.moveToItemBtn.clicked.connect(self.moveToLocation)
        self.ui.updateItemLocationBtn.clicked.connect(self.updateLocation)
        self.ui.recordDepthBtn.clicked.connect(self.recordDepth)
        self.ui.removeItemBtn.clicked.connect(self.removeLocation)
        self.ui.saveLocationsBtn.clicked.connect(self.saveLocations)
        self.ui.loadLocationsBtn.clicked.connect(self.loadLocations)
        
        self.ui.recordHomeLocationBtn.clicked.connect(self.recordHomeLocation)
        self.ui.updateHomeLocationBtn.clicked.connect(self.updateHomeLocation)
        self.ui.moveToHomeLocationBtn.clicked.connect(self.moveToHomeLocation)
        self.ui.removeHomeLocationBtn.clicked.connect(self.removeHomeLocation)        
    
        ##################################################
        # signals
        self.dev.isStagePositionChanged.connect(self.updateIsStagePositions)
        self.dev.setStagePositionChanged.connect(self.updateSetStagePositions)
        self.dev.isManipulatorPositionChanged.connect(self.updateIsManipulatorPositions)
        self.dev.setManipulatorPositionChanged.connect(self.updateSetManipulatorPositions)
        
        self.listenControlerButtonChanged.connect(self.listenControlerButtonState)
        self.listenSocketButtonChanged.connect(self.listenSocketButtonState)
        
    #################################################################################################
    def connectSM5_c843(self):
        self.setStatusMessage('initializing C843')
        try:
            self.dev.c843
        except AttributeError:
            self.dev.init_C843()
            self.ui.C843XYPowerBtn.setChecked(True)
            self.ui.C843ZPowerBtn.setChecked(True)
            self.enableReferencePowerBtns()
        else:
            if self.receiveControlerInput.is_alive():
                self.activateController()
            if self.socketListenThread.is_alive():
                self.activateSocket()
            self.dev.delete_C843()
            self.ui.C843XYPowerBtn.setChecked(False)
            self.ui.C843ZPowerBtn.setChecked(False)
            self.disableAndEnableBtns(False)
        
        # SM5
        self.setStatusMessage('initializing Luigs and Neumann SM5')
        try :
            self.dev.luigsNeumann
        except AttributeError:
            self.dev.init_SM5()
            if self.dev.is_SM5_connected():
                self.ui.SM5Dev1PowerBtn.setChecked(True)
                self.ui.SM5Dev2PowerBtn.setChecked(True)
                self.readSM5SpeedFromDevice()
                self.loadSM5StepValues()
                self.autoUpdateManipulatorLocations.start()
                
            else:
                reply = QtGui.QMessageBox.warning(self, 'Warning','Switch on Luigs & Neumann SM5 controller.',  QtGui.QMessageBox.Ok )
        else:
            if self.autoUpdateManipulatorLocations.is_alive():
                self.updateManiuplators=False
                self.autoUpdateManipulatorLocations.join()
                self.autoUpdateManipulatorLocations = Thread(target=self.autoUpdateManip)
            self.dev.delete_SM5()
            self.ui.SM5Dev1PowerBtn.setChecked(False)
            self.ui.SM5Dev2PowerBtn.setChecked(False)
        #
        self.unSetStatusMessage('initializing stages')
    
    #################################################################################################
    def switchOnOffC843Motors(self,axes):
        # if active : deactivate controler first
        if self.receiveControlerInput.is_alive():
            print 'activate controler'
            self.activateController()
        # switch on or off motors
        if axes == 'xy':
            self.dev.C843_switch_servo_on_off('x')
            self.dev.C843_switch_servo_on_off('y')
        #
        elif axes=='z':
            self.dev.C843_switch_servo_on_off('z')

    #################################################################################################
    def switchOnOffSM5Dev1Motors(self):
        if self.SM5Dev1PowerBtn.isChecked():
            self.dev.SM5_switch_on_axis(1,'x')
            self.dev.SM5_switch_on_axis(1,'y')
            self.dev.SM5_switch_on_axis(1,'z')
        elif not self.SM5Dev1PowerBtn.isChecked():
            self.dev.SM5_switch_off_axis(1,'x')
            self.dev.SM5_switch_off_axis(1,'y')
            self.dev.SM5_switch_off_axis(1,'z')

    #################################################################################################
    def switchOnOffSM5Dev2Motors(self):
        if self.SM5Dev2PowerBtn.isChecked():
            self.dev.SM5_switch_on_axis(2,'x')
            self.dev.SM5_switch_on_axis(2,'y')
            self.dev.SM5_switch_on_axis(2,'z')
        elif not self.SM5Dev2PowerBtn.isChecked():
            self.dev.SM5_switch_off_axis(2,'x')
            self.dev.SM5_switch_off_axis(2,'y')
            self.dev.SM5_switch_off_axis(2,'z')
    #################################################################################################
    def referenceChoseLocations(self):
        #
        fileName = QFileDialog.getOpenFileName(self, 'Choose C843 stage location file', 'C:\\Users\\2-photon\\experiments\\ManipulatorControl\\','Python object file (*.p)')
            
        if len(fileName)>0:
                self.referenceStage(False,fileName)
    
    #################################################################################################
    def referenceStage(self,moveStage=False,fileName=None):
        #
        self.setStatusMessage('referencing axes')
        #
        if fileName:
            self.dev.C843_openReferenceFile(fileName)
        
        if  self.dev.C843_reference_state(moveStage):
            self.ui.refChoseLocationBtn.setEnabled(False)
            self.ui.refSavedLocationBtn.setEnabled(False)
            self.ui.refNegativeBtn.setEnabled(False)
            
            self.updateStageLocations()
            self.getMinMaxOfStage()
            self.setMovementValues(self.dev.defaultMoveSpeed)
            # moves the stage back to the default location
            if moveStage:
                self.dev.moveStageToDefaultLocation()
        else:
            reply = QtGui.QMessageBox.warning(self, 'Warning','Reference failed.',  QtGui.QMessageBox.Ok )
        #
        self.disableAndEnableBtns(True)
        self.unSetStatusMessage('referencing axes')
        
    #################################################################################################
    def activateController(self):
        #
        if self.receiveControlerInput.is_alive():
            self.listenControlerButtonChanged.emit('inactive')
            self.listenToControler=False
            self.receiveControlerInput = Thread(target=self.controlerInput)
            self.enableDisableControllerBtns(False)
            print 'controler inactive'
        else:
            self.listenControlerButtonChanged.emit('active')
            self.enableDisableControllerBtns(True)
            self.receiveControlerInput.start()
            print 'controler active'

    #################################################################################################
    def activateSocket(self):
        #
        if self.socketListenThread.is_alive():
            self.listenSocketButtonChanged.emit('inactive')
            self.listenToSocket=False
            self.socketListenThread = Thread(target=self.socketListening)
            print 'socket inactive'
        else:
            self.listenSocketButtonChanged.emit('active')
            self.socketListenThread.start()
            print 'socket active'
    
    #################################################################################################        
    def autoUpdateManip(self):
        self.updateManiuplators=True
        while self.updateManiuplators:
            with self.SM5_ModLock:
                self.dev.SM5_getPosition()
                self.dev.SM5_copyIsToSetLoctions()
            time.sleep(.5)
    
    #################################################################################################  
    def socketListening(self):
        self.listenToSocket = True
        print 'before connect'
        self.dev.socket_connect()
        while self.listenToSocket:
            do_read = False
            try:
                #print 'waiting for for connection to be established'
                #self.c,addr = self.s.accept() #Establish a connection with the client
                #print 'select select'
                do_read = self.dev.socket_monitor_activity()
            except socket.error:
                pass
            if do_read:
                try:
                    #print 'before recv'
                    data = self.dev.socket_read_data()
                    if data == 'disconnect':
                        self.dev.socket_send_data('OK..'+data)
                        print 'socket connection was closed by remote host'
                        self.activateSocket() # fist close connection
                        self.activateSocket() # then re-initiate listening
                        break
                    if not 'getPos' in data:
                        print "Got data: ", data
                    res = self.dev.performRemoteInstructions(data)
                    self.dev.socket_send_data(str(res)+'...'+data)
                except socket.error:
                    print 'socket connection closed due to error'
                    self.activateSocket()
                    break
        print 'after thread'
        self.dev.socket_close_connection()

    #################################################################################################
    def controlerInput(self):
        # Initialize the joysticks
        pygame.init()
        pygame.joystick.init()
        
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        
        oldSetZ = self.dev.setStage[2]
        self.listenToControler = True
        while self.listenToControler:
            for event in pygame.event.get(): # User did something
                #	# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                if event.type == pygame.JOYBUTTONDOWN:
                    pass
                    #print ("Joystick button pressed.")
                if event.type == pygame.JOYBUTTONUP:
                    pass
                    #print ("Joystick button released.")
            #
            xAxis = joystick.get_axis( 0 )
            yAxis = joystick.get_axis( 1 )
            #print xAxis, yAxis
            # x-Axis
            if abs(xAxis) > 0.5 :
                self.dev.moveStageToNewLocation(0,-np.sign(xAxis)*self.dev.moveStep)
            # y-Axis
            if abs(yAxis) > 0.5 :
                self.dev.moveStageToNewLocation(1,-np.sign(yAxis)*self.dev.moveStep)
            # z-Axis up and down is button 4 and 6
            if joystick.get_button( 4 ):
                self.dev.moveStageToNewLocation(2,-self.dev.moveStep)
            if joystick.get_button( 6 ) :
                self.dev.moveStageToNewLocation(2,self.dev.moveStep)
            # change speed settings
            if joystick.get_button( 0 ):
                self.setMovementValues('fine')
            if joystick.get_button( 1 ):
                self.setMovementValues('small')
            if joystick.get_button( 2 ):
                self.setMovementValues('medium')
            if joystick.get_button( 3 ):
                self.setMovementValues('coarse')
            # chose which manipulator to move
            if joystick.get_button( 8 ):
                self.ui.activateDev1.setChecked(True)
            if joystick.get_button( 9 ):
                self.ui.activateDev2.setChecked(True)
            
            # manipulator steps
            if joystick.get_button( 7 ):
                if self.ui.activateDev1.isChecked():
                    #print 1,'x',self.dev.manip1MoveStep
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(1,'x',self.dev.manip1MoveStep)
                if self.ui.activateDev2.isChecked():
                    #print 2,'x',self.dev.manip1MoveStep
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(2,'x',self.dev.manip2MoveStep)
            if joystick.get_button( 5 ):
                if self.ui.activateDev1.isChecked():
                    #print 1,'x',-1*self.dev.manip1MoveStep
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(1,'x',-1*self.dev.manip1MoveStep)
                if self.ui.activateDev2.isChecked():
                    #print 2,'x',-1*self.dev.manip1MoveStep
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(2,'x',-1*self.dev.manip2MoveStep)
            # Manipulator Dev 1
            setZ = self.dev.setStage[2]
            if self.ui.activateDev1.isChecked() and self.ui.trackStageZMovementDev1Btn.isChecked():
                mov = oldSetZ - setZ
                if mov:
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(1,'z',-1*mov)

            elif self.ui.activateDev1.isChecked() and self.ui.trackStageXMovementDev1Btn.isChecked():
                mov = (oldSetZ - setZ)/np.cos(self.dev.alphaDev1*np.pi/180.)
                if mov:
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(1,'x',-1*mov)
            # Manipulator Dev 2
            if self.ui.activateDev2.isChecked() and self.ui.trackStageZMovementDev2Btn.isChecked():
                mov = oldSetZ - setZ
                if mov:
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(2,'z',-1*mov)
            elif self.ui.activateDev2.isChecked() and self.ui.trackStageXMovementDev2Btn.isChecked():
                mov = (oldSetZ - setZ)/np.cos(self.dev.alphaDev2*np.pi/180.)
                if mov:
                    with self.SM5_ModLock:
                        self.dev.moveManipulatorToNewLocation(2,'x',-1*mov)
            oldSetZ = self.dev.setStage[2]
            # Limit to 10 frames per second
            self.clock.tick(10)
    #################################################################################################
    def getMinMaxOfStage(self):
        self.dev.getMinMaxOfStage()
        self.ui.minMaxXLocationValueLabel.setText(str(round(self.dev.maxStage[0],self.dev.precision)))
        self.ui.minMaxYLocationValueLabel.setText(str(round(self.dev.maxStage[1],self.dev.precision)))
        self.ui.minMaxZLocationValueLabel.setText(str(round(self.dev.maxStage[2],self.dev.precision)))
    
    #################################################################################################
    def setMovementValues(self,moveSize):
        if moveSize == 'fine':
            self.ui.fineBtn.setChecked(True)
        elif moveSize == 'small':
            self.ui.smallBtn.setChecked(True)
        elif moveSize == 'medium':
            self.ui.mediumBtn.setChecked(True)
        elif moveSize == 'coarse':
            self.ui.coarseBtn.setChecked(True)
        #
        self.dev.setMovementValuesStage(moveSize)
        
        self.ui.stepLineEdit.setText(str(self.dev.moveStep))
        self.ui.speedLineEdit.setText(str(self.dev.moveSpeed))
        self.ui.precisionLineEdit.setText(str(self.dev.movePrecision))
        
        #self.propagateSpeeds()
    #################################################################################################
    def setC843StepValue(self):
        moveStep = float(self.ui.stepLineEdit.text())
        self.dev.setMovementValuesStage(None,moveStep,None,None)
        
    #################################################################################################
    def setC843SpeedValue(self):
        moveSpeed = float(self.ui.speedLineEdit.text())
        self.dev.setMovementValuesStage(None,None,moveSpeed,None)
    
    #################################################################################################
    def setC843PrecisionValue(self):
        movePrecision = float(self.ui.precisionLineEdit.text())
        self.dev.setMovementValuesStage(None,None,None,movePrecision)
    
    
    #################################################################################################
    def readSM5SpeedFromDevice(self):
        vel = self.dev.getSM5PositingVelocityFast('x')
        self.ui.device1SpeedLE.setText(str(vel[0]))
        self.ui.device2SpeedLE.setText(str(vel[1]))
    #################################################################################################
    def setSM5Speed(self,dev):
        if dev == 1:
            velocity = float(self.ui.device1SpeedLE.text())
        elif dev == 2:
            velocity = float(self.ui.device2SpeedLE.text())
        self.dev.setSM5Speed(dev,velocity)
    
    #################################################################################################
    def loadSM5StepValues(self):   
        self.dev.loadSM5StepValues()
        self.ui.device1StepLE.setText(str(self.dev.manip1MoveStep))
        self.ui.device2StepLE.setText(str(self.dev.manip2MoveStep))
    
    #################################################################################################
    def setSM5Step(self):
        manip1 = float(self.ui.device1StepLE.text())
        manip2 = float(self.ui.device2StepLE.text())
        self.dev.setSM5Step([manip1,manip2])
    #################################################################################################
    def updateStageLocations(self):
        # C843
        self.dev.C843_get_position()
        
    #################################################################################################
    def updateSetStagePositions(self):
        for i in range(3):
            if i == 0:
                self.ui.setXLocationLineEdit.setText(str(round(self.dev.setStage[0],self.dev.precision)))
            elif i == 1:
                self.ui.setYLocationLineEdit.setText(str(round(self.dev.setStage[1],self.dev.precision)))
            elif i == 2:
                self.ui.setZLocationLineEdit.setText(str(round(self.dev.setStage[2],self.dev.precision)))
    #################################################################################################
    def updateIsStagePositions(self):
        self.ui.isXLocationValueLabel.setText(str(round(self.dev.isStage[0],self.dev.precision)))
        self.ui.isYLocationValueLabel.setText(str(round(self.dev.isStage[1],self.dev.precision)))
        self.ui.isZLocationValueLabel.setText(str(round(self.dev.isStage[2],self.dev.precision)))
        
        self.updateHomeTable()    
    
    #################################################################################################
    def recordCell(self,nElectrode,identity):
        xyzU = self.dev.isStage
        
        nC = len(self.cells)
        
        self.cells[nC] = {}
        self.cells[nC]['number'] = self.nItem
        self.cells[nC]['type'] = identity # 'MLI'
        self.cells[nC]['electrode'] = nElectrode
        self.cells[nC]['location'] = np.array([round(xyzU[0],self.dev.precision),round(xyzU[1],self.dev.precision),round(xyzU[2],self.dev.precision)])
        self.cells[nC]['depth'] = 0.

        print 'added ',str(nC),'item'	
        self.nItem+=1
        
        self.updateTable()
        
        #self.repaint()
    #################################################################################################
    def updateTable(self):
        print len(self.cells), self.rowC
        # expand table when list is loaded directly from file
        while (len(self.cells)+1) > (self.rowC):
            self.ui.cellListTable.insertRow(self.rowC)
            self.ui.cellListTable.setRowHeight(self.rowC,self.rowHeight)
            self.rowC+=1
        for r in range(len(self.cells)):
            for c in range(5):
                if c==0:
                    self.ui.cellListTable.setItem(r, c, QtGui.QTableWidgetItem(str(self.cells[r]['number'])))
                elif c==1:
                    if self.cells[r]['type']=='PC':
                        self.ui.cellListTable.setItem(r, c, QtGui.QTableWidgetItem('PC'))
                    elif  self.cells[r]['type']=='MLI':
                        self.ui.cellListTable.setItem(r, c, QtGui.QTableWidgetItem('MLI'))
                    #elif  self.cells[r]['type']=='surface':
                    #	self.cellListTable.setItem(r, c, QtGui.QTableWidgetItem('S'))
                elif c==2:
                    self.ui.cellListTable.setItem(r, c, QtGui.QTableWidgetItem(str(self.cells[r]['electrode'])))
                elif c==3:
                    if not self.cells[r]['depth'] == 0.:
                        depth = self.cells[r]['depth']
                        self.ui.cellListTable.setItem(r, c, QtGui.QTableWidgetItem(str(depth)))
                    #pass
                elif c==4:
                    loc = str(self.cells[r]['location'][0])+','+str(self.cells[r]['location'][1])+','+str(self.cells[r]['location'][2])
                    self.ui.cellListTable.setItem(r, c, QtGui.QTableWidgetItem(loc))    
    #################################################################################################
    def moveToLocation(self):
        
        self.setStatusMessage('moving stage to cell')

        r = self.ui.cellListTable.selectionModel().selectedRows()
        nR = 0
        for index in sorted(r):
            row = index.row()
            nR+=1
        print 'row: ',row
        xyz = ([self.cells[row]['location'][0],self.cells[row]['location'][1],self.cells[row]['location'][2]])
        print 'move to :', xyz
        
        for i in range(3):
            self.dev.moveStageToNewLocation(i,self.cells[row]['location'][i],moveType='absolute')

        self.unSetStatusMessage('moving stage to cell')
    #################################################################################################
    def updateLocation(self):
        r = self.ui.cellListTable.selectionModel().selectedRows()
        nR = 0
        for index in sorted(r):
            row = index.row()
            nR +=1
        self.cells[row]['location'] = np.array([round(self.dev.isStage[0],self.dev.precision),round(self.dev.isStage[1],self.dev.precision),round(self.dev.isStage[2],self.dev.precision)])
        self.updateTable()
        #self.repaint()
    
    #################################################################################################
    def removeLocation(self):
        #print self.cells
        r = self.ui.cellListTable.selectionModel().selectedRows()
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
        self.updateTable()
        self.ui.cellListTable.removeRow((nCells-1))
        self.ui.cellListTable.insertRow((nCells-1))
        self.ui.cellListTable.setRowHeight((nCells-1),self.rowHeight)
    #################################################################################################
    def recordDepth(self):
        
        r = self.ui.cellListTable.selectionModel().selectedRows()
        nR = 0
        for index in sorted(r):
            row = index.row()
            nR+=1
        
        self.cells[row]['depth'] = (self.cells[row]['location'][2] - round(self.dev.isStage[2],self.dev.precision))

        self.updateTable()
        print 'recorded depth of cell # ',str(self.cells[row]['number'])        
      
    #################################################################################################
    def saveLocations(self):
        print self.today_date
        saveDir = 'C:\\Users\\2-photon\\experiments\\ManipulatorControl\\cell_locations_'+self.today_date+'.p'
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File',saveDir, '.p')
        print str(filename),filename
        if filename:
            programData = {}
            programData['cells'] = self.cells
            programData['homeLocations'] = self.homeLocs
            pickle.dump(programData,open(filename,"wb"))
            self.fileSaved = True
    #################################################################################################
    def loadLocations(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Choose cell location file', 'C:\\Users\\2-photon\\experiments\\ManipulatorControl\\','Python object file (*.p)')
            
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
        # expand table when list is loaded directly from file
        while (len(self.homeLocs)+1) > (self.rowHomeC):
            self.ui.homeLocationsTable.insertRow(self.rowHomeC)
            self.ui.homeLocationsTable.setRowHeight(self.rowHomeC,self.rowHeight)
            self.rowHomeC+=1

        for r in range(len(self.homeLocs)):
            for c in range(4):
                if c==0:
                    self.ui.homeLocationsTable.setItem(r, c, QtGui.QTableWidgetItem(str(self.homeLocs[r]['number'])))
                elif c==1:
                    self.ui.homeLocationsTable.setItem(r, c, QtGui.QTableWidgetItem(str(round(self.dev.isStage[0]-self.homeLocs[r]['x'],self.dev.precision))))
                elif c==2:
                    self.ui.homeLocationsTable.setItem(r, c, QtGui.QTableWidgetItem(str(round(self.dev.isStage[1]-self.homeLocs[r]['y'],self.dev.precision))))
                elif c==3:
                    self.ui.homeLocationsTable.setItem(r, c, QtGui.QTableWidgetItem(str(round(self.dev.isStage[2]-self.homeLocs[r]['z'],self.dev.precision))))
    #################################################################################################
    def recordHomeLocation(self):
        nC = len(self.homeLocs)
        
        self.homeLocs[nC] = {}
        self.homeLocs[nC]['number'] = self.nHomeItem
        
        self.homeLocs[nC]['x'] = round(self.dev.isStage[0],self.dev.precision)
        self.homeLocs[nC]['y'] = round(self.dev.isStage[1],self.dev.precision)
        self.homeLocs[nC]['z'] = round(self.dev.isStage[2],self.dev.precision) 
        
        self.updateHomeTable()
        print 'added ',str(nC),'home item'   
        self.nHomeItem+=1
        self.repaint()
    #################################################################################################
    def updateHomeLocation(self):
        r = self.ui.homeLocationsTable.selectionModel().selectedRows()
        for index in sorted(r):
            row = index.row()
        
        self.homeLocs[row]['x'] = round(self.dev.isStage[0],self.dev.precision) 
        self.homeLocs[row]['y'] = round(self.dev.isStage[1],self.dev.precision) 
        self.homeLocs[row]['z'] = round(self.dev.isStage[2],self.dev.precision)
        self.updateHomeTable()
        self.repaint()
    #################################################################################################
    def removeHomeLocation(self):
        #print self.cells
        r = self.ui.homeLocationsTable.selectionModel().selectedRows()
        for index in sorted(r):
            row = index.row()

        nLocations = len(self.homeLocs)
        #print nCells, row

        del self.homeLocs[row]
        if (nLocations-1) != row:
            for i in range(row,(nLocations-1)):
                self.homeLocs[i] = self.homeLocs[i+1]
            del self.homeLocs[(nLocations-1)]
        self.updateHomeTable()
        self.ui.homeLocationsTable.removeRow((nLocations-1))
        self.ui.homeLocationsTable.insertRow((nLocations-1))
        self.ui.homeLocationsTable.setRowHeight((nLocations-1),self.rowHeight)
        self.repaint()
    #################################################################################################
    def moveToHomeLocation(self):
        
        self.setStatusMessage('moving stage to home location')

        r = self.ui.homeLocationsTable.selectionModel().selectedRows()
        for index in sorted(r):
            row = index.row()

        print 'row: ',row

        for i in range(3):
            self.dev.moveStageToNewLocation(i,self.homeLocs[row][self.axes[i]],moveType='absolute')
        
        self.unSetStatusMessage('moving stage to home location')
    
    #################################################################################################
    def updateSetManipulatorPositions(self):
        self.ui.xSetPosDev1LE.setText(str(round(self.dev.setDev1[0],self.dev.precision)))
        self.ui.ySetPosDev1LE.setText(str(round(self.dev.setDev1[1],self.dev.precision)))
        self.ui.zSetPosDev1LE.setText(str(round(self.dev.setDev1[2],self.dev.precision)))
        
        self.ui.xSetPosDev2LE.setText(str(round(self.dev.setDev2[0],self.dev.precision)))
        self.ui.ySetPosDev2LE.setText(str(round(self.dev.setDev2[1],self.dev.precision)))
        self.ui.zSetPosDev2LE.setText(str(round(self.dev.setDev2[2],self.dev.precision)))
            
    #################################################################################################
    def updateIsManipulatorPositions(self):
        self.ui.xIsPosDev1LE.setText(str(round(self.dev.isDev1[0],self.dev.precision)))
        self.ui.yIsPosDev1LE.setText(str(round(self.dev.isDev1[1],self.dev.precision)))
        self.ui.zIsPosDev1LE.setText(str(round(self.dev.isDev1[2],self.dev.precision)))
        
        self.ui.xIsPosDev2LE.setText(str(round(self.dev.isDev2[0],self.dev.precision)))
        self.ui.yIsPosDev2LE.setText(str(round(self.dev.isDev2[1],self.dev.precision)))
        self.ui.zIsPosDev2LE.setText(str(round(self.dev.isDev2[2],self.dev.precision)))
        
    #################################################################################################
    def setStatusMessage(self,statusText):
        self.ui.statusbar.showMessage(statusText+' ...')
        self.ui.statusbar.setStyleSheet('QStatusBar{color: red;font-weight:bold;}')
        self.ui.statusbar.repaint()
    #################################################################################################
    def unSetStatusMessage(self,statusText):
        self.ui.statusbar.showMessage(statusText+' ... done')
        self.ui.statusbar.setStyleSheet('QStatusBar{color: black;font-weight:normal}')
        #self.statusValue.repaint()   
    #################################################################################################
    def enableReferencePowerBtns(self):
        self.ui.C843XYPowerBtn.setEnabled(True)
        self.ui.C843ZPowerBtn.setEnabled(True)
        self.ui.SM5Dev1PowerBtn.setEnabled(True)
        self.ui.SM5Dev2PowerBtn.setEnabled(True)
        self.ui.refChoseLocationBtn.setEnabled(True)
        self.ui.refSavedLocationBtn.setEnabled(True)
        self.ui.refNegativeBtn.setEnabled(True)
    #################################################################################################
    def disableAndEnableBtns(self,newSetting):
        # connection panel
        self.ui.C843XYPowerBtn.setEnabled(newSetting)
        self.ui.C843ZPowerBtn.setEnabled(newSetting)
        self.ui.SM5Dev1PowerBtn.setEnabled(newSetting)
        self.ui.SM5Dev2PowerBtn.setEnabled(newSetting)
        self.ui.refChoseLocationBtn.setEnabled(newSetting)
        self.ui.refSavedLocationBtn.setEnabled(newSetting)
        self.ui.refNegativeBtn.setEnabled(newSetting)
        # Move panel
        self.ui.controllerActivateBtn.setEnabled(newSetting)
        self.ui.listenToSocketBtn.setEnabled(newSetting)
        # recorded locations
        self.ui.electrode1MLIBtn.setEnabled(newSetting)
        self.ui.electrode1PCBtn.setEnabled(newSetting)
        self.ui.electrode2MLIBtn.setEnabled(newSetting)
        self.ui.electrode2PCBtn.setEnabled(newSetting)
        
        self.ui.recordHomeLocationBtn.setEnabled(newSetting)
        self.ui.updateHomeLocationBtn.setEnabled(newSetting)
        self.ui.moveToHomeLocationBtn.setEnabled(newSetting)
        self.ui.removeHomeLocationBtn.setEnabled(newSetting)
        
        self.ui.moveToItemBtn.setEnabled(newSetting)
        self.ui.recordDepthBtn.setEnabled(newSetting)
        self.ui.saveLocationsBtn.setEnabled(newSetting)
        self.ui.updateItemLocationBtn.setEnabled(newSetting)
        self.ui.removeItemBtn.setEnabled(newSetting)
        self.ui.loadLocationsBtn.setEnabled(newSetting)
    ###################################################################################################
    def enableDisableControllerBtns(self, newSetting):
        
        self.ui.fineBtn.setEnabled(newSetting)
        self.ui.smallBtn.setEnabled(newSetting)
        self.ui.mediumBtn.setEnabled(newSetting)
        self.ui.coarseBtn.setEnabled(newSetting)
        
        self.ui.activateDev1.setEnabled(newSetting)
        self.ui.activateDev2.setEnabled(newSetting)
        
        self.ui.trackStageZMovementDev1Btn.setEnabled(newSetting)
        self.ui.trackStageXMovementDev1Btn.setEnabled(newSetting)
        self.ui.trackStageZMovementDev2Btn.setEnabled(newSetting)
        self.ui.trackStageXMovementDev2Btn.setEnabled(newSetting)
    
    ###################################################################################################
    def listenControlerButtonState(self, newState):
        if newState == 'inactive':
            self.ui.controllerActivateBtn.setChecked(False)
            self.ui.controllerActivateBtn.setText('Activate controller')
            self.ui.controllerActivateBtn.setStyleSheet('background-color:None')
        elif newState == 'active':
            self.ui.controllerActivateBtn.setChecked(True)
            self.ui.controllerActivateBtn.setText('Deactivate Controller')
            self.ui.controllerActivateBtn.setStyleSheet('background-color:red')
    
    ###################################################################################################
    def listenSocketButtonState(self, newState):
        if newState == 'inactive':
            self.ui.listenToSocketBtn.setChecked(False)
            self.ui.listenToSocketBtn.setText('Listen to Socket')
            self.ui.listenToSocketBtn.setStyleSheet('background-color:None')
        elif newState == 'active':
            self.ui.listenToSocketBtn.setChecked(True)
            self.ui.listenToSocketBtn.setText('Stop listening to Socket')
            self.ui.listenToSocketBtn.setStyleSheet('background-color:red')
    
    #########################################################################################
    def closeEvent(self, event):
        print 'stopping threads'
        self.updateManiuplators = False
        self.listenToSocket = False
        self.listenToControler = False
        time.sleep(.2)
        self.dev.closeConnections()
        
        # save locations and dispaly quitting dialog
        if not self.fileSaved and self.nItem>0:
            reply = QtGui.QMessageBox.question(self, 'Message',"Do you want to save the cell locations before quitting?",  QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Yes:
                self.saveLocations()
                event.accept()
            elif reply == QtGui.QMessageBox.No:
                event.accept()
            else:
                event.ignore()    
        else:
            reply = QtGui.QMessageBox.question(self, 'Message',"Do you want to quit?",  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()    
                
        
        
        
        
        
        
        
        
        
        
        
        