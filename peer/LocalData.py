#!/usr/bin/env python
import json


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	json_file = 'peer/data.json'

	session_id = str()

	# ('ipv4', 'ipv6', 'port')
	superpeer = tuple(json.load(open('peer/data.json'))["superpeer"])

	# 'pktid'
	sent_packet = str()

	# 'pktid'
	received_packets = list()

	# ('ipv4', 'ipv6', 'port')
	superpeer_candidates = list()

	# friend management ------------------------------------------------------------
	@classmethod
	def get_superpeer(cls) -> tuple:
		return cls.superpeer

	@classmethod
	def set_superpeer(cls, superpeer: tuple) -> None:
		data = json.load(open(cls.json_file))
		data["superpeer"] = superpeer
		json.dump(data, open('peer/data.json', 'w'))
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

	@classmethod
	def superpeer_is_empty(cls) -> bool:
		if len(cls.superpeer) > 0:
			return False
		else:
			return True
	# -----------------------------------------------------------------------------

	# superpeer_candidates management ---------------------------------------------
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

	# query management-------------------------------------------------------------
	@classmethod
	def get_shared_files(cls) -> list:
		return json.load(open(cls.json_file))["files"]

	@classmethod
	def get_shared_file_md5(cls, file: tuple) -> str:
		return file[0]

	@classmethod
	def get_shared_file_name(cls, file: tuple) -> str:
		return file[1]

	@classmethod
	def add_shared_file(cls, file_md5: str, file_name: str) -> None:
		data = json.load(open(cls.json_file))
		data["files"].append((file_md5, file_name))
		json.dump(data, open("peer/data.json", "w"))

	@classmethod
	def is_shared_file(cls, file: tuple) -> bool:
		data = json.load(open(cls.json_file))
		if data["files"].count(file) > 0:
			return True
		return False

	@classmethod
	def get_shared_file(cls, index: int) -> tuple:
		data = json.load(open(cls.json_file))
		return data["files"][index]

	@classmethod
	def remove_shared_file(cls, file: tuple) -> None:
		data = json.load(open(cls.json_file))
		data["files"].remove(list(file))
		json.dump(data, open("peer/data.json", "w"))

	@classmethod
	def clear_shared_files(cls) -> None:
		data = {"files": [], "superpeer": []}
		json.dump(data, open("peer/data.json", "w"))
	# ------------------------------------------------------------------------------

	#  received packets management --------------------------------------------------
	@classmethod
	def add_received_packet(cls, pktid: str) -> None:
		cls.received_packets.append(pktid)

	@classmethod
	def delete_received_packet(cls, pktid: str) -> None:
		cls.received_packets.remove(pktid)

	@classmethod
	def exist_in_received_packets(cls, pktid: str) -> bool:
		return pktid in cls.received_packets
	# -----------------------------------------------------------------------------
