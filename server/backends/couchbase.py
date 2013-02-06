# -*- coding: UTF-8 -*-

from __future__                import absolute_import
from couchbase.client          import Couchbase
from couchbase.exception       import MemcachedError

# ------------------------------------------------------------------------------

class CouchbaseBackend:

	def __init__(self, application):
		self.application = application
		self.buckets = {}

		self.parse_config()

	def parse_config(self):
		parser = self.application.config.config_parser
		
		self.server   		= parser.get("couchbase", "Server")
		self.port     		= parser.getint("couchbase", "Port")
		#self.user           = parser.get("couchbase", "User")
		#self.password       = parser.get("couchbase", "Password")
		self.default_bucket = parser.get("couchbase", "DefaultBucket")

	def get_bucket(self, bucket):
		if bucket not in self.buckets:
			self.buckets[bucket] = Couchbase("%s:%s" % (self.server, self.port), bucket, "")[bucket]
		return self.buckets[bucket]

	def get(self, bucket, type, oid):
		bucket = self.get_bucket(bucket)
		try:
			return bucket.get(oid)[2]
		except MemcachedError as e:
			if str(e) == "Memcached error #1:  Not found":
				return None
			raise

	def set(self, bucket, key, data):
		bucket = self.get_bucket(bucket)
		bucket.set(key, 0, 0, data)

	def remove(self, bucket, oid):
		bucket = self.get_bucket(bucket)
		return bucket.delete(oid)
