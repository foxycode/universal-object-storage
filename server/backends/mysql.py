# -*- coding: UTF-8 -*-

from __future__      import absolute_import
from MySQLdb.cursors import DictCursor

import MySQLdb

# ------------------------------------------------------------------------------

class MysqlBackend:

	def __init__(self, application):
		self.application = application
		
		self.parse_config()

		self.db = MySQLdb.connect(
			host = self.server,
			user = self.user,
			passwd = self.password,
			db = self.default_database,
			charset = "utf8",
			cursorclass = DictCursor,
		)

	def parse_config(self):
		parser = self.application.config.config_parser
		
		self.server   		  = parser.get("mysql", "Server")
		self.user     		  = parser.get("mysql", "User")
		self.password 		  = parser.get("mysql", "Password")
		self.default_database = parser.get("mysql", "DefaultDatabase")

	def list(self, bucket, type):
		cursor = self.db.cursor()
		try:
			cursor.execute("""
				SELECT `id` FROM `%s`
			""" % type)
			return cursor.fetchall()
		except Exception as e:
			raise
		finally:
			cursor.close()

	def get(self, bucket, type, oid):
		cursor = self.db.cursor()
		try:
			cursor.execute("""
				SELECT * FROM `%s` WHERE `id` = %s
			""" % (type, oid))
			return cursor.fetchone()
		except Exception as e:
			raise
		finally:
			cursor.close()

	def set(self, bucket, key, data):
		raise NotImplementedError

	def remove(self, bucket, oid):
		raise NotImplementedError
