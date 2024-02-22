import json
import boto3
from pathlib import Path

def lambda_handler(event, context):
    with open('/tmp/repo.json', 'w') as f:
        f.write(json.dumps(event))
    obj_key = Path(event["Records"][0]["s3"]["object"]["key"])
    s3 = boto3.resource('s3')
    event_json = f'{obj_key.stem}.json'
    print(f'Uploading to {event_json}')
    s3.Bucket('lb-gh2gl').upload_file('/tmp/repo.json', event_json)
    return {
        'statusCode': 200,
        'event': json.dumps(event)
    }