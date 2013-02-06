# -*- coding: UTF-8 -*-

from tornado.options import options
from ConfigParser    import SafeConfigParser, NoOptionError

# ------------------------------------------------------------------------------

class Config:

    def __init__(self, filename = options.config):
        fp = open(filename, "r")
        parser = SafeConfigParser()
        parser.readfp(fp)
        fp.close()

        self.config_parser   = parser
        self.default_backend = parser.get("control", "DefaultBackend")

        options.port          = parser.getint("control", "Port")
        options.debug         = bool(parser.getint("control", "Debug"))
        options.logging       = parser.get("control", "Logging")
        options.log_to_stderr = bool(parser.getint("control", "LogToStderr"))

# ------------------------------------------------------------------------------
