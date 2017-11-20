from ctypes import *
from numpy import *
import pdb
import time
import os.path
import pickle
#import pco_camera_open_close
#import pco_get_live_image_1
import matplotlib.pyplot as plt

IS_SUCCESS = 1

#######################################################################
#######################################################################
# Helper functions
def check(fn_name,fn_return,verb):
	if (fn_return == IS_SUCCESS):
		if verb:
			print 'c843: ', fn_name , 'call successful'
	else:
		print 'c843: ', fn_name , 'call failed with error', fn_return
	

#######################################################################
#######################################################################
class c843_class(object):
	###############################################################
	def __init__(self):
		print 'init'
		
		# general class parameters
		self.verbose = False
		self.fnameLocations = 'c843_locations.p'
		# c843 units are mm - scaling_factor defines translation to any interface
		self.scaling_factor = 1000. # converstion to \mu m
		
		# import shared library 
		self.c843 = cdll.LoadLibrary('C843_GCS_DLL_x64.dll') #WinDLL(None,handle=self.libHandle)
		self.boardNumber = c_long(1)
		self.ID  = self.c843.C843_Connect(self.boardNumber)
		if self.ID < 0:
			print 'Connection to board failed'
			sys.exit(1)
		print 'Boardnumber : ',self.ID
		self.iID  = c_long(self.ID)
		
		# dictionary to keep camera status
		self.glvar = {}
		self.glvar['c843_connected'] = 1
		# x-axis
		self.glvar['1'] = {}
		self.glvar['1']['referenced'] = 0
		self.glvar['1']['maxTravelRange'] = None
		
		# y-axis
		self.glvar['2'] = {}
		self.glvar['2']['referenced'] = 0
		self.glvar['2']['maxTravelRange'] = None
		# z-axis
		self.glvar['3'] = {}
		self.glvar['3']['referenced'] = 0
		self.glvar['3']['maxTravelRange'] = None
		#
		self.glvar['out_ptr'] = self.c843
		self.glvar['board_id'] = self.iID
		
		self.openReferenceFile(self.fnameLocations)
		
		if self.verbose:
			print 'C843 ready'
		
	###############################################################
	def __del__(self):
		# save file only if there is no internal error
		errorCode = c_long()
		errorCode = self.c843.C843_GetError(self.iID)
		
		self.saveStageLocations()
		
		self.c843.C843_CloseConnection(self.iID)
		self.glvar['c843_connected'] = 0
		if self.verbose:
		    print 'c843_connected should be 0 is :' , str(self.glvar['c843_connected'])
		del self.c843
		print 'Connection to c843 closed.'
	###############################################################
	def openReferenceFile(self, fName):
		if os.path.isfile(fName):
			if self.verbose:
				print 'Location file exists'
			self.loc = pickle.load(open(fName))
			if all((not self.loc['1']==None, not self.loc['2']==None, not self.loc['3']==None)):
				self.referenceLocations=True
			else:
				self.referenceLocations=False
		else:
			if self.verbose:
				print 'No location file found. New locations evoked.'
			self.loc = {}
			self.loc['1'] = None
			self.loc['2'] = None
			self.loc['3'] = None
			self.referenceLocations=False
	###############################################################
	def saveStageLocations(self):
		if self.glvar['1']['referenced'] and self.glvar['2']['referenced'] and self.glvar['3']['referenced']:
			pickle.dump(self.loc,open(self.fnameLocations,"wb"))
			sprint 'stage locations saved'
			
	###############################################################
	def init_stage(self,nAxis):
		# e.g. 1,2 or 3
		szAxes = c_char_p(str(nAxis))
		# specific motor configuration of the setup
		# e.g. 'PLC-85MICOS' for x and y, or 'M-111.1DG' for z- axis
		if nAxis==1 or nAxis==2:
			stageName = 'PLC-85MICOS'
		elif nAxis==3:
			stageName = 'M-122.2DDBIS'
		
		stages = c_char_p(str(stageName))
		# Assigns szAxes to stages.
		check('C843_CS',self.c843.C843_CST(self.iID, szAxes , stages ),self.verbose)
		# Initializes motion control chip for szAxes, Switches the servo on.
		check('C843_INI',self.c843.C843_INI(self.iID, szAxes), self.verbose)
		#
	###############################################################
	def reference_stage(self,nAxis,moveForReference):
		
		#moveDirection='neg'
		# e.g. 1,2 or 3
		szAxes = c_char_p(str(nAxis))
		# read current reference mode
		curRefMode = c_bool()
		check('C843_qRON',self.c843.C843_qRON(self.iID, szAxes ,byref(curRefMode)),self.verbose)
		
		# reference locations from file, no reference move executed
		if (not moveForReference) and (self.referenceLocations):
			if self.verbose:
				print 'Reference locations from file.'
			setRefMode = c_bool(False)
			if curRefMode != setRefMode:
				check('C843_RON',self.c843.C843_RON(self.iID, szAxes ,byref(setRefMode)),self.verbose)
			
			# set absolute position
			setAbsPosition = c_double(self.loc[str(nAxis)])
			check('C843_POS',self.c843.C843_POS(self.iID, szAxes ,byref(setAbsPosition)),self.verbose)
		
		# reference mode of axis is ON, the axis must be driven to the reference switch
		else:
			referenceMoveSuccessful = False
			while not referenceMoveSuccessful:
				# reinitialization is necessary if reference move failed
				self.init_stage(nAxis)
				
				if self.verbose:
					print 'Reference move to ',moveDirection,'switch limit.'
				setRefMode = c_bool(True)
				if curRefMode != setRefMode:
					check('C843_RON',self.c843.C843_RON(self.iID, szAxes ,byref(setRefMode)),self.verbose)
				
				# Check if the given axes have a reference
				hasref = c_bool()
				check('C843_qREF',self.c843.C843_qREF(self.iID, szAxes ,byref(hasref)),self.verbose)
				if self.verbose:
					print str(nAxis), 'qREF', hasref.value
				if hasref.value:
					# Reference move of szAxes.
					res = self.c843.C843_REF(self.iID, szAxes)	
				#Moves axis szAxes to its negative limit switch. Used to reference an axis without a reference switch.
				else:
					ref = c_char_p()
					haslim = c_bool()
					res = check('C843_qLIM',self.c843.C843_qLIM(self.iID, szAxes, byref(haslim) ), self.verbose)
					if self.verbose:
						print str(nAxis), 'qLIM : ', haslim.value
					if haslim.value:
						# Moves axis 'szAxes' to its negative limit switch. 
						#if moveDirection == 'pos':
						#	check('C843_MPL',self.c843.C843_MPL(self.iID, szAxes),self.verbose)
						# Moves axis 'szAxes' to its positive limit switch
						#else:
						check('C843_MNL',self.c843.C843_MNL(self.iID, szAxes),self.verbose)
				
				isreferencing = True
				if self.verbose:
					print "Referencing",
				while isreferencing:
					isref = c_bool()
					check('C843_IsReferencing',self.c843.C843_IsReferencing(self.iID, szAxes, byref(isref)),self.verbose)
					isreferencing = isref.value
					if self.verbose:
						print ".",
					time.sleep(0.5)
				if self.verbose:
					print ' done.'
				
				refResult = c_bool()
				check('C843_GetRefResult',self.c843.C843_GetRefResult(self.iID, szAxes, byref(refResult)),self.verbose)
				referenceMoveSuccessful = refResult.value
			
			
		refOK = c_bool()
		check('C843_IsReferenceOK',self.c843.C843_IsReferenceOK(self.iID, szAxes, byref(refOK)),self.verbose)
		
		
		# Get the high and low end of the travel range of szAxes in working units.
		maxTravelRange = c_double()
		check('C843_qTMX',self.c843.C843_qTMX(self.iID, szAxes, byref(maxTravelRange)),self.verbose)
		minTravelRange = c_double()
		check('C843_qTMN',self.c843.C843_qTMN(self.iID, szAxes,byref(minTravelRange)),self.verbose)
		
		self.loc[str(nAxis)] = self.get_position(nAxis)/self.scaling_factor
		
		self.glvar[str(nAxis)]['referenced'] = 1
		self.glvar[str(nAxis)]['minMaxTravelRange'] = array([minTravelRange.value,maxTravelRange.value])
		
		return refOK
		
	##################################################################
	def get_velocity(self,nAxis):
		# e.g. 1,2 or 3
		szAxes = c_char_p(str(nAxis))
		curVel = c_double()
		check('C843_qVEL',self.c843.C843_qVEL(self.iID, szAxes, byref(curVel)),self.verbose)
		return curVel.value

	########################################################################################
	def get_position(self,nAxis):
		# e.g. 1,2 or 3
		szAxes = c_char_p(str(nAxis))
		curPos = c_double()
		check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(curPos)),self.verbose)
		return (curPos.value)*self.scaling_factor
	
	##################################################################
	def set_velocity(self,nAxis,newVelocity):
		# e.g. 1,2 or 3
		szAxes = c_char_p(str(nAxis))
		newVel = c_double(newVelocity)
		check('C843_VEL',self.c843.C843_VEL(self.iID, szAxes, byref(newVel)),self.verbose)
		#return newVel.value
	
	########################################################################################
	def move_to_absolute_position(self,nAxis,newPos):
		
		# e.g. 1,2 or 3
		szAxes = c_char_p(str(nAxis))
		curPos = c_double()
		check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(curPos)),self.verbose)
		if self.verbose:
			print 'Start position: ' + str(curPos.value)
		
		targetPos = c_double(newPos/self.scaling_factor)

		check('C843_MOV',self.c843.C843_MOV(self.iID, szAxes , byref(targetPos)),self.verbose)
		ismoving = True
		while ismoving :
			#pos = c_double()
			#check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(pos)),self.verbose)
			#if self.verbose:
			#	print 'Intermediate position: ' + str(pos.value)
			ismov = c_bool()
			# command without check function in order to avoid command line clutter
			self.c843.C843_IsMoving(self.iID, szAxes,byref(ismov))
			ismoving = ismov.value
			time.sleep(0.01)

		pos = c_double()
		check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(pos)),self.verbose)
		if self.verbose:
			print 'End position: ' + str(pos.value)
		
		self.loc[str(nAxis)] = pos.value
	
	########################################################################################
	def relative_move(self,nAxis,relPos):
		
		# e.g. 1,2 or 3
		szAxes = c_char_p(str(nAxis))
		curPos = c_double()
		check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(curPos)),self.verbose)
		if self.verbose:
			print 'Start position: ' + str(curPos.value)
		
		relTargetPos = c_double(relPos/self.scaling_factor)

		check('C843_MVR',self.c843.C843_MVR(self.iID, szAxes , byref(relTargetPos)),self.verbose)
		ismoving = True
		while ismoving :
			pos = c_double()
			check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(pos)),self.verbose)
			if self.verbose:
				print 'Intermediate position: ' + str(pos.value)
			ismov = c_bool()
			check('C843_IsMoving',self.c843.C843_IsMoving(self.iID, szAxes,byref(ismov)),self.verbose)
			ismoving = ismov.value
			time.sleep(1)

		pos = c_double()
		check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(pos)),self.verbose)
		if self.verbose:
			print 'End position: ' + str(pos.value)
		
		self.loc[str(nAxis)] = pos.value
	
	
	########################################################################################
	def check_for_movement(self,nAxis):
		szAxes = c_char_p(str(nAxis))
		ismov = c_bool()
		check('C843_IsMoving',self.c843.C843_IsMoving(self.iID, szAxes,byref(ismov)),self.verbose)
		return ismov.value
	
	########################################################################################
	def switch_servo_on_off(self,nAxis):
		szAxes = c_char_p(str(nAxis))
		self.isOn = c_bool()
		check('C843_qSVO',self.c843.C843_qSVO(self.iID, szAxes,byref(self.isOn)),self.verbose)
		if self.isOn:
			self.stop_any_move()
			switchOn = c_bool(False)
			check('C843_SVO',self.c843.C843_SVO(self.iID, szAxes,byref(switchOn)),self.verbose)
			if self.verbose:
				print 'Servo switched off'
		else:
			switchOn = c_bool(True)
			check('C843_SVO',self.c843.C843_SVO(self.iID, szAxes,byref(switchOn)),self.verbose)
			if self.verbose:
				print 'Servo switched on'
	
	########################################################################################
	def stop_any_move(self):
		# 
		check('C843_STP',self.c843.C843_STP(self.iID),self.verbose)
		
		# read positions after abort
		for nAxis in range(1,4):
			szAxes = c_char_p(str(nAxis))
			pos = c_double()
			check('C843_qPOS',self.c843.C843_qPOS(self.iID, szAxes, byref(pos)),self.verbose)
			if self.verbose:
				print 'Interrrupt position: ' + str(pos.value)
		
			self.loc[str(nAxis)] = pos.value
		
		
	########################################################################################
	def get_min_max_travel_range(self,nAxis):
		return (self.glvar[str(nAxis)]['minMaxTravelRange'])*self.scaling_factor
	
	########################################################################################
	def get_all_positions(self,axesNumbers):
		return ((self.loc[str(axesNumbers[0])])*self.scaling_factor,(self.loc[str(axesNumbers[1])])*self.scaling_factor,(self.loc[str(axesNumbers[2])])*self.scaling_factor)
		
