#!/usr/bin/env bash

#sam delete --stack-name upload-lambda --no-prompts
sam package --template-file upload_lambda.yml --output-template-file pkg_lambda.yaml --s3-bucket lb-lambdas --region ap-southeast-1
sam deploy --template-file pkg_lambda.yaml --stack-name upload-lambda --region ap-southeast-1 --capabilities CAPABILITY_IAM
