from http_handler import Intake24HttpHandler
from surveys import Surveys


class Intake24Client:
    def __init__(self):
        http_handler = Intake24HttpHandler()
        self.surveys = Surveys(http_handler)
