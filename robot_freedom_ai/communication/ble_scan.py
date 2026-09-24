# Source - https://stackoverflow.com/a/78371732
# Posted by petzval
# Retrieved 2026-04-03, License - CC BY-SA 4.0

#Separate devices.txt file defines characteristics
#
#DEVICE = My Pi         TYPE=MESH    NODE=1  ADDRESS = B8:27:EB:F1:50:C3
#  PRIMARY_SERVICE = 1800
#    LECHAR = Device name  PERMIT=06  SIZE=06  UUID=2A00   ; index 0
#  PRIMARY_SERVICE = 112233445566778899AABBCCDDEEFF00
#    LECHAR = My data  PERMIT=16  SIZE=16 UUID=ABCD        ; index 1 notify 
#https://stackoverflow.com/questions/78368208/python-raspberry-pi-as-ble-sender-for-sensor-data
#https://github.com/petzval/btferret
#pip install bleak  
#https://pypi.org/project/bleak/ 
import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

asyncio.run(main())

 

