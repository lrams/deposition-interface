from appJar import gui 
import numpy
import time
import random
import Pyserial
import nidaqmx
from decimal import Decimal
Pyserial.initialize()

num = 1
app = gui()

#Interprets data from TMP serial responses
def intData(data):

	#Ensures data reads 0 and no array errors happen if data is empty
	if len(data) == 0:
		data = '00000000010000'
	
	datlen = int(data[8] + data[9]) #Extracts length of the data from the string
	output = ''
	for i in range(10,10 + datlen):
		output += data[i]
	return output
		
#Reads voltage from the pressure sensor via NI board
def readPressureLL():
	with nidaqmx.Task() as task:
			task.ai_channels.add_ai_voltage_chan('Dev1/ai1',max_val=10)
			voltage = task.read()
	return 10**(1.667*voltage-11.46) #Pressure in Torr returned
	
def readPressureMC():
	with nidaqmx.Task() as task:
			task.ai_channels.add_ai_voltage_chan('Dev1/ai0',max_val=10)
			voltage = task.read()
	return 10**(1.667*voltage-11.46) #Pressure in Torr returned

def exitb():
    app.stop()

#Updates all info from the NI board
def NiUpdate():
    while (True):
        app.queueFunction(app.setLabel, "PrLl", "Load Lock Pressure: {:.3e} Torr ".format(readPressureLL()))
		app.queueFunction(app.setLabel, "PrMc", "Main Chamber Pressure: {:.3e} Torr ".format(readPressureMC()))
        time.sleep(2)

#Updates info from the Pump
def serialPump():
		while (True):
			rpmd = intData(Pyserial.getRpm())
			tempMotor = intData(
			tempBearing =
			tempElec =
			
			app.queueFunction(app.setLabel, "llrpms", str(int(rpmd)) + " Hz")
			time.sleep(1)

#updates the time displayed	
def timeUpdate():
	app.queueFunction(app.setLabel, "date", str(time.ctime()))

#toggles the TMP on/off
def pumpOn():
	Pyserial.s485.write(Pyserial.buildFrameStr('001','00','313','06','=?'))
	print(Pyserial.s485.readline())
	Pyserial.pumpT(1)
def pumpOff():
	Pyserial.pumpT(0)

#gui definitions
app.setBg(colour="grey")
#app.setSize("800x600")
app.setTitle("Sputtering Deposition System")

app.addLabel("date",time.ctime())

app.startLabelFrame("Pressures:")
app.addLabel("PrMc","Main Chamber Pressure:   Torr ",0,0)
app.addLabel("PrLl","Load Lock Pressure:   Torr ",1,0)
app.stopLabelFrame()

app.startLabelFrame("System Status:")

app.addLabel("llp","LL Pump Status:",0,0)
app.addLabel("llps","ON",0,1)
app.addLabel("llrpm", "TMP Speed:",1,0)
app.addLabel("llrpms", "", 1, 1)
app.addLabel("cpv","Cryopump Valve Status:",2,0)
app.addLabel("cpvs","OPEN",2,1)
app.stopLabelFrame()

app.addVerticalSeparator(0,1,0,10,colour="black")

app.startLabelFrame("Controls:",1,2,2,2)
app.setPadding([10,10])
app.addButton("LL Pump ON",pumpOn,0,0)
app.addButton("LL Pump OFF", pumpOff,1,0)
app.stopLabelFrame()



app.thread(NiUpdate)
app.thread(serialPump)
app.registerEvent(timeUpdate)
app.go()
