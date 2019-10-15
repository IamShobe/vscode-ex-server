from main import index_packages
from logging import getLogger

bind = "0.0.0.0:8443"
workers = 1

def when_ready(server):
    server.log.info("Trying to index packages...")
    logger = getLogger("app")
    gunicorn_logger = getLogger("gunicorn.error")
    logger.handlers.extend(gunicorn_logger.handlers)
    index_packages()
