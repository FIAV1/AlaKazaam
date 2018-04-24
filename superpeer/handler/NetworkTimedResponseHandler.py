#!/usr/bin/env python

import socket
from utils import net_utils, shell_colors as shell, Logger
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
			response = sd.recv(300).decode()
		except socket.error as e:
			shell.print_red(f'Unable to read the response from the socket: {e}\n')
			sd.close()
			return
		sd.close()

		command = response[0:4]

		if command == "AQUE":

			if len(response) != 212:
				self.log.write_red(f'Invalid packet received: {response}\nUnable to reply.')
				return

			pktid = response[4:20]
			ip_peer = response[20:75]
			port_peer = int(response[75:80])
			file_md5 = response[80:112]
			filename = response[112:212]

			if pktid != LocalData.get_sent_net_quer_packet():
				return

			if not LocalData.exist_net_peer_file(ip_peer, port_peer, file_md5, filename):
				LocalData.add_net_peer_file(ip_peer, port_peer, file_md5, filename)

		else:
			self.log.write_red(f'Invalid packet received: {response}\nUnable to reply.')

		return
