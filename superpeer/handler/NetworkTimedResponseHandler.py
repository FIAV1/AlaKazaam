#!/usr/bin/env python

import socket
import ipaddress
from utils import Logger
from common.HandlerInterface import HandlerInterface
from superpeer.LocalData import LocalData


class NetworkTimedResponseHandler(HandlerInterface):

	def __init__(self, log: Logger.Logger):
		self.log = log

	def serve(self, sd: socket.socket) -> None:
		""" Handle the peer request

		:param sd: the socket descriptor used for read the request
		:return None
		"""

		try:
			packet = sd.recv(300).decode()
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

		command = packet[0:4]

		if command == "AQUE":

			if len(packet) != 212:
				self.log.write_red(f'Invalid packet received: {packet}\nUnable to reply.')
				return

			pktid = packet[4:20]
			ip_peer = packet[20:75]
			port_peer = int(packet[75:80])
			file_md5 = packet[80:112]
			filename = packet[112:212]

			if pktid != LocalData.get_sent_net_quer_packet():
				return

			if not LocalData.exist_net_peer_file(ip_peer, port_peer, file_md5, filename):
				LocalData.add_net_peer_file(ip_peer, port_peer, file_md5, filename)

		else:
			self.log.write_red(f'Invalid packet received: {packet}\nUnable to reply.')

		return
