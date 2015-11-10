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
import params
from PyQt4 import QtCore 
from PyQt4 import QtGui

#from shapely.geometry import MultiPolygon, Polygon
#from shapely.topology import TopologicalError
#from skimage import transform as tf
#import itertools as it
#from random import shuffle
#import warnings as wa

import c843_class
import LandNSM5
import manipulatorGUI

from PyQt4.QtCore import *
from PyQt4.QtGui import *

#################################################################
class manipulatorControl():
    
    isStagePositionChanged = QtCore.Signal(object)
    setStagePositionsChanged = QtCore.Signal(object)
    
    """Instance of the hdf5 Data Manager Qt interface."""
    def __init__(self):
        
        
        self.gui = manipulatorGUI.manipulatorControlGui(self)
        self.gui.setWindowTitle('Manipulator Control')
        self.gui.setGeometry(params.xLocation, params.yLocation,params.widthSize,params.heightSize)
        
        self.gui.show()
        
        self.today_date = time.strftime("%Y%m%d")[2:]
        
        #self.connectSignals()
        
        # parameters for socket connection
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a socket object
        host = params.host #socket.gethostname() #Get the local machine name
        port = params.port # Reserve a port for your service
        self.s.bind((host,port)) #Bind to the port
        
        # precision of values to show and store
        self.precision = params.precision
        self.locationDiscrepancy = params.locationDiscrepancy
        
        # angles of the manipulators with respect to a vertical line
        self.alphaDev1 = params.alphaDev1
        self.alphaDev2 = params.alphaDev2
        self.manip1MoveStep = params.manip1MoveStep
        self.manip2MoveStep = params.manip2MoveStep
        
        self.axes         = np.array(['x','y','z'])
        self.stageAxes    = collections.OrderedDict([('x',2),('y',1),('z',3)])
        self.stageNumbers = collections.OrderedDict([(0,self.stageAxes['x']),(1,self.stageAxes['y']),(2,self.stageAxes['z'])])
        
        # movement parameters
        self.stepWidths = collections.OrderedDict([('fine',params.fineStepWidth),('small',params.smallStepWidth),('medium',params.mediumStepWidth),('coarse',params.coarseStepWidth)])
        
        self.speeds = collections.OrderedDict([('fine',params.fineSpeed),('small',params.smallSpeed),('medium',params.mediumSpeed),('coarse',params.coarseSpeed)])
        
        self.defaultMoveSpeed = 'fine'

        self.sm5Lock = Lock()
        self.c843Lock = Lock()

    
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
    
    #################################################################################################
    def init_C843(self):
        
        self.c843 = c843_class.c843_class()
        self.c843.init_stage(self.stageAxes['x'])
        self.c843.init_stage(self.stageAxes['y'])
        self.c843.init_stage(self.stageAxes['z'])
    #################################################################################################
    def delete_C843(self):
        del self.C843
    #################################################################################################
    def init_SM5(self):
        self.luigsNeumann = LandNSM5.LandNSM5()
    
    #################################################################################################
    def is_SM5_connected():
        return self.luigsNeumann.connected
        
    #################################################################################################
    def delete_SM5(self):
        del self.luigsNeumann
    
    #################################################################################################
    def C843_switch_servo_on_off(axis):
        self.c843.switch_servo_on_off(self.stageAxes[axis])
    
    #################################################################################################
    def SM5_switch_on_axis(device,axis):
        self.luigsNeumann.switchOnAxis(device,axis)
        
    #################################################################################################
    def SM5_switch_off_axis(device,axis):
        self.luigsNeumann.switchOffAxis(device,axis)
    
    #################################################################################################
    def C843_openReferenceFile(fileName):
        self.c843.openReferenceFile(fileName)
        
    #################################################################################################
    def C843_reference_state(moveStage):
        ref = [False]*3
        for i in range(3):
            ref[i] = self.c843.reference_stage(self.stageAxes[self.axes[i]],moveStage)
        return all(ref)
    
    #################################################################################################
    def getSM5PositingVelocityFast(axis):
        with self.sm5Lock:
            self.velManip1 = self.luigsNeumann.getPositioningVelocityFast(1,axis)
            self.velManip2 = self.luigsNeumann.getPositioningVelocityFast(2,axis)
        return [vel1,vel2]
    
    #################################################################################################
    def C843_get_position(isStage):
        for i in range(3):
            isStage[i] = self.c843.get_position(self.stageNumbers[i])
        
    
    #################################################################################################
    def SM5_getPosition(dev,axis=None):
        if axis is None:
            if dev == 1:
                with self.sm5Lock:
                    [self.isXDev1,self.isYDev1,self.isZDev1] = [self.luigsNeumann.getPosition(1,'x'),self.luigsNeumann.getPosition(1,'y'),self.luigsNeumann.getPosition(1,'z')]
            elif dev == 2:
                with self.sm5Lock:
                    [self.isXDev2,self.isYDev2,self.isZDev2] = [self.luigsNeumann.getPosition(2,'x'),self.luigsNeumann.getPosition(2,'y'),self.luigsNeumann.getPosition(2,'z')]
        else:
            if 'x' in axis:
                with self.sm5Lock:
                    self.isXDev1 = self.luigsNeumann.getPosition(1,'x')
                    self.isXDev2 = self.luigsNeumann.getPosition(2,'x')
            if 'y' in axis:
                with self.sm5Lock:
                    self.isYDev1 = self.luigsNeumann.getPosition(1,'y')
                    self.isYDev2 = self.luigsNeumann.getPosition(2,'y')
            if 'z' in axis:
                with self.sm5Lock:
                    self.isZDev1 = self.luigsNeumann.getPosition(1,'z')
                    self.isZDev2 = self.luigsNeumann.getPosition(2,'z')
    #################################################################################################
    def socket_connect():
        self.s.listen(1)
        self.connection,addr = self.s.accept()
        print 'established connection with ',addr
        #return self.c
    #################################################################################################
    def socket_monitor_activity():
        r, _, _ = select.select([self.connection], [], [])
        #data = self.c.recv(1024)
        #print r
        return bool(r)
    #################################################################################################
    def socket_read_data():
        return self.connection.recv(params.dataSize)
    #################################################################################################
    def socket_send_data(data):
        self.connection.send(data)
    #################################################################################################
    def socket_close_connection():
        self.connection.close()
    #################################################################################################
    def performRemoteInstructions(self,rawData):
        data = rawData.split(',')
        #
        if data[0] == 'getPos':
            with self.c843Lock:
                self.C843_get_position()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'relativeMoveTo':
            moveStep = float(data[2])
            with self.c843Lock:
                self.C843_get_position()
                oldIsStage = copy(self.isStage)
                # to do : implemente loop to converge against precise target location
                self.choseRightSpeed(abs(moveStep))
                self.moveStageToNewLocation(np.where(self.axes==data[1])[0][0],moveStep)
                self.isStagePositionChanged.emit()
                self.moveSpeed = self.moveSpeedBefore
                self.C843_propagateSpeeds()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'absoluteMoveTo':
            moveStep = float(data[2])
            with self.c843Lock:
                self.choseRightSpeed(abs(moveStep-self.isStage[np.where(self.axes==data[1])[0][0]]))
                self.moveStageToNewLocation(np.where(self.axes==data[1])[0][0],moveStep,moveType='absolute')
                self.isStagePositionChanged.emit()
                self.moveSpeed = self.moveSpeedBefore
                self.C843_propagateSpeeds()
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
        self.C843_propagateSpeeds()
    
    #################################################################################################
    def determine_stage_speed(self,moveSize):
        self.moveStep = self.stepWidths[moveSize]
        self.moveSpeed = self.speeds[moveSize]
        self.C843_propagateSpeeds()
    #################################################################################################
    def C843_propagateSpeeds(self):
        for i in range(3):
            self.c843.set_velocity(self.stageNumbers[i],self.moveSpeed)
    
    #################################################################################################
    def moveStageToNewLocation(self,axis,moveSign,moveType='relative'):
        
        # define movement length
        if moveType == 'relative':
            self.setStage[axis] += self.moveStep*moveSign
        if moveType == 'absolute':
            self.setStage[axis] = self.moveStep*moveSign
        # check if limits are reached
        if self.setStage[axis] < self.minStage[axis]:
            self.setStage[axis] = self.minStage[axis]
        elif self.setStage[axis] > self.maxStage[axis]:
            self.setStage[axis] = self.maxStage[axis]
        
        self.setStagePositionsChanged.emit()
        # update set locations
        #if axis==0:
        #    self.setXLocationLineEdit.setText(str(round(self.setStage[axis],self.precision)))
        #elif axis==1:
        #    self.setYLocationLineEdit.setText(str(round(self.setStage[axis],self.precision)))
        #elif axis==2:
        #    self.setZLocationLineEdit.setText(str(round(self.setStage[axis],self.precision)))
        while any(abs(self.isStage - self.setStage)> self.locationDiscrepancy):
            wait = True
            while wait:
                with self.c843Lock:
                    isMoving = self.c843.check_for_movement(self.stageNumbers[axis])
                if not isMoving: 
                    wait = False
            with self.c843Lock:
                self.c843.move_to_absolute_position(self.stageNumbers[axis],self.setStage[axis])
        self.isStagePositionChanged.emit()
    
    #################################################################################################
    def setManiplatorSpeed(self,dev,speed):
        with self.sm5Lock:
            self.luigsNeumann.setPositioningVelocityFast(dev,'x',speed)
    
    #################################################################################################
    def setManiplatorStep(self,steps):
        self.manip1MoveStep = steps[0]
        self.manip2MoveStep = steps[1]
        
    #################################################################################################
    def moveManipulatorToNewLocation(self,dev,axis,moveStep):
        if dev == 1:
            if axis == 'x':
                self.setXDev1+= self.moveStep
            elif axis == 'y':
                self.setYDev1+= self.moveStep
            elif axis == 'z':
                self.setZDev1+= self.moveStep
        elif dev == 2:
            if axis == 'x':
                self.setXDev2+= self.moveStep
            elif axis == 'y':
                self.setYDev2+= self.moveStep
            elif axis == 'z':
                self.setZDev2+= self.moveStep
                
        self.setManipulatorPositionsChanged.emit()
        #print self.loc
        if 'z' in axis:
            movementSize = self.moveStep
        else:
            movementSize= -1.*self.moveStep
        
        if abs(movementSize) > self.locationDiscrepancy:
            if dev == 1:
                with self.sm5Lock : #.acquire()
                    self.luigsNeumann.goVariableFastToRelativePosition(1,axis,float(movement))
            elif dev == 2:
                with self.sm5Lock : #.acquire()
                    self.luigsNeumann.goVariableFastToRelativePosition(2,axis,float(movement))
            # update locations
            self.SM5_getPosition(dev,axis)
            # show new loctions in gui
            self.isManipulatorPositionChanged.emit()
        
        #self.updateManipulatorLocations(axis)
        # release update thread here
        #self.sm5Lock.release()
        #self.initializeSetLocations()
        
