## Add OIDC
- Provider URL: `https://token.actions.githubusercontent.com`.
- Get the certificate from Github: `$ openssl s_client -servername token.actions.githubusercontent.com -showcerts -connect token.actions.githubusercontent.com:443 < /dev/null 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' | sed "0,/-END CERTIFICATE-/d" > certificate.crt`
- Calculate fingerprint: `openssl x509 -in certificate.crt -fingerprint -sha1 -noout | sed 's/sha1 Fingerprint=//g' | sed 's/://g'`
- client ID: `sts.amazonaws.com`
- Generate json template to create the OIDC provider: `aws iam create-open-id-connect-provider --generate-cli-skeleton > id_provider.json`
- Fill in the details in the json file
- create a new OIDC provider for github: `aws iam create-open-id-connect-provider --cli-input-json file://id_provider.json`
## Create a role and scope it to the OIDC provider
- Use the policy in `trust_policy.json`
- Create a role with the trust policy: `aws iam create-role --role-name GitHubAction-AssumeRoleWithAction --assume-role-policy-document file://trust_policy.json`
- Allow the created role to upload files to a specific path in an S3 bucket using the policy from `bucket_access.json`: `aws iam put-role-policy --role-name GitHubAction-AssumeRoleWithAction --policy-name GitHubAction-AssumeRoleWithAction --policy-document file://bucket_access.json`

## Lambda function
SAM will be used to create the lambda function. The function will be triggered by the S3 bucket when a file is uploaded. The function will then copy the file to another S3 bucket.
- Package lambda: `sam package --template-file upload_lambda.yml --output-template-file pkg_lambda.yaml --s3-bucket lb-lambdas --region ap-southeast-1`
- Deploy lambda: `sam deploy --template-file pkg_lambda.yaml --stack-name upload-lambda --region ap-southeast-1 --capabilities CAPABILITY_IAM`