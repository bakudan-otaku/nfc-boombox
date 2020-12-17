
"""
Should be a Thread that handles everything there is about the NFC Control,
So if a NFC Card with a Text Tag comes along it will do everything nessesary.
"""
from gpiozero import Button
from mpd import MPDClient
from nfcboombox import LockableMPDClient
from nfcboombox import NfcControl

import time
import threading
import sys, os

def_playButton = 15 # Pin 10
def_stopButton = 26 # Pin 37
def_nextButton = 27 # Pin 13
def_previousButton = 16 # Pin 36
def_vollUpButton = 17 # Pin 11
def_vollDownButton = 23 # Pin 16
def_powerLED = 12 # Pin 32
def_pull_up_down = None
def_active = False
def_btime=0.001
def_htime=0.2

"""
Checks and prints the status of mpd periodicaly
"""
class CheckStatus(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.daemon = True

    def run(self):
        while True:
            status = None
            with self.client:
                status = self.client.status()
            print("Status Thread: " + str(status) + "\n")
            time.sleep(1)

    def __str__(self):
        return self.__class__.__name__

"""
A Button witch adds the client object.
"""
class myButton(Button):
    def __init__(
            self, gpioC=None, pin=None, pull_up=def_pull_up_down, active_state=def_active, bounce_time=def_btime,
            hold_time=def_htime, hold_repeat=False, pin_factory=None):
        super(myButton, self).__init__(
            pin, pull_up=pull_up, active_state=active_state, bounce_time=bounce_time,
            hold_time=hold_time, hold_repeat=hold_repeat, pin_factory=pin_factory)
        self.gpioC=gpioC

"""
overlooks all GPIOs.
"""
class GPIOControl(threading.Thread):
    def __init__(self, client, playGPIO, stopGPIO, nextGPIO, previousGPIO, vollUpGPIO, vollDownGPIO, powerLED = None, vollMax=100.0 ):
        threading.Thread.__init__(self)
        self.client = client
        self.shutdown = threading.Event()
        self.shutdown.clear()

        self.playButton = myButton(gpioC=self, pin=playGPIO)
        self.stopButton = myButton(gpioC=self, pin=stopGPIO)
        self.nextButton = myButton(gpioC=self, pin=nextGPIO)
        self.previousButton = myButton(gpioC=self, pin=previousGPIO)
        self.vollUpButton = myButton(gpioC=self, pin=vollUpGPIO, hold_repeat=True)
        self.vollDownButton = myButton(gpioC=self, pin=vollDownGPIO, hold_repeat=True)
        self.powerLED = powerLED
        self.vollMax = vollMax

        if self.powerLED != None:
            pass

    def run(self):
        self.playButton.when_pressed = GPIOControl.playB
        self.stopButton.when_pressed = GPIOControl.stopB
        self.nextButton.when_pressed = GPIOControl.nextB
        self.previousButton.when_pressed = GPIOControl.previousB
        self.vollUpButton.when_held = GPIOControl.vollUpB
        self.vollDownButton.when_held = GPIOControl.vollDownB

        while not self.shutdown.is_set():
            # vollume -> LED handling
            self.shutdown.wait(timeout=0.2)

    def stop(self):
        self.shutdown.set()

    def playB(self):
        print("play")
        with self.gpioC.client:
            status = self.gpioC.client.status()
            if status['state'] == 'play':
                self.gpioC.client.pause()
            if status['state'] == 'pause' or status['state'] == 'stop':
                self.gpioC.client.play()

    def stopB(self):
        print("stop")
        with self.gpioC.client:
            self.gpioC.client.stop()

    def nextB(self):
        print("next")
        with self.gpioC.client:
            status = self.gpioC.client.status()
            if not status['state'] == 'stop':
                self.gpioC.client.next()

    def previousB(self):
        print("previous")
        with self.gpioC.client:
            status = self.gpioC.client.status()
            if not status['state'] == 'stop':
                self.gpioC.client.previous()

    def vollUpB(self):
        print("vollUp")
        with self.gpioC.client:
            vol = int(self.gpioC.client.status()['volume'])
            if not vol == self.gpioC.vollMax:
                self.gpioC.client.setvol(vol + 1)

    def vollDownB(self):
        print("vollDown")
        with self.gpioC.client:
            vol = int(self.gpioC.client.status()['volume'])
            if not vol == 0:
                self.gpioC.client.setvol(vol - 1)

class BoomBox(object):
    
    def __init__(self):
        self.client = LockableMPDClient()
        self.client.connect("localhost", 6600)
        self.modules = []
        
        module = CheckStatus(self.client)
        self.modules.append(module)

        module = NfcControl(self.client)
        self.modules.append(module)

        module = GPIOControl(self.client, def_playButton, def_stopButton, def_nextButton, def_previousButton, def_vollUpButton, def_vollDownButton, vollMax = 35.0)
        self.modules.append(module)

    def main(self):
        print(self.__class__.__name__)
        status = None
        with self.client:
            status = self.client.status()
        print("Main Status Test 2: " + str(status) + "\n")
        print("start Modules")
        for m in self.modules:
            m.start()

        while True:
            time.sleep(10)
            for m in self.modules:
                if not m.isAlive():
                    print("ERROR Thread " + str(m) + " died")

    def shutdown(self):
        for m in self.modules:
            if hasattr(m, 'stop') and callable( m.stop ):
                m.stop()
                m.join()

if __name__ == "__main__":
    main = BoomBox()
    try:
        main.main()
    except KeyboardInterrupt:
        try:
            main.shutdown()
            sys.exit(0)
        except SystemExit:
            main.shutdown()
            os._exit(0)
    
