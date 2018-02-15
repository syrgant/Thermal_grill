import serial
import time
import datetime
import serial.tools.list_ports
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
#import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')
from matplotlib.widgets import Slider
import tkinter as tk
import _thread

# import random to use testFunc()
import random

DEBUG_MODE = False


class TGinterface:
    def __init__(self):
        self._root = tk.Tk()
        self._root.geometry("{0}x{1}".format(self._root.winfo_screenwidth(), self._root.winfo_screenheight()))

        self.aLog = []
        self.bLog = []
        self.tLog = []
        self.scaleLog = []
        self.run_animation = False
        self.des_temp_a = "na"
        self.des_temp_b = "na"
        self.counter = 0
        self.diff_temp_a = 0
        self.diff_temp_b = 0
        self.calibrated = False
        self.changing_temp = False

        self.top_var = tk.StringVar()
        self.top_label = tk.Label(self._root, textvariable=self.top_var)
        self.top_var.set("Press button to start")
        self.top_label.pack(side="top")

        self.temp_a = tk.StringVar()
        self.temp_b = tk.StringVar()
        self.temp_a.set("Desired: na / Current Temp: na")
        self.temp_b.set("Desired: na / Current Temp: na")

        F1 = tk.Frame(self._root)
        F2 = tk.Frame(self._root)
        F3 = tk.Frame(self._root)
        F4 = tk.Frame(self._root)
        F1.pack(fill="x", expand=True)
        F2.pack(fill="x", expand=True)
        F3.pack(fill="x", expand=True)
        F4.pack(fill="x", expand=True)
        F1.place(relx=0.25, rely=0.4, anchor="center")
        F2.place(relx=0.75, rely=0.4, anchor="center")
        F3.place(relx=0.25, rely=0.3, anchor="center")
        F4.place(relx=0.75, rely=0.3, anchor="center")

        self.L1 = tk.Label(F1, text="Temperature A ")
        self.E1 = tk.Entry(F1, width=3)
        self.L1.pack(side="left")
        self.E1.pack(side="left")
        self.Display1 = tk.Label(F3, textvariable=self.temp_a)
        self.Display1.pack(side="top")

        self.L2 = tk.Label(F2, text="Temperature B ")
        self.E2 = tk.Entry(F2, width=3)
        self.L2.pack(side="left")
        self.E2.pack(side="left")
        self.Display2 = tk.Label(F4, textvariable=self.temp_b)
        self.Display2.pack(side="top")

        self.button = tk.Button(self._root, text="Start", command=self.connect)
        self.button1 = tk.Button(self._root, text="Calibrate", command=self.calibrate)
        self.slider = tk.Scale(self._root, from_=0, to=10, length=200, tickinterval=1, orient="horizontal")
        self.button3 = tk.Button(self._root, text="Save Data", command=self.saveResults)
        self.button2 = tk.Button(self._root, text="QUIT", command=self.endProgram)
        self._root.bind_all('<Key>', self.key)
        self.button.pack(side="top", pady=5, ipady=2, ipadx=5)
        #self.button1.pack(side="top", pady=5, ipady=2, ipadx=5)
        self.slider.pack(side="top", pady=5, ipady=2, ipadx=5)
        self.button2.pack(side="bottom", pady=5, ipady=2, ipadx=5)
        self.button3.pack(side="bottom", ipady=2, ipadx=5)

        self.ser = serial.Serial()
        self.ser.port = ""
        self.ser.baudrate = 9600
        self.ser.timeout = 1
        self.ser.xonxoff = False     #disable software flow control
        self.ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2

        self._fig = Figure(figsize=(5,3), dpi=100)
        self.a = self._fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self._fig, self._root)
        self.canvas.show()
        self.canvas._tkcanvas.pack(side="bottom", fill=tk.X, expand=False)

    def testFunc(self):
        # DONT use without importing random
        self.run_animation = True
        _thread.start_new_thread(self.testData, ())

    def testData(self):
        t = 0
        while t < 20:
            #x = self.ser.readline().decode('UTF-8')
            a = str(random.randint(10, 30))
            b = str(random.randint(10, 30))
            self.aLog.append(float(a))
            self.bLog.append(float(b))
            self.tLog.append(float(t))
            self.scaleLog.append(str(self.slider.get()))
            self.temp_a.set("Desired: " + self.des_temp_a + " / Current Temp: " + a)
            self.temp_b.set("Desired: " + self.des_temp_b + " / Current Temp: " + b)
            self.plotPoints()
            t += 0.5
            time.sleep(0.5)

    def submit(self):
    	self.send_output()

    def key(self, event):
        if event.keysym == 'Return':
        	if self.ser.isOpen():
        		self.send_output()
        	else:
        		print("Start Serial Connection")

        if event.keysym == 'Escape':
            self.quit()

    def connect(self):
        for pinfo in serial.tools.list_ports.comports():
            if pinfo.serial_number == '756333132333516171D1':
                self.ser = serial.Serial(pinfo.device)
                if self.ser.isOpen():
                    self.run_animation = True
                    #self.top_var.set("Running")
                    _thread.start_new_thread(self.getSerial, ())

        if self.ser.port == "":
        	self.top_var.set("No serial connections detected")
        else:
            self.run_animation = True
            self.top_var.set("Running")
            _thread.start_new_thread(self.getSerial, ())
        self.top_var.set("Calibrating")
        time.sleep(3)
        self.calibrate()
        self.top_var.set("Running")

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
        a = self.E1.get()
        b = self.E2.get()
        try:
            a = int(a)
            self.des_temp_a = str(a)
            a = self.four_dig(a)

            b = int(b)
            self.des_temp_b = str(b)
            b = self.four_dig(b)

            out = a + b
            out = out.encode('utf-8')
            if DEBUG_MODE:
                print("Sending output: ", out)
            #record "live" temp for the time it is changing

            def changing():
                self.changing_temp = True
                time.sleep(4)
                self.changing_temp = False
            _thread.start_new_thread(changing, ())
            self.ser.write(out)
        except ValueError:
            print("Bad input")

    def getSerial(self):
        t = 0
        while self.ser.port != "":
            try:
                read_val = self.ser.readline().decode()
            except:
                print("Was not able to read from Arduino, make sure it is connected and restart the program.")
                break
            if DEBUG_MODE:
                print("Recieved: {} at {}".format(read_val, time.strftime('%a %H:%M:%S')))
            if (self.calibrated and not self.changing_temp):
                a = self.des_temp_a
                b = self.des_temp_b
            else:
                a = str(read_val[2:4:])
                b = str(read_val[10:12:])
            self.aLog.append(float(a)+float(self.diff_temp_a))
            self.bLog.append(float(b)+float(self.diff_temp_b))
            self.tLog.append(float(t))
            self.scaleLog.append(str(self.slider.get()))
            self.temp_a.set("Desired: " + self.des_temp_a + " / Current Temp: " + a)
            self.temp_b.set("Desired: " + self.des_temp_b + " / Current Temp: " + b)
            self.plotPoints()
            t += 0.5
            time.sleep(0.5)

    def calibrate(self):
        #set both temp to 20, wait, set to 22
        self.calibrated = True
        def change_temp(temp):
            self.E1.delete(0, 'end')
            self.E1.insert(0, str(temp))
            self.E2.delete(0, 'end')
            self.E2.insert(0, str(temp))
            self.send_output()
            return

        def delay_change():
            #create a for loop instead of this
            change_temp(20)
            time.sleep(3)
            print("changing temp and slider read is " + str(self.slider.get()))
            change_temp(22)
            time.sleep(7)
            self.diff_temp_a = float(22) - float(self.aLog[-1])
            self.diff_temp_b = float(22) - float(self.bLog[-1])
            return
        _thread.start_new_thread(delay_change, ())
        return

        #afterwards set the current temp to the desired temp so that the graph is accurate


    def plotPoints(self):
        #global counter
        if self.run_animation:
            xList = []
            yList = []
            xListb = []
            yListb = []

            if self.counter < 25:
                for a in self.aLog:
                    yList.append(a)
                for b in self.bLog:
                    yListb.append(b)
                for t in self.tLog:
                    xList.append(t)
                    xListb.append(t)

            elif self.counter >= 25:
                for i in range(self.counter - 25, self.counter):
                    y1 = self.aLog[i]
                    y2 = self.bLog[i]
                    yList.append(y1)
                    yListb.append(y2)
                    x = self.tLog[i]
                    xList.append(x)
                    xListb.append(x)

            self.a.clear()
            self.a.plot(xList, yList)
            self.a.plot(xListb, yListb)
            self.counter += 1
            self._fig.canvas.draw()

    def saveResults(self):
        #write file as comma separated strings
        file = open("resultsData.txt","w")
        file.write("Time, A, B, Pain Rating" + '\n')
        if self.counter > 0:
            for i in range(0, self.counter):
                file.write(str(self.tLog[i]) + ", " + str(self.aLog[i]) + ", " + str(self.bLog[i]) + ", " + str(self.scaleLog[i]) + '\n')
                #Add slider.get() output into saveResults() then reset

    def run(self):
        self._root.mainloop()

    def endProgram(self):
        self.run_animation = False
        if self.ser.isOpen():
            self.ser.close()
        self.ser.port = ""
        self._root.destroy()

if __name__ == "__main__":
    app = TGinterface()
    app.run()
    #app.geometry("{0}x{1}+0+0".format(app.winfo_screenwidth(), app.winfo_screenheight()))
    #ani = animation.FuncAnimation(f, TGinterface.animate, interval=500)
    #app.run()
