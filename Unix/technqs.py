import math

def checksum(pin):
	pin %= 10000000
	a = 0
	t = pin
	while t:
		a += 3 * (t % 10)
		t = math.floor(t / 10)
		a += t % 10
		t = math.floor(t / 10)
	return (pin * 10) + ((10 - (a % 10)) % 10)

def fill(number, width):
	return str(number).zfill(width)

def reverse(_string):
	return _string[::-1]

def pin24(mac):
	wpspin = fill(int(checksum(int(mac, 16) & 0xFFFFFF)), 8)
	return wpspin

def pin28(mac):
	wpspin = fill(int(checksum(int(mac, 16) & 0xFFFFFFF)), 8)
	return wpspin

def pin32(mac):
	wpspin = fill(int(checksum(int(mac, 16) % 0x100000000)), 8)
	return wpspin

def pin36(mac):
	wpspin = fill(int(checksum(int(mac, 16) % 0x1000000000)), 8)
	return wpspin

def pin40(mac):
	wpspin = fill(int(checksum(int(mac, 16) % 0x10000000000)), 8)
	return wpspin

def pin44(mac):
	wpspin = fill(int(checksum(int(mac, 16) % 0x100000000000)), 8)
	return wpspin

def pin48(mac):
	wpspin = fill(int(checksum(int(mac, 16))), 8)
	return wpspin

def pin24rh(mac):
	wpspin = fill(format(int(mac, 16) & 0xFFFFFF, '02x'), 6)
	wpspin = fill(int(checksum(int(wpspin[4:6] + wpspin[2:4] + wpspin[0:2], 16))), 8)
	return wpspin

def pin32rh(mac):
	wpspin = fill(format(int(mac, 16) % 0x100000000, '02x'), 8)
	wpspin = fill(int(checksum(int(wpspin[6:8] + wpspin[4:6] + wpspin[2:4] + wpspin[0:2], 16))), 8)
	return wpspin

def pin48rh(mac):
	wpspin = fill(format(int(mac, 16), '02x'), 12)
	wpspin = fill(int(checksum(int(wpspin[10:12] + wpspin[8:10] + wpspin[6:8] + wpspin[4:6] + wpspin[2:4] + wpspin[0:2], 16))), 8)
	return wpspin

def pin24rn(mac):
	wpspin = fill(int(checksum(int(reverse(fill(format(int(mac, 16) & 0xFFFFFF, '02x'), 6)), 16))), 8)
	return wpspin

def pin32rn(mac):
	wpspin = fill(int(checksum(int(reverse(fill(format(int(mac, 16) % 0x100000000, '02x'), 8)), 16))), 8)
	return wpspin

def pin48rn(mac):
	wpspin = fill(int(checksum(int(reverse(fill(format(int(mac, 16), '02x'), 12)), 16))), 8)
	return wpspin

def pin24rb(mac):
	wpspin = fill(int(checksum(int(reverse(fill(str(bin(int(mac, 16) & 0xFFFFFF))[2:], 24)), 2))), 8)
	return wpspin

def pin32rb(mac):
	wpspin = fill(int(checksum(int(reverse(fill(str(bin(int(mac, 16) % 0x100000000))[2:], 32)), 2))), 8)
	return wpspin

def pin48rb(mac):
	wpspin = fill(int(checksum(int(reverse(fill(str(bin(int(mac, 16)))[2:], 48)), 2))), 8)
	return wpspin

def pinDLink(mac):
	wpspin = (int(mac, 16) & 0xFFFFFF) ^ 0x55AA55
	wpspin ^= ((wpspin & 0xF) << 4) | ((wpspin & 0xF) << 8) | ((wpspin & 0xF) << 12) | ((wpspin & 0xF) << 16) | ((wpspin & 0xF) << 20)
	wpspin %= 10000000
	if wpspin < 1000000:
		wpspin += ((wpspin % 9) * 1000000) + 1000000
	wpspin = fill(int(checksum(wpspin)), 8)
	return wpspin

def pinDLinkInc1(mac):
	wpspin = ((int(mac, 16) + 1) & 0xFFFFFF) ^ 0x55AA55
	wpspin ^= ((wpspin & 0xF) << 4) | ((wpspin & 0xF) << 8) | ((wpspin & 0xF) << 12) | ((wpspin & 0xF) << 16) | ((wpspin & 0xF) << 20)
	wpspin %= 10000000
	if wpspin < 1000000:
		wpspin += ((wpspin % 9) * 1000000) + 1000000
	wpspin = fill(int(checksum(wpspin)), 8)
	return wpspin

def pinEasyBox(mac):
	wpspin = int(mac, 16)
	sn = fill(int(wpspin & 0xFFFF), 5)
	k1 = (int(sn[1]) + int(sn[2]) + ((wpspin & 0xFF) >> 4) + (wpspin & 0xF)) & 0xF
	k2 = (int(sn[3]) + int(sn[4]) + ((wpspin & 0xFFFF) >> 12) + ((wpspin & 0xFFF) >> 8)) & 0xF
	hpin = [k1 ^ int(sn[4]), k1 ^ int(sn[3]), k2 ^ ((wpspin & 0xFFF) >> 8), k2 ^ ((wpspin & 0xFF) >> 4),((wpspin & 0xFF) >> 4) ^ int(sn[4]), (wpspin & 0xF) ^ int(sn[3]), k1 ^ int(sn[2])]
	HEX = ""
	for i in hpin:
		HEX += format(i, 'x')
	wpspin = int(HEX, 16)
	wpspin = fill(int(checksum(wpspin)), 8)
	return wpspin

