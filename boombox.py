
"""
Should be a Thread that handles everything there is about the NFC Control,
So if a NFC Card with a Text Tag comes along it will do everything nessesary.
"""
from mpd import MPDClient
from nfcboombox import LockableMPDClient
from nfcboombox import NfcControl

import time
import threading
import sys, os


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


class BoomBox:
    modules = []
    client = None
    
    def __init__(self):
        self.client = LockableMPDClient()
        self.client.connect("localhost", 6600)

        module = CheckStatus(self.client)
        self.modules.append(module)

        module = NfcControl(self.client)
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
    
