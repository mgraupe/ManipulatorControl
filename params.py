###################################################
# Gui placement and size on computer screen
xLocation = 10
yLocation = 30
widthSize = 537
heightSize = 971

###################################################
# precision of values to show and store
precision = 1
locationDiscrepancy = 0.1

###################################################
# C843
fineStepWidth = 1.
smallStepWidth = 10.
mediumStepWidth = 100.
coarseStepWidth  = 1000.

fineSpeed = 0.01
smallSpeed = 0.05
mediumSpeed = 0.2
coarseSpeed = 1.5

defaultXLocation = 10.
defaultYLocation = 10.
defaultZLocation = 18100. #6000.

###################################################
# Luigs and Neumann
# angles of the manipulators with respect to a vertical line
alphaDev1 = 30. # in degrees
alphaDev2 = 30. # in degrees

manip1MoveStep = 2. # in um
manip2MoveStep = 2. # in um
        
###################################################
# parameters for socket connection
host = '172.20.61.89' #socket.gethostname() #Get the local machine name
port = 5555 # Reserve a port for your service
dateSize = 1024 # size of data-packages sent back and forth