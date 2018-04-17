#!/usr/bin/env python
from utils import hasher, net_utils
from peer.LocalData import LocalData
from utils import shell_colors as shell
from utils.Downloader import Downloader
import os


class MenuHandler:

	def serve(self, choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""
		sp_ip4 = LocalData.get_superpeer_ip4()
		sp_ip6 = LocalData.get_superpeer_ip6()
		sp_port = LocalData.get_superpeer_port()
		p_ssid = LocalData.session_id

		if choice == "ADFF":
			shell.print_blue('\nFiles available for sharing:')
			for count, file in enumerate(os.scandir('shared')):
				file_md5 = hasher.get_md5(f'shared/{file.name}')
				print(f'{count}] {file.name} | {file_md5}')
			index = input('Choose a file to share (q to cancel): ')

			if index == "q":
				print('\n')
				return

			files = LocalData.get_shared_files()

			while True:
				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected\n')
					continue

				if 0 <= index <= len(files)-1:
					file_name = LocalData.get_shared_file_name(files[index])
					file_md5 = LocalData.get_shared_file_md5(files[index])

					# controlla se il file è già in condivisione
					if not LocalData.is_shared_file(files[index]):

						# crea il pacchetto e lo invia al super peer
						packet = choice + p_ssid + file_md5 + file_name.ljust(100)
						try:
							net_utils.send_packet_and_close(sp_ip4, sp_ip6, sp_port, packet)
							shell.print_green(f'Packet sent to supernode: {sp_ip4}|{sp_ip6} [{sp_port}]')
						except net_utils.socket.error:
							shell.print_red(f'\nError while sending packet to supernode: {sp_ip4}|{sp_ip6} [{sp_port}]\n')

						# aggiunge il file alla struttura dati ed esce
						LocalData.add_shared_file(file_md5, file_name)
						shell.print_blue(f'\nNew shared file added {file.name} | {file_md5}')
						break
					else:
						# il file è già in condivisione
						shell.print_yellow(f'\n{file_name} | {file_md5} already in sharing.\n')
						break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected\n')
					continue

		elif choice == "DEFF":
			# scelta del file da rimuovere
			shell.print_blue('File currently in sharing:')
			for count, file in enumerate(LocalData.get_shared_files(), start=1):
				print(f'{count}] {LocalData.get_shared_file_name(file)} | {LocalData.get_shared_file_md5(file)}')

			while True:
				index = input('Choose a file to remove from sharing (q to cancel): ')

				if index == "q":
					print('\n')
					return

				# recupera i files in sharing
				files = LocalData.get_shared_files()

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected\n')
					continue

				if 0 <= index <= len(files)-1:
					# recupera il file dalla DS
					file = LocalData.find_shared_file(index)

					# crea ed invia il pacchetto al supernode
					packet = choice + p_ssid + LocalData.get_shared_file_md5(file)
					try:
						net_utils.send_packet_and_close(sp_ip4, sp_ip6, sp_port, packet)
					except net_utils.socket.error:
						shell.print_red(f'\nError while sending packet to supernode: {sp_ip4}|{sp_ip6} [{sp_port}]\n')

					# rimuove il file dalla DS
					LocalData.remove_shared_file(file)

					shell.print_green(f'\n{LocalData.get_shared_file_name(file)} | {LocalData.get_shared_file_md5(file)} removed successfully.')
					break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected\n')
					continue

		elif choice == "FIND":
			while True:
				search = input('\nInsert file\'s name (q to cancel): ')

				if search == "q":
					print('\n')
					return

				if not 0 < len(search) <= 20:
					shell.print_red('\nQuery string must be a valid value (0 - 20 chars).')
					continue

				break

			packet = choice + p_ssid + search.ljust(20)

			try:
				socket = net_utils.send_packet(sp_ip4, sp_ip6, sp_port, packet)
				socket.settimeout(25)

			except net_utils.socket.error:
				shell.print_red(f'\n{search} not found.\n')
				return

			try:
				command = socket.recv(4).decode()
				if command != "AFIN":
					shell.print_red(f'\nReceived a packet with a wrong command ({command}).\n')
					return

			except net_utils.socket.error:
				shell.print_red(f'\nError while receiving the response from the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}]\n')
			except ValueError:
				shell.print_red(f'\nInvalid packet from superpeer: {sp_ip4}|{sp_ip6} [{sp_port}]\n')

			downloadables = []
			num_downloadables = int(socket.recv(3))
			for i in range(num_downloadables):
				try:
					file_md5 = socket.recv(32).decode()
					file_name = socket.recv(100).decode()
					num_copies = int(socket.recv(3))
				except net_utils.socket.error:
					shell.print_red(f'\nError while receiving the response from the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}]\n')
					continue
				except ValueError:
					shell.print_red(f'\nInvalid packet from superpeer: {sp_ip4}|{sp_ip6} [{sp_port}]\n')
					continue
				for j in range(num_copies):
					try:
						(source_ip4, source_ip6) = net_utils.get_ip_pair(socket.recv(55).decode())
						source_port = int(socket.recv(5))
					except net_utils.socket.error:
						shell.print_red(f'\nError while receiving the response from the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}]\n')
						continue
					except ValueError:
						shell.print_red(f'\nInvalid packet from superpeer: {sp_ip4}|{sp_ip6} [{sp_port}]\n')
						continue
					downloadables.append((file_name, file_md5, source_ip4, source_ip6, source_port))

			shell.print_blue(f'\nFiles found:')
			for count, downloadable in enumerate(downloadables, start=1):
				print(f'{count}]', end='')
				shell.print_blue(f'{downloadable[0]}|{downloadable[1]}', end='')
				print(' <=> ', end='')
				shell.print_yellow(f'{sp_ip4}|{sp_ip6} [{sp_port}]')

			while True:
				index_d = input('Choose a file to download (q to cancel): ')

				if index_d == "q":
					print('\n')
					return

				try:
					index_d = int(index_d) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(downloadables)} expected\n')
					continue

				if 0 <= index_d <= len(downloadables) - 1:
					packet = "RETR" + downloadables[index_d][1]
					try:
						Downloader(downloadables[index_d][2], downloadables[index_d][3], downloadables[index_d][4], packet, downloadables[index_d][0])
						shell.print_green(f'\nDownload di {downloadables[index_d][0]} completato con successo.\n')
					except OSError:
						shell.print_red(f'\nError while downloading {downloadables[index_d][0]}.\n')
					break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(downloadables)} expected\n')
					continue

		elif choice == "SHOWSUPER":
			print(f'\nYour current superpeer is: {sp_ip4}|{sp_ip6} [{sp_port}]\n')

		elif choice == "LOGO":
			packet = choice + p_ssid
			sock = net_utils.send_packet(sp_ip4, sp_ip6, sp_port, packet)

			try:
				command = sock.recv(4).decode()
				if command != "LOGO":
					shell.print_red(f'\nWrong response code "{command}": "{choice}" expected.\n')

				num_files = int(sock.recv(3))
				shell.print_blue(f'\n{num_files} files has been removed from sharing.\n')
			except net_utils.socket.error:
				shell.print_red(f'\nError while receiving the response for "{choice}".\n')

			LocalData.clear_shared_files()

		else:
			pass
