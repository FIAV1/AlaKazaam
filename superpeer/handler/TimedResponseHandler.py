#!/usr/bin/env python

import socket
from utils import net_utils, shell_colors as shell
from common.HandlerInterface import HandlerInterface
from superpeer.LocalData import LocalData


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

		if command == "AQUE":
			try:
				response = sd.recv(300).decode()
			except socket.error as e:
				shell.print_red(f'Unable to read the {command} response from the socket: {e}\n')
				sd.close()
				return
			sd.close()

			if len(response) != 212:
				shell.print_red(f"Invalid response: : {command} -> {response}. Expected: AQUE<pkt_id><ip_peer><port_peer><file_md5><filename>")
				return

			pktid = response[0:16]
			ip_peer = response[16:71]
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_peer)
			port_peer = int(response[71:76])
			file_md5 = response[76:108]
			filename = response[108:208]

			if pktid != LocalData.get_sent_packet():
				return

			if not LocalData.exist_peer_files(ip4_peer, ip6_peer, port_peer, file_md5, filename):
				LocalData.add_peer_files(ip4_peer, ip6_peer, port_peer, file_md5, filename)

		elif command == "ASUP":
			try:
				response = sd.recv(300).decode()
			except socket.error as e:
				shell.print_red(f'Unable to read the {command} response from the socket: {e}\n')
				sd.close()
				return
			sd.close()

			if len(response) != 76:
				shell.print_red(f"Invalid response: : {command} -> {response}. Expected: ASUP<pkt_id><ip_peer><port_peer>")
				return

			pktid = response[0:16]
			ip_peer = response[16:71]
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_peer)
			port_peer = int(response[71:76])

			if pktid != LocalData.get_sent_packet():
				return

			if not LocalData.is_super_friend(ip4_peer, ip6_peer, port_peer):
				LocalData.add_super_friend(ip4_peer, ip6_peer, port_peer)
				shell.print_green('New superfriend found: ', end='')
				print(f'{ip4_peer}|{ip6_peer} [{port_peer}]')

		else:
			wrong_response = sd.recv(300).decode()
			sd.close()
			shell.print_red(f"\nInvalid response: {command} -> {wrong_response}\n")

		return
