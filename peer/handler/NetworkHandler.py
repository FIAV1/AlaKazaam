#!/usr/bin/env python

import socket
from common.HandlerInterface import HandlerInterface
from utils import Logger


class NetworkHandler(HandlerInterface):

	def __init__(self, log: Logger.Logger):
		self.log = log

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
			pass

		else:
			self.log.write_red('Invalid packet. Unable to reply.')
			sd.close()

		return
