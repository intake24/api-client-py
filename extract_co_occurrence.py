import argparse
import json
import logging
import sys

from api_client import Intake24Client
from surveys import RecallSubmission, RecallMeal

parser = argparse.ArgumentParser(description="Extract food co-occurrence data from recall submissions.")

parser.add_argument("--ignore", "-i", metavar="ignore_ids", type=str, default=[], nargs="*",
                    help="survey IDs to ignore (e.g. demo)")

parser.add_argument("--min", "-n", metavar="min_N", type=int, nargs="?", default=50,
                    help="minimum number of submissions required to include a survey (surveys having fewer "
                         "submissions will be ignored), default is 50")

parser.add_argument("--batch", "-b", metavar="batch_size", type=int, nargs="?", default=100,
                    help="submission batch size to be processed at once, default is 100, max allowed is 500")

parser.add_argument("--config", "-c", metavar="api_config_name", type=str, nargs="?",
                    help="Intake24 API configuration name",
                    required=True)

parser.add_argument("--output", "-o", metavar="output_file", type=str, nargs="?", help="Output file path")

options = parser.parse_args()

batch_size = max(10, min(500, options.batch))

logging.basicConfig(level=logging.DEBUG)

client = Intake24Client(options.config)

surveys = client.surveys.list()

survey_ids = set(map(lambda x: x["id"], surveys)) - set(options.ignore)

# d = datetime.utcnow().replace(tzinfo=timezone.utc, microsecond=0).isoformat()
# print(d)

logger = logging.getLogger("dumprecalls")


def get_food_codes(meal: RecallMeal) -> [str]:
    return [f["code"] for f in meal["foods"]]


def process_submission(submission: RecallSubmission) -> [[str]]:
    return [get_food_codes(m) for m in submission["meals"]]


def process_survey(survey_id: str) -> [[str]]:
    logger.info("Processing survey \"%s\"", survey_id)
    submission_count = client.surveys.get_submission_count(survey_id)

    if submission_count < options.min:
        logger.info(f"Survey \"{survey_id}\" has fewer than {options.min} submissions, skipping")
        return []
    else:
        offset = 0
        co_occurence_lists = []

        while True:
            next_batch = client.surveys.get_submissions(survey_id, offset, batch_size)
            if len(next_batch) == 0:
                logger.info(f"Done processing {survey_id}")
                break
            else:
                for submission in next_batch:
                    co_occurence_lists.extend(process_submission(submission))
                offset += len(next_batch)
                logger.info(f"Processed {offset} out of {submission_count} submissions")

        return co_occurence_lists

co_occurrences = []

for id in survey_ids:
    co_occurrences.extend(process_survey(id))

result = json.dumps(co_occurrences)

if options.output is not None:
    with open(options.output, "w") as f:
        f.write(result)
else:
    sys.stdout.write(result)
