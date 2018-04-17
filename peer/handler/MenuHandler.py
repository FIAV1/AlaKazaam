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
			for file in os.scandir('shared'):
				file_md5 = hasher.get_md5(f'shared/{file.name}')
				# verifica se il file è gia presente nella struttura dati
				present = LocalData.is_shared_file(file_md5)

				if not present:
					# aggiunge il file alla struttura dati se non già presente
					LocalData.add_shared_file((file_md5, file.name))
					shell.print_blue(f'\nNew shared file added {file.name} | {file_md5}')

					# crea il pacchetto e lo invia al super peer
					packet = choice + LocalData.session_id + file_md5 + file.name.ljust(100)
					net_utils.send_packet_and_close(LocalData.get_superpeer_ip4(), LocalData.get_superpeer_ip6(), LocalData.get_superpeer_port(), packet)
					shell.print_green(f'Packet sent to Supernode {LocalData.get_superpeer_ip4()}|{LocalData.get_superpeer_ip6()} [{LocalData.get_superpeer_port()}]')
				# TODO verificare se necessario aggiungere i file contenuti in shared allo startup del peer

		elif choice == "DEFF":
			pass

		elif choice == "FIND":
			pass

		elif choice == "SHOWSUPER":
			pass

		else:
			pass
