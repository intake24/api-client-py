import logging

from http_handler import Intake24HttpHandler
from surveys import Surveys


class Intake24Client:
    def __init__(self, api_configuration_name):
        logger = logging.getLogger("intake24client")

        http_handler = Intake24HttpHandler(api_configuration_name, logger)
        self.surveys = Surveys(http_handler)
