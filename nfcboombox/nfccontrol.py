"""
Everything to controll the mpd via NFC.
Every NFC Tag that has a Text-Record that starts with "mpc:" will handled
"""
from .pirc522 import RFIDLocked, NdefMessage, MIFARE1k
import threading
import time
from datetime import datetime


class MPDReccord:
    def __init__(self, record_raw):
        pass
    
class NfcControl(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.last_card = None
        self.last_card_ts = None

        self.rdr = RFIDLocked()
        self.util = self.rdr.util()

    def stop(self):
        # running should be locked
        self.rdr.stop()

    def run(self):
        running = True
        # Use this ^ for threadsave stop
        while running:
            running = self.rdr.wait_for_tag()
            # check if thread stop did kill the wait
            if not running:
                shutdown = False
                with self.rdr.shutdown_lock:
                    shutdown = self.rdr.shutdown
                if shutdown:
                    break
                else:
                    running = True
            (error, data) = self.rdr.request()
            if error:
                continue
            (error, uid) = self.rdr.anticoll()
            if error:
                continue
            # Set tag as used in util. This will call RFID.select_tag(uid)
            self.util.set_tag(uid)
            # Save authorization info (key B) to util. It doesn't call RFID.card_auth(), that's called when needed
            self.util.auth(self.rdr.auth_b, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            
            (error, data) = self.util.dump_data()
            if error:
                continue
            card = MIFARE1k(uid, data)
            if card == None:
                continue
            
            with self.client:
                status = self.client.status()
            # reset if not playing, so you can restart a Card if you stop first.

            # da muss ich mir noch was überlegen
            if card == self.last_card:
                (datetime.now() - ts).seconds > 10
            
            if not card == self.last_card:
                self.last_card = card
                self.last_card_ts = datetime.now()
                messages = card.get_messages()
                j = 0
                for m in messages:
                    print("j: " + str(j))
                    j += 1
                    ndefm = NdefMessage(m)
                    i = 0
                    for r in ndefm.records:
                                
                        # Check if text
                        # split by :
                        # Check for [0] = mpc
                        # Check for [1] in commands
                        print(str(i) + ":" + r.payload.get_contend())
                        i += 1
                time.sleep(1)


            # We must stop crypto
            self.util.deauth()

        self.rdr.cleanup()



            
        
    
