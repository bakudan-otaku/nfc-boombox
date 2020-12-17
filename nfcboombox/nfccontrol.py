"""
Everything to controll the mpd via NFC.
Every NFC Tag that has a Text-Record that starts with "mpc:" will handled
"""
from .pirc522 import RFIDLocked, NdefMessage, MIFARE1k
import threading
import time
from datetime import datetime
import RPi.GPIO as GPIO

class MPDRecord:
    valid_commands = [ "play", "clear", "stop", "add" ]
    add_commands = [ "play", "add"]
    def __init__(self, record_raw):
        self.raw = record_raw
        self.command = ""
        self.arg = ""

    def validate(self):
        raw = self.raw.split(':')
        if not raw[0] == "mpc":
            return False

        if not raw[1] in self.valid_commands:
            return False

        self.command = raw[1]

        if len(raw) > 2 and self.command in self.add_commands:
            for i in range(2, len(raw)):
                self.arg += raw[i]
                if not (i + 1) == len(raw):
                    self.arg += ":"

        return True
    
class NfcControl(threading.Thread):
    def __init__(self, client):
        super(NfcControl, self).__init__()
        self.client = client

        self.rdr = RFIDLocked()
        self.util = self.rdr.util()

    def stop(self):
        # running should be locked
        self.rdr.stop()

        GPIO.cleanup()

    def run(self):
        running = True
        # Use this ^ for threadsave stop
        card_ts = None
        last_card = None
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
                self.util.deauth()
                continue

            # We must stop crypto
            self.util.deauth()
            
            card = MIFARE1k(uid, data)
            if card == None:
                continue
            
            with self.client:
                status = self.client.status()
            # reset if not playing, so you can restart a Card if you stop first.
            
            if card == last_card:
                if (datetime.now() - card_ts).seconds < 10:
                    # ignore and set ts:
                    card_ts = datetime.now()
                    continue
            # save Timestamp and card:
            last_card = card
            card_ts = datetime.now()
            
            messages = card.get_messages()
            commands = []
            i = 0
            for m in messages:
                ndefm = NdefMessage(m)
                for r in ndefm.records:
                                
                    # Check if text
                    # My Format for Text Record: mpc:clear|play|stop|add:arg
                    # Todo: volume
                    # MusicPath optional with play, "must" with add
                    # split by :
                    # Check for [0] = mpc
                    # Check for [1] in commands
                    if r.payload.rtd_type == "Text":
                        print(str(i) + ":" + r.payload.get_contend())
                        i += 1
                        commands.append(MPDRecord(r.payload.get_contend()))

            add = []
            clear = False
            stop = False
            play = False
            for command in commands:
                if command.validate():
                    clear = clear or command.command == "clear"
                    stop = stop or command.command == "stop"
                    play = play or command.command == "play"
                    if not command.arg == "":
                        clear = clear or command.command == "play"
                        add.append(command.arg)

            # Todo: catch Exceptions
            with self.client:
                if stop:
                    self.client.stop()
                if clear:
                    self.client.clear()
                for a in add:
                    print("add: '" + a + "'")
                    self.client.add(a)
                if play:
                    self.client.play(0)
            # Cool down after everthing
            time.sleep(1)

        self.rdr.cleanup()

