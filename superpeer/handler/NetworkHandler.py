#!/usr/bin/env python

import socket
from common.HandlerInterface import HandlerInterface
from superpeer.LocalData import LocalData
from utils import Logger, net_utils
import ipaddress


class NetworkHandler(HandlerInterface):

	def __init__(self, log: Logger.Logger):
		self.log = log

	def __delete_packet(self, pktid: str) -> None:
		""" Delete a packet received from the net

		:param pktid: id of the packet
		:return: None
		"""
		if LocalData.exist_in_received_packets(pktid):
			LocalData.delete_received_packet(pktid)

	def forward_packet(self, ip_sender: str, ip_source: str, ttl: str, packet: str) -> None:
		""" Forward a packet in the net to neighbours

		:param ip_sender: ip address of sender host
		:param ttl: packet time to live
		:param packet: string representing the packet
		:return: None
		"""
		new_ttl = int(ttl) - 1

		if new_ttl > 0:
			ip4_peer, ip6_peer = net_utils.get_ip_pair(ip_source)

			# get the recipients list without the peer who sent the packet
			recipients = LocalData.get_friends_recipients(ip_sender, ip4_peer, ip6_peer)

			packet = packet[:80] + str(new_ttl).zfill(2) + packet[82:]

			for peer in recipients:
				ip4 = LocalData.get_friend_ip4(peer)
				ip6 = LocalData.get_friend_ip6(peer)
				port = LocalData.get_friend_port(peer)
				try:
					net_utils.send_packet_and_close(ip4, ip6, port, packet)
				except socket.error as e:
					pass

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
			pass

		elif command == "LOGI":
			pass

		elif command == "ADDF":
			pass

		elif command == "DELF":
			pass

		elif command == "FIND":
			pass

		elif command == "LOGO":
			pass

		elif command == "QUER":
			pass

		else:
			self.log.write_red('Invalid packet. Unable to reply.')
			sd.close()

		return
