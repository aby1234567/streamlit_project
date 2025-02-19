import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

info_handler = logging.FileHandler('info.log')
warning_handler = logging.FileHandler('warning.log')
error_handler = logging.FileHandler('error.log')
critical_handler = logging.FileHandler('critical.log')

info_handler.setLevel(logging.INFO)
warning_handler.setLevel(logging.WARNING)
error_handler.setLevel(logging.ERROR)
critical_handler.setLevel(logging.CRITICAL)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

info_handler.setFormatter(formatter)
warning_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
critical_handler.setFormatter(formatter)

logger.addHandler(info_handler)
logger.addHandler(warning_handler)
logger.addHandler(error_handler)
logger.addHandler(critical_handler)


