import json
from pathlib import Path
import gitlab
from aws_lambda_powertools.utilities import parameters
import os
import boto3


def lambda_handler(event, context):
    with open('/tmp/repo.json', 'w') as f:
        f.write(json.dumps(event))
    obj_key = Path(event["Records"][0]["s3"]["object"]["key"])
    # Remove all extensions
    while obj_key.suffix:
        obj_key = obj_key.with_suffix('')
    s3 = boto3.resource('s3')

    event_json = f'{obj_key.stem}.json'
    print(f'Uploading to {event_json}')
    # s3.Bucket('lb-gh2gl').upload_file('/tmp/repo.json', event_json)

    ## Gitlab section
    gl_domain = "https://gitlab.com"
    gl_private_token = json.loads(parameters.get_secret("gitlab_token"))
    gl = gitlab.Gitlab(gl_domain, private_token=gl_private_token["gl_token"])
    gl.auth()
    gl.projects.list(get_all=True)

    return {
        'statusCode': 200,
        'event': f"Pipelines {obj_key.stem}"
    }