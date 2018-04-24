#!/usr/bin/env python
from utils import hasher, net_utils
from peer.LocalData import LocalData
from utils import shell_colors as shell
from utils.Downloader import Downloader
import os


class MenuHandler:

	@staticmethod
	def serve(choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""
		sp_ip4 = LocalData.get_superpeer_ip4()
		sp_ip6 = LocalData.get_superpeer_ip6()
		sp_port = LocalData.get_superpeer_port()
		p_ssid = LocalData.session_id

		if choice == "ADFF":
			# check se shared dir esiste
			if not os.path.exists('shared'):
				shell.print_red('\nCannot find the shared folder.')
				return

			# se non ci sono file nella shared dir avvisa ed esce
			if not os.scandir('shared'):
				shell.print_yellow('No file available for sharing. Add files to shared dir to get started.\n')
				return

			temp_files = []
			shell.print_blue('\nFiles available for sharing:')
			for count, file in enumerate(os.scandir('shared'), 1):
				# stampa i risultati della scandir
				file_md5 = hasher.get_md5(f'shared/{file.name}')
				print(f'{count}] {file.name} | {file_md5}')
				temp_files.append((file.name, file_md5))

			while True:
				index = input('Choose a file to share (q to cancel): ')

				if index == "q":
					print('\n')
					return

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(temp_files)} expected\n')
					continue

				if 0 <= index <= len(temp_files)-1:
					file_name = LocalData.get_shared_file_name(temp_files[index])
					file_md5 = LocalData.get_shared_file_md5(temp_files[index])

					# controlla se il file è già in condivisione
					if not LocalData.is_shared_file(temp_files[index]):

						# crea il pacchetto e lo invia al super peer
						packet = choice + p_ssid + file_md5 + file_name.ljust(100)
						try:
							net_utils.send_packet_and_close(sp_ip4, sp_ip6, sp_port, packet)
							shell.print_green(f'Packet sent to supernode: {sp_ip4}|{sp_ip6} [{sp_port}]')
						except net_utils.socket.error:
							shell.print_red(f'\nError while sending packet to supernode: {sp_ip4}|{sp_ip6} [{sp_port}]\n')

						# aggiunge il file alla struttura dati ed esce
						LocalData.add_shared_file(file_md5, file_name)
						shell.print_blue(f'\nNew shared file added {file_name} | {file_md5}')
						break
					else:
						# il file è già in condivisione
						shell.print_yellow(f'\n{file_name} | {file_md5} already in sharing.\n')
						break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(temp_files)} expected\n')
					continue

		elif choice == "DEFF":
			# recupera i files in sharing
			files = LocalData.get_shared_files()

			# check se ci sono file in sharing
			if not files:
				shell.print_yellow('No files currently in sharing. Add files choosing the command from the menu.\n')
				return

			# scelta del file da rimuovere
			shell.print_blue('\nFile currently in sharing:')
			for count, file in enumerate(files, 1):
				print(f'{count}] {LocalData.get_shared_file_name(file)} | {LocalData.get_shared_file_md5(file)}')

			while True:
				index = input('Choose a file to remove from sharing (q to cancel): ')

				if index == "q":
					print('\n')
					return

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected\n')
					continue

				if 0 <= index <= len(files)-1:
					# recupera il file dalla DS
					file = LocalData.get_shared_file(index)

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
					shell.print_red('\nQuery string must be a valid value (1 - 20 chars).')
					continue

				break

			packet = choice + p_ssid + search.ljust(20)

			try:
				socket = net_utils.send_packet(sp_ip4, sp_ip6, sp_port, packet)

			except net_utils.socket.error:
				shell.print_red(f'\nError while sending the request to the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
				return

			try:
				socket.settimeout(25)
				command = socket.recv(4).decode()
				if command != "AFIN":
					shell.print_red(f'\nReceived a packet with a wrong command ({command}).\n')
					return

			# TODO: da rimuovere dopo i test (?)
			except net_utils.socket.error:
				shell.print_red(f'\nError while receiving the response from the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
				return
			except ValueError:
				shell.print_red(f'\nInvalid packet from superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
				return

			# ('file_name', 'file_md5', sources[])
			downloadables = list()

			try:
				num_downloadables = int(socket.recv(3))

				# check se ci sono file da scaricare
				if num_downloadables == 0:
					shell.print_yellow(f'{search} not found.\n')
					return
			# TODO: da rimuovere dopo i test (?)
			except net_utils.socket.error:
				shell.print_red(f'\nError while receiving the response from the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
				return

			for i in range(num_downloadables):
				# ('owner_ip4', 'owner_ip6', 'owner_port')
				sources = list()

				try:
					file_md5 = socket.recv(32).decode()
					file_name = socket.recv(100).decode()
					num_copies = int(socket.recv(3))
				# TODO: da rimuovere dopo i test (?)
				except net_utils.socket.error:
					shell.print_red(f'\nError while receiving the response from the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
					continue
				except ValueError:
					shell.print_red(f'\nInvalid packet from superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
					continue

				for j in range(num_copies):
					try:
						(source_ip4, source_ip6) = net_utils.get_ip_pair(socket.recv(55).decode())
						source_port = int(socket.recv(5))
						sources.append((source_ip4, source_ip6, source_port))
					# TODO: da rimuovere dopo i test (?)
					except net_utils.socket.error:
						shell.print_red(f'\nError while receiving the response from the superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
						continue
					except ValueError:
						shell.print_red(f'\nInvalid packet from superpeer: {sp_ip4}|{sp_ip6} [{sp_port}].\n')
						continue
				if sources:
					# prepara una lista con tutti i file che possono essere scaricati
					downloadables.append((file_name, file_md5, sources))

			if not downloadables:
				shell.print_red(f'\nSomething went wrong while retrieving {search}\n')
				return

			shell.print_green(f'\nFiles found:')
			for count, downloadable in enumerate(downloadables, 1):
				print(f'{count}] {downloadable[0]} | {downloadable[1]}')

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

				if not 0 <= index_d <= len(downloadables) - 1:
					shell.print_red(f'\nWrong index: number in range 1 - {len(downloadables)} expected\n')
					continue
				else:
					available_file_name = downloadables[index_d][0]
					available_file_md5 = downloadables[index_d][1]
					availables = downloadables[index_d][2]

					shell.print_green(f'\nAvailable sources for {available_file_name}:')
					for count, available in enumerate(availables, 1):
						print(f'{count}] {available[0]}|{available[1]} [{available[2]}]')

					while True:
						index_a = input(f'Choose a source for {available_file_name} (q to cancel): ')

						if index_a == "q":
							print('\n')
							return

						try:
							index_a = int(index_a) - 1
						except ValueError:
							shell.print_red(f'\nWrong index: number in range 1 - {len(availables)} expected\n')
							continue

						if 0 <= index_a <= len(availables) - 1:
							packet = "RETR" + available_file_md5
							try:
								Downloader(availables[index_a][0], availables[index_a][1], availables[index_a][2], packet, available_file_name)
								shell.print_green(f'\n{available_file_name} downloaded successfully.\n')
							except OSError:
								shell.print_red(f'\nError while downloading {available_file_name}.\n')
							break
						else:
							shell.print_red(f'\nWrong index: number in range 1 - {len(availables)} expected\n')
							continue
					break

		elif choice == "SHOWSUPER":
			print(f'\nYour current superpeer is: {sp_ip4}|{sp_ip6} [{sp_port}]\n')

		elif choice == "LOGO":
			packet = choice + p_ssid
			sock = net_utils.send_packet(sp_ip4, sp_ip6, sp_port, packet)

			try:
				command = sock.recv(4).decode()
				if command != "ALGO":
					shell.print_red(f'\nWrong response code "{command}": "{choice}" expected.\n')

				num_files = int(sock.recv(3))
				shell.print_blue(f'\n{num_files} files has been removed from sharing.\n')
			except net_utils.socket.error:
				shell.print_red(f'\nError while receiving the response for "{choice}".\n')

			LocalData.clear_shared_files()

		else:
			pass
