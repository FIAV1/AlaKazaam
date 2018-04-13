#!/usr/bin/env python

import os
from utils import net_utils, shell_colors as shell
from superpeer import superpeer
from peer import peer


if __name__ == '__main__':

	shell.print_blue('           _      ', end='')
	shell.print_yellow(' _  __                    ', end='')
	shell.print_blue('           ')
	shell.print_blue('     /\   | |     ', end='')
	shell.print_yellow('| |/ /                    ', end='')
	shell.print_blue('           ')
	shell.print_blue('    /  \  | | __ _', end='')
	shell.print_yellow('| \' / __ _ ______ _  __ _', end='')
	shell.print_blue(' _ __ ___ ')
	shell.print_blue('   / /\ \ | |/ _` ', end='')
	shell.print_yellow('|  < / _` |_  / _` |/ _` |', end='')
	shell.print_blue(' \'_ ` _ \ ')
	shell.print_blue('  / ____ \| | (_| ', end='')
	shell.print_yellow('| . \ (_| |/ / (_| | (_| |', end='')
	shell.print_blue(' | | | | | ')
	shell.print_blue(' /_/    \_\_|\__,_', end='')
	shell.print_yellow('|_|\_\__,_/___\__,_|\__,_|', end='')
	shell.print_blue('_| |_| |_| ')

	if not os.path.exists('shared'):
		os.mkdir('shared')

	net_utils.prompt_parameters_request()

	choice = ''
	while choice != 'q':
		choice = input('Are you a super peer? (y/n): ')
		if choice == 'y':
			superpeer.startup()
			break
		elif choice == 'n':
			peer.startup()
			break
		else:
			shell.print_red('Input code is wrong. Choose y or n!\n')
