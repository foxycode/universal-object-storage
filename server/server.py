#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from tornado.escape import _json_encode, to_unicode, json_decode

import tornado.options
import tornado.ioloop
import tornado.web

# ------------------------------------------------------------------------------

from tornado.util import bytes_type
from datetime     import datetime
from decimal      import Decimal

def recursive_unicode(obj):
    """
    Walks a simple data structure, converting byte strings to unicode.

	Supports lists, tuples, and dictionaries.
	"""
    if isinstance(obj, dict):
        return dict((recursive_unicode(k), recursive_unicode(v)) for (k, v) in obj.items())
    elif isinstance(obj, list):
        return list(recursive_unicode(i) for i in obj)
    elif isinstance(obj, tuple):
        return tuple(recursive_unicode(i) for i in obj)
    elif isinstance(obj, bytes_type):
        return to_unicode(obj)
    elif isinstance(obj, datetime):
    	return obj.isoformat()
    elif isinstance(obj, Decimal):
    	return float(obj)
    else:
        return obj

def json_encode(value):
	return _json_encode(recursive_unicode(value)).replace("</", "<\\/")

# ------------------------------------------------------------------------------

from tornado.web import Application

class ObjectStorage(Application):

	def __init__(self, handlers=None, default_host="", transforms=None,
                 wsgi=False):
		from config import Config

		self.config = Config(tornado.options.options.config)

		tornado.options.parse_command_line()

		settings = {
			"debug" : tornado.options.options.debug
		}

		from backends import couchbase, mysql

		self.backends = {
			'couchbase' : couchbase.CouchbaseBackend(self),
			'mysql'     : mysql.MysqlBackend(self)
		}
		self.backends['default'] = self.backends[self.config.default_backend]

		Application.__init__(self, handlers, default_host, transforms,
							 wsgi, **settings)

# ------------------------------------------------------------------------------

import uuid
import md5

class MainHandler(tornado.web.RequestHandler):

	@property
	def backends(self):
		return self.application.backends

	@property
	def default_backend(self):
		return self.backends['default']

	"""
	def get(self):
		data = self.backends['mysql'].list("eshop", "cw_product")
		for row in data:
			obj = self.backends['mysql'].get("eshop", "cw_product", row['id'])
			id = obj['id']
			obj = json_encode(obj)

			oid = uuid.uuid4().hex
			info_obj = {
				'backend'        : 'mysql',
				'bucket'         : 'eshop',
				'type'           : 'cw_product',
				'id'             : id,
				'content-type'   : 'application/json',
				'Content-Length' : len(obj),
				'content-md5'    : md5.md5(obj).hexdigest(),
				'owner'          : '055ad66cae36471a8f0c622f373d0745',
				'acl'            : 'public'
			}
			self.application.backends['default'].set("default", oid, info_obj)
	"""

	def get(self):
		view = self.application.backends['default'].get_bucket("default").view("_design/all/_view/ALL")
		for row in view:
			self.write("%s<br />" % row)
			#self.application.backends['default'].remove("default", row['id'])

	"""
	def get(self):
		oid = uuid.uuid4().hex

		obj = {
			"id"    : oid,
			"name"  : "Some cool product",
			"price" : 1500,
		}
		obj = json_encode(obj)
		self.application.backends['couchbase'].set("eshop", oid, obj)

		info_obj = {
			'backend'        : 'couchbase',
			'bucket'         : 'eshop',
			'type'           : 'product',
			'content-type'   : 'application/json',
			'Content-Length' : len(obj),
			'content-md5'    : md5.md5(obj).hexdigest(),
			'owner'          : '055ad66cae36471a8f0c622f373d0745',
			'acl'            : 'public'
		}
		self.application.backends['default'].set("default", oid, info_obj)

		view = self.application.backends['default'].get_bucket("default").view("_design/all/_view/ALL")
		for row in view:
			self.write("%s<br />" % row)
			#self.application.backends['default'].remove("default", id)
	"""

# ------------------------------------------------------------------------------

