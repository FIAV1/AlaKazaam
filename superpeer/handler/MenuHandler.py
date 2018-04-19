#!/usr/bin/env python

from utils import net_utils, hasher, shell_colors as shell
from utils.Downloader import Downloader
import uuid
import os
from socket import socket
from superpeer.LocalData import LocalData
from common.ServerThread import ServerThread
from superpeer.handler.TimedResponseHandler import TimedResponseHandler
from utils.SpinnerThread import SpinnerThread
from threading import Timer
from superpeer.database import database
from superpeer.model import file_repository, peer_repository

class MenuHandler:

	def __broadcast(self, packet: str) -> None:
		""" Send the packet to a pool of hosts

		:param packet: packet to be sent
		:return: None
		"""
		superfriends = LocalData.get_super_friends()

		for superfriend in superfriends:

			try:
				net_utils.send_packet_and_close(
					LocalData.get_super_friend_ip4(superfriend),
					LocalData.get_super_friend_ip6(superfriend),
					LocalData.get_super_friend_port(superfriend),
					packet)
			except socket.error as e:
				shell.print_red(f'\nUnable to send the packet on the socket: {e}')
				return


	def serve(self, choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""

		if choice == "SUPE":
			# SUPE[4B].Packet_Id[16B].IP_Peer[55B].Port_Peer[5B].TTL[2B]
			pktid = str(uuid.uuid4().hex[:16].upper())
			ip = net_utils.get_local_ip_for_response()
			port = net_utils.get_asup_port()
			ttl = '04'

			packet = choice + pktid + ip + str(port).zfill(5) + ttl
			LocalData.set_sent_supe_packet(pktid)

			old_superfriends_len = len(LocalData.get_super_friends())

			server = ServerThread(port, TimedResponseHandler())
			server.daemon = True
			server.start()

			spinner = SpinnerThread('Searching peers (ENTER to continue)', 'Research done!')
			spinner.start()

			timer = Timer(20, lambda: (spinner.stop(), server.stop()))
			timer.start()

			self.__broadcast(packet)
			input()
			print('\033[1A', end='\r')

			if timer.is_alive():
				spinner.stop()
				spinner.join()
				timer.cancel()
				timer.join()
				server.stop()
				server.join()
			else:
				spinner.join()
				timer.join()
				server.join()

			if len(LocalData.get_super_friends()) == old_superfriends_len:
				shell.print_yellow('\nNo new superpeer found.\n')

		elif choice == "ADFF":

			if not os.path.exists('shared'):
				shell.print_red('\nCannot find the shared folder.')
				return

			dir_file = list()

			for count, dir_entry in enumerate(os.scandir('shared'), 1):
				dir_file.append((dir_entry.name, hasher.get_md5(dir_entry.path), dir_entry.stat().st_size))
				print(f'\n{count}) {dir_entry.name}')
				shell.print_yellow(f' {hasher.get_md5(dir_entry.path)}')
				print(f' size: {dir_entry.stat().st_size}')

			if count == 0:
				shell.print_yellow('\nNo file in the shared folder.')
				return

			while True:

				index = input('\nPlease select a file to share(pres q to exit): ')

				if index == 'q':
					print('\n')
					dir_file.clear()
					return

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {count} expected.')
					continue

				if 0 <= index <= count - 1:
					chosen_file = dir_file.pop(index)

					filename = LocalData.get_shared_filename(chosen_file)
					filemd5 = LocalData.get_shared_filemd5(chosen_file)
					filedim = LocalData.get_shared_dim(chosen_file)

					if not LocalData.exist_shared_file(filename, filemd5, filedim):
						LocalData.add_shared_file(filename, filemd5, filedim)
						shell.print_green('\nThe file is now shared.')
					else:
						shell.print_yellow('\nThe file is already shared.')

					dir_file.clear()

					break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {count} expected.')
				continue

		elif choice == "DEFF":

			for count, file in enumerate(LocalData.get_shared_files()):
				print(f'\n{count}) {LocalData.get_shared_filename(file)}')
				shell.print_yellow(f' {LocalData.get_shared_filemd5(file)}')
				print(f' size: {LocalData.get_shared_dim(file)}')

			if count == 0:
				shell.print_yellow('\nNo file in sharing.')
				return

			while True:

				index = input('\nPlease select a file to delete from sharing(pres q to exit): ')

				if index == 'q':
					print('\n')
					return

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {count} expected.')
					continue

				if 0 <= index <= count - 1:

					deleted_file = LocalData.get_shared_file_by_index(index)

					shell.print_blue(f'\n{LocalData.get_shared_filename(deleted_file)}')
					shell.print_yellow(f' {LocalData.get_shared_filemd5(deleted_file)}')
					shell.print_blue(' removed from sharing.')

					break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {count} expected.')
				continue

		elif choice == "QUER":

			while True:
				search = input('\nEnter the file name: ')

				if not 0 <= len(search) <= 20:
					shell.print_red('\nFile name must be between 1 and 20 chars long.\n')
					continue
				break

			# Read matching files from DB
			try:
				conn = database.get_connection('directory.db')
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				shell.print_red(f'\nError while getting connection from database: {e}')
				return

			try:
				total_db_file = file_repository.get_files_count_by_querystring(conn, search)

				# TODO remove after testing
				if total_db_file == 0:
					shell.print_yellow('\nNo matching results from the DB.\n')
				else:

					db_files = file_repository.get_files_by_querystring(conn, search)

					# print('\nFile from peers: ')

					for file in db_files:
						peers = peer_repository.get_peers_by_file(conn, file.file_md5)

						for peer in peers:

							ip4_peer, ip6_peer = net_utils.get_ip_pair(peer.ip)
							# stampa di debug
							# print(f'\n{LocalData.peer_file_index(ip4_peer, ip6_peer, peer.port, file.file_md5, file.file_name)}')
							# shell.print_yellow(f' {file.file_md5}')
							# print(f' {file.file_name} from {ip4_peer|ip6_peer} on port {peer.port}')
							LocalData.add_peer_files(ip4_peer, ip6_peer, peer.port, file.file_md5, file.file_name)

				conn.commit()
				conn.close()

			except database.Error as e:
				conn.rollback()
				conn.close()
				LocalData.clear_peer_files()
				shell.print_red(f'\nError while retrieving data from database: {e}')

			# Send a search for a file on the superpeer network
			# QUER[4B].Packet_Id[16B].IP_Peer[55B].Port_Peer[5B].TTL[2B].Search[20B]
			pktid = str(uuid.uuid4().hex[:16].upper())
			ip = net_utils.get_local_ip_for_response()
			port = net_utils.get_aque_port()
			ttl = '05'

			packet = choice + pktid + ip + str(port).zfill(5) + ttl + search.ljust(20)
			LocalData.set_sent_quer_packet(pktid)

			server = ServerThread(port, TimedResponseHandler())
			server.daemon = True
			server.start()

			spinner = SpinnerThread('Searching files (ENTER to continue)', 'Research done!')
			spinner.start()

			timer = Timer(20, lambda: (spinner.stop(), server.stop()))
			timer.start()

			self.__broadcast(packet)
			input()
			print('\033[1A', end='\r')

			if timer.is_alive():
				spinner.stop()
				spinner.join()
				timer.cancel()
				timer.join()
				server.stop()
				server.join()
			else:
				spinner.join()
				timer.join()
				server.join()

			# Retrieving the list of database's files and superpeer network's files
			peer_files = LocalData.get_peer_files()

			# TODO remove after testing
			if len(peer_files) <= total_db_file:
				shell.print_yellow('\nNo matching results from the superpeer network.\n')

			if len(peer_files) < 1:
				shell.print_red('\nNo file matching the keyword.\n')
				return

			for peer_file in peer_files:

				peer_ip4 = LocalData.get_file_owner_ip4(peer_file)
				peer_ip6 = LocalData.get_file_owner_ip6(peer_file)
				peer_port = LocalData.get_file_owner_port(peer_file)
				file_md5 = LocalData.get_file_md5(peer_file)
				file_name = LocalData.get_file_name(peer_file)

				print(f'\n{LocalData.peer_file_index(peer_ip4, peer_ip6, peer_port, file_md5, file_name) + 1}')
				shell.print_yellow(f' {file_md5}')
				shell.print_blue(f' {file_name}')
				print(f' from {peer_ip4}|{peer_ip6} on port {peer_port}')

			while True:
				index = input('\nPlease select a file to download: ')

				if index == 'q':
					print('\n')
					LocalData.clear_peer_files()
					return

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(peer_files)} expected.')
					continue

				if 0 <= index <= len(peer_files):

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
					shell.print_red(f'\nWrong index: number in range 1 - {len(peer_files)} expected.')
					continue

		elif choice == "LISTPEERS":
			# chiamata a database per listare i peer (oppure i super peer?--> altro command)
			pass

		elif choice == "LISTFILES":
			# listare i file del DB --> dare la possibilità di scaricare
			# creare RETR --> Downloader.py
			pass

		else:
			pass
