import sys
import pygame
from threading import *
from functools import partial

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import manipulatorTemplate 
#import manipulator


#################################################################
class manipulatorControlGui(QMainWindow,manipulatorTemplate.Ui_MainWindow,Thread):
    
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
        #self.autoUpdateManipulatorLocations = Thread(target=self.autoUpdateManip)
        #self.socketListenThread = Thread(target=self.socketListening) # listenThread
        
        
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
        
        #self.ui.refChoseLocationBtn.clicked.connect(self.referenceChoseLocations)
        #self.ui.refSavedLocationBtn.clicked.connect(partial(self.referenceStage,False))
        #self.ui.refNegativeBtn.clicked.connect(partial(self.referenceStage,True))
        
        #################################################
        ## Move panel
        #self.ui.controllerActivateBtn.clicked.connect(self.activateController)
        #self.ui.listenToSocketBtn.clicked.connect(self.listenToSocket)
        
        #self.ui.fineBtn.clicked.connect(partial(self.setMovementValues,'fine'))
        #self.ui.smallBtn.clicked.connect(partial(self.setMovementValues,'small'))
        #self.ui.mediumBtn.clicked.connect(partial(self.setMovementValues,'medium'))
        #self.ui.coarseBtn.clicked.connect(partial(self.setMovementValues,'coarse'))
        #self.ui.stepLineEdit.editingFinished.connect(self.getStepValue)
        #self.ui.speedLineEdit.editingFinished.connect(self.getSpeedValue)
        
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
                self.controllerActivateBtn.setChecked(False)
                self.listenToSocketBtn.setChecked(False)
                self.controllerActivateBtn.setText('Activate Controller')
                self.listenToSocketBtn.setText('Listen to Socket')
                self.listenControlerDone=True
                self.listenSocket = False
                self.receiveControlerInput = Thread(target=self.controlerInput)
                self.socketListenThread = Thread(target=self.socketListening)
                #self.activate = Thread(ThreadStart(self.controlerInput))
                print 'controller deactive'
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
                self.updateManiuplatorsDone=True
                self.autoUpdateManipulatorLocations.join()
                self.autoUpdateManipulatorLocations = Thread(target=self.autoUpdateManip)
            self.dev.delete_SM5()
            self.SM5Dev1PowerBtn.setChecked(False)
            self.SM5Dev2PowerBtn.setChecked(False)
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

    
        
        
        
        
        
        
        
        
        
        