#!/usr/bin/env python

from utils import net_utils, Logger, shell_colors as shell
from superpeer.LocalData import LocalData
from superpeer.database import database
from superpeer.model import peer_repository, file_repository

db_file = 'directory.db'


class MenuHandler:

	def serve(self, choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""

		if choice == "SUPE":
			pass

		elif choice == "ADFF":
			pass

		elif choice == "DEFF":
			pass

		elif choice == "QUER":
			pass

		elif choice == "LISTSUPERPEERS":

			shell.print_green('\nList of known peers:')

			if not LocalData.get_super_friends():
				shell.print_red('You do not know any superpeers.')
			else:
				for count, friend in enumerate(LocalData.get_super_friends(), 1):
					friend_ip4 = LocalData.get_super_friend_ip4(friend)
					friend_ip6 = LocalData.get_super_friend_ip6(friend)
					friend_port = LocalData.get_super_friend_port(friend)
					shell.print_blue(
						f'{count}] {friend_ip4} {friend_ip6} {str(friend_port)}')

		elif choice == "LISTPEERS":

			try:
				conn = database.get_connection(db_file)
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

			try:
				peer_list = peer_repository.find_all(conn)

				if not peer_list:
					shell.print_red('You do not know any peers.')
					conn.close()
					return

				else:
					for count, peer_row in enumerate(peer_list, 1):
						shell.print_blue(f'{count}]' + peer_row['ip'] + peer_row['port'] + '\n')

			except database.Error as e:
				conn.rollback()
				conn.close()
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

		elif choice == "LISTFILES":
			try:
				conn = database.get_connection(db_file)
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

			try:
				files = file_repository.find_all(conn)

				if not files:
					shell.print_red('You do not have any files.')
					conn.close()
					return

				else:

					for count, file_row in enumerate(files, 1):
						print('\nLogged peers files:')
						shell.print_green(f'{count}] {file_row["file_name"]}|{file_row["file_md5"]}:')

					print('\nYour shared files:')
					for count, shared_file in enumerate(LocalData.get_shared_files(), 1):
						shell.print_green(
							f'{count}] {LocalData.get_shared_file_name(shared_file)}|{LocalData.get_shared_file_md5(shared_file)}\n')

			except database.Error as e:
				conn.rollback()
				conn.close()
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

		else:
			pass
