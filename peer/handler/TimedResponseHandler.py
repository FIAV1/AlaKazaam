#!/usr/bin/env python

import socket
from utils import net_utils, shell_colors as shell
from common.HandlerInterface import HandlerInterface
from peer.LocalData import LocalData


class TimedResponseHandler(HandlerInterface):

	def serve(self, sd: socket.socket) -> None:
		""" Handle the peer request

		:param sd: the socket descriptor used for read the request
		:return None
		"""
		try:
			command = sd.recv(4).decode()
		except OSError as e:
			shell.print_red(f'\nUnable to read the command from the socket: {e}\n')
			sd.close()
			return

		try:
			response = sd.recv(300).decode()
		except socket.error as e:
			shell.print_red(f'Unable to read the response from the socket: {e}\n')
			shell.print_red(f"\nInvalid response: {command} -> {response}\n")
			sd.close()
			return
		sd.close()

		if command == "ASUP":

			if len(response) != 76:
				shell.print_red(f"Invalid response: : {command} -> {response}. Expected: ASUP<pkt_id><ip_peer><port_peer>")
				return

			pktid = response[0:16]
			ip_peer = response[16:71]
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_peer)
			port_peer = int(response[71:76])

			if pktid != LocalData.get_sent_packet():
				return

			LocalData.add_superpeer_candidate(ip4_peer, ip6_peer, port_peer)

		else:
			wrong_response = sd.recv(300).decode()
			sd.close()
			shell.print_red(f"\nInvalid response: {command} -> {wrong_response}\n")

		return
