#!/usr/bin/python3
import odroid_wiringpi as wpi
import sys
import threading
import subprocess
import time
conf={
    'pin': 0,
    'program': '/home/adrianp/bin/scan-to-dir.sh'
}

DEBOUNCE_TIME = 0.3 #in seconds
SAMPLE_FREQUENCY = 10 #in hertz
MAXIMUM = (DEBOUNCE_TIME * SAMPLE_FREQUENCY)

input = 0
integrator = 0
output = 0

def readValue():
    return wpi.digitalRead(conf["pin"])

def debounce():
    #integrator debounce inspired by Kenneth A. Kuhn -- https://hackaday.com/2010/11/09/debounce-code-one-post-to-rule-them-all/

    global integrator, output
    # Step 1: Update the integrator based on the input signal.  Note that the
    # integrator follows the input, decreasing or increasing towards the limits as
    # determined by the input state (0 or 1).

    if input == 0:
        if integrator > 0:
            integrator -= 1
    elif integrator < MAXIMUM:
        integrator += 1
    
    # Step 2: Update the output state based on the integrator.  Note that the
    # output will only change states if the integrator has reached a limit, either
    # 0 or MAXIMUM.

    if integrator == 0:
        output = 0
    elif integrator >= MAXIMUM:
        output = 1
        integrator = MAXIMUM

def thread_process(name):
    print("Thread: starting", name)
    sys.stdout.flush()

    process = subprocess.run([name], encoding="ascii", capture_output=True)
    print(process.stdout)
    sys.stdout.flush()

    print("Thread: stopping", name)
    sys.stdout.flush()
 
wpi.wiringPiSetup()

wpi.pinMode(conf["pin"], 0)
print("Set pin "+str(conf["pin"])+" as input")
sys.stdout.flush()

currentThread = None
lastinput = input
again = False
while True:
    input = readValue()
    debounce()
    #print("DBG: input:{}, output={}, again={}".format(input, output, again))
    #join the old thread
    if currentThread:
        if not currentThread.is_alive():
            print("Joining old thread")
            sys.stdout.flush()
            currentThread.join()
            currentThread = None
        
    if currentThread == None and again == True:
        # even if the button is not currently pressed, run the operation
        print("Starting new thread (again)")
        sys.stdout.flush()
        currentThread = threading.Thread(target=thread_process, args=(conf['program'],))
        currentThread.start()
        again = False
    if output == 0 and output != lastinput:
        print("Button has been pressed")
        sys.stdout.flush()
        if currentThread:
            if currentThread.is_alive():
                #thread is still running, but the user wants to run the program once it finished again.
                print("Program still running, but will run it again once finished!")
                sys.stdout.flush()
                again = True
        #run the process in a new thread if none is running
        if currentThread == None:
            print("Starting new thread")
            sys.stdout.flush()
            currentThread = threading.Thread(target=thread_process, args=(conf['program'],))
            currentThread.start()
            again = False

    lastinput = output
    time.sleep(float(1/SAMPLE_FREQUENCY))

