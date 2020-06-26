from appJar import gui 
import time
import TPumpControl
import CPumpControl
from decimal import Decimal
import piplates.DAQC2plate as DAQ

TPumpControl.initialize()
CPumpControl.initialize()

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

    
def readPressureLL():
    voltage = DAQ.getADC(0,0) - DAQ.getADC(0,1)
    vadj = 1.004029*voltage - 0.000386 # Calibrated for Pi Plate Error
    return 10**(1.66666667*vadj-11.46) #Pressure in Torr returned

def readPressureMC():
    voltage = DAQ.getADC(0,2) - DAQ.getADC(0,3)
    vadj = 1.004029*voltage - 0.000386 # Calibrated for Pi Plate Error
    return 10**(1.66666667*vadj-11.46) #Pressure in Torr returned

def exitb():
    app.stop()

#Updates all info from the ADC
def ADCupdate():
    while (True):
        app.queueFunction(app.setLabel, "PrLl", "Load Lock Pressure: {:.3e} Torr ".format(readPressureLL()))
        app.queueFunction(app.setLabel, "PrMc", "Main Chamber Pressure: {:.3e} Torr ".format(readPressureMC()))
        time.sleep(2)

#Updates info from the TMP
def serialTPump():
    while (True):
        rpmd = intData(TPumpControl.getRotSpeed())
        tempPwstg = intData(TPumpControl.getTemp('pwstg'))
        tempElec = intData(TPumpControl.getTemp('elec'))
        tempPbot = intData(TPumpControl.getTemp('pbot'))
        tempBearing = intData(TPumpControl.getTemp('bearing'))
        tempMotor = intData(TPumpControl.getTemp('motor'))

        app.queueFunction(app.setLabel, "llHzs", str(int(rpmd)) + " Hz")
        app.queueFunction(app.setLabel, "Tpwrstg", "Power Stage Temperature: " + str(int(tempPwstg)) + " C")
        app.queueFunction(app.setLabel, "Telec", "Electronics Temperature: " + str(int(tempElec)) + " C")
        app.queueFunction(app.setLabel, "Tpbot", "Pump Bottom Temperature: " + str(int(tempPbot)) + " C")
        app.queueFunction(app.setLabel, "Tbearing", "Bearing Temperature: " + str(int(tempBearing)) + " C")
        app.queueFunction(app.setLabel, "Tmotor", "Motor Temperature: " + str(int(tempMotor)) + " C")
 
        time.sleep(1)

def serialCPump():
    while True:
        tempFstg = CPumpControl.getStageTemp('first')
        tempSstg = CPumpControl.getStageTemp('second')
        status = CPumpControl.pumpPower('status')
        
        app.queueFunction(app.setLabel, "Cstatus","Cryopump Status: " + str(status))
        app.queueFunction(app.setLabel, "Cfstg", "First Stage Temperature: " + str(tempFstg))
        app.queueFunction(app.setLabel, "Csstg", "Second Stage Temperature: " + str(tempSstg))
        
        time.sleep(1)

#updates the time displayed 
def timeUpdate():
    app.queueFunction(app.setLabel, "date", str(time.ctime()))

#toggles the TMP on/off
def pumpOn():
    TPumpControl.pumpT(1)
def pumpOff():
    TPumpControl.pumpT(0)

def pumpStOn():
    TPumpControl.standbyT(1)
def pumpStOff():
    TPumpControl.standbyT(0)
    
def cPumpOn():
    CPumpControl.pumpPower('on')
def cPumpOff():
    CPumpControl.pumpPower('off')
    
#gui definitions
#app.setBg(colour="white")
#app.setSize("800x600")
app.setTitle("Sputtering Deposition System")
app.setFont(size=26)

app.startTabbedFrame("Main Frame")
#app.setBg(colour="grey")

app.startTab("Main")
app.setBg(colour="grey")

app.addLabel("date",time.ctime())

app.startLabelFrame("Pressures:")
app.addLabel("PrMc","Main Chamber Pressure:   Torr ",0,0)
app.addLabel("PrLl","Load Lock Pressure:   Torr ",1,0)
app.stopLabelFrame()

app.startLabelFrame("System Status:")
app.addLabel("llp","LL Pump Status:",0,0)
app.addLabel("llps","ON",0,1)
app.addLabel("llHz", "TMP Speed:",1,0)
app.addLabel("llHzs", "", 1, 1)
app.addLabel("cpv","Cryopump Valve Status:",2,0)
app.addLabel("cpvs","OPEN",2,1)
app.stopLabelFrame()

app.addVerticalSeparator(0,1,0,10,colour="black")

app.startLabelFrame("Controls:",1,2,2,2)
app.setPadding([10,10])
app.addButton("LL Pump ON",pumpOn,0,0)
app.addButton("LL Standby ON",pumpStOn,1,0)
app.addButton("LL Standby OFF",pumpStOff,2,0)
app.addButton("LL Pump OFF", pumpOff,3,0)
app.addButton("Cryopump ON", cPumpOn,4,0)
app.addButton("Cryopump Off", cPumpOff,5,0)
app.stopLabelFrame()

app.stopTab()

app.startTab("Turbo Pump Sensors")

app.startLabelFrame("Temperatures")
app.addLabel("Tpwrstg", "Power Stage Temperature: ")
app.addLabel("Telec", "Electronics Temperature: ")
app.addLabel("Tpbot", "Pump Bottom Temperature: ")
app.addLabel("Tbearing", "Bearing Temperature: ")
app.addLabel("Tmotor", "Motor Temperature: ")
app.stopLabelFrame()

app.stopTab()

app.startTab("Cryopump Sensors")

app.addLabel("Cstatus","Cryopump Status: ")
app.addLabel("Cfstg", "First Stage Temperature: ")
app.addLabel("Csstg", "Second Stage Temperature: ")

app.stopTab()

app.stopTabbedFrame()

app.thread(serialTPump)
app.thread(serialCPump)
app.thread(ADCupdate)
app.registerEvent(timeUpdate)
app.go()
