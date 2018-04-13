#!/usr/bin/env python

import socket
from utils import shell_colors
from common.HandlerInterface import HandlerInterface


class ResponseHandler(HandlerInterface):

	def serve(self, sd: socket.socket) -> None:
		""" Handle the peer request

		:param sd: the socket descriptor used for read the request
		:return None
		"""
		try:
			command = sd.recv(4).decode()
		except OSError as e:
			shell_colors.print_red(f'\nUnable to read the command from the socket: {e}\n')
			sd.close()
			return

		if command == "AQUE":
			pass

		elif command == "ASUP":
			pass

		else:
			wrong_response = sd.recv(300).decode()
			sd.close()
			shell_colors.print_red(f"\nInvalid response: {command} -> {wrong_response}\n")

		return
