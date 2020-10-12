#! python
import os
import sys
from os.path import join, dirname, isdir
import pdb
import time
import numpy as np
import re
import socket
import select
import collections
from threading import *
from PyQt4 import QtCore, QtGui

#from shapely.geometry import MultiPolygon, Polygon
#from shapely.topology import TopologicalError
#from skimage import transform as tf
#import itertools as it
#from random import shuffle
#import warnings as wa

import c863_class
import c843_class
import LandNSM5
import params
from manipulatorGUI import manipulatorControlGui

#################################################################
class manipulatorControl(QtCore.QObject):
    
    #isStagePositionChanged = QtCore.Signal()
    #setStagePositionsChanged = QtCore.Signal()
    setStagePositionChanged = QtCore.Signal()
    isStagePositionChanged = QtCore.Signal()
    setManipulatorPositionChanged = QtCore.Signal()
    isManipulatorPositionChanged = QtCore.Signal()
    #programIsClosing = QtCore.Signal(object)
    """Instance of the hdf5 Data Manager Qt interface."""
    def __init__(self):
        
        super(manipulatorControl,self).__init__()
        self.gui = manipulatorControlGui(self)
        self.gui.setWindowTitle('Manipulator Control')
        self.gui.setGeometry(params.xLocation, params.yLocation,params.widthSize,params.heightSize)
        
        self.gui.show()
        
        self.today_date = time.strftime("%Y%m%d")[2:]
        
        #self.connectSignals()
        self.stage = params.stage
        
        # parameters for socket connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a socket object
        host = params.host #socket.gethostname() #Get the local machine name
        port = params.port # Reserve a port for your service
        self.sock.bind((host,port)) #Bind to the port
        #self.sock.settimeout(10)
        
        # precision of values to show and store
        self.precision = params.precision
        self.locationDiscrepancy = params.locationDiscrepancy
        self.focusDistance = params.focusDistance
        
        # angles of the manipulators with respect to a horizontal line
        self.alphaDev1 = params.alphaDev1
        self.alphaDev2 = params.alphaDev2
        
        self.axes         = np.array(['x','y','z'])
        self.stageAxes    = collections.OrderedDict([('x',1),('y',2),('z',3)])
        self.stageNumbers = collections.OrderedDict([(0,self.stageAxes['y']),(1,self.stageAxes['x']),(2,self.stageAxes['z'])])
        self.maxLoops = params.maximalStageMoves
        
        # movement parameters
        self.stepWidths = collections.OrderedDict([('fine',params.fineStepWidth),('small',params.smallStepWidth),('medium',params.mediumStepWidth),('coarse',params.coarseStepWidth)])
        
        self.stepPrecision = collections.OrderedDict([('fine',params.fineStepPrecision),('small',params.smallStepPrecision),('medium',params.mediumStepPrecision),('coarse',params.coarseStepPrecision)])
        
        self.speeds = collections.OrderedDict([('fine',params.fineSpeed),('small',params.smallSpeed),('medium',params.mediumSpeed),('coarse',params.coarseSpeed)])
        
        self.defaultMoveSpeed = 'fine'
        
        self.defaultLocations = np.array([params.defaultXLocation,params.defaultYLocation,params.defaultZLocation])
        self.sm5Lock = Lock()
        self.stageLock = Lock()

    
    #################################################################################################
    # destroy class instances
    def __del__(self):
        # sutter class
        try: 
            self.stageClass
        except AttributeError:
            pass
        else:
            del self.stageClass
        # tdt class
        try: 
            self.luigsNeumann
        except AttributeError:
            pass
        else:
            del self.luigsNeumann
    
    #################################################################################################
    def init_stageClass(self):
        
        if self.stage == 'C843':
            self.stageClass = c843_class.c843_class()
            self.stageClass.init_stage(self.stageAxes['x'])
            self.stageClass.init_stage(self.stageAxes['y'])
            self.stageClass.init_stage(self.stageAxes['z'])
            self.isStage = np.zeros(3)
        elif self.stage == 'C863':
            self.stageClass = c863_class.c863_class()
            self.stageClass.init_stage(self.stageAxes['x'])
            self.stageClass.init_stage(self.stageAxes['y'])
            self.stageClass.init_stage(self.stageAxes['z'])
            self.isStage = np.zeros(3)
        else:
            print 'define valid stage name'
    #################################################################################################
    def delete_stageClass(self):
        del self.stageClass
    #################################################################################################
    def init_SM5(self):
        self.luigsNeumann = LandNSM5.LandNSM5()
        self.isDev1 = np.zeros(3)
        self.isDev2 = np.zeros(3)
        #self.SM5_getPosition()
        #self.setDev1 = np.copy(self.isDev1)
        #self.setDev2 = np.copy(self.isDev2)
        #self.setManipulatorPositionChanged.emit()
    
    #################################################################################################
    def is_SM5_connected(self):
        return self.luigsNeumann.connected
        
    #################################################################################################
    def delete_SM5(self):
        del self.luigsNeumann
    
    #################################################################################################
    def C843_switch_servo_on_off(self,axis):
        with self.stageLock:
            self.stageClass.switch_servo_on_off(self.stageAxes[axis])
    
    #################################################################################################
    def SM5_switch_on_axis(self,device,axis):
        self.luigsNeumann.switchOnAxis(device,axis)
        
    #################################################################################################
    def SM5_switch_off_axis(self,device,axis):
        self.luigsNeumann.switchOffAxis(device,axis)
    
    #################################################################################################
    def C843_openReferenceFile(self,fileName):
        with self.stageLock:
            self.stageClass.openReferenceFile(fileName)
    
    #################################################################################################
    def C843_saveLocations(self):
        with self.stageLock:
            try: 
                self.stageClass
            except AttributeError:
                pass
            else:
                self.stageClass.saveStageLocations()
            
    #################################################################################################
    def C843_reference_state(self,moveStage):
        ref = [False]*3
        with self.stageLock:
            for i in range(3):
                ref[i] = self.stageClass.reference_stage(self.stageAxes[self.axes[i]],moveStage)
        self.isStage = np.zeros(3)
        self.C843_get_position()
        self.setStage = np.copy(self.isStage)
        return all(ref)
    
    #################################################################################################
    def getSM5PositingVelocityFast(self,axis):
        with self.sm5Lock:
            vel1 = self.luigsNeumann.getPositioningVelocityFast(1,axis)
            vel2 = self.luigsNeumann.getPositioningVelocityFast(2,axis)
        return [vel1,vel2]
    
    #################################################################################################
    def C843_get_position(self):
        with self.stageLock:
            for i in range(3):
                self.isStage[i] = self.stageClass.get_position(self.stageNumbers[i])
        self.isStagePositionChanged.emit()
    
    #################################################################################################
    def SM5_getPosition(self,dev=None,axis=None):
        if axis is None:
            with self.sm5Lock:
                for i in range(3):
                    self.isDev1[i] = self.luigsNeumann.getPosition(1,self.axes[i])
                    self.isDev2[i] = self.luigsNeumann.getPosition(2,self.axes[i])
        else:
            with self.sm5Lock:
                self.isDev1[np.where(self.axes==axis)[0][0]] = self.luigsNeumann.getPosition(1,axis)
                self.isDev2[np.where(self.axes==axis)[0][0]] = self.luigsNeumann.getPosition(2,axis)

        self.isManipulatorPositionChanged.emit()
    #################################################################################################
    def SM5_copyIsToSetLoctions(self):
        self.setDev1 = np.copy(self.isDev1)
        self.setDev2 = np.copy(self.isDev2)
        self.setManipulatorPositionChanged.emit()
    #################################################################################################
    def socket_connect(self):
        self.sock.listen(1)
        print 'after listen'
        self.connection,addr = self.sock.accept()
        print 'established connection with ',addr
        #return self.c
    #################################################################################################
    def socket_monitor_activity(self):
        r, _, _ = select.select([self.connection], [], [])
        #data = self.c.recv(1024)
        #print r
        return bool(r)
    #################################################################################################
    def socket_read_data(self):
        return self.connection.recv(params.dataSize)
    #################################################################################################
    def socket_send_data(self,data):
        self.connection.send(data+'\n')
    #################################################################################################
    def socket_close_connection(self):
        self.connection.close()
    #################################################################################################
    def performRemoteInstructions(self,rawData):
        data = rawData.split(',')
        #
        if data[0] == 'getPos':
            self.C843_get_position()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'relativeMoveTo':
            moveStep = float(data[2])
            self.C843_get_position()
            print data[1], data[2], self.axes
            oldIsStage = np.copy(self.isStage)
            # to do : implemente loop to converge against precise target location
            self.choseRightSpeed(abs(moveStep))
            #pdb.set_trace()
            print np.where(self.axes==data[1])[0][0],moveStep,'relative'
            #pdb.set_trace()
            self.moveStageToNewLocation(np.where(self.axes==data[1])[0][0],moveStep)
            self.moveSpeed = self.moveSpeedBefore
            self.movePrecision =  self.movePrecisionBefore 
            self.C843_propagateSpeeds()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'absoluteMoveTo':
            moveStep = float(data[2])
            self.choseRightSpeed(abs(moveStep-self.isStage[np.where(self.axes==data[1])[0][0]]))
            print np.where(self.axes==data[1])[0][0],moveStep,'absolute'
            self.moveStageToNewLocation(np.where(self.axes==data[1])[0][0],moveStep,moveType='absolute')
            # second call for higher move precision
            #self.moveStageToNewLocation(np.where(self.axes==data[1])[0][0],moveStep,moveType='absolute')
            self.moveSpeed = self.moveSpeedBefore
            self.movePrecision =  self.movePrecisionBefore 
            self.C843_propagateSpeeds()
            return (1,self.isStage[0],self.isStage[1],self.isStage[2])
        elif data[0] == 'checkMovement':
            isXMoving = self.stageClass.check_for_movement(self.stageAxes['x'])
            isYMoving = self.stageClass.check_for_movement(self.stageAxes['y'])
            isZMoving = self.stageClass.check_for_movement(self.stageAxes['z'])
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
        self.movePrecisionBefore = self.movePrecision
        # start from finest movement
        self.moveSpeed = self.speeds['fine']
        self.movePrecision = self.stepPrecision['fine']
        for key, value in self.stepWidths.iteritems():
            if abs(stepSize) >= value[0]:
                self.moveSpeed = self.speeds[key]
                self.movePrecision = self.stepPrecision[key]
            else :
                break
        #print stepSize, self.moveSpeed
        self.C843_propagateSpeeds()
    
    #################################################################################################
    def setMovementValuesStage(self,moveSize,moveSt=None,moveSp=None,movePr=None):
        if moveSize:
            self.moveStep = self.stepWidths[moveSize]
            self.moveSpeed = self.speeds[moveSize]
            self.movePrecision = self.stepPrecision[moveSize]
        else:
            if moveSt:
                self.moveStep = [moveSt,moveSt,moveSt] 
            if moveSp:
                self.moveSpeed = moveSp
            if movePr:
                self.movePrecision = movePr
        self.C843_propagateSpeeds()
        
    #################################################################################################
    def moveStageToDefaultLocation(self):
        for i in range(3):
            print('a')
            self.choseRightSpeed(self.defaultLocations[i]-self.isStage[i])
            print('b')
            self.moveStageToNewLocation(i,self.defaultLocations[i],moveType='absolute')
            print('c')
            self.moveSpeed = self.moveSpeedBefore
            self.movePrecision =  self.movePrecisionBefore 
        self.C843_propagateSpeeds()
        print('d')
    
    #################################################################################################
    def moveFocus(self,newZLocation):
        #for i in range(3):
        self.choseRightSpeed(newZLocation-self.isStage[2])
        self.moveStageToNewLocation(2,newZLocation)
        self.moveSpeed = self.moveSpeedBefore
        self.movePrecision =  self.movePrecisionBefore 
        self.C843_propagateSpeeds()
    
    #################################################################################################
    def C843_propagateSpeeds(self):
        with self.stageLock:
            for i in range(3):
                self.stageClass.set_velocity(self.stageNumbers[i],self.moveSpeed)
    
    #################################################################################################
    def moveStageToNewLocation(self,axis,moveStep,moveType='relative'):
        
        # define movement length
        if moveType == 'relative':
            self.setStage[axis] += moveStep
        if moveType == 'absolute':
            self.setStage[axis] = moveStep
        # check if limits are reached
        if self.setStage[axis] < self.minStage[axis]:
            self.setStage[axis] = self.minStage[axis]
        elif self.setStage[axis] > self.maxStage[axis]:
            self.setStage[axis] = self.maxStage[axis]
        
        self.setStagePositionChanged.emit()

        nLoops = 0
        #while (abs(self.setStage[axis] - self.isStage[axis])> self.locationDiscrepancy) and (nLoops<self.maxLoops):
        while (abs(self.setStage[axis] - self.isStage[axis])>= self.movePrecision):
            print axis, self.setStage[axis], self.isStage[axis]
            wait = True
            while wait:
                with self.stageLock:
                    isMoving = self.stageClass.check_for_movement(self.stageNumbers[axis])
                if not isMoving: 
                    wait = False
                print 'waiting due to movement'
            #self.choseRightSpeed(abs(self.setStage[axis]-self.isStage[axis]))
            with self.stageLock:
                print('1')
                self.stageClass.move_to_absolute_position(self.stageNumbers[axis],self.setStage[axis])
            #self.moveSpeed = self.moveSpeedBefore
            #self.C843_propagateSpeeds()
            self.C843_get_position()
            nLoops+=1
        print 'loops', nLoops, ' to reach precision : ', self.movePrecision
    #################################################################################################
    def setSM5Speed(self,dev,speed):
        with self.sm5Lock:
            self.luigsNeumann.setPositioningVelocityFast(dev,'x',speed)
    #################################################################################################
    def loadSM5StepValues(self):
        self.manip1MoveStep = params.manipulator1MoveStep
        self.manip2MoveStep = params.manipulator2MoveStep
        
    #################################################################################################
    def setSM5Step(self,steps):
        self.manip1MoveStep = steps[0]
        self.manip2MoveStep = steps[1]
        
    #################################################################################################
    def moveManipulatorToNewLocation(self,dev,axis,moveStep):
        if dev == 1:
            self.setDev1[np.where(self.axes==axis)[0][0]] += moveStep
        elif dev == 2:
            self.setDev2[np.where(self.axes==axis)[0][0]] += moveStep
                
        self.setManipulatorPositionChanged.emit()

        #if abs(movementSize) > self.locationDiscrepancy:
        loops=0
        while any(abs(self.setDev1 - self.isDev1) > self.locationDiscrepancy) or any(abs(self.setDev2 - self.isDev2) > self.locationDiscrepancy):
            if dev == 1:
                movement = (self.setDev1 - self.isDev1)[np.where(self.axes==axis)[0][0]]
                if not 'z' in axis:
                   movement = -movement
                with self.sm5Lock : 
                    print 1,axis,float(movement), self.luigsNeumann.getPositioningVelocityFast(1,axis)
                    self.luigsNeumann.goVariableFastToRelativePosition(1,axis,float(movement))
            elif dev == 2:
                movement = (self.setDev2 - self.isDev2)[np.where(self.axes==axis)[0][0]]
                if not 'z' in axis:
                   movement = -movement
                with self.sm5Lock :
                    #print 2,axis,float(movement), self.luigsNeumann.getPositioningVelocityFast(2,axis)
                    self.luigsNeumann.goVariableFastToRelativePosition(2,axis,float(movement))
            # update locations
            self.SM5_getPosition(dev,axis)
            # show new loctions in gui
            self.isManipulatorPositionChanged.emit()
            if loops > 20 : 
                print 'device location cannot be obtained'
                break
            loops+=1
        
    #################################################################################################
    def getMinMaxOfStage(self):
        # read maximal and minimal values
        self.minStage = np.zeros(3)
        self.maxStage = np.zeros(3)
        
        for i in range(3):
            with self.stageLock:
                (self.minStage[i],self.maxStage[i]) = self.stageClass.get_min_max_travel_range(self.stageNumbers[i])

    #########################################################################################
    def closeConnections(self):
        
        print 'closing connections to hardware',
        
        # trick to stop socket.accept() call
        #try:
        #    self.socketClose = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket object
        #    self.socketClose.connect(('172.20.61.89',params.port))
        #    self.socketClose.send('disconnect')
        #    self.socketClose.close()
        #except socket.error:
        #    pass
        
        self.sock.close()
        print 'socket closed',
        try : 
            self.connection
        except AttributeError:
            pass
        else:
            self.connection.close()
        
        print 'connection closed',
        
        # delete class istances
        try :
            self.stageClass
        except AttributeError:
            pass
        else:
            del self.stageClass
        
        print 'stage class closed',

        #####################################################
        try :
            self.luigsNeumann
        except AttributeError:
            pass
        else:
            del self.luigsNeumann

        print 'done'

##########################################################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    form = manipulatorControl()
    #form.show()
    app.exec_()        

    
