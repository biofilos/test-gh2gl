import json
import boto3
from pathlib import Path
import gitlab
from aws_lambda_powertools.utilities import parameters
import os

import boto3

# def get_secret(secret_name, region_name):
#     session = boto3.session.Session()
#     client = session.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )
#
#     get_secret_value_response = client.get_secret_value(
#         SecretId=secret_name
#     )
#
#     if 'SecretString' in get_secret_value_response:
#         secret = get_secret_value_response['SecretString']
#     else:
#         secret = base64.b64decode(get_secret_value_response['SecretBinary'])
#
#     return secret
#
# # Usage
# secret_name = "gitlab_token"
# region_name = "us-west-2"  # replace with your AWS region

# gl_private_token = get_secret(secret_name, region_name)

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

    return {
        'statusCode': 200,
        'event': f"Pipelines {obj_key.stem}"
    }