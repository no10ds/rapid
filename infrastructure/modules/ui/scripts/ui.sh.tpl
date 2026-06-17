#!/bin/bash

if [ ! -z "${ROLE_TO_ASSUME}" ]; then
echo "assume aws role ${ROLE_TO_ASSUME}"
eval $(aws sts assume-role --role-arn arn:aws:iam::992382722318:role/${ROLE_TO_ASSUME} --role-session-name rapid-cli | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\(.AccessKeyId)\nexport AWS_SECRET_ACCESS_KEY=\(.SecretAccessKey)\nexport AWS_SESSION_TOKEN=\(.SessionToken)\n"')
fi

url="${REGISTRY_URL}/${VERSION}.zip"
router_url="${REGISTRY_URL}/${VERSION}-router-lambda.zip"

wget $url
wget $router_url

unzip -o "${VERSION}.zip"
cd out/ || { echo "./out folder does not exist"; exit 1; }

aws s3 cp . s3://${BUCKET_ID} --recursive

cd ..

rm -rf ./out
