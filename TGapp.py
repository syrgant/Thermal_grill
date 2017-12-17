import serial
import time
import serial.tools.list_ports
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')
from matplotlib.widgets import Slider

import tkinter as tk
from tkinter import *

#import random  # for testing
import _thread

#ser = serial.Serial('/dev/cu.usbmodem1421', 9600, timeout=1)

ser = serial.Serial()
ser.port = ""

ser.baudrate = 9600
ser.timeout = 1
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2
#ser.bytesize = serial.EIGHTBITS #number of bits per bytes
#ser.parity = serial.PARITY_NONE #set parity check: no parity
#ser.stopbits = serial.STOPBITS_ONE  #number of stop bits

f = Figure(figsize=(5,3), dpi=100)
a = f.add_subplot(111)

aLog = []
#aLog.append([])
#aLog.append([])
bLog = []
#bLog.append([])
#bLog.append([])
tLog = []

run = False
des_temp_a = "na"
des_temp_b = "na"

counter = 0

def animate(i):
    global counter
    if run:
        xList = []
        yList = []
        xListb = []
        yListb = []
        if counter < 25:
            for item in aLog:
                y = item
                yList.append(y)

            for item in bLog:
                y = item
                yListb.append(y)

            for item in tLog:
                x = item
                xList.append(x)
                xListb.append(x)
        elif counter >= 25:
            for i in range(counter - 25, counter):
                y1 = aLog[i]
                y2 = bLog[i]
                yList.append(y1)
                yListb.append(y2)
                x = tLog[i]
                xList.append(x)
                xListb.append(x)
        a.clear()
        a.plot(xList, yList)
        a.plot(xListb, yListb)
        counter += 1

def testData():
    t = 0
    while t <= 60:
        a = t * 0.2
        b = t * 0.1 + 5
        #a = random.randint(0, 10)
        #b = random.randint(0, 10)
        aLog.append(a)
        bLog.append(b)
        tLog.append(t)
        t += 0.5
        time.sleep(0.5)

def getSerial():
    global aLog
    global bLog
    global tLog
    global ser
    global var
    global des_temp_a
    global des_temp_b

    t = 0
    while run and not ser.port == "":
        x = ser.readline().decode('UTF-8')
        a = x[2:4]
        b = x[10:12]
        aLog.append(float(a))
        bLog.append(float(b))
        tLog.append(float(t))
        temp_a.set("Desired: " + des_temp_a + " / Current Temp: " + a)
        temp_b.set("Desired: " + des_temp_b + " / Current Temp: " + b)
        app.update()
        t += 0.5
        time.sleep(0.5)

def saveResults():
    file = open("resultsData.txt","w")
    file.write("Time, A, B" + '\n')
    if counter > 0:
        for i in range(0, counter):
            file.write(str(tLog[i]) + ", " + str(aLog[i]) + ", " + str(bLog[i]) + '\n')

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        global var
        global temp_a
        global temp_b

        var = StringVar()
        self.label = Label(self, textvariable=var)
        var.set("Press button to start")
        temp_a = StringVar()
        temp_b = StringVar()
        temp_a.set("Desired: na / Current Temp: na")
        temp_b.set("Desired: na / Current Temp: na")
        self.F1 = Frame(self)
        self.F2 = Frame(self)
        self.F3 = Frame(self)
        self.F4 = Frame(self)
        self.F1.pack(fill="x", expand=True)
        self.F2.pack(fill="x", expand=True)
        self.F1.place(relx=0.25, rely=0.4, anchor="center")
        self.F2.place(relx=0.75, rely=0.4, anchor="center")
        self.F3.place(relx=0.25, rely=0.3, anchor="center")
        self.F4.place(relx=0.75, rely=0.3, anchor="center")
        self.L1 = Label(self.F1, text="Temperature A ")
        self.E1 = Entry(self.F1, width=3)
        self.L1.pack(side="left")
        self.E1.pack(side="left")
        self.Display1 = Label(self.F3, textvariable=temp_a)
        self.Display1.pack(side="top")
        self.L2 = Label(self.F2, text="Temperature B ")
        self.E2 = Entry(self.F2, width=3)
        self.L2.pack(side="left")
        self.E2.pack(side="left")
        self.Display2 = Label(self.F4, textvariable=temp_b)
        self.Display2.pack(side="top")
        self.button = tk.Button(self, text="Start", command=self.connect)
        self.button3 = tk.Button(self, text="Save Data", command=saveResults)
        self.button2 = tk.Button(self, text="QUIT", command=self.end_program)
        self.bind_all('<Key>', self.key)
        self.button.pack(side="top", pady=5, ipady=2, ipadx=5)
        self.label.pack(side="top")
        self.button2.pack(side="bottom", pady=5, ipady=2, ipadx=5)
        self.button3.pack(side="bottom", ipady=2, ipadx=5)


        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()

        #toolbar = NavigationToolbar2TkAgg(canvas, self)
        #toolbar.update()
        #slider = Slider(canvas, 'Frame', 0, 10, valinit=0,valfmt='%d')

        canvas._tkcanvas.pack(side="bottom", fill=tk.X, expand=False)
        #slider.pack(side="bottom", fill=tk.X, expand=False)
        #canvas.get_tk_widget().pack(side="bottom", fill=tk.X, expand=False)

    def testFunc(self):
        global run
        _thread.start_new_thread(testData, ())
        run = True


    def submit(self):
    	self.send_output()

    def key(self, event):
        global ser
        if event.keysym == 'Return':
        	if ser.isOpen():
        		self.send_output()
        	else:
        		print("Start Serial Connection")

        if event.keysym == 'Escape':
            self.quit()

    def connect(self):
        global ser
        global run
        global des_temp_a
        global des_temp_b

        ports = list(serial.tools.list_ports.comports())
        for p in ports:
        	if "Arduino" in p[1]:
        		ser.port = p[0]
        		ser.open()
        		break

        if ser.port == "":
        	var.set("No serial connections detected")
        else:
            run = True
            var.set("Running")
            time.sleep(1)
            _thread.start_new_thread(getSerial, ())

    def four_dig(self, input):
        # convert temp into Arduino  command.
        # Arduino ranges from 0V - 0 to 5V - 4094. Every volt is 10 degrees
        if input > 49:
        	input = 49
        input1 = input * 82
        input1 = str(input1)
        if (len(input1)==1):
            return "000" + input1
        elif (len(input1)==2):
            return "00" + input1
        elif (len(input1)==3):
            return "0" + input1
        elif (len(input1)==4):
            return input1
        else:
            return -1

    def send_output(self):
        global des_temp_a
        global des_temp_b
        a = self.E1.get()
        b = self.E2.get()
        try:
    	    a = int(a)
    	    des_temp_a = str(a)
    	    a = self.four_dig(a)

    	    b = int(b)
    	    des_temp_b = str(b)
    	    b = self.four_dig(b)

    	    out = a + b
    	    out = out.encode('utf-8')
    	    ser.write(out)

        except ValueError:
            print("Bad input")


    def end_program(self):
        global run
        global ser

        run = False
        if ser.isOpen():
            ser.close()
        self.quit()


app = Application()
app.geometry("{0}x{1}+0+0".format(app.winfo_screenwidth(), app.winfo_screenheight()))
ani = animation.FuncAnimation(f, animate, interval=500)
app.mainloop()

#if __name__ == "__main__":
#root = tk.Tk()
#root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
#view = Application(root)
#view.pack(side="top", fill="both", expand=True)
#root.mainloop()
