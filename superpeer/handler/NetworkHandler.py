#!/usr/bin/env python

import socket
from threading import Timer
from common.HandlerInterface import HandlerInterface
from superpeer.LocalData import LocalData
from utils import Logger, net_utils
import ipaddress
import uuid
from superpeer.database import database
from superpeer.model.Peer import Peer
from superpeer.model.File import File
from superpeer.model import peer_repository
from superpeer.model import file_repository
from common.ServerThread import ServerThread
from .NetworkTimedResponseHandler import NetworkTimedResponseHandler
from utils.Uploader import Uploader


class NetworkHandler(HandlerInterface):

	def __init__(self, db_file: str, log: Logger.Logger):
		self.db_file = db_file
		self.log = log

	def __delete_packet(self, pktid: str) -> None:
		""" Delete a packet received from the net

		:param pktid: id of the packet
		:return: None
		"""
		if LocalData.exist_in_received_packets(pktid):
			LocalData.delete_received_packet(pktid)

	def __forward_packet(self, ip_sender: str, ip_source: str, ttl: str, packet: str) -> None:
		""" Forward a packet in the net to neighbours

		:param ip_sender: ip address of sender host
		:param ttl: packet time to live
		:param packet: string representing the packet
		:return: None
		"""
		new_ttl = int(ttl) - 1

		if new_ttl > 0:
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_source)

			# get the recipients list without the peer who sent the packet and the peer who forwarded it
			recipients = LocalData.get_super_friends_recipients(ip_sender, ip4_peer, ip6_peer)

			packet = packet[:80] + str(new_ttl).zfill(2) + packet[82:]

			for superfriend in recipients:
				ip4 = LocalData.get_super_friend_ip4(superfriend)
				ip6 = LocalData.get_super_friend_ip6(superfriend)
				port = LocalData.get_super_friend_port(superfriend)
				try:
					net_utils.send_packet_and_close(ip4, ip6, port, packet)
					self.log.write_blue(f'Forwarding to {ip4}|{ip6} [{port}] -> ', end='')
					self.log.write(f'{packet}')
				except socket.error as e:
					self.log.write_red(f'Unable to forward a packet to {ip4}|{ip6} [{port}]: {e}')

	def __broadcast_packet(self, packet: str) -> None:
		""" Send the packet to a pool of hosts
		:param packet: packet to be broadcasted
		:return: None
		"""

		for superfriend in LocalData.get_super_friends():
			ip4 = LocalData.get_super_friend_ip4(superfriend)
			ip6 = LocalData.get_super_friend_ip6(superfriend)
			port = LocalData.get_super_friend_port(superfriend)
			try:
				net_utils.send_packet_and_close(ip4, ip6, port, packet)
				self.log.write_blue(f'Broadcasting to {ip4}|{ip6} [{port}] -> ', end='')
				self.log.write(f'{packet}')
			except socket.error as e:
				self.log.write_red(f'Unable to broadcast a packet to {ip4}|{ip6} [{port}]: {e}')

	def serve(self, sd: socket.socket) -> None:
		""" Handle a network packet

		:param sd: the socket descriptor used for read the packet
		:return: None
		"""

		try:
			packet = sd.recv(200).decode()
		except socket.error as e:
			self.log.write_red(f'Unable to read the packet from the socket: {e}')
			sd.close()
			return

		# log the packet received
		socket_ip_sender = sd.getpeername()[0]
		if ipaddress.IPv6Address(socket_ip_sender).ipv4_mapped is None:
			socket_ip_sender = ipaddress.IPv6Address(socket_ip_sender).compressed
		else:
			socket_ip_sender = ipaddress.IPv6Address(socket_ip_sender).ipv4_mapped.compressed

		socket_port_sender = sd.getpeername()[1]
		self.log.write_green(f'{socket_ip_sender} [{socket_port_sender}] -> ', end='')
		self.log.write(f'{packet}')

		command = packet[:4]

		if command == "SUPE":
			sd.close()
			if len(packet) != 82:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to reply.')
				return

			pktid = packet[4:20]
			ip_peer = packet[20:75]
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_peer)
			port_peer = int(packet[75:80])
			ttl = packet[80:82]

			# packet management
			if pktid == LocalData.get_sent_supe_packet():
				# if the SUPE i sent has been forwarded to me erroneously
				return

			if not LocalData.exist_in_received_packets(pktid):
				LocalData.add_received_packet(pktid, ip_peer, port_peer)
				t = Timer(20, function=self.__delete_packet, args=(pktid,))
				t.start()
			else:
				return

			# send the NEAR acknowledge
			response = "ASUP" + pktid + net_utils.get_local_ip_for_response() +\
						str(net_utils.get_network_port()).zfill(5)
			try:
				net_utils.send_packet_and_close(ip4_peer, ip6_peer, port_peer, response)
				self.log.write_blue(f'Sending to {ip4_peer}|{ip6_peer} [{port_peer}] -> ', end='')
				self.log.write(f'{response}')
			except socket.error as e:
				self.log.write_red(f'An error has occurred while sending an {response} to {ip4_peer}|{ip6_peer} [{port_peer}]: {e}')

			# forwarding the packet to other superpeers
			self.__forward_packet(socket_ip_sender, ip_peer, ttl, packet)

		elif command == "LOGI":
			error_response = "ALGI" + '0' * 16

			if len(packet) != 64:
				self.log.write_red(f'Invalid packet received: {packet}')
				try:
					sd.send(error_response.encode())
					sd.close()
					self.log.write_blue(f'Sending to {socket_ip_sender} [{socket_port_sender}] -> ', end='')
					self.log.write(f'{error_response}')
				except socket.error as e:
					self.log.write_red(f'An error has occurred while sending an ALGI response to {socket_ip_sender}: {e}')
					return
				return

			ip = packet[4:59]
			port = packet[59:64]

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				try:
					sd.send(error_response.encode())
					sd.close()
					self.log.write_blue(f'Sending to {socket_ip_sender} [{socket_port_sender}] -> ', end='')
					self.log.write(f'{error_response}')
				except socket.error as e:
					self.log.write_red(f'An error has occurred while sending {error_response} to {socket_ip_sender}: {e}')
					return
				return

			try:
				peer = peer_repository.find_by_ip(conn, ip)

				# if the peer didn't already logged in
				if peer is None:
					session_id = str(uuid.uuid4().hex[:16].upper())
					peer = peer_repository.find(conn, session_id)

					# while the generated session_id exists
					while peer is not None:
						session_id = str(uuid.uuid4().hex[:16].upper())
						peer = peer_repository.find(conn, session_id)

					peer = Peer(session_id, ip, port)
					peer.insert(conn)

				conn.commit()
				conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				try:
					sd.send(error_response.encode())
					sd.close()
					self.log.write_blue(f'Sending to {socket_ip_sender} [{socket_port_sender}] -> ', end='')
					self.log.write(f'{error_response}')
				except socket.error as e:
					self.log.write_red(f'An error has occurred while sending {error_response} to {socket_ip_sender}: {e}')
					return
				return

			response = "ALGI" + peer.session_id

			try:
				sd.send(response.encode())
				sd.close()
				self.log.write_blue(f'Sending to {socket_ip_sender} [{socket_port_sender}] -> ', end='')
				self.log.write(f'{response}')
			except socket.error as e:
				self.log.write_red(f'An error has occurred while sending {response} to {socket_ip_sender}: {e}')
				return

		elif command == "ADFF":
			sd.close()

			if len(packet) != 152:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to add the file in the DB.')
				return

			session_id = packet[4:20]
			md5 = packet[20:52]
			name = packet[52:152].lower().lstrip().rstrip()

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				peer = peer_repository.find(conn, session_id)

				if peer is None:
					conn.close()
					self.log.write_red('Unauthorized request received: SessionID is invalid')
					return

				file = file_repository.find(conn, md5)

				if file is None:
					file = File(md5, name, 0)
					file.insert(conn)
					file_repository.add_owner(conn, md5, session_id)
				else:
					file.file_name = name
					file.update(conn)
					if not file_repository.peer_has_file(conn, session_id, md5):
						file_repository.add_owner(conn, md5, session_id)

				conn.commit()
				conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			self.log.write_blue(f'Successfully added file: {file.file_name} ({file.file_md5})')

		elif command == "DEFF":
			sd.close()

			if len(packet) != 52:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to delete the file from the DB.')
				return

			session_id = packet[4:20]
			md5 = packet[20:52]

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				peer = peer_repository.find(conn, session_id)

				if peer is None:
					conn.close()
					self.log.write_red('Unauthorized request received: SessionID is invalid')
					return

				if not file_repository.peer_has_file(conn, session_id, md5):
					conn.close()
					return

				peer_repository.file_unlink(conn, session_id, md5)

				copy = file_repository.get_copies(conn, md5)

				if copy == 0:
					file = file_repository.find(conn, md5)
					file.delete(conn)

				conn.commit()
				conn.close()

			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			self.log.write_blue(f'Successfully removed file: {file.file_name} ({file.file_md5})')

		elif command == "FIND":
			if len(packet) != 40:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to reply.')
				sd.close()
				return

			session_id = packet[4:20]
			query = packet[20:40].lower().lstrip().rstrip()

			if query != '*':
				query = '%' + query + '%'

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				sd.close()
				return

			# check in my peers files (DB)
			try:
				peer = peer_repository.find(conn, session_id)

				if peer is None:
					self.log.write_red('Unauthorized request received: SessionID is invalid')
					sd.close()
					return
				else:
					file_rows = file_repository.get_files_by_querystring(conn, query)

					for file_row in file_rows:
						file_md5 = file_row['file_md5']
						file_name = file_row['file_name']

						owner_rows = peer_repository.get_peers_by_file(conn, file_md5)

						for owner_row in owner_rows:
							owner_ip = owner_row['ip']
							owner_port = owner_row['port']

							LocalData.add_net_peer_file(owner_ip, owner_port, file_md5, file_name)

					conn.commit()
					conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				sd.close()
				return

			# check in my shared files
			for shared_file in LocalData.search_in_shared_files(query.strip('%')):
				LocalData.add_net_peer_file(
					net_utils.get_local_ip_for_response(),
					net_utils.get_network_port(),
					LocalData.get_shared_filemd5(shared_file),
					LocalData.get_shared_filename(shared_file)
				)

			# flooding the QUER
			pktid = str(uuid.uuid4().hex[:16].upper())
			ip = net_utils.get_local_ip_for_response()
			port = net_utils.get_aque_port()
			ttl = '05'
			query = packet[20:40]

			packet = "QUER" + pktid + ip + str(port).zfill(5) + ttl + query

			LocalData.set_sent_net_quer_packet(pktid)

			server = ServerThread(port, NetworkTimedResponseHandler(self.log))
			server.daemon = True
			server.start()

			timer = Timer(20, lambda: server.stop())
			timer.start()

			self.__broadcast_packet(packet)

			timer.join()

			try:
				self.log.write_blue(f'Sending {socket_ip_sender} [{socket_port_sender}] -> ', end='')
				self.log.write('AFIN')

				# send the AFIN packet
				fragment = "AFIN" + str(LocalData.get_net_peer_files_md5_amount()).zfill(3)
				sd.send(fragment.encode())

				self.log.write_blue(f'Sending fragment -> ', end='')
				self.log.write(f'{fragment}')

				for md5 in LocalData.get_net_peer_files().keys():
					fragment = md5 + LocalData.get_net_peer_file_name_by_md5(md5).ljust(100) + str(LocalData.get_net_peer_file_copy_amount_by_md5(md5)).zfill(3)
					sd.send(fragment.encode())

					self.log.write_blue(f'Sending fragment -> ', end='')
					self.log.write(f'{fragment}')

					for file_tuple in LocalData.get_net_peer_files_list_by_md5(md5):
						fragment = LocalData.get_net_peer_file_owner_ip(file_tuple) + str(LocalData.get_net_peer_file_owner_port(file_tuple)).zfill(5)
						sd.send(fragment.encode())

						self.log.write_blue(f'Sending fragment -> ', end='')
						self.log.write(f'{fragment}')

			except socket.error as e:
				self.log.write_red(f'An error has occurred while sending an AFIN response to {socket_ip_sender}: {e}')
				sd.close()

			LocalData.clear_net_peer_files()

		elif command == "LOGO":
			if len(packet) != 20:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to reply.')
				sd.close()
				return

			session_id = packet[4:20]

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				sd.close()
				return

			try:
				peer = peer_repository.find(conn, session_id)

				if peer is None:
					conn.close()
					self.log.write_red('Unauthorized request received: SessionID is invalid')
					sd.close()
					return

				deleted = file_repository.delete_peer_files(conn, session_id)

				peer.delete(conn)

				conn.commit()
				conn.close()

			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				sd.close()
				return

			response = "ALGO" + str(deleted).zfill(3)

			try:
				sd.send(response.encode())
				sd.close()
				self.log.write_blue(f'Sending {socket_ip_sender} [{socket_port_sender}] -> ', end='')
				self.log.write(f'{response}')
			except socket.error as e:
				self.log.write_red(f'An error has occurred while sending {response} to {socket_ip_sender}: {e}')
				return

		elif command == "QUER":
			sd.close()
			if len(packet) != 102:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to reply.')
				return

			self.log.write(f'{packet}')

			pktid = packet[4:20]
			ip_peer = packet[20:75]
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_peer)
			port_peer = int(packet[75:80])
			ttl = packet[80:82]
			query = packet[82:102].lower().lstrip().rstrip()

			if query != '*':
				query = '%' + query + '%'

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			# check in my peers files (DB)
			try:
				total_file = file_repository.get_files_count_by_querystring(conn, query)
				if total_file != 0:

					file_rows = file_repository.get_files_by_querystring(conn, query)

					for file_row in file_rows:
						file_md5 = file_row['file_md5']
						file_name = file_row['file_name']

						owner_rows = peer_repository.get_peers_by_file(conn, file_md5)

						for owner_row in owner_rows:
							owner_ip = owner_row['ip']
							owner_port = owner_row['port']

							response = "AQUE" + pktid + owner_ip + owner_port + file_md5 + file_name.ljust(100)

							try:
								net_utils.send_packet_and_close(ip4_peer, ip6_peer, port_peer, response)
								self.log.write_blue(f'Sending {ip4_peer}|{ip6_peer} [{port_peer}] -> ', end='')
								self.log.write(f'{response}')
							except socket.error as e:
								self.log.write_red(f'An error has occurred while sending {response}: {e}')
					conn.commit()
					conn.close()
				else:
					conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			# check in my shared files
			for local_shared_file in LocalData.search_in_shared_files(query.strip('%')):
				local_ip = net_utils.get_local_ip_for_response()
				local_port = str(net_utils.get_network_port()).zfill(5)
				file_md5 = LocalData.get_shared_filemd5(local_shared_file)
				file_name = LocalData.get_shared_filename(local_shared_file).ljust(100)
				response = "AQUE" + pktid + local_ip + local_port + file_md5 + file_name

				try:
					net_utils.send_packet_and_close(ip4_peer, ip6_peer, port_peer, response)
					self.log.write_blue(f'Sending {ip4_peer}|{ip6_peer} [{port_peer}] -> ', end='')
					self.log.write(f'{response}')
				except socket.error as e:
					self.log.write_red(f'An error has occurred while sending {response}: {e}')

			# forwarding the packet to other superpeers
			self.__forward_packet(socket_ip_sender, ip_peer, ttl, packet)

		elif command == "RETR":
			if len(packet) != 36:
				self.log.write_blue('Sending -> ', end='')
				self.log.write('Invalid packet. Unable to reply.')
				sd.send('Invalid packet. Unable to reply.'.encode())
				sd.close()
				return

			file_md5 = packet[4:36]

			file_name = LocalData.get_shared_filename_by_filemd5(file_md5)

			if file_name is None:
				self.log.write_blue('Sending -> ', end='')
				self.log.write('Sorry, the requested file is not available anymore by the selected peer.')
				sd.send('Sorry, the requested file is not available anymore by the selected peer.'.encode())
				sd.close()
				return

			try:
				f_obj = open('shared/' + file_name, 'rb')
			except OSError as e:
				self.log.write_red(f'Cannot open the file to upload: {e}')
				self.log.write_blue('Sending -> ', end='')
				self.log.write('Sorry, the peer encountered a problem while serving your packet.')
				sd.send('Sorry, the peer encountered a problem while serving your packet.'.encode())
				sd.close()
				return

			try:
				Uploader(sd, f_obj, self.log).start()
				self.log.write_blue(f'Sent {sd.getpeername()[0]} [{sd.getpeername()[1]}] -> ', end='')
				self.log.write(f'{file_name}')
				sd.close()

			except OSError as e:
				self.log.write_red(f'Error while sending the file: {e}')
				sd.close()
				return

		else:
			sd.close()
			self.log.write_red(f'Invalid packet received from {socket_ip_sender} [{socket_port_sender}]: ', end='')
			self.log.write(f'{packet}')

		return
