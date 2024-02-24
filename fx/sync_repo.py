import json
import time
from pathlib import Path
import gitlab
from aws_lambda_powertools.utilities import parameters
import os
import boto3
import tarfile


def lambda_handler(event, context):
    with open('/tmp/repo.json', 'w') as f:
        f.write(json.dumps(event))
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    obj_key = Path(event["Records"][0]["s3"]["object"]["key"])
    obj_key_str = str(obj_key)
    # Remove all extensions
    while obj_key.suffix:
        obj_key = obj_key.with_suffix('')
    s3 = boto3.client('s3')
    base_name = obj_key.stem
    manifest_path = Path(f"/manifests/{base_name}.json")
    s3.download_file(bucket, obj_key, str(manifest_path))
    manifest = json.load(manifest_path.open())
    gitlab_repo = manifest["gitlab_repo"]
    branch = manifest["branch"]
    ## Gitlab section
    gl_domain = "https://gitlab.com"
    gl_private_token = json.loads(parameters.get_secret("gitlab_token"))
    gl = gitlab.Gitlab(gl_domain, private_token=gl_private_token["gl_token"])
    gl.auth()
    project = gl.projects.get(gitlab_repo)
    trigger = project.triggers.create({
        "description": "Triggered by lambda"
    })
    vars = {"s3_path": f"s3://{bucket}/{obj_key_str}", "gitlab_path": obj_key_str}

    pipeline = project.trigger_pipeline(branch, trigger.token, variables=vars)
    while pipeline.finished_at is None:
        pipeline.refresh()
        time.sleep(1)

    return {
        'statusCode': 200,
        'event': f"Pipelines {obj_key.stem}"
    }