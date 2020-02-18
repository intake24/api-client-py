import argparse

from api_client import Intake24Client

parser = argparse.ArgumentParser(description="Dump recall data to JSON files.")

parser.add_argument("--ignore", "-i", metavar="ignore_ids", type=str, default=[], nargs="*",
                    help="survey IDs to ignore (e.g. demo)")

parser.add_argument('-n', metavar='min_N', type=int, nargs="?", default=50,
                    help="minimum number of submissions required to include a survey (surveys having fewer "
                         "submissions will be ignored), default is 50")

options = parser.parse_args()

client = Intake24Client()

surveys = client.surveys.list()

survey_ids = set(map(lambda x: x["id"], surveys)) - set(options.ignore)

for id in survey_ids:
    print(f"Processing survey {id}")
