#!/usr/bin/env python

from superpeer.database import database
from .Peer import Peer


def find(conn: database.sqlite3.Connection, session_id: str) -> 'Peer':
	""" Retrieve the peer with the given session_id

	Parameters:
		conn - the db connection
		session_id - session id for a peer

	Returns:
		peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers WHERE session_id = ?', (session_id,))
	row = c.fetchone()

	if row is None:
		return None

	peer = Peer(session_id, row['ip'], row['port'])

	return peer


def find_all(conn: database.sqlite3.Connection) -> list():
	""" Retrieve all the peers

	Parameters:
		conn - the db connection
	Returns:
		list - all the peers
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers')
	peer_rows = c.fetchall()

	return peer_rows


def find_by_ip(conn: database.sqlite3.Connection, ip: str) -> 'Peer':
	""" Retrieve the peer with the given session_id

	Parameters:
		conn - the db connection
		session_id - session id for a peer

	Returns:
		peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers WHERE ip = ?', (ip,))
	row = c.fetchone()

	if row is None:
		return None

	peer = Peer(row['session_id'], ip, row['port'])

	return peer


def file_unlink(conn: database.sqlite3.Connection, session_id: str, file_md5: str) -> bool:
	""" Unlink the peer with the given session_id from the file

	Parameters:
		conn - the db connection
		session_id - session id for a peer
		file_md5 - md5 hash of a file

	Returns:
		bool - true or false either if it succeds or fails
	"""

	c = conn.cursor()
	c.execute('DELETE FROM files_peers WHERE file_md5 = ? AND session_id = ?', (file_md5, session_id,))


def get_peers_by_file(conn: database.sqlite3.Connection, file_md5: str) -> list:
	""" Retrieve all the peers that have the given file
		Parameters:
			conn - the db connection
			query - keyword for the search
		Returns:
			peers list - the list of corresponding peers
	"""
	c = conn.cursor()

	c.execute(
		'SELECT p.session_id, p.ip, p.port '
		'FROM peers AS p NATURAL JOIN files_peers AS f_p '
		'WHERE f_p.file_md5 = ?',
		(file_md5,)
	)
	peer_rows = c.fetchall()

	return peer_rows
