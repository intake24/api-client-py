import datetime
from typing import TypedDict, List, Dict

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


class RecallMealTime(TypedDict):
    hours: int
    minutes: int


class RecallMissingFood(TypedDict):
    name: str
    brand: str
    description: str
    portionSize: str
    leftovers: str


class RecallPortionSize(TypedDict):
    servingWeight: float
    leftoversWeight: float
    portionWeight: float
    method: str
    data: dict


class RecallFood(TypedDict):
    code: str
    englishDescription: str
    localDescription: List[str]
    searchTerm: str
    nutrientTableId: str
    nutrientTableCode: str
    isReadyMeal: bool
    portionSize: RecallPortionSize
    reasonableAmount: bool
    foodGroupId: int
    brand: str
    customData: dict
    fields: dict
    nutrients: Dict[int, float]


class RecallMeal(TypedDict):
    name: str
    time: RecallMealTime
    customData: dict
    foods: List[RecallFood]
    missingFoods: List[RecallMissingFood]


class RecallSubmission(TypedDict):
    id: str  # Actually UUID
    userId: int
    userAlias: List[str]
    userCustomData: dict
    surveyCustomData: dict
    startTime: str
    endTime: str
    meals: List[RecallMeal]


class Surveys:
    def __init__(self, http_handler: Intake24HttpHandler):
        self.http_handler = http_handler

    def list(self) -> List[Survey]:
        return self.http_handler.send_with_auth("GET", "/surveys").json()

    def get_submission_count(self, survey_id: str) -> int:
        return self.http_handler.send_with_auth("GET", f"/v2/surveys/{survey_id}/submission-count").json()["count"]

    def get_submissions(self, survey_id: str, offset: int, limit: int, date_from: datetime = None,
                        date_to: datetime = None, user_name: str = None) -> List[RecallSubmission]:
        return self.http_handler.send_with_auth("GET", f"/data-export/{survey_id}/submissions",
                                                params={"dateFrom": date_from, "dateTo": date_to,
                                                        "userName": user_name, "offset": offset, "limit": limit}).json()
