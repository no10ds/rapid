#!/bin/bash
BREAK="------------------------"
ARGS=--no-cli-pager
BUCKET=$1
DYNAMODB_TABLE=$2

function create_bucket(){
    echo "Creating bucket"
    aws s3api create-bucket --bucket $BUCKET --acl private $ARGS --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION

    echo "- Adding versioning"
    aws s3api put-bucket-versioning --bucket $BUCKET --versioning-configuration Status=Enabled $ARGS

    echo "- Adding encryption"
    aws s3api put-bucket-encryption --bucket $BUCKET \
        --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}' $ARGS
}

function create_table(){
    echo "Creating DynamoDB table"
    aws dynamodb create-table \
        --table-name $DYNAMODB_TABLE \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode  PAY_PER_REQUEST \
        $ARGS
}

main () {
    echo $break
    echo "Creating terraform backend"
    echo $break
    echo "Args:"
    echo "- Bucket: $1"
    echo "- DynamoDB Table: $2"
    echo $break
    create_bucket
    echo $break
    echo $break
    create_table
    echo $break
    echo "Finished backend creation"
}

main