##################################################################################
##################################################################################
##################################################################################    
    

    #################################################################################################
    def activateController(self):
        #
        if self.activate.is_alive():
            self.controllerActivateBtn.setText('Activate controller')
            self.controllerActivateBtn.setStyleSheet('background-color:None')
            self.done=True
            self.activate = Thread(target=self.controlerInput)
            self.enableDisableControllerBtns(False)
            print 'controler deactive'
        else:
            self.controllerActivateBtn.setText('Deactivate Controller')
            self.controllerActivateBtn.setStyleSheet('background-color:red')
            self.enableDisableControllerBtns(True)
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
            #self.enableDisableControllerBtns(False)
            #self.activate = Thread(ThreadStart(self.controlerInput))
            print 'socket deactive'
        else:
            self.listenToSocketBtn.setText('Stop listening to Socket')
            self.listenToSocketBtn.setStyleSheet('background-color:red')
            #self.enableDisableControllerBtns(True)
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
        self.isXLocationValueLabel.setText(str(round(self.isStage[0],self.precision)))
        self.isYLocationValueLabel.setText(str(round(self.isStage[1],self.precision)))
        self.isZLocationValueLabel.setText(str(round(self.isStage[2],self.precision)))
        
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
    def setStepValue(self,moveSt):
        self.moveStep = moveSt

    #################################################################################################
    def setSpeedValue(self,moveSp):
        self.moveSpeed = moveSp
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
    def enableDisableControllerBtns(self, newSetting):
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
    app = QtGui.QApplication(sys.argv)
    form = manipulatorControl()
    #form.show()
    app.exec_()        

    