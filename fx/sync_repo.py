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
    manifest_s3 = f"manifests/{base_name}.json"
    manifest_local = f"/tmp/{base_name}.json"
    s3.download_file(bucket, manifest_s3, manifest_local)
    manifest = json.load(open(manifest_local))
    gitlab_repo = manifest["gitlab_repo"]
    branch = manifest["branch"]
    ## Gitlab section
    gl_domain = "https://gitlab.com"
    gl_private_token = json.loads(parameters.get_secret("gitlab_token"))["gl_token"]
    # Login to Gitlab
    with gitlab.Gitlab(gl_domain, private_token=gl_private_token) as gl:
        gl.auth()
        # Select repo
        project = gl.projects.get(gitlab_repo)
        trigger = project.triggers.create({
            "description": "Triggered by lambda"
        })
        # These variables are used in the .gitlab-ci.yml file
        vars = {
            "s3_path": f"s3://{bucket}/{obj_key_str}",
            "gitlab_path": obj_key_str, "run_now": "yes",
            "access_token": gl_private_token,
            "branch": branch,
            "gitlab_repo": gitlab_repo
        }
        # Wait until the latest pipeline is finished
        while project.pipelines.list(ref=branch, status="running") or project.pipelines.list(ref=branch, status="pending"):
            time.sleep(1)
        pipeline = project.trigger_pipeline(branch, trigger.token, variables=vars)
        while pipeline.finished_at is None:
            pipeline.refresh()
            time.sleep(1)
        trigger.delete()
    return {
        'statusCode': 200,
        'event': f"Pipelines {obj_key.stem}"
    }
