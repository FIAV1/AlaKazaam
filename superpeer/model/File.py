#!/usr/bin/env python

from superpeer.database import database


class File:

	def __init__(self, file_md5, file_name, download_count):
		self.file_md5 = file_md5
		self.file_name = file_name
		self.download_count = download_count

	def insert(self, conn: database.sqlite3.Connection) -> None:
		""" Insert the file into the db

		Parameters:
			conn - the db connection
		Returns:
			None
		"""
		conn.execute('INSERT INTO files VALUES (?,?,?)', (self.file_md5, self.file_name, self.download_count))

	def update(self, conn: database.sqlite3.Connection) -> None:
		""" Update the file into the db

		Parameters:
			conn - the db connection
		Returns:
			None
		"""
		query = """UPDATE files
		SET file_name=:name, download_count=:count
		WHERE file_md5 =:md5"""

		conn.execute(query, {'md5': self.file_md5, 'name': self.file_name, 'count': self.download_count})

	def delete(self, conn: database.sqlite3.Connection) -> None:
		""" Remove the file from the db

		Parameters:
			conn - the db connection
		Returns:
			None
		"""

		conn.execute('DELETE FROM files WHERE file_md5=?', (self.file_md5,))
