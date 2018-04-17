#!/usr/bin/env python
from utils import hasher, net_utils
from peer.LocalData import LocalData
from utils import shell_colors as shell
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
			for file in os.scandir('shared'):
				file_md5 = hasher.get_md5(f'shared/{file.name}')
				# verifica se il file è gia presente nella struttura dati
				present = LocalData.is_shared_file(file_md5)

				if not present:
					# aggiunge il file alla struttura dati se non già presente
					LocalData.add_shared_file(file_md5, file.name)
					shell.print_blue(f'\nNew shared file added {file.name} | {file_md5}')

					# crea il pacchetto e lo invia al super peer
					packet = choice + p_ssid + file_md5 + file.name.ljust(100)
					# TODO: verifica se send_packet_and_close necessita di try-except
					net_utils.send_packet_and_close(sp_ip4, sp_ip6, sp_port, packet)
					shell.print_green(f'Packet sent to supernode: {sp_ip4}|{sp_ip6} [{sp_port}]')
				# TODO verificare se necessario aggiungere i file contenuti in shared allo startup del peer

		elif choice == "DEFF":
			# scelta del file da rimuovere
			shell.print_blue('File currently in sharing:')
			for count, file in enumerate(LocalData.get_shared_files(), start=1):
				print(f'{count}] {LocalData.get_shared_file_name(file)} | {LocalData.get_shared_file_md5(file)}')
			index = input('Choose a file to remove from sharing (q to cancel): ')

			if index == "q":
				print('\n')
				return

			# recupera i files in sharing
			files = LocalData.get_shared_files()

			while True:
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
					# TODO: verifica se send_packet_and_close necessita di try-except
					net_utils.send_packet_and_close(sp_ip4, sp_ip6, sp_port, packet)

					# rimuove il file dalla DS
					LocalData.remove_shared_file(file)

					shell.print_yellow(f'\n{LocalData.get_shared_file_name(file)} | {LocalData.get_shared_file_md5(file)} removed successfully.')
					break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected\n')
					continue

		elif choice == "FIND":
			pass

		elif choice == "SHOWSUPER":
			pass

		else:
			pass