def pinASUS(mac):
	wpspin = fill(format(int(mac, 16), '02x'), 12)
	b = [int(wpspin[0:2], 16), int(wpspin[2:4], 16), int(wpspin[4:6], 16), int(wpspin[6:8], 16),int(wpspin[8:10], 16), int(wpspin[10:12], 16)]
	pin = []
	for i in range(7):
		pin.append((b[i % 6] + b[5]) % (10 - ((i + b[1] + b[2] + b[3] + b[4] + b[5]) % 7)))
	wpspin = fill(int(checksum(int(''.join(str(i) for i in pin), 10))), 8)
	return wpspin

def pinAircon(mac):
	wpspin = fill(format(int(mac, 16), '02x'), 12)
	b = [int(wpspin[0:2], 16), int(wpspin[2:4], 16), int(wpspin[4:6], 16), int(wpspin[6:8], 16),int(wpspin[8:10], 16), int(wpspin[10:12], 16)]
	wpspin = ((b[0] + b[1]) % 10) + (((b[5] + b[0]) % 10) * 10) + (((b[4] + b[5]) % 10) * 100) + (((b[3] + b[4]) % 10) * 1000) + (((b[2] + b[3]) % 10) * 10000) + (((b[1] + b[2]) % 10) * 100000) + (((b[0] + b[1]) % 10) * 1000000)
	wpspin = fill(int(checksum(wpspin)), 8)
	return wpspin

def pinInvNIC(mac):
	wpspin = fill(int(checksum(~(int(mac, 16) & 0xFFFFFF) & 0xFFFFFF)), 8)
	return wpspin

def pinNIC2(mac):
	wpspin = fill(int(checksum((int(mac, 16) & 0xFFFFFF) * 2)), 8)
	return wpspin

def pinNIC3(mac):
	wpspin = fill(int(checksum((int(mac, 16) & 0xFFFFFF) * 3)), 8)
	return wpspin

def pinOUIaddNIC(mac):
	wpspin = fill(format(int(mac, 16), '02x'), 12)
	oui = int(wpspin[0:6], 16)
	nic = int(wpspin[6:12], 16)
	wpspin = (oui + nic) % 0x1000000
	wpspin = fill(int(checksum(wpspin)), 8)
	return wpspin

def pinOUIsubNIC(mac):
	wpspin = fill(format(int(mac, 16), '02x'), 12)
	oui = int(wpspin[0:6], 16)
	nic = int(wpspin[6:12], 16)
	if nic < oui:
		wpspin = oui - nic
	else:
		wpspin = (oui + 0x1000000 - nic) & 0xFFFFFF
	wpspin = fill(int(checksum(wpspin)), 8)
	return wpspin

def pinOUIxorNIC(mac):
	wpspin = fill(format(int(mac, 16), '02x'), 12)
	oui = int(wpspin[0:6], 16)
	nic = int(wpspin[6:12], 16)
	wpspin = oui ^ nic
	wpspin = fill(int(checksum(wpspin)), 8)
	return wpspin

def Dynamic_1(mac):
	wpspin = fill(int(checksum(1234567)), 8)
	return wpspin

def Dynamic_2(mac):
	wpspin = fill(int(checksum(2017252)), 8)
	return wpspin

def Dynamic_3(mac):
	wpspin = fill(int(checksum(4626484)), 8)
	return wpspin

def Dynamic_4(mac):
	wpspin = fill(int(checksum(7622990)), 8)
	return wpspin

def Dynamic_5(mac):
	wpspin = fill(int(checksum(6232714)), 8)
	return wpspin

def Dynamic_6(mac):
	wpspin = fill(int(checksum(6817554)), 8)
	return wpspin

def Dynamic_7(mac):
	wpspin = fill(int(checksum(9566146)), 8)
	return wpspin

def Dynamic_8(mac):
	wpspin = fill(int(checksum(2085483)), 8)
	return wpspin

def Dynamic_9(mac):
	wpspin = fill(int(checksum(4397768)), 8)
	return wpspin

def Dynamic_10(mac):
	wpspin = fill(int(checksum(529417)), 8)
	return wpspin

def Dynamic_11(mac):
	wpspin = fill(int(checksum(9995604)), 8)
	return wpspin

def Dynamic_12(mac):
	wpspin = fill(int(checksum(3561153)), 8)
	return wpspin

def Dynamic_13(mac):
	wpspin = fill(int(checksum(6795814)), 8)
	return wpspin

def Dynamic_14(mac):
	wpspin = fill(int(checksum(3425928)), 8)
	return wpspin

def Static_1(mac):
	wpspin = "12345678"
	return wpspin

def Static_2(mac):
	wpspin = "87654321"
	return wpspin

def Static_3(mac):
	wpspin = "09876543"
	return wpspin
