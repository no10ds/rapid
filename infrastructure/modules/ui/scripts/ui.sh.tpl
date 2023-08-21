#!/bin/bash

url="${REGISTRY_URL}/${VERSION}.zip"
router_url="${REGISTRY_URL}/${VERSION}-router-lambda.zip"

wget $url
wget $router_url

unzip -o "${VERSION}.zip"
cd out/ || { echo "./out folder does not exist"; exit 1; }

aws s3 cp . s3://${BUCKET_ID} --recursive

cd ..

rm -rf ./out