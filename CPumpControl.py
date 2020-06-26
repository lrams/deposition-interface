import serial
from threading import Lock
import numpy as np
s232 = 0
s232Lock = Lock()


# Initialize rs232 port to the cryopump
def initialize():
    try:
        print('Connecteing to port...')
        global s232
        s232 = serial.Serial(port='/dev/ttyUSB1',baudrate=2400,timeout=1,parity=serial.PARITY_EVEN,bytesize=serial.SEVENBITS,stopbits=serial.STOPBITS_ONE)
        print('Port Opened Successfully')
    except:
        print('Error: Port USB1 not open, exit program and check port')
        
def buildFrameString(data):
    # Checksum algorithm descibed in pg B-2 of CryopumpRS232.pdf
    outStr = '$'
    ordSum = 0
    # Sums the ASCII values of the data string, then mod 256
    for i in data:
        ordSum += ord(i)
    modSum = ordSum % 256
    # Binary string representation of modSum fixed to 8 bit length
    binRep = '0b' + bin(modSum)[2:].zfill(8)
    
    d1 = int(binRep[2]) ^ int(binRep[8])
    d0 = int(binRep[3]) ^ int(binRep[9])
    nBinRep = binRep[:-2] + str(d1) + str(d0)
    
    maskedBinRep = nBinRep[:2] + '00' + nBinRep[-6:]
    
    chkSum = chr(int(maskedBinRep,2) + int('0x30',16))
    outStr += data + chkSum + '\r'
    return bytearray(outStr,'ascii')

def getStageTemp(stage):
    if stage == 'first':
        comm = 'J'
    elif stage == 'second':
        comm = 'K'
    else:
        return 'Bad Function Call'
    output = buildFrameString(comm)
    s232Lock.acquire()
    s232.write(output)
    reply = s232.readline()
    s232Lock.release()
    return reply

def pumpPower(command):
    if command == 'on':
        param = '1'
    elif command == 'off':
        param = '0'
    elif command == 'status':
        param = '?'
    else:
        return 'Bad Function Call'
    
    output = buildFrameString('A' + param)
    s232Lock.acquire()
    s232.write(output)
    reply = s232.readline()
    s232Lock.release()
    return reply
