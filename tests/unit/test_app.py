import sys
from unittest.mock import Mock

import pytest
import requests


@pytest.fixture()
def snsSingleAlarmEvent():
    """Generates SNS Event from a Cloudwatch Alarm"""

    return {
        "Records": [
            {
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:us-east-2:123456789012:sns-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
                "EventSource": "aws:sns",
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "21be56ed-a058-49f5-8c98-aedd2564c486",
                    "TopicArn": "arn:aws:sns:eu-south-1:123456789012:my-topic",
                    "Subject": "ALARM: \"sample-event-UnHealthyHostCount\" in EU (Milan)",
                    "Message": "{\"AlarmName\":\"sample-event-UnHealthyHostCount\",\"AlarmDescription\":null,\"AWSAccountId\":\"123456789012\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 out of the last 1 datapoints [4.0 (22/10/20 18:47:00)] was greater than the threshold (1.0) (minimum 1 datapoint for OK -> ALARM transition).\",\"StateChangeTime\":\"2020-10-22T18:55:49.694+0000\",\"Region\":\"EU (Milan)\",\"AlarmArn\":\"arn:aws:cloudwatch:eu-south-1:123456789012:alarm:sample-event-UnHealthyHostCount\",\"OldStateValue\":\"OK\",\"Trigger\":{\"MetricName\":\"UnHealthyHostCount\",\"Namespace\":\"AWS/ApplicationELB\",\"StatisticType\":\"Statistic\",\"Statistic\":\"SUM\",\"Unit\":null,\"Dimensions\":[{\"value\":\"targetgroup/sample-event/e8a0ec2c9817e9c7\",\"name\":\"TargetGroup\"},{\"value\":\"eu-south-1c\",\"name\":\"AvailabilityZone\"},{\"value\":\"app/my-app/c65416decbc1646a\",\"name\":\"LoadBalancer\"}],\"Period\":300,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"GreaterThanThreshold\",\"Threshold\":1.0,\"TreatMissingData\":\"- TreatMissingData:                    missing\",\"EvaluateLowSampleCountPercentile\":\"\"}}",
                    "Timestamp": "2020-10-22T18:55:49.738Z",
                    "SignatureVersion": "1",
                    "Signature": "ZCueiiosXP6jWMDaZI6moje4p85u32AZvLslW+o27Dp9vpRYz1XZdAMdg+HmouuYYhZ32kw9HNVzaCQi+MuIZLfc5njvRt1R1/BSQQr6YRebeWHPBdWlBtCN+7N6xBhCssjiIKSHmOtDEN0r44XuxkrkzMpHOvQwItCzmGNWS4TwFGvNYzVA5+T0cCH/yyHI7svm9ftdJGew/lZWsRpLw2Oh46cve30OqAryorZSY3X5UbDKl+H3PdS7adTpJRJQ/Fq2Ve7G2VPQHz2ewNMVVKPoXvWo6SUYiAzti7sR/siICQetz4hrgzip3R5enM2YbZipyWi97Wq4pnetwka54g==",
                    "SigningCertURL": "https://sns.eu-south-1.amazonaws.com/SimpleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem",
                    "UnsubscribeURL": "https://sns.eu-south-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-south-1:123456789012:my-topic:2c602bff-dab7-45a7-8e52-cd6cd2a4424f"
                }
            }
        ]
    }


def test_lambda_handler(snsSingleAlarmEvent, mocker, requests_mock):
    try:
        # clean up modules cache
        del sys.modules["src.app"]
    except KeyError:
        pass
    mocker.patch.dict('os.environ', {'TopicTable': 'tablename'})
    mock_table = Mock()
    mock_table.get_item.return_value = {
        'Item': {
            'id': "ALARM: \"sample-event-UnHealthyHostCount\" in EU (Milan)",
            'webhookURL': 'mock://myURL',
        }
    }
    mock_bootstrap = Mock()
    mock_bootstrap.topic_table = mock_table
    mocker.patch('src.app.Bootstrap.make', return_value=mock_bootstrap)
    from src import app
    requests_mock.register_uri('POST', 'mock://myURL', json={
        'ok': True,
    })
    ret = app.lambda_handler(snsSingleAlarmEvent, "")
    print(f'{mock_table.get_item.call_args_list=}')
    print(f'{mock_bootstrap.call_args_list=}')
    print(f'{ret=}')
    assert ret['succeeded'] == 1
    assert mock_table.get_item.call_count == 1
