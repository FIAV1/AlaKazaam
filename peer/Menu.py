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
			print('\n- Main Menù -----------------------')
			print('| <1> Search a file to download   |')
			print('| <2> Share a file                |')
			print('| <3> Delete a shared file        |')
			print('| <4> Show your superpeer         |')
			print('-----------------------------------')
			choice = input('Select an option (q to logout): ')

			if choice in {'1', '2', '3', '4'}:
				if choice == '1':
					command = 'FIND'
				elif choice == '2':
					command = 'ADFF'
				elif choice == '3':
					command = 'DEFF'
				elif choice == '4':
					command = 'SHOWSUPER'

				self.handler.serve(command)
			elif choice != 'q':
				shell_colors.print_red('Input code is wrong. Choose one action!\n')

		self.handler.serve('LOGO')
		shell_colors.print_blue('\nBye!\n')
