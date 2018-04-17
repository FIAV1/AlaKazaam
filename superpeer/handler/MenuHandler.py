#!/usr/bin/env python

from utils import net_utils, shell_colors as shell
import uuid
from superpeer.LocalData import LocalData
from common.ServerThread import ServerThread
from superpeer.handler.TimedResponseHandler import TimedResponseHandler
from utils.SpinnerThread import SpinnerThread
from threading import Timer
from database import database

class MenuHandler:

	def __broadcast(self, packet: str) -> None:
		""" Send the packet to a pool of hosts

		:param packet: packet to be sent
		:return: None
		"""
		superfriends = LocalData.get_super_friends()

		for superfriend in superfriends:
			net_utils.send_packet_and_close(
				LocalData.get_super_friend_ip4(superfriend),
				LocalData.get_super_friend_ip6(superfriend),
				LocalData.get_super_friend_port(superfriend),
				packet)

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
			LocalData.set_sent_packet(pktid)

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
				shell.print_red('\nNo new superpeer found.\n')
			else:
				for friend in LocalData.get_super_friends():
					shell.print_green(
						f'\nNew superpeer found: {LocalData.super_friend_index(friend[0],friend[1],friend[2])})' 
						f' {LocalData.get_super_friend_ip4(friend)|LocalData.get_super_friend_ip6(friend)}'
						f' on port {LocalData.get_super_friend_port(friend)}')

		elif choice == "ADFF":
			# aggiungere un record da database
			pass

		elif choice == "DEFF":
			# eliminare un record dal database
			pass

		elif choice == "QUER":
			# QUER[4B].Packet_Id[16B].IP_Peer[55B].Port_Peer[5B].TTL[2B].Search[20B]
			pktid = str(uuid.uuid4().hex[:16].upper())
			ip = net_utils.get_local_ip_for_response()
			port = net_utils.get_aque_port()
			ttl = '5'

			while True:
				search = input('\nEnter the file name: ')

				if not 0 <= len(search) <= 20:
					shell.print_red('\nFile name must be between 1 and 20 chars long.\n')
					continue
				break

			packet = choice + pktid + ip + str(port).zfill(5) + ttl + search.ljust(20)
			LocalData.set_sent_packet(pktid)

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

			network_files = LocalData.get_peer_files()

			if len(network_files) < 1:
				shell.print_red('\nNo matching results from the superpeer network.\n')
			else:
				for file in LocalData.get_peer_files():
					print(f'\nFile found from network: {LocalData.peer_file_index(file[0], file[1], file[2], file[3], file[4])}')
					shell.print_yellow(f' {LocalData.get_peer_file_md5(file)}')
					print(f' {LocalData.get_peer_file_name(file)}'
						f' from {LocalData.get_peer_file_ip4(file)|LocalData.get_peer_file_ip6(file)}'
						f' on port {LocalData.get_peer_file_port(file)}')


			try:
				conn = database.get_connection('directory.db')
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				shell.print_red(f'\nError while retrieving data from database: {e}')

			# lettura da database dei peer file con corrispondenza
			# print dei file presenti(!?aggiunta alla struttura dati?!?)
			# dare all'utente la possibilità di scegliere il file
			# usare quei parametri per costruire RETR
			# chiamare il Download.py
			# pulire la struttura dati

		elif choice == "LISTPEERS":
			# chiamata a database per listare i peer (oppure i super peer?--> altro command)
			pass

		elif choice == "LISTFILES":
			# listare i file del DB --> dare la possibilità di scaricare
			# creare RETR --> Downloader.py
			pass

		else:
			pass
