#!/usr/bin/env python

import socket
import random
from utils import shell_colors
from utils import progress_bar


class Downloader:

	def __init__(self, host_ip4: str, host_ip6: str, host_port: int, packet: str, file_name: str):
		self.host_ip4 = host_ip4
		self.host_ip6 = host_ip6
		self.host_port = host_port
		self.packet = packet
		self.file_name = file_name.lstrip().rstrip()

	def __create_socket(self) -> (socket.socket, int):
		""" Create the active socket
		:return: the active socket and the version
		"""
		# Create the socket
		if random.random() <= 0.5:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			version = 4
		else:
			sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			version = 6

		return sock, version

	def __connect(self, ip4_peer: str, ip6_peer: str, port_peer: int, packet: str) -> socket.socket:
		""" Send the packet to the specified host
		:param ip4_peer: host's ipv4 address
		:param ip6_peer: host's ipv6 address
		:param port_peer: host's port
		:param packet: packet to be sent
		:return: sock: the socket which will receive the response
		"""
		sock, version = self.__create_socket()

		if version == 4:
			sock.connect((ip4_peer, port_peer))
		else:
			sock.connect((ip6_peer, port_peer))

		sock.send(packet.encode())

		return sock

	def start(self) -> None:
		""" Start file download

		:return: None
		"""

		try:
			sock = self.__connect(self.host_ip4, self.host_ip6, self.host_port, self.packet)
		except socket.error as e:
			shell_colors.print_red(f'\nImpossible to send data to {self.host_ip4}|{self.host_ip6} [{self.host_port}]: {e}\n')
			return

		ack = sock.recv(4).decode()
		if ack != "ARET":
			shell_colors.print_red(f'\nInvalid command received: {ack}. Expected: ARET\n')
			sock.close()
			return

		total_chunks = int(sock.recv(6).decode())
		shell_colors.print_blue(f'\n#chunk: {total_chunks}')

		try:
			f_obj = open('shared/' + self.file_name, 'wb')
		except OSError as e:
			shell_colors.print_red(f'\nSomething went wrong: {e}\n')
			raise e

		progress_bar.print_progress_bar(0, total_chunks, prefix='Downloading:', suffix='Complete', length=50)
		for i in range(total_chunks):
			chunk_size = sock.recv(5)
			# if not all the 5 expected bytes has been received
			while len(chunk_size) < 5:
				chunk_size += sock.recv(1)
			chunk_size = int(chunk_size)

			data = sock.recv(chunk_size)
			# if not all the expected bytes has been received
			while len(data) < chunk_size:
				data += sock.recv(1)
			f_obj.write(data)
			progress_bar.print_progress_bar(i + 1, total_chunks, prefix='Downloading:', suffix='Complete', length=50)

		f_obj.close()
