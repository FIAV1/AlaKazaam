#!/usr/bin/env python

from utils import net_utils, Logger, shell_colors as shell
from .LocalData import LocalData
from common.ServerThread import ServerThread
from .handler import NetworkHandler, MenuHandler
from .Menu import Menu
from superpeer.database import database

DB_FILE = 'superpeer/database/directory.db'


def startup():

	if not database.exist(DB_FILE):
		database.create_database(DB_FILE)
	else:
		database.reset_database(DB_FILE)

	while len(LocalData.get_super_friends()) == 0:
		shell.print_blue('\nThis process will allow you to add a known peer to your list of known peers.\n')
		ip4, ip6, port = net_utils.prompt_friend_request()

		LocalData.add_super_friend(ip4, ip6, port)
		shell.print_green(f'\nSuccessfully added the new peer: {ip4}|{ip6} [{port}]\n')

	log = Logger.Logger('superpeer/superpeer.log')

	server = ServerThread(net_utils.get_network_port(), NetworkHandler.NetworkHandler(DB_FILE, log))
	server.daemon = True
	server.start()

	Menu(MenuHandler.MenuHandler()).show()
