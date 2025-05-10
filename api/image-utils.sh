#!/usr/bin/env bash
set -eu -o pipefail

LATEST_TAG=$(git rev-parse --short HEAD)
IGNORE_LIST_FILE=vulnerability-ignore-list.txt

RETRIES=0
SCAN_CHECK_COUNT_MAX=3

UNKNOWN_VULNERABILITIES=0

PROD_TAG="PROD"
VULNERABLE_TAG="VULNERABLE"
SCAN_TIMEOUT_TAG="SCAN_TIMEOUT"
DEPLOYMENT_FAILED_TAG="DEPLOYMENT_FAILED"

function _scan_in_progress {
  echo "Checking if the scan is in progress"

  STATUS=$(aws ecr describe-image-scan-findings \
  --region "$AWS_REGION" \
  --repository-name "$API_IMAGE_NAME" \
  --image-id imageTag="$LATEST_TAG" \
  | jq '.imageScanStatus.status' \
  | jq -r .)

  if [ $STATUS = "IN_PROGRESS" ]
  then
    echo "The scan is in progress"
    return 0 # True
  else
    echo "The scan has COMPLETED"
    return 1 # False
  fi
}

function _wait_for_scan_to_complete {
  while _scan_in_progress && [[ $RETRIES -lt SCAN_CHECK_COUNT_MAX ]]; do
    RETRIES=$RETRIES+1
    BACKOFF=$(( 5 ** RETRIES))
    echo "Backing off for $BACKOFF seconds. Waiting for scan to complete..."
    sleep $BACKOFF;
  done
}

function _get_high_or_critical_vulnerabilities {
  VULNS=()
  while IFS='' read -r line; do VULNS+=("$line"); done < <(aws ecr describe-image-scan-findings \
  --region "$AWS_REGION" \
  --repository-name "$API_IMAGE_NAME" \
  --image-id imageTag="$1" \
  | jq '.imageScanFindings.findings[] | select(.severity == "HIGH" or .severity == "CRITICAL") | (.name + "_" + .uri)' \
  | jq -r .)
}

function _get_unknown_vulnerabilities_count {
  if [ ${#VULNS[@]} -eq 0 ]; then
    echo "No vulnerabilities found"
    exit 0
  else
    for VULN in "${VULNS[@]}"
    do
      CVE=$(echo $VULN | awk -F'_' '{print $1}')
      if ( grep -qc "$CVE" "$IGNORE_LIST_FILE" )
      then
        continue
      else
        echo "$VULN" | tr "_" " "
        UNKNOWN_VULNERABILITIES=$((UNKNOWN_VULNERABILITIES+1))
      fi
    done
  fi
}

function get_image_sha_if_exists {
  #This makes bash to NOT throw an error if the PROD tag does not exist
  set +e
  IMAGE_METADATA="$( aws ecr describe-images \
  --region "$AWS_REGION" \
  --repository-name="$API_IMAGE_NAME" \
  --image-ids=imageTag="$1" 2> /dev/null )"
  set -e
  if [[ $? == 0 ]]; then
      echo "${IMAGE_METADATA}" | jq '.imageDetails[0].imageDigest' -r
  else
      echo " "
  fi
}

function tag_prod_image {
  EXISTING_PROD_SHA=$(get_image_sha_if_exists "$PROD_TAG")
  LATEST_IMAGE_SHA=$(get_image_sha_if_exists "$LATEST_TAG")

  if [[ "$EXISTING_PROD_SHA" = "$LATEST_IMAGE_SHA" ]]; then
    echo "Image SHAs are the same - NOT re-tagging"
  else
    echo "Image SHAs are different - tagging PROD candidate"
    tag_image "$PROD_TAG" "$LATEST_TAG"
  fi
}

function tag_prod_failure {
  tag_image "$DEPLOYMENT_FAILED_TAG-$LATEST_TAG" "$PROD_TAG"
  _untag_and_delete "$PROD_TAG"
  _untag_and_delete "$LATEST_TAG"
}

function tag_latest_patch {
  TAG=$(sed -E 's|(((v[[:digit:]]+)\.[[:digit:]]+)\.[[:digit:]]+)|\2.x-latest|' <<< "$1")
  echo "$TAG"
  tag_image "$TAG" "$1"
}

function tag_latest_minor {
  TAG=$(sed -E 's|(((v[[:digit:]]+)\.[[:digit:]]+)\.[[:digit:]]+)|\3.x.x-latest|' <<< "$1")
  echo "$TAG"
  tag_image "$TAG" "$1"
}

function tag_image {
  echo "Tagging image $2 as $1"

  MANIFEST=$(aws ecr batch-get-image \
  --region "$AWS_REGION" \
  --repository-name "$API_IMAGE_NAME" \
  --image-ids imageTag="$2" \
  --query 'images[].imageManifest' --output text)

  aws ecr put-image \
  --region "$AWS_REGION" \
  --repository-name "$API_IMAGE_NAME" \
  --image-tag "$1" \
  --image-manifest "$MANIFEST" > /dev/null
}

function _untag_and_delete {
  echo "Untagging image with tag $1"

  aws ecr batch-delete-image \
  --region "$AWS_REGION" \
  --repository-name "$API_IMAGE_NAME" \
  --image-ids imageTag="$1" > /dev/null
}

function _handle_exhausted_retries {
  echo "Exhausted scan check retries"
  retag_image "$SCAN_TIMEOUT_TAG"
  exit 1;
}

function _handle_unknown_vulnerabilities {
  echo "Breached vulnerability threshold. Please see details of unknown unknown vulnerabilities above."
  retag_image "$VULNERABLE_TAG"
  exit 1
}

function retag_image {
  tag_image "$1-$LATEST_TAG" "$LATEST_TAG"
  _untag_and_delete "$LATEST_TAG"
}

function _check_for_vulnerabilities {
  _get_high_or_critical_vulnerabilities "$1"
  _get_unknown_vulnerabilities_count
}

function pipeline_post_scanning_processing {
  _wait_for_scan_to_complete

  if [[ $RETRIES -eq 3 ]]; then
    _handle_exhausted_retries
  fi

  _check_for_vulnerabilities "$LATEST_TAG"

  if [ $UNKNOWN_VULNERABILITIES -gt 0 ]
  then
    _handle_unknown_vulnerabilities
  fi

  echo "Scan results check successful. All vulnerabilities accounted for"
}

function scheduled_scan_result_check {
  _check_for_vulnerabilities "$1"

  if [ $UNKNOWN_VULNERABILITIES -gt 0 ]
  then
    echo "Vulnerabilities found in $1 image during scheduled scan results check"
     exit 1
  else
    echo "No vulnerabilities found in $1"
  fi
}

"$@"
