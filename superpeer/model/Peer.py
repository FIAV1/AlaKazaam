#!/usr/bin/env python

from superpeer.database import database


class Peer:

    def __init__(self, session_id, ip, port):
        self.session_id = session_id
        self.ip = ip
        self.port = port

    def insert(self, conn: database.sqlite3.Connection) -> None:
        """ Insert the peer into the db

        Parameters:
            conn - the db connection
        Returns:
            None
        """
        conn.execute('INSERT INTO peers VALUES (?,?,?)', (self.session_id, self.ip, self.port))

    def delete(self, conn: database.sqlite3.Connection) -> None:
        """ Delete the peer from the db

        Parameters:
            conn - the db connection
        Returns:
            None
        """
        conn.execute('DELETE FROM peers WHERE session_id = ?', (self.session_id,))
