#!/usr/bin/env python


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	# ('ipv4', 'ipv6', 'port')
	super_friends = list()

	# {'pktid' : (ip, port)}
	received_packets = dict()

	# 'pktid'
	sent_packet = str()

	# super_super_friends management --------------------------------------------------------
	@classmethod
	def is_super_friend(cls, ip4_peer: str, ip6_peer: str, port_peer: int) -> bool:
		return (ip4_peer, ip6_peer, port_peer) in cls.super_friends

	@classmethod
	def get_super_friends(cls) -> list:
		return cls.super_friends

	@classmethod
	def add_super_friend(cls, ip4_peer: str, ip6_peer: str, port_peer: int) -> None:
		cls.super_friends.append((ip4_peer, ip6_peer, port_peer))

	@classmethod
	def super_friend_index(cls, ip4_peer: str, ip6_peer: str, port_peer: int) -> int:
		return cls.super_friends.index((ip4_peer, ip6_peer, port_peer))

	@classmethod
	def get_super_friends_recipients(cls, ip_sender: str, ip4_source: str, ip6_source: str) -> list:
		recipients = cls.super_friends.copy()

		for peer in cls.super_friends:
			if ip_sender == peer[0] or ip_sender == peer[1]:
				recipients.remove(peer)

			elif ip4_source == peer[0] or ip6_source == peer[1]:
				recipients.remove(peer)

		return recipients

	@classmethod
	def get_super_friend_ip4(cls, peer: tuple) -> str:
		return peer[0]

	@classmethod
	def get_super_friend_ip6(cls, peer: tuple) -> str:
		return peer[1]

	@classmethod
	def get_super_friend_port(cls, peer: tuple) -> int:
		return peer[2]

	@classmethod
	def remove_super_friend(cls, super_friend_index: int) -> None:
		cls.super_friends.pop(super_friend_index)

	# -----------------------------------------------------------------------------

	# received packets management --------------------------------------------------
	@classmethod
	def add_received_packet(cls, pktid: str, ip_peer: str, port_peer: int) -> None:
		cls.received_packets[pktid] = (ip_peer, port_peer)

	@classmethod
	def delete_received_packet(cls, pktid: str) -> None:
		del cls.received_packets[pktid]

	@classmethod
	def exist_in_received_packets(cls, pktid: str) -> bool:
		return pktid in cls.received_packets
	# -----------------------------------------------------------------------------

	# query management-------------------------------------------------------------
	@classmethod
	def set_sent_packet(cls, pktid: str) -> None:
		cls.sent_packet = pktid

	@classmethod
	def get_sent_packet(cls) -> str:
		return cls.sent_packet
	# -----------------------------------------------------------------------------
