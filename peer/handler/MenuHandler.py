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

		if choice == "ADFF":
			# scansiona la dir shared per trovare tutti i file
			shell.print_blue('\nFiles in shared:')
			for file, count in enumerate(os.scandir('shared'), start=1):
				# aggiunge i file alla struttura dati
				file_md5 = hasher.get_md5(f'shared/{file.name}')
				LocalData.add_file(file_md5, file.name)
				# stampa i risultati
				print(f'{count}] {file.name} | {file_md5}')

			files = LocalData.get_files()

			while True:
				index = input('\nChoose the file to be added: ')
				try:
					index = int(index)
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected.\n')
					continue

				if 1 < index < len(files):
					# invia il pacchetto al supernodo ed esce dal ciclo
					packet = choice + LocalData.session_id + LocalData.get_file_md5(files[index]) + LocalData.get_file_name(files[index]).ljust(100)
					net_utils.send_packet_and_close(LocalData.get_superpeer_ip4(), LocalData.get_superpeer_ip6(), LocalData.get_superpeer_port(), packet)
					shell.print_green(f'\nPacket sent to Supernode {LocalData.get_superpeer_ip4()}|{LocalData.get_superpeer_ip6()} [{LocalData.get_superpeer_port()}]\n')
					break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(files)} expected.\n')
					continue

		elif choice == "DEFF":
			pass

		elif choice == "FIND":
			pass

		elif choice == "SHOWSUPER":
			pass

		else:
			pass
