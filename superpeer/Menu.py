#!/usr/bin/env python

from peer.handler import MenuHandler
from utils import shell_colors


class Menu:

	def __init__(self, handler: MenuHandler):
		self.handler = handler

	def show(self) -> None:
		""" Shows the menu that interacts with the user

		:return: None
		"""

		choice = ''
		while choice != 'q':
			print('\n- Main Menù ----------------------------')
			print('| <1> Search a file to download          |')
			print('| <2> Search other superpeers around you |')
			print('| <3> Add a file                         |')
			print('| <4> Delete a file                      |')
			print('| <5> List your known superpeers         |')
			print('| <6> List your known peers              |')
			print('| <7> List all files                     |')
			print('------------------------------------------')
			choice = input('Select an option (q to exit): ')

			if choice in {'1', '2', '3', '4', '5', '6', '7'}:
				if choice == '1':
					command = "QUER"
				elif choice == '2':
					command = "SUPE"
				elif choice == '3':
					command = "ADFF"
				elif choice == '4':
					command = "DEFF"
				elif choice == '5':
					command = "LISTSUPERPEERS"
				elif choice == '6':
					command = "LISTPEERS"
				elif choice == '7':
					command = "LISTFILES"

				self.handler.serve(command)
			elif choice != 'q':
				shell_colors.print_red('Input code is wrong. Choose one action!\n')

		shell_colors.print_blue('\nBye!\n')
