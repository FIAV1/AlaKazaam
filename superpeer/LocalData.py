#!/usr/bin/env python

import re


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	# ('ipv4', 'ipv6', 'port')
	super_friends = list()

	# {'pktid' : (ip, port)}
	received_packets = dict()

	# 'pktid'
	sent_supe_packet = str()

	# 'pktid'
	sent_quer_packet = str()

	# {'md5' : ('name', 'ipv4', 'ipv6', 'port')}
	peer_files = dict()

	# ('filename', 'md5', 'dim')
	shared_files = list()

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

# sent packet management-------------------------------------------------------------
	@classmethod
	def set_sent_supe_packet(cls, pktid: str) -> None:
		cls.sent_supe_packet = pktid

	@classmethod
	def get_sent_supe_packet(cls) -> str:
		return cls.sent_supe_packet

	@classmethod
	def set_sent_quer_packet(cls, pktid: str) -> None:
		cls.sent_quer_packet = pktid

	@classmethod
	def get_sent_quer_packet(cls) -> str:
		return cls.sent_quer_packet
# -----------------------------------------------------------------------------

# peer_files management--------------------------------------------------------
	@classmethod
	def get_peer_files(cls) -> dict:
		return cls.peer_files

	@classmethod
	def add_peer_files(cls, ip4_peer: str, ip6_peer: str, port_peer: int, filemd5: str, filename: str) -> None:
		if filemd5 in cls.peer_files.keys():
			cls.peer_files[filemd5].append((filename, ip4_peer, ip6_peer, port_peer))
		else:
			cls.peer_files[filemd5] = list()
			cls.peer_files[filemd5].append((filename, ip4_peer, ip6_peer, port_peer))

	@classmethod
	def exist_peer_files(cls, ip4_peer: str, ip6_peer: str, port_peer: int, filemd5: str, filename: str) -> bool:
		if filemd5 in cls.peer_files.keys():
			return (filename, ip4_peer, ip6_peer, port_peer) in cls.peer_files[filemd5]
		return False

	@classmethod
	def get_peer_files_md5_amount(cls) -> int:
		return len(cls.peer_files.keys())

	@classmethod
	def get_peer_file_copy_amount_by_md5(cls, filemd5: str) -> int:
		if filemd5 in cls.peer_files.keys():
			return len(cls.peer_files[filemd5])
		return 0

	@classmethod
	def get_peer_file_name_by_md5(cls, filemd5: str) -> int:
		return cls.peer_files[filemd5][0][0]

	@classmethod
	def get_peer_files_list_by_md5(cls, filemd5: str) -> list:
		if filemd5 in cls.peer_files.keys():
			return cls.peer_files[filemd5]
		return list()

	@classmethod
	def get_peer_file_name(cls, file_tuple: tuple) -> str:
		return file_tuple[0]

	@classmethod
	def get_peer_file_owner_ipv4(cls, file_tuple: tuple) -> str:
		return file_tuple[1]

	@classmethod
	def get_peer_file_owner_ipv6(cls, file_tuple: tuple) -> str:
		return file_tuple[2]

	@classmethod
	def get_peer_file_owner_port(cls, file_tuple: tuple) -> str:
		return file_tuple[3]

	@classmethod
	def clear_peer_files(cls) -> None:
		cls.peer_files.clear()
# -----------------------------------------------------------------------------

# shared files management -----------------------------------------------------
	@classmethod
	def get_shared_files(cls) -> list:
		return cls.shared_files

	@classmethod
	def add_shared_file(cls, filename: str, file_md5: str, file_size: int) -> None:
		cls.shared_files.append((filename.lower(), file_md5, file_size))

	@classmethod
	def exist_shared_file(cls, filename: str, file_md5: str, file_size: int) -> bool:
		return (filename, file_md5, file_size) in cls.shared_files

	@classmethod
	def search_in_shared_files(cls, query_name: str) -> list:
		results = list()
		for file in cls.shared_files:
			if re.search(query_name, file[0]):
				results.append(file)
		return results

	@classmethod
	def get_shared_filename_by_filemd5(cls, file_md5: str) -> str:
		for file in cls.shared_files:
			if file[1] == file_md5:
				return file[0]

	@classmethod
	def get_shared_filename(cls, file: tuple) -> str:
		return file[0]

	@classmethod
	def get_shared_filemd5(cls, file: tuple) -> str:
		return file[1]

	@classmethod
	def get_shared_dim(cls, file: tuple) -> int:
		return int(file[2])

	@classmethod
	def clear_shared_files(cls) -> None:
		cls.shared_files.clear()

	@classmethod
	def get_shared_file_by_index(cls, index: int) -> tuple:
		return cls.shared_files.pop(index)
# -----------------------------------------------------------------------------
