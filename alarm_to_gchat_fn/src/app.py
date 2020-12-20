# import requests
import json
import os
import traceback
from typing import List, Dict, Optional, TypedDict

import boto3
import requests


class GChatAlarmConfiguration(TypedDict):
    id: str  # the id for the given alarm, usually the subject
    webhookURL: str  # the URL to send the message to


class Bootstrap:
    """
    This class is used to perform any initial preparation for the environment.
    i.e.
    """

    _cached: Optional["Bootstrap"] = None

    def __init__(self) -> None:
        super().__init__()
        dynamodb = boto3.resource("dynamodb")
        self.topic_table = dynamodb.Table(os.environ["TopicTable"])

    @classmethod
    def make(cls) -> "Bootstrap":
        if cls._cached is None:
            cls._cached = Bootstrap()
        return cls._cached


Bootstrap.make()


def lambda_handler(event, _):
    print(f"{event=}")
    bootstrap = Bootstrap.make()
    succeeded, failed = 0, 0
    for record in event["Records"]:
        subject = record["Sns"]["Subject"]
        db_record = get_db_record(subject, record, bootstrap)
        webhook_url = get_webhook(db_record)
        trailing_card = get_trailing_card(db_record)
        print(f"{webhook_url=} {trailing_card=}")
        if webhook_url is None:
            failed += 1
            continue
        try:
            message = message_from_record(record, trailing_card)
            send_message(message, webhook_url)
            succeeded += 1
        except:
            print(f"record failed: {record=}")
            traceback.print_exc()
            failed += 1
    return {
        "succeeded": succeeded,
        "failed": failed,
        "total": succeeded + failed,
    }


def message_from_record(record, trailing_card: Optional[Dict]) -> Dict:
    message: Dict = json.loads(record["Sns"]["Message"])
    widgets: List[Dict] = list()
    header = {
        "title": record["Sns"]["Subject"],
        "subtitle": "AWS Notification",
    }
    for key, value in message.items():
        if isinstance(value, int):
            value = str(value)
        if isinstance(value, str):
            widget = {
                "keyValue": {
                    "topLabel": key,
                    "content": value,
                    "contentMultiline": True,
                }
            }
            widgets.append(widget)

    cards = [{"header": header}, {"sections": {"widgets": widgets}}]
    if trailing_card is not None:
        cards.append(trailing_card)

    aux: Dict = {"cards": cards}

    print(json.dumps(aux))

    return aux


def send_message(message: Dict, url: str):
    res = requests.post(url, json=message)
    print(f"{res.status_code=}, {res.json()=}")


def get_db_record(subject, record, b: Bootstrap) -> Optional[Dict]:
    topic_table = b.topic_table
    db_record = topic_table.get_item(
        Key={
            "id": subject,
        },
        ConsistentRead=False,
    )
    print(f"{db_record=}")
    item = db_record.get("Item")
    if item is None:
        topic_table.put_item(
            Item={
                "id": subject,
                "reason": "È arrivato un messaggio a questo topic, impostare il campo webhookURL",
                "message": record,
            }
        )
    return item


def get_webhook(db_record: Optional[Dict]) -> Optional[str]:
    webhook_url = (db_record or {}).get("webhookURL")
    return webhook_url


def get_trailing_card(db_record: Dict) -> Optional[Dict]:
    return db_record.get("googleChat", {}).get("trailingCard")
