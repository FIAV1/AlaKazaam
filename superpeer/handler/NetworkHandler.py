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

			for peer in recipients:
				ip4 = LocalData.get_super_friend_ip4(peer)
				ip6 = LocalData.get_super_friend_ip6(peer)
				port = LocalData.get_super_friend_port(peer)
				try:
					net_utils.send_packet_and_close(ip4, ip6, port, packet)
				except socket.error as e:
					self.log.write_red(f'An error has occurred while forwarding {packet}\n{e}')

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
			if pktid == LocalData.get_sent_packet():
				# if the SUPE i sent has been forwarded to me erroneously
				return

			if not LocalData.exist_in_received_packets(pktid):
				LocalData.add_received_packet(pktid, ip_peer, port_peer)
				t = Timer(300, function=self.__delete_packet, args=pktid)
				t.start()
			else:
				return

			# send the NEAR acknowledge
			response = "ASUP" + pktid + net_utils.get_local_ip_for_response() +\
						str(net_utils.get_network_port()).zfill(5)
			try:
				net_utils.send_packet_and_close(ip4_peer, ip6_peer, port_peer, response)
			except socket.error as e:
				self.log.write_red(f'An error has occurred while sending an ASUP response: {e}')

			# forwarding the packet to other superpeers
			self.__forward_packet(socket_ip_sender, ip_peer, ttl, packet)

		elif command == "LOGI":
			error_response = "ALGI" + '0' * 16

			if len(packet) != 64:
				self.log.write_red(f'Invalid packet received: {packet}')
				sd.send(error_response.encode())
				sd.close()
				return

			ip = packet[4:59].decode()
			port = packet[59:64].decode()

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				sd.send(error_response.encode())
				sd.close()
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
				sd.send(error_response.encode())
				sd.close()
				return

			response = "ALGI" + peer.session_id

			ip4_peer, ip6_peer = net_utils.get_ip_pair(peer.ip)
			self.log.write_blue(f'Sending {ip4_peer}|{ip6_peer} [{port}] -> ', end='')
			self.log.write(f'{response}')
			sd.send(response.encode())

		elif command == "ADFF":
			sd.close()

			if len(packet) != 152:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to add the file in the DB.')
				return

			session_id = packet[4:20].decode()
			md5 = packet[20:52].decode()
			name = packet[52:152].decode().lower()

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

			self.log.write_blue(f'Successfully added file: {file.name} ({file.md5})')

		elif command == "DEFF":
			sd.close()

			if len(packet) != 52:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to delete the file from the DB.')
				return

			session_id = packet[4:20].decode()
			md5 = packet[20:52].decode()

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

			self.log.write_blue(f'Successfully removed file: {file.name} ({file.md5})')

		elif command == "FIND":
			pass

		elif command == "LOGO":
			if len(packet) != 20:
				self.log.write_red(f'Invalid packet received: {packet}')
				sd.send('Invalid request. Usage is: LOGO<your_session_id>'.encode())
				sd.close()
				return

			session_id = packet[4:20].decode()

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				sd.send('An error has occurred while trying to serve your request'.encode())
				sd.close()
				return

			try:
				peer = peer_repository.find(conn, session_id)

				if peer is None:
					conn.close()
					self.log.write_red('Unauthorized request received: SessionID is invalid')
					sd.send('Unauthorized request: your SessionID is invalid'.encode())
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
				sd.send('An error has occurred while trying to serve your request'.encode())
				sd.close()
				return

			response = "ALGO" + str(deleted).zfill(3)

			ip4_peer, ip6_peer = net_utils.get_ip_pair(peer.ip)
			self.log.write_blue(f'Sending {ip4_peer}|{ip6_peer} [{port}] -> ', end='')
			self.log.write(f'{response}')
			sd.send(response.encode())

		elif command == "QUER":
			sd.close()
			if len(packet) != 102:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to reply.')
				return

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

			try:
				total_file = file_repository.get_files_count_by_querystring(conn, query)
				if total_file == 0:
					conn.close()
					return

				file_list = file_repository.get_files_by_querystring(conn, query)

				conn.commit()
				conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			for file_row in file_list:
				file_md5 = file_row['file_md5']
				file_name = file_row['file_name']

				response = "AQUE" + pktid + net_utils.get_local_ip_for_response() + file_md5 + file_name
				net_utils.send_packet_and_close(ip4_peer, ip6_peer, port_peer, response)

				self.log.write_blue(f'Sending {ip4_peer}|{ip6_peer} [{port_peer}] -> ', end='')
				self.log.write(f'{response}')

			# forwarding the packet to other superpeers
			self.__forward_packet(socket_ip_sender, ip_peer, ttl, packet)

		else:
			sd.close()
			self.log.write_red(f'Invalid packet received from {socket_ip_sender} [{socket_port_sender}]: ', end='')
			self.log.write(f'{packet}')

		return
