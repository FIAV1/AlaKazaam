#!/usr/bin/env python


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	session_id = str()

	# ('ipv4', 'ipv6', 'port')
	superpeer = tuple()

	# 'pktid'
	sent_packet = str()

	# 'pktid'
	received_packets = list()

	# ('ipv4', 'ipv6', 'port')
	superpeer_candidates = list()

	# friend management --------------------------------------------------------
	@classmethod
	def get_superpeer(cls) -> tuple:
		return cls.superpeer

	@classmethod
	def set_superpeer(cls, superpeer: tuple) -> None:
		cls.superpeer = superpeer

	@classmethod
	def get_superpeer_ip4(cls) -> str:
		return cls.superpeer[0]

	@classmethod
	def get_superpeer_ip6(cls) -> str:
		return cls.superpeer[1]

	@classmethod
	def get_superpeer_port(cls) -> int:
		return cls.superpeer[2]
	# -----------------------------------------------------------------------------

	# superpeer_candidates management --------------------------------------------------------
	@classmethod
	def get_superpeer_candidates(cls) -> list:
		return cls.superpeer_candidates

	@classmethod
	def add_superpeer_candidate(cls, ip4_peer: str, ip6_peer: str, port_peer: int) -> None:
		cls.superpeer_candidates.append((ip4_peer, ip6_peer, port_peer))

	@classmethod
	def get_superpeer_candidate_by_index(cls, index: int) -> tuple:
		return cls.superpeer_candidates.pop(index)
	# -----------------------------------------------------------------------------

	# query management-------------------------------------------------------------
	@classmethod
	def set_sent_packet(cls, pktid: str) -> None:
		cls.sent_packet = pktid

	@classmethod
	def get_sent_packet(cls) -> str:
		return cls.sent_packet
	# -----------------------------------------------------------------------------

	# received packets management --------------------------------------------------
	@classmethod
	def add_received_packet(cls, pktid: str) -> None:
		cls.received_packets = pktid

	@classmethod
	def delete_received_packet(cls, pktid: str) -> None:
		cls.received_packets.remove(pktid)

	@classmethod
	def exist_in_received_packets(cls, pktid: str) -> bool:
		return pktid in cls.received_packets
	# -----------------------------------------------------------------------------
