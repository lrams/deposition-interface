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
		s485 = serial.Serial(port='COM6',baudrate=9600,timeout=1)
		print('Port Opened Successfully')
	except:
		print('Error: Port COM6 not open, exit program and check port')

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
def getRpm():
	wstr = buildFrameStr(devaddr,'00','309','02','=?')
	s485Lock.acquire()
	s485.write(wstr)
	val = s485.readline().decode("utf-8")
	s485Lock.release()
	return val

def getTemp(num):
	param = str(num)
	wstr = buildFrameStr(devaddr,'00',param,'02','=?')
	s485Lock.acquire()
	s485.write(wstr)
	val = s485.readline().decode("utf-8")
	s485Lock.release()
	return val


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
