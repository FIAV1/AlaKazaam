#!/usr/bin/env python

from utils import net_utils, Logger, shell_colors as shell
from utils.Downloader import Downloader
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
				print('The server has encountered an error while trying to serve the request.')
				return

			try:
				peer_list = peer_repository.find_all(conn)

				if not peer_list:
					shell.print_red('You do not know any peers.')
					conn.close()

				else:
					for count, peer_row in enumerate(peer_list, start=1):
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
				print('The server has encountered an error while trying to serve the request.')
				return

			while True:
					index = input('\nPlease select a file to download: ')

					if index == 'q':
						print('\n')
						LocalData.clear_peer_files()
						return

					try:
						index = int(index) - 1

					except ValueError:
						shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected.')
						continue

					if 0 <= index <= len(files):

						chosen_peer_file = LocalData.get_peer_file_by_index(index)
						host_ip4 = LocalData.get_file_owner_ip4(chosen_peer_file)
						host_ip6 = LocalData.get_file_owner_ip6(chosen_peer_file)
						host_port = LocalData.get_file_owner_port(chosen_peer_file)
						file_md5 = LocalData.get_file_md5(chosen_peer_file)
						file_name = LocalData.get_file_name(chosen_peer_file)

						# preparo packet per retr, faccio partire server in attesa download, invio packet e attendo
						packet = 'RETR' + file_md5

					try:
						Downloader(host_ip4, host_ip6, host_port, packet, file_name).start()

						shell.print_green(f'\nDownload of {file_name} completed.\n')
						LocalData.clear_peer_files()
						# LocalData.add_shared_file(file_name, file_md5, os.stat('shared/' + file_name).st_size)

					except OSError:
						shell.print_red(f'\nError while downloading {file_name}\n')
						break

					else:
						shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected.')
						continue

		else:
			pass
