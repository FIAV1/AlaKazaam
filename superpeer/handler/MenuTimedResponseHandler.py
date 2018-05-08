#!/usr/bin/env python

import socket
from utils import net_utils, shell_colors as shell
from common.HandlerInterface import HandlerInterface
from superpeer.LocalData import LocalData


class MenuTimedResponseHandler(HandlerInterface):

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
				shell.print_red(f"Invalid response: : {command} -> {response}. Expected: AQUE<pkt_id><ip_peer><port_peer><file_md5><filename>")
				return

			pktid = response[4:20]
			ip_peer = response[20:75]
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_peer)
			port_peer = int(response[75:80])
			file_md5 = response[80:112]
			filename = response[112:212].lstrip().rstrip()

			if pktid != LocalData.get_sent_menu_quer_packet():
				return

			if not LocalData.exist_menu_peer_file(ip4_peer, ip6_peer, port_peer, file_md5, filename):
				LocalData.add_menu_peer_file(ip4_peer, ip6_peer, port_peer, file_md5, filename)
				index = LocalData.menu_peer_file_index(ip4_peer, ip6_peer, port_peer, file_md5, filename)
				print(f'{index +1}] ', end='')
				print(f'{filename} ', end='')
				shell.print_yellow(f'md5={file_md5} ', end='')
				print(f'({ip4_peer}|{ip6_peer} [{port_peer}])')

		elif command == "ASUP":

			if len(response) != 80:
				shell.print_red(f"Invalid response: : {command} -> {response}. Expected: ASUP<pkt_id><ip_peer><port_peer>")
				return

			pktid = response[4:20]
			ip_peer = response[20:75]
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_peer)
			port_peer = int(response[75:80])

			if pktid != LocalData.get_sent_supe_packet():
				return

			if not LocalData.is_super_friend(ip4_peer, ip6_peer, port_peer):
				LocalData.add_super_friend(ip4_peer, ip6_peer, port_peer)
				shell.print_green('New superfriend found: ', end='')
				print(f'{ip4_peer}|{ip6_peer} [{port_peer}]')

		else:
			shell.print_red(f"\nInvalid response: {command} -> {response}\n")

		return
