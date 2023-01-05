import logging
import logging.handlers

serv_logger = logging.getLogger('server.main')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s ")

tfh = logging.handlers.TimedRotatingFileHandler('server_main.log', when='D', interval=1)
tfh.setLevel(logging.DEBUG)
tfh.setFormatter(formatter)

serv_logger.addHandler(tfh)
serv_logger.setLevel(logging.DEBUG)