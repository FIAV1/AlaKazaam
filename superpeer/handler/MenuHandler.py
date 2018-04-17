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

			for count, friend in enumerate(LocalData.get_super_friends(), start=1):
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
				return "The server has encountered an error while trying to serve the request."

			try:
				peer_list = peer_repository.find_all(conn)

				if peer_list is None:
					shell.print_red('You do not know any peers.')
					conn.close()
					return
				else:
					for count, peer_row in enumerate(peer_list, start=1):
						shell.print_blue(f'{count}]' + peer_row['ip'] + peer_row['port'] + '\n')

			except database.Error as e:
				conn.rollback()
				conn.close()
				print(f'Error: {e}')
				return "The server has encountered an error while trying to serve the request."

		elif choice == "LISTFILES":
			try:
				conn = database.get_connection(db_file)
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				print(f'Error: {e}')
				return "The server has encountered an error while trying to serve the request."

			try:
				files = file_repository.find_all(conn)

				if files is None:
					shell.print_red('You do not have any files.')
					conn.close()
					return
				else:
					for count, file_row in enumerate(files, start=1):
						peer_list = peer_repository.get_peers_by_file(conn, file_row['file_md5'])

						shell.print_green(f'{count}]' + file_row['file_md5'] + file_row['file_name'] + ':')
						print('(')
						for peer_row in peer_list:
							peer_ip = peer_row['ip']
							peer_port = peer_row['port']
							print(f'{peer_ip} [{peer_port}]; ')
						print(')\n')

			except database.Error as e:
				conn.rollback()
				conn.close()
				print(f'Error: {e}')
				return "The server has encountered an error while trying to serve the request."

		else:
			pass
