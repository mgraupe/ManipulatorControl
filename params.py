###################################################
# Gui placement and size on computer screen
xLocation = -3600
yLocation = -950
widthSize = 537
heightSize = 971

###################################################
# precision of values to show and store
precision = 1
locationDiscrepancy = 0.5

###################################################
# stage class : C843 or C863

stage = 'C863' # or 'C843'
fineStepWidth = [2.,2.,2.]
smallStepWidth = [10.,10.,5.]
mediumStepWidth = [100.,100.,20.]
coarseStepWidth  = [1000.,1000.,1000.]

fineSpeed = 0.02
smallSpeed = 0.05
mediumSpeed = 0.2
coarseSpeed = 0.9

fineStepPrecision = 0.2
smallStepPrecision = 0.5
mediumStepPrecision = 1.
coarseStepPrecision  = 3.


defaultXLocation = 12000. #12000.
defaultYLocation = 12000. #12000.
defaultZLocation = 24000. #6000.

maximalStageMoves = 8.

focusDistance = 6570.

###################################################
# Luigs and Neumann
# angles of the manipulators with respect to a vertical line
alphaDev1 = 38. # in degrees
alphaDev2 = 38. # in degrees

manipulator1MoveStep = 2. # in um
manipulator2MoveStep = 2. # in um
        
###################################################
# parameters for socket connection
host = '127.0.0.1' #socket.gethostname() #Get the local machine name
port = 5555 # Reserve a port for your service
dataSize = 1024 # size of data-packages sent back and forth
