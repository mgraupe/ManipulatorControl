import sys
import pygame
import select
from threading import *
from functools import partial

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import manipulatorTemplate 
#import manipulator


#################################################################
class manipulatorControlGui(QMainWindow,manipulatorTemplate.Ui_MainWindow,Thread):
    
    isStagePositionChanged = Signal(object)
    isManipulatorPositionChanged = Signal(object)
    
    def __init__(self,dev):
        
        self.dev = dev

        # initialize the UI and parent class
        QMainWindow.__init__(self)
        
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
        self.ui.homeLocationsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.ui.homeLocationsTable.setColumnWidth(0,30)
        self.ui.homeLocationsTable.setColumnWidth(1,100)
        self.ui.homeLocationsTable.setColumnWidth(2,100)
        self.ui.homeLocationsTable.setColumnWidth(3,100)
        
        self.cells = {}
        self.nItem = 0
        self.rowC = 6
        
        self.ui.cellListTable.setRowCount(self.rowC)
        for i in range(self.rowC):
            self.ui.cellListTable.setRowHeight(i,self.rowHeight)
        self.ui.cellListTable.setSelectionMode(self.ui.cellListTable.ContiguousSelection)
        self.ui.cellListTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # configure column widths in cellListTable
        self.ui.cellListTable.setColumnWidth(0,30)
        self.ui.cellListTable.setColumnWidth(1,38)
        self.ui.cellListTable.setColumnWidth(2,30)
        self.ui.cellListTable.setColumnWidth(3,58)
        self.ui.cellListTable.setColumnWidth(4,150)
        
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        
        
        self.disableAndEnableBtns(False)
        self.enableDisableControllerBtns(False)
        
        #self.activate = Thread(target=self.controlerInput)
        #self.receiveControlerInput = Thread(target=self.controlerInput)
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
        self.ui.stepLineEdit.editingFinished.connect(self.getStepValue)
        self.ui.speedLineEdit.editingFinished.connect(self.getSpeedValue)
        
        #self.ui.device1StepLE.editingFinished.connect(self.setManiplatorStep)
        #self.ui.device2StepLE.editingFinished.connect(self.setManiplatorStep)
        
        #self.ui.device1SpeedLE.editingFinished.connect(partial(self.setManiplatorSpeed,1))
        #self.ui.device2SpeedLE.editingFinished.connect(partial(self.setManiplatorSpeed,2))
        
        #################################################
        ## Location panel 
        #self.ui.electrode1MLIBtn.clicked.connect(partial(self.recordCell,1,'MLI'))
        #self.ui.electrode1PCBtn.clicked.connect(partial(self.recordCell,1,'PC'))
        #self.ui.electrode2MLIBtn.clicked.connect(partial(self.recordCell,2,'MLI'))
        #self.ui.electrode2PCBtn.clicked.connect(partial(self.recordCell,2,'PC'))
        
        #self.ui.moveToItemBtn.clicked.connect(self.moveToLocation)
        #self.ui.updateItemLocationBtn.clicked.connect(self.updateLocation)
        #self.ui.recordDepthBtn.clicked.connect(self.recordDepth)
        #self.ui.removeItemBtn.clicked.connect(self.removeLocation)
        #self.ui.saveLocationsBtn.clicked.connect(self.saveLocations)
        #self.ui.loadLocationsBtn.clicked.connect(self.loadLocations)
        
        #self.ui.recordHomeLocationBtn.clicked.connect(self.recordHomeLocation)
        #self.ui.updateHomeLocationBtn.clicked.connect(self.updateHomeLocation)
        #self.ui.moveToHomeLocationBtn.clicked.connect(self.moveToHomeLocation)
        #self.ui.removeHomeLocationBtn.clicked.connect(self.removeHomeLocation)        
    
        #self.dev.setPositionChanged.connect(self.update)
        #self.dev.isPositionChanged.connect(self.updateLimits)
        
        ##################################################
        # signals
        self.isStagePositionChanged.connect(self.updateIsStagePositions)
        self.isManipulatorPositionChanged.connect(self.updateIsManipulatorPositions)
        
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
            self.C843XYPowerBtn.setChecked(False)
            self.C843ZPowerBtn.setChecked(False)
            self.disableAndEnableBtns(False)
        
        # SM5
        self.setStatusMessage('initializing Luigs and Neumann SM5')
        try :
            self.dev.luigsNeumann
        except AttributeError:
            self.dev.init_SM5()
            if self.dev.is_SM5_connected():
                self.SM5Dev1PowerBtn.setChecked(True)
                self.SM5Dev2PowerBtn.setChecked(True)
                self.autoUpdateManipulatorLocations.start()
            else:
                reply = QMessageBox.warning(self, 'Warning','Switch on Luigs & Neumann SM5 controller.',  QMessageBox.Ok )
        else:
            if self.autoUpdateManipulatorLocations.is_alive():
                self.updateManiuplators=False
                self.autoUpdateManipulatorLocations.join()
                self.autoUpdateManipulatorLocations = Thread(target=self.autoUpdateManip)
            self.dev.delete_SM5()
            self.SM5Dev1PowerBtn.setChecked(False)
            self.SM5Dev2PowerBtn.setChecked(False)
            self.readManipulatorSpeed()
        #
        self.unSetStatusMessage('initializing stages')
    
    #################################################################################################
    def switchOnOffC843Motors(self,axes):
        # if active : deactivate controler first
        if self.receiveControlerInput.is_alive():
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
        self.ui.setStatusMessage('referencing axes')
        #
        if fileName:
            self.dev.C843_openReferenceFile(fileName)
        
        if  self.dev.C843_reference_state(moveStage):
            self.ui.refChoseLocationBtn.setEnabled(False)
            self.ui.refSavedLocationBtn.setEnabled(False)
            self.ui.refNegativeBtn.setEnabled(False)
            
            self.updateStageLocations()
            self.initializeSetLocations()
            self.getMinMaxOfStage()
            self.setMovementValues(self.defaultMoveSpeed)
        else:
            reply = QMessageBox.warning(self, 'Warning','Reference failed.',  QMessageBox.Ok )
        #
        self.ui.disableAndEnableBtns(True)
        self.ui.unSetStatusMessage('referencing axes')
        
    #################################################################################################
    def activateController(self):
        #
        if self.receiveControlerInput.is_alive():
            self.ui.controllerActivateBtn.setText('Activate controller')
            self.ui.controllerActivateBtn.setStyleSheet('background-color:None')
            self.listenToControler=False
            self.receiveControlerInput = Thread(target=self.controlerInput)
            self.ui.enableDisableControllerBtns(False)
            print 'controler inactive'
        else:
            self.ui.controllerActivateBtn.setText('Deactivate Controller')
            self.ui.controllerActivateBtn.setStyleSheet('background-color:red')
            self.ui.enableDisableControllerBtns(True)
            self.receiveControlerInput.start()
            print 'controler active'

    #################################################################################################
    def activateSocket(self):
        #
        if self.socketListenThread.is_alive():
            self.ui.listenToSocketBtn.setChecked(False)
            self.ui.listenToSocketBtn.setText('Listen to Socket')
            self.ui.listenToSocketBtn.setStyleSheet('background-color:None')
            self.listenToSocket=False
            self.socketListenThread = Thread(target=self.socketListening)
            print 'socket inactive'
        else:
            self.ui.listenToSocketBtn.setChecked(True)
            self.ui.listenToSocketBtn.setText('Stop listening to Socket')
            self.ui.listenToSocketBtn.setStyleSheet('background-color:red')
            self.socketListenThread.start()
            print 'socket active'
    
    #################################################################################################        
    def autoUpdateManip(self):
        self.updateManiuplators=True
        while self.updateManiuplators:
            pos1 = self.dev.SM5_getPosition(1)
            pos2 = self.dev.SM5_getPosition(2)
            self.isManipulatorPositionChanged.emit()
            time.sleep(1)
    
    #################################################################################################  
    def socketListening(self):
        self.listenToSocket = True
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
                        #self.listenToSocket = False
                        #self.listenThread = Thread(target=self.socketListening)
                        break
                    #print "Got data: ", data, 'from', addr[0],':',addr[1]
                    res = self.dev.performRemoteInstructions(data)
                    self.dev.socket_send_data(str(res)+'...'+data)
                except socket.error:
                    print 'socket connection closed due to error'
                    #self.activateSocket()
                    break
                #self.c.close()
        self.dev.socket_close_connection()
        self.activateSocket()
        
        #self.ui.listenToSocketBtn.setChecked(False)
        #self.ui.listenToSocketBtn.setText('Listen to Socket')
        #self.ui.listenToSocketBtn.setStyleSheet('background-color:None')
        #print 'thread ended by remote host'
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
        self.dev.determine_stage_speed()
        
        self.ui.stepLineEdit.setText(str(self.dev.moveStep))
        self.ui.speedLineEdit.setText(str(self.dev.moveSpeed))
        
        #self.propagateSpeeds()
    #################################################################################################
    def updateIsManipulatorPositions():
        self.xIsPosDev1LE.setText(str(round(self.isXDev1,self.precision)))
        self.yIsPosDev1LE.setText(str(round(self.isYDev1,self.precision)))
        self.zIsPosDev1LE.setText(str(round(self.isZDev1,self.precision)))
        
        self.xIsPosDev2LE.setText(str(round(self.isXDev2,self.precision)))
        self.yIsPosDev2LE.setText(str(round(self.isYDev2,self.precision)))
        self.zIsPosDev2LE.setText(str(round(self.isZDev2,self.precision)))
    
    #################################################################################################
    def readManipulatorSpeed():
        vel = self.dev.getSM5PositingVelocityFast('x')
        self.device1SpeedLE.setText(str(vel[0]))
        self.device2SpeedLE.setText(str(vel[1]))
    #################################################################################################
    def getStepValue(self):
        moveStep = float(self.stepLineEdit.text())
        self.dev.setStepValue(moveStep)
        
    #################################################################################################
    def getSpeedValue(self):
        moveSpeed = float(self.speedLineEdit.text())
        self.dev.setSpeedValue(moveSpeed)
    #################################################################################################
    def updateStageLocations(self):
        # C843
        self.dev.C843_get_position()
        self.isStagePositionChanged.emit()
    
    #################################################################################################
    def updateIsStagePositions():
        self.isXLocationValueLabel.setText(str(round(self.dev.isStage[0],self.precision)))
        self.isYLocationValueLabel.setText(str(round(self.dev.isStage[1],self.precision)))
        self.isZLocationValueLabel.setText(str(round(self.dev.isStage[2],self.precision)))
        
        self.updateHomeTable()    
    #################################################################################################
    def initializeSetLocations(self):
        for i in range(3):
            self.setStage[i] = self.dev.isStage[i]
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
    def setStatusMessage(self,statusText):
        self.ui.statusbar.showMessage(statusText+' ...')
        self.ui.statusbar.setStyleSheet('color: red')
        #self.statusbar.repaint()
    #################################################################################################
    def unSetStatusMessage(self,statusText):
        self.ui.statusbar.showMessage(statusText+' ... done')
        self.ui.statusbar.setStyleSheet('color: black')
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

    
        
        
        
        
        
        
        
        
        
        