class ObjectHandler(tornado.web.RequestHandler):

	@property
	def backends(self):
		return self.application.backends

	@property
	def default_backend(self):
		return self.backends['default']

	def get_bucket_from_host(self):
		"""
		@returns string bucket name by request hostname
		"""

		# TODO: Implement internal map lookup by self.request.host
		return "default"

	def get_object_info(self, oid):
		"""
		@param oid: uuid of object

		@returns info dict
		"""

		"""
		Get bucket with object information from request hostname
		"""
		bucket = self.get_bucket_from_host()
		obj = self.default_backend.get(bucket, "info", oid)
		if obj:
			obj = json_decode(obj)
		return obj

	def get_object_acl(self, oid, uid):
		"""
		@param oid: object uuid
		@param uid: user uuid

		@returns acl dict
		"""
		return {
			'read'   : True,
			'write'  : True,
			'delete' : True,
			'grant'  : False,
		}

	def check_authorized(self, oid, operation):
		"""
		@param oid:       uuid of object
		@param operation: operation to check

		@returns bool authorized or not
		"""

		"""
		TODO: Here comes authorization checking which returns user uid.
		"""
		uid = "055ad66cae36471a8f0c622f373d0745"
		
		return self.get_object_acl(oid, uid)[operation]

	def get(self, type, oid):
		"""
		@param type: type of object
		@param oid:  uuid of object

		@returns requested object
		"""
		print type, oid
		info = self.get_object_info(oid)
		if not info:
			raise tornado.web.HTTPError(404, "Not Found")

		backend = self.backends[info['backend']]
		obj = backend.get(info['bucket'], type, info['id'] if "id" in info else oid)
		if not obj:
			raise tornado.web.HTTPError(404, "Not Found")

		if info['content-type'] == "application/json":
			self.set_header("Content-Type", "application/json; charset=UTF-8")
			obj = json_encode(obj)
		else:
			self.set_header("Content-Type", info['content-type'])
		self.set_header('Content-MD5', info['content-md5'])
		#self.set_header('Content-Length', info['content-length']) # neni potreba, server spocita sam
		self.set_header('X-OS-Owner', info['owner'])
		self.set_header('X-OS-ACL', info['acl'])

		self.write(obj)

	def get_object_description(self, type):
		return {
			'backend'        : 'couchbase',
			'bucket'         : 'eshop',
			'content-type'   : 'application/json',
			'acl'            : 'public'
		}

	def put(self, type):
		"""
		@param type: type of object
		"""

		"""
		Phase 1: Get object type description
		"""
		desc = self.get_object_description(type)

		"""
		Phase 2: Check user authorization
		"""
		auth = self.get_header("Authorization", None)
		if auth:
			# User sent Authorization header, check if it is ok
			authorized = self.check_authorized(oid, "read")
			if not authorized:
				return tornado.web.HTTPError(403, "Forbidden")
		else:
			# User did not sent Authorization header, ask for it
			return tornado.web.HTTPError(401, "Unauthorized")

		"""
		Phase 3: Check object validity
		"""
		if not self.request.body:
			return {
				'error' : 'No data given'
			}

		if desc['content-type'] == "application/json":
			try:
				data = json_decode(self.request.body)
			except:
				return {
					'error' : 'Content type mismatch'
				}
		else:
			data = self.request.body

		"""
		Phase 4: Save object
		"""
		backend = self.get_backend(desc['backend'])
		oid = backend.set(desc['bucket'], data)

		if not oid:
			return {
				'error' : 'Save error'
			}

		return {
			'status' : 'ok',
			'oid' : oid
		}

	def delete(self, type, oid):
		"""
		@param type: type of object
		@param oid:  uuid of object
		"""

		"""
		Phase 1: Lookup into Object Storage own database (backend) to get info
		about object.
		"""
		info = self.get_object_info(oid)

		"""
		Phase 2: Check object ACL
		"""
		auth = self.get_header("Authorization", None)
		if auth:
			# User sent Authorization header, check if it is ok
			authorized = self.check_authorized(oid, "delete")
			if not authorized:
				return tornado.web.HTTPError(403, "Forbidden")
		else:
			# User did not sent Authorization header, ask for it
			return tornado.web.HTTPError(401, "Unauthorized")

		"""
		Phase 3: Delete object
		"""
		backend = self.get_backend(info['backend'])
		backend.remove(info['bucket'], oid)

		return {
			'status' : 'ok',
			'oid' : oid
		}

# ------------------------------------------------------------------------------

handlers = [
	(r"/", MainHandler),
	(r"/([a-z0-9-_]+)", ObjectHandler),
	(r"/([a-z0-9-_]+)/([abcdef0-9]{32})", ObjectHandler),
]

# ------------------------------------------------------------------------------

tornado.options.define("debug", type=bool, default=None, help="Enables debug mode.")
tornado.options.define("port", type=int, default="8888", help="Server port.")
tornado.options.define("config", type=str, default="config/config.ini")

# ------------------------------------------------------------------------------

if __name__ == "__main__":
	application = ObjectStorage(handlers)
	application.listen(tornado.options.options.port)
	tornado.ioloop.IOLoop.instance().start()
