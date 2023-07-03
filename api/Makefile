-include .env
export


.PHONY: help test

ECS_SERVICE=rapid-ecs-service
ECS_CLUSTER=rapid-cluster
LATEST_COMMIT_HASH=$(shell git rev-parse --short HEAD)
ACCOUNT_ECR_URI=$(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
IMAGE_NAME=data-f1-registry
PUBLIC_URI=public.ecr.aws
PUBLIC_IMAGE=no10-rapid/api


help: 			## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##
precommit: 		## Python precommit checks (lint, security, tests)
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) security
	@$(MAKE) test-coverage
	@echo "You're good to go 🎉"

check: 			## Development checks (lint, tests)
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test-coverage

lint: 			## Lint checks with flake8
	@./batect lint

format: 		## Format code with Black
	@./batect format

##
test: 			## Run unit python tests
	@./batect test-unit

test-focus: 		## Run unit python tests marked with `@pytest.mark.focus`
	@./batect test-unit-focus

test-e2e:		## Run E2E tests
	@./batect test-e2e

test-e2e-focus:		## Run E2E tests marked with `@pytest.mark.focus`
	@./batect test-e2e-focus

test-coverage:  	## Run python tests with coverage report
	@./batect test-coverage

# Security  --------------------
##
security: 		## Run security checks
	@$(MAKE) detect-secrets
	@$(MAKE) detect-vulns

detect-secrets: 	## Check source code for possible secrets
	@./batect detect-secrets

ignore-secrets: 	## Mark detected non-secrets as ignored
	@./batect ignore-secrets

detect-vulns: 		## Check source code for common vulnerabilities
	@./batect detect-vulnerabilities

scan-for-vulns-and-tag:	## Scan ECR's latest image and tag as vulnerable
			## if high or critical vulnerabilities are found
	@./image-utils.sh "pipeline_post_scanning_processing"

scheduled-prod-scan: 	## Handle scheduled scan result for production image
	@./image-utils.sh "scheduled_scan_result_check" "PROD"

# Running --------------------
##
run: 			## Run the application base image
	@./batect run-app

run-dev: 		## Run the application with hot reload
	@./batect run-local-dev

# Maintenance -------------------------

shell: 			## Run the application environment and drop me into a shell
	@./batect shell

# Deployment -------------------------
##

tag-image:	        ## Tag the image with the latest commit hash
	@docker tag rapid-api-service-image:latest $(ACCOUNT_ECR_URI)/$(IMAGE_NAME):$(LATEST_COMMIT_HASH)

upload-to-registry: 	## Upload the tagged image to the image registry
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ACCOUNT_ECR_URI) && docker push $(ACCOUNT_ECR_URI)/$(IMAGE_NAME):$(LATEST_COMMIT_HASH)

tag-and-upload:		## Tag and upload the latest image
	@$(MAKE) tag-image
	@$(MAKE) upload-to-registry

tag-prod-candidate:	## Tag the uploaded image as a candidate for PROD deployment
	@./image-utils.sh "tag_prod_image"

tag-prod-failure:	## Tag the failed deployment image as a failure
	@./image-utils.sh "tag_prod_failure"

app-live-in-prod:	## Deploy the latest version of the app
	@aws ecs update-service --region $(AWS_REGION) --force-new-deployment --service $(ECS_SERVICE) --cluster $(ECS_CLUSTER)

check-app-is-running:
	@echo "starting wait services to be stable"
	@aws ecs wait services-stable --region $(AWS_REGION) --services $(ECS_SERVICE) --cluster $(ECS_CLUSTER)
	@echo "finished waiting for services to be stable"

clean-pipeline-docker-context:
	@yes | $(MAKE) clean-docker


# Release -------------------------
##

release:
	@git checkout ${commit}
	@git tag -a "${version}" -m "Release tag for version ${version}"
	@git checkout -
	@git push origin ${version}
	@./batect generate_latest_changelog
	@gh release create ${version} -F latest_release_changelog.md
	@rm -rf latest_release_changelog.md

tag-release-image:			## Tag the image with the tag name
	@docker tag rapid-api-service-image:latest $(PUBLIC_URI)/$(PUBLIC_IMAGE):${GITHUB_REF_NAME}

upload-release-image-to-registry:	## Upload the tagged release image to the image registry
	@aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(PUBLIC_URI) && docker push $(PUBLIC_URI)/$(PUBLIC_IMAGE):${GITHUB_REF_NAME}

tag-and-upload-release-image:		## Tag and upload the release image
	@$(MAKE) tag-release-image
	@$(MAKE) upload-release-image-to-registry

tag-generic-release-images:		## Tag generic release images (e.g.: v1.4.x-latest and v1.x.x-latest)
	@./image-utils.sh "tag_latest_minor" ${GITHUB_REF_NAME}
	@./image-utils.sh "tag_latest_patch" ${GITHUB_REF_NAME}

# Setup and config --------------------
##
create-local-venv:	## Create local venv for development
	@./local-venv-setup.sh

create-runtime-env:	## Manually (re)create the environment image
	@./batect runtime-environment

# Clean up and reset --------------------
##

clean-docker: 		## Clean up docker images, containers, volumes
	@docker system prune -a

clean-env: 		## Clean up environment
	@docker image rm -f rapid-api-service-image &&\
	  rm -rf .pytest_cache &&\
	  rm -rf .coverage &&\
	  rm -rf venv

clean-slate: 		## Runs clean-env  and clean-docker
	@$(MAKE) clean-docker && $(MAKE) clean-env
