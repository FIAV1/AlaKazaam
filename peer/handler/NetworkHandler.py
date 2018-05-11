#!/usr/bin/env python

import socket
from common.HandlerInterface import HandlerInterface
from utils import Logger, net_utils
from utils.Uploader import Uploader
from peer.LocalData import LocalData
from threading import Timer


class NetworkHandler(HandlerInterface):

	def __init__(self, log: Logger.Logger):
		self.log = log

	def __delete_packet(self, pktid: str) -> None:
		""" Delete a packet from the net

		:param pktid: id of the packet
		:return: None
		"""
		if LocalData.exist_in_received_packets(pktid):
			LocalData.delete_received_packet(pktid)

	def __forward_packet(self, ttl: str, packet: str) -> None:
		""" Forward a supe packet in the net to superpeer

		:param ip_sender: ip address of sender host
		:param ttl: packet time to live
		:param packet: string representing the packet
		:return: None
		"""
		new_ttl = int(ttl) - 1

		if new_ttl > 0:
			packet = packet[:80] + str(new_ttl).zfill(2) + packet[82:]
			superpeer_ip4 = LocalData.get_superpeer_ip4()
			superpeer_ip6 = LocalData.get_superpeer_ip6()
			superpeer_port = LocalData.get_superpeer_port()

			net_utils.send_packet_and_close(superpeer_ip4, superpeer_ip6, superpeer_port, packet)

	def serve(self, sd: socket.socket) -> None:
		""" Handle the neighbours packet

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
		socket_port_sender = sd.getpeername()[1]

		self.log.write_green(f'{socket_ip_sender} [{socket_port_sender}] -> ', end='')
		self.log.write(f'{packet}')

		command = packet[:4]

		if command == "SUPE":
			sd.close()

			if len(packet) != 82:
				self.log.write_red('Invalid packet. Unable to reply.')
				return

			pktid = packet[4:20]
			ip_peer = packet[20:75]
			port_peer = int(packet[75:80])
			ttl = packet[80:82]

			# packet management
			if pktid == LocalData.get_sent_packet():
				return

			if not LocalData.exist_in_received_packets(pktid):
				LocalData.add_received_packet(pktid)
				t = Timer(20, function=self.__delete_packet, args=(pktid,))
				t.start()
			else:
				return

			# forwarding the supe packet to superpeer
			self.__forward_packet(ttl, packet)

		elif command == "RETR":
			if len(packet) != 36:
				self.log.write_blue('Sending -> ', end='')
				self.log.write('Invalid packet. Unable to reply.')
				sd.send('Invalid packet. Unable to reply.'.encode())
				sd.close()
				return

			file_md5 = packet[4:36]

			file_name = LocalData.get_shared_file_name_from_md5(file_md5)

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
			self.log.write_red('Invalid packet. Unable to reply.')
			sd.close()

		return
