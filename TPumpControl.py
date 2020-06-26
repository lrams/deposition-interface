import serial
from threading import Lock
devaddr='001'
s485 = 0
s485Lock = Lock()

#Initializes RS485 Port to the TMP (Turbo Molecular Pump)
def initialize():
    try:
        print('Connecteing to port...')
        global s485
        s485 = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)
        print('Port Opened Successfully')
    except:
        print('Error: Port USB0 not open, exit program and check port')

#Builds an ASCII bytestring to send to the TMP
def buildFrameStr(addr, action, params, datalength, data):
    ordsum = 0
    outstr = addr + action + params + datalength + data
    for i in outstr:
        ordsum += ord(i)
    checksum = str(ordsum % 256)
    while (len(checksum) < 3):
    	checksum = '0' + checksum
    #print(checksum)
    outstr += checksum + '\r'
    return bytearray(outstr, 'ascii')

#Returns the current Rpm of the TMP
def getRotSpeed():
    wstr = buildFrameStr(devaddr,'00','309','02','=?')
    s485Lock.acquire()
    s485.write(wstr)
    val = s485.readline().decode("utf-8")
    s485Lock.release()
    return val

#Gets various temperatures from the pump
def getTemp(val):
    #Parameters:
    #Temp of power stage = 324
        #Temp of electronics = 326
        #Temp of pump bottom = 330
        #Temp of bearing = 342
        #Temp of motor = 346
    if val == 'pwstg':
        param = '324'
    elif val == 'elec':
        param = '326'
    elif val == 'pbot':
        param = '330'
    elif val == 'bearing':
        param = '342'
    elif val == 'motor':
        param = '346'
    wstr = buildFrameStr(devaddr,'00',param,'02','=?')
    s485Lock.acquire()
    s485.write(wstr)
    val = s485.readline().decode("utf-8")
    s485Lock.release()
    return val

#Toggles Standby mode
def standbyT(num):
    if num == 1:
        wstr = buildFrameStr(devaddr,'10','002','06','111111')
    elif num == 0:
        wstr = buildFrameStr(devaddr,'10','002','06','000000')
    s485Lock.acquire()
    s485.write(wstr)
    print(s485.readline())
    s485Lock.release()

#Toggles Pump on or off
def pumpT(num):
    if num == 1:
        wstr = buildFrameStr(devaddr,'10','010','06','111111')
    elif num == 0:
        wstr = buildFrameStr(devaddr,'10','010','06','000000')
    s485Lock.acquire()
    s485.write(wstr)
    print(s485.readline())
    s485Lock.release()
