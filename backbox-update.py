#!/usr/bin/env python

# Copyright(c) 2011-2013 Raffaele Forte <raffaele.forte@gmail.com>
# http://www.backbox.org/
#
# backbox-update is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# backbox-update is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with backbox-update. If not, see <http://www.gnu.org/licenses/>.

import argparse
import datetime
import os
import subprocess
import sys

DEVNULL = open(os.devnull, 'w')

BLUE = '\033[1;94m'
GREEN = '\033[1;92m'
RED = '\033[1;91m'
ENDC = '\033[1;00m'


def print_banner():
	header = BLUE + ' __________                __   __________                \n' + ENDC
	header += BLUE + ' \______   \_____   _____ |  | _\______   \ _______  ___  \n' + ENDC
	header += BLUE + '  |    |  _/\__  \ / ____\|  |/ /|    |  _//    \  \/  /  \n' + ENDC
	header += BLUE + '  |    |   \ / __ \\\  \___|    < |    |   \  <>  >    <  \n' + ENDC
	header += BLUE + '  |______  /(____  /\____ \__|_ \|______  /\____/__/\_ \\ \n' + ENDC
	header += BLUE + '         \/      \/      \/    \/       \/            \/  \n' + ENDC
	header += ' \_______________________________________' + BLUE + ' Update Script   \n' + ENDC
	print header


def print_menu():
	menu_items = ['Update all'] + tools()
	for num, tool in enumerate(menu_items):
		print '  %2i)\t %s' % (num, tool)


def gem_update():
	print BLUE + '\n[i] Running gems update\n' + ENDC
	subprocess.check_call("gem update --no-rdoc --no-ri", shell=True)


def aptget(command):
	print BLUE + '[i] Running apt-get\n' + ENDC
	subprocess.check_call('apt-get ' + command, shell=True)


def aptget_update():
	now = datetime.datetime.now()
	then = datetime.datetime.fromtimestamp(os.path.getmtime('/var/lib/apt/periodic/update-success-stamp'))
	delta = now - then
	if delta.total_seconds() > 900:
		print BLUE + '\n[i] Running apt-get update\n' + ENDC
		subprocess.check_call('apt-get update -qq', stdout=DEVNULL, stderr=DEVNULL, shell=True)
		print 'Reading package lists... Done\n'
	else:
		print BLUE + '\n[i] Skipping apt-get update\n' + ENDC
		print 'Reading package lists... Already done\n'


def tools():
	tools = os.listdir('/menu/update/')
	tools.sort()
	return tools
		

def get_tool():
	menu_items = ['Update all'] + tools()
	try:
		n = input('\nMake your choice ' + BLUE + '> ' + ENDC)
		item = [menu_items[n]]
	except Exception:
		sys.exit(RED + '\n[!] Invalid option. Quitting...\n' + ENDC)
	return item[0]


def update(tool, sys_type):
	aptget_update()
	if tool == 'Update all':
		aptget('dist-upgrade -y -f --no-install-recommends')
		
		if sys_type.lower() == 'desktop' :
			answer = raw_input('\nDo you want reinstall backbox-desktop? [y/N] ' + BLUE + '> ' + ENDC)
			if answer.lower() == 'y':
				print ''
				aptget('install -y backbox-desktop --reinstall')
		elif sys_type.lower() == 'minimal' :
			answer = raw_input('\nDo you want reinstall backbox-minimal? [y/N] ' + BLUE + '> ' + ENDC)
			if answer.lower() == 'y':
				print ''
				aptget('install -y backbox-minimal --reinstall')
		else :
			sys.exit(RED + '\n[!] Bad system type. Options: [desktop|minimal]\n' + ENDC)
		
		print BLUE + '\n[i] Updating tools\n' + ENDC
		for num, tool in enumerate(tools()):
			try:
				subprocess.check_call('sh /menu/update/' + tool, stdout=DEVNULL, stderr=DEVNULL, shell=True)
				print '  %2i)\t %-15s ' % (num + 1, tool) + '\t' + GREEN + 'ok' + ENDC 
			except:
				print '  %2i)\t %-15s ' % (num + 1, tool) + '\t' + RED + 'ko' + ENDC
				pass 
		#gem_update()
		print BLUE + '\n[i] System updated!\n' + ENDC
		sys.exit()
	else:
		aptget('install ' + tool)
		print BLUE + '\n[i] Running /menu/update/' + tool + ' script\n' + ENDC
		subprocess.call('sh /menu/update/' + tool, shell=True)


def main():
	
	# Parse command line arguments
	parser = argparse.ArgumentParser(description='BackBox Update script helps you to keep updated your system and tools', version='%(prog)s v.0.6 - Copyleft by Raffaele Forte')
	parser.add_argument('-l', '--list', action='store_true', help='show all tools')
	parser.add_argument('type', help='system type, "desktop" or "minimal"')
	group = parser.add_argument_group('update options, only root:')
	group.add_argument('-a', '--all', action='store_true', help='update all, system and tools')
	group.add_argument('-g', '--gems', action='store_true', help='update ruby gems')
	group.add_argument('-t', '--tool', action='store', help='update of single tool')
	args = parser.parse_args()
	
	print_banner()
	
	# Show all tools
	if args.list :
		print_menu()
		print BLUE + '\n[i] Done!\n' + ENDC
		sys.exit()

	# Check root privileges
	if os.geteuid() != 0:
		sys.exit(RED + '[!] Please run this script as root\n' + ENDC)

	# Update all, system and tools
	if args.all :
		update('Update all', args.type)
		sys.exit()

	# Update gems
	if args.gems :
		gem_update()
		print BLUE + '\n[i] Done!\n' + ENDC
		sys.exit()

	# Update single tool
	if args.tool :
		if args.tool in tools():
			update(args.tool, args.type)
			sys.exit()
		else:
			sys.exit(RED + '[!] Tool not in list\n' + ENDC)
	
	# Start interactive mode
	while True:
		print_menu()
		tool = get_tool()
		update(tool, args.type)
		print_banner()


if __name__ == '__main__':
	try:
		main()
	# Handle keyboard interrupts
	except KeyboardInterrupt:
		sys.exit(RED + '\n\n[!] Quitting...\n' + ENDC)
	# Handle exceptions
	except Exception, error:
		sys.exit(RED + '\n[!] ' + str(error) + '\n' + ENDC)
