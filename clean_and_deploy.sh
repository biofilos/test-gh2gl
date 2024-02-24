#!/usr/bin/env bash
set -e

REGION=ap-southeast-1
SAM_DOC=upload_lambda.yml
PKG_DOC=pkg_lambda.yaml
STACK_NAME=upload-lambda
CF_BUCKET=lb-lambdas

sam build -t ${SAM_DOC}
sam package --output-template-file ${PKG_DOC} --s3-bucket ${CF_BUCKET} --region ${REGION}
sam deploy --template-file ${PKG_DOC} --stack-name ${STACK_NAME} --region ${REGION} --capabilities CAPABILITY_IAM
