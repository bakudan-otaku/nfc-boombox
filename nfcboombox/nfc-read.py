#!/bin/python3

## Simple read data from Card, stop at hitting a "null"
import signal
import sys

from .pi-rc522.pirc522 import RFID, NdefMessage

run = True
rdr = RFID()
util = rdr.util()
util.debug = False
readout = []
encryption_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

def end_read(signal,frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    sys.exit()

signal.signal(signal.SIGINT, end_read)

rdr.wait_for_tag()

(error, data) = rdr.request()
if not error:
    print("\nDetected: ")

(error, uid) = rdr.anticoll()
if not error:
    print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

    util.set_tag(uid)
    util.auth(rdr.auth_b, encryption_key)
    messages = util.dump_data().get_messages()
    for message in messages:
        for record in NdefMessage(message).records:
            if record.payload.rtd_type == "Text":
                print(record.payload.get_contend())
rdr.cleanup()

print("\ndata: " + str(readout))
