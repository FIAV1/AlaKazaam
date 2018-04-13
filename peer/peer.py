#!/usr/bin/env python

from utils import net_utils, Logger, shell_colors as shell
from .LocalData import LocalData
from common.ServerThread import ServerThread
from .handler import NetworkHandler, MenuHandler, TimedResponseHandler
from .Menu import Menu
import uuid
from threading import Timer
import random
import socket


def startup():

	while True:
		while True:
			shell.print_blue('\nThis process will allow you to add your known peer.\n')
			superpeer = net_utils.prompt_friend_request()
			LocalData.set_superpeer(superpeer)

			# 1) Lancia una SUPE al nodo conosciuto
			pktid = str(uuid.uuid4().hex[:16].upper())
			ip = net_utils.get_local_ip_for_response()
			port = str(net_utils.get_network_port())
			ttl = '04'
			packet = 'SUPE' + pktid + ip + port + ttl

			super_ip4 = LocalData.get_superpeer_ip4()
			super_ip6 = LocalData.get_superpeer_ip6()
			super_port = LocalData.get_superpeer_port()

			try:
				net_utils.send_packet_and_close(super_ip4, super_ip6, super_port, packet)
			except socket.error as e:
				shell.print_red(f'There was an error in the login process: {e}')
				continue

			# 2) Attende ASUP per 20 sec
			server = ServerThread(net_utils.get_network_port(), TimedResponseHandler.ResponseHandler())
			timer = Timer(20, lambda: server.stop())
			server.start()
			timer.start()
			server.join()

			# 3) Se non è possibile agganciarsi ad un super, devo far reinserire il peer all'utente
			if len(LocalData.get_superpeer_candidates()) == 0:
				shell.print_red('Cannot contact a superpeer from the peer you provide, please retry.')
				continue

			# 3) Se il peer aggiunto era veramente un superpeer, allora non lo cambio
			elif LocalData.get_superpeer() in LocalData.get_superpeer_candidates():
				break

			# 3) Se invece era un superpeer falzo, pesco un super a random dalla lista dei candidati
			else:
				index = random.randint(0, len(LocalData.get_superpeer_candidates()))
				superpeer = LocalData.get_superpeer_candidate_by_index(index)
				LocalData.set_superpeer(superpeer)
				break

		# Lancio una LOGI al superpeer scelto
		ip = net_utils.get_local_ip_for_response()
		port = str(net_utils.get_network_port())
		packet = "LOGI" + ip + port

		super_ip4 = LocalData.get_superpeer_ip4()
		super_ip6 = LocalData.get_superpeer_ip6()
		super_port = LocalData.get_superpeer_port()

		try:
			sock = net_utils.send_packet(super_ip4, super_ip6, super_port, packet)
			response = sock.recv(100).decode()

			if len(response) != 20:
				shell.print_red('There was an error in the login process: ', end='')
				print(f'unexpected: {response}', end='')
				shell.print_red('Please retry.')
				continue

			session_id = response[4:20]

			if session_id == '0' * 16:
				shell.print_red('There was an error in the login process: ', end='')
				print(f'unexpected session_id: {session_id}', end='')
				shell.print_red('Please retry.')
				continue

			LocalData.session_id = response[4:20]
			break
		except socket.error as e:
			shell.print_red(f'There was an error in the login process: {e}', end='')
			shell.print_red('Please retry.')
			sock.close()
			continue

	shell.print_green(f'Successfully logged to the superpeer: {super_ip4}|{super_ip6} [{super_port}]\n')

	log = Logger.Logger('peer.log')

	server = ServerThread(net_utils.get_network_port(), NetworkHandler.NetworkHandler(log))
	server.daemon = True
	server.start()

	Menu(MenuHandler.MenuHandler()).show()
