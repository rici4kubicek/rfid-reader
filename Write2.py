#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#
import MFRC522
import signal

continue_reading = True

# Keys
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
KEY2 = [0xFF, 0xFF, 0xFF, 0xFF]

# Selecting key
KEY = DEFAULT_KEY

def format_uid(uid):
    s = ""
    for i in range(0, len(uid)):
        s += "%x" % uid[i]
    return s.upper()

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522(0, 0)

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
(status, TagSize) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
while True:
    if TagSize > 0:
        message = "Sector [1 - %s]: " % (TagSize - 1)
    else:
        message = "Sector: "

    try:
        Sector = input(message)
    except:
        print("")
        break

    else:
        if TagSize > 0:
            if Sector >= 32:
                MaxChars = 16 * 15
            else:
                MaxChars = 16 * 3
            message = "Data [max %s chars]: " % MaxChars
        else:
            message = "Data: "
        try:
            text="abcdefg"
        except:
            print("\n")
            continue
        else:
            print("Waiting for Tag...\n")

    while True:
        (status, TagSize) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        if status != MIFAREReader.MI_OK:
            continue

        if Sector < 1 or Sector > (TagSize - 1):
            print("Sector out of range (1 - %s)\n" % (TagSize - 1))
            break

        # Selecting blocks
        BaseBlockLength = 4
        if Sector < 32:
            BlockLength = BaseBlockLength
            StartAddr = Sector * BlockLength
        else:
            BlockLength = 16
            StartAddr = 32 * BaseBlockLength + (Sector - 32) * BlockLength

        BlockAddrs = []
        for i in range(0, (BlockLength - 1)):
            BlockAddrs.append((StartAddr + i))
        TrailerBlockAddr = (StartAddr + (BlockLength - 1))

        # Initializing tag
        (Status, UID) = MIFAREReader.MFRC522_Anticoll(1)

        if UID[0] == 0x88:
            UID[0] = UID[1]
            UID[1] = UID[2]
            UID[2] = UID[3]

            SAK1 = MIFAREReader.MFRC522_SAK(UID)

            (Status, UID2) = MIFAREReader.MFRC522_Anticoll(2)
            UID[3] = UID2[0]
            UID[4] = UID2[1]
            UID.append(UID2[2])
            UID.append(UID2[3])

            print("Tag UID {} {} {} {} {} {} {}".format(hex(UID[0]),hex(UID[1]),hex(UID[2]),hex(UID[3]),hex(UID[4]),hex(UID[5]),hex(UID[6])))

        if Status != MIFAREReader.MI_OK:
            break

        data = []
        i = 0
        while i < 4:
            i = i+1
            data.append(0)

        data[0] = 21
        data[1] = 22
        data[2] = 31
        data[3] = 32

        SAK2 = MIFAREReader.MFRC522_SelectTag2(UID)

        MIFAREReader.MFRC522_Write(4, data)

        MIFAREReader.MFRC522_Read(4)

        break

MIFAREReader.AntennaOff()