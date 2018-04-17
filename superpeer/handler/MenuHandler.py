#!/usr/bin/env python

from utils import net_utils, shell_colors as shell
import uuid
from superpeer.LocalData import LocalData
from common.ServerThread import ServerThread
from superpeer.handler.TimedResponseHandler import TimedResponseHandler
from utils.SpinnerThread import SpinnerThread
from threading import Timer

class MenuHandler:

	def __broadcast(self, packet: str) -> None:
		""" Send the packet to a pool of hosts

		:param packet: packet to be sent
		:return: None
		"""
		superfriends = LocalData.get_super_friends()

		for superfriend in superfriends:
			net_utils.send_packet_and_close(
				LocalData.get_super_friend_ip4(superfriend),
				LocalData.get_super_friend_ip6(superfriend),
				LocalData.get_super_friend_port(superfriend),
				packet)

	def serve(self, choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""

		if choice == "SUPE":
			# SUPE[4B].Packet_Id[16B].IP_Peer[55B].Port_Peer[5B].TTL[2B]
			pktid = str(uuid.uuid4().hex[:16].upper())
			ip = net_utils.get_local_ip_for_response()
			port = net_utils.get_asup_port()
			ttl = '04'

			packet = choice + pktid + ip + str(port).zfill(5) + ttl
			LocalData.set_sent_packet(pktid)

			old_superfriends_len = len(LocalData.get_super_friends())

			server = ServerThread(port, TimedResponseHandler())
			server.daemon = True
			server.start()

			spinner = SpinnerThread('Searching peers (ENTER to continue)', 'Research done!')
			spinner.start()

			timer = Timer(300, lambda: (spinner.stop(), server.stop()))
			timer.start()

			self.__broadcast(packet)
			input()

			print('\033[1A', end='\r')

			if timer.is_alive():
				spinner.stop()
				spinner.join()
				timer.cancel()
				timer.join()
				server.stop()
				server.join()
			else:
				spinner.join()
				timer.join()
				server.join()

			if len(LocalData.get_super_friends()) == old_superfriends_len:
				shell.print_red('\nNo new superpeer found.\n')

		elif choice == "ADFF":
			pass

		elif choice == "DEFF":
			pass

		elif choice == "QUER":
			pass

		elif choice == "LISTPEERS":
			pass

		elif choice == "LISTFILES":
			pass

		else:
			pass
