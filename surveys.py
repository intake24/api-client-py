from typing import TypedDict, List

from http_handler import Intake24HttpHandler


class Survey(TypedDict):
    id: str
    schemeId: int
    localeId: str
    state: int
    startDate: str
    endDate: str
    suspensionReason: List[str]
    allowGeneratedUsers: bool
    externalFollowUpURL: List[str]
    supportEmail: str
    description: List[str]
    finalPageHtml: List[str]
    submissionNotificationUrl: List[str]
    feedbackEnabled: bool
    numberOfSubmissionsForFeedback: int
    storeUserSessionOnServer: List[bool]


class Surveys:
    def __init__(self, http_handler: Intake24HttpHandler):
        self.http_handler = http_handler

    def list(self) -> List[Survey]:
        return self.http_handler.send_with_auth("GET", "/surveys").json()

    def get_submissions(self, id: str) -> List:
        pass
