import json


def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'ctx': json.dumps(context),
        'event': json.dumps(event)
    }