from odin.http.server import HttpServer
from odin.config.parser import ConfigParser, ConfigError

import sys
import logging
import signal
import threading

try:
    from zmq.eventloop import ioloop
    ioloop.install()
    using_zmq_loop = True
except ImportError:   # pragma: no cover
    using_zmq_loop = False

import tornado.ioloop


def sigint_handler(signum, frame):  # pragma: no cover
    logging.info("Interrupt signal received, shutting down")
    tornado.ioloop.IOLoop.instance().stop()


def main(argv=None):

    config = ConfigParser()

    # Define configuration options and add to the configuration parser
    config.define("http_addr", default="0.0.0.0", option_help="Set HTTP server address")
    config.define("http_port", default=8888, option_help="Set HTTP server port")
    config.define("debug_mode", default=False, option_help="Enable tornado debug mode")

    # Parse configuration options and any configuration file specified
    try:
        config.parse(argv)
    except ConfigError as e:
        logging.error("Failed to parse configuration: {}".format(e))
        return 2

    # Resolve the list of adapters specified
    try:
        adapters = config.resolve_adapters()
    except ConfigError as e:
        logging.warning("Failed to resolve API adapters: {}".format(e))
        adapters = []

    logging.info("Using the {} IOLoop instance".format("0MQ" if using_zmq_loop else "tornado"))

    # Launch the HTTP server
    http_server = HttpServer(config.debug_mode, adapters)
    http_server.listen(config.http_port, config.http_addr)

    logging.info("HTTP server listening on {}:{}" .format(
        config.http_addr, config.http_port))

    # Register a SIGINT signal handler only if this is the main thread
    if isinstance(threading.current_thread(), threading._MainThread): # pragma: no cover
        signal.signal(signal.SIGINT, sigint_handler)

    # Enter IO processing loop
    tornado.ioloop.IOLoop.instance().start()

    logging.info("ODIN server shutdown")

    return 0

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
