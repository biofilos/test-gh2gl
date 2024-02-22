import json


def lambda_handler(event, context):
    with open('/tmp/repo.json', 'w') as f:
        f.write(json.dumps(event))
    print(event["Records"][0]["s3"]["object"]["key"])
    return {
        'statusCode': 200,
        'event': json.dumps(event)
    }