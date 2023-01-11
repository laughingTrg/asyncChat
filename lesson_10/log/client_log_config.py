import logging

cli_logger = logging.getLogger('client.main')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s ")

fh = logging.FileHandler('cli_main.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

cli_logger.addHandler(fh)
cli_logger.setLevel(logging.DEBUG)