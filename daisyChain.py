from pipython import GCSDevice
import numpy as np


# C-863 controller with device ID 3, this is the master device
# E-861 controller with device ID 7
# C-867 controller with device ID 1


c863 = GCSDevice('C-863.11')
c863.OpenUSBDaisyChain(description='0195500449')
daisychainid = c863.dcid


m1 = GCSDevice('C-863.11')
m1.ConnectDaisyChainDevice(1, daisychainid)

m2 = GCSDevice('C-863.11')
m2.ConnectDaisyChainDevice(2, daisychainid)

m3 = GCSDevice('C-863.11')
m3.ConnectDaisyChainDevice(3, daisychainid)
#mo1 = m1.GCSDevice('C-863.11')

#c863.ConnectDaisyChainDevice(1, daisychainid)
#with GCSDevice('C-863.11') as m1:
#    motor1 = m1
##    m1.ConnectDaisyChainDevice(2, daisychainid)
#with GCSDevice('C-863.11') as m2:
#        motor2 = m2
#        m2.ConnectDaisyChainDevice(3, daisychainid)
#        with GCSDevice('C-863.11') as m3:
#            motor3 = m3


#print('on/off :',m1.qSVO())
#m1.SVO('1',True)
#m2.SVO('1',True)
#m1.STP()
try:
    m1.HLT('1')
except BaseException as e:
    print(str(e))
else:
    pass

print('on/off :',m1.qSVO())
m1.SVO('1',True)
print('qfrf :',m1.qFRF())
print('fpl :',m1.FPL())
print('qfrf :',m1.qFRF())
isMoving = True
while isMoving:
    print('.',)
    res = m1.IsMoving()
    isMoving = res['1']
print('qfrf :',m1.CLR())
print('m1 clr :',m1.CLR())
print('m2 clr :',m2.CLR())
print('m2 clr :',m2.CLR())
#print('m1 qron :',m1.qRON())
#m1.RON('1',True)
#m1.REF()
#m1.FPL()
#print(qron)
#print(m1.qVEL())
#m1.VEL('1',0.75)
#print('qfrf :',m1.qFRF())

#print(m1.GetInterfaceDescription())
#print('\n{}:\n{}:\n{}'.format(m1.GetInterfaceDescription(), m1.qIDN(), m1.qPOS()))
#print('\n{}:\n{}:\n{}'.format(m2.GetInterfaceDescription(), m2.qIDN(), m2.qPOS()))
#print('\n{}:\n{}:\n{}'.format(m3.GetInterfaceDescription(), m3.qIDN(), m3.qPOS()))


#def main():
    #"""Connect three controllers on a daisy chain."""
    #with GCSDevice('C-863.11') as c863:
        ## c863.OpenRS232DaisyChain(comport=1, baudrate=115200)
        #c863.OpenUSBDaisyChain(description='0195500449')
        ## c863.OpenTCPIPDaisyChain(ipaddress='192.168.178.42')
        #daisychainid = c863.dcid
        #c863.ConnectDaisyChainDevice(1, daisychainid)
        #with GCSDevice('C-863.11') as e861:
            #e861.ConnectDaisyChainDevice(2, daisychainid)
            #with GCSDevice('C-863.11') as c867:
                #c867.ConnectDaisyChainDevice(3, daisychainid)
                #print('\n{}:\n{}'.format(c863.GetInterfaceDescription(), c863.qIDN()))
                #print('\n{}:\n{}'.format(e861.GetInterfaceDescription(), e861.qIDN()))
                #print('\n{}:\n{}'.format(c867.GetInterfaceDescription(), c867.qIDN()))


#if __name__ == '__main__':
    ## import logging
    ## logging.basicConfig(level=logging.DEBUG)
    #main()
