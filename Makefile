-include .env
export

PYTHON_VERSION=3.10.6

.PHONY: help

help: 				## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

precommit:
	pre-commit install

security-check:
	@$(MAKE) detect-secrets
	@$(MAKE) detect-vulnerabilities

detect-secrets:
	@git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline

ignore-secrets:
	detect-secrets scan > .secrets.baseline

detect-vulnerabilities:
	bandit -qr api/api sdk/rapid

##
##----- API -----
##

# API Testing --------------------
api-test:			## Run api python unit tests
	@cd api/; ./batect test-unit

api-test-coverage:		## Run api python unit tests with coverage report
	@cd api/; ./batect test-coverage

api-test-focus:			## Run api python tests marked with `@pytest.mark.focus`
	@cd api/; ./batect test-unit-focus

api-test-e2e:			## Run api python e2e tests
	@cd api/; ./batect test-e2e

api-test-e2e-focus:		## Run api python e2e tests marked with `@pytest.mark.focus`
	@cd api/; ./batect test-e2e-focus

# API Security --------------------
##
api-scan-for-vulns-and-tag:	## Scan api ecr for latest image and tag as vulnerable
	@cd api/; ./image-utils.sh "pipeline_post_scanning_processing"

api-scheduled-prod-scan:	## Handle api scheduled scan result for production image
	@cd api/; ./image-utils.sh "scheduled_scan_result_check" "PROD"

# API Running --------------------
##
api-run:			## Run the api application base image
	@cd /api; ./batect run-app

api-run-dev:			## Run the api application with hot reload
	@cd /api; ./batect run-local-dev

# API Setup and Config --------------------
##
api-create-local-venv:		## Create the api local venv for deployment
	@cd api/; ./local-venv-setup.sh

api-create-image:		## Manually (re)create the api environment image
	@cd api/; ./batect runtime-environment

api-shell:			## Run the api application and drop me into a shell
	@cd api/; ./batect shell

api-lint:			## Run the api lint checks with flake8
	@cd api/; ./batect lint

api-format:			## Run the api code format with black
	@cd api/; ./batect format

# API Release --------------------
##
api-tag-and-upload:		## Tag and upload the latest api image
	@cd api/; $(MAKE) tag-and-upload

##
clean-pipeline-docker-context:
	@cd api/; $(MAKE) clean-docker

##
##----- Infrastructure -----
##

infra-assume-role:		## Assume role to perform infrastructure tasks
	@cd infrastructure/; ./scripts/assume_role.sh

infra-backend:			## Create terraform backend for infrastructure
	@cd infrastructure/; ./scripts/infra_make_helper.sh create_backend

##

infra-init:			## Terraform init: make infra-init block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_init "${block}"

infra-plan:			## Terraform view infrastructure changes: make infra-plan block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf plan "${block}" "${env}"

infra-apply:			## Terraform apply infrastructure changes: make infra-apply block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf apply "${block}" "${env}"

infra-destroy:			## Terraform destory entire infrastructure: make infra-destroy block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf destroy "${block}" "${env}"

infra-output:			## Print infrastructure output: make infra-output block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf output "${block}" "${env}"

##
##----- SDK -----
##
sdk-setup:			## Setup Python required for the sdk
	@cd sdk/; $(MAKE) python; $(MAKE) venv;

# SDK Testing --------------------
##
sdk-test:			## Run sdk unit tests
	@cd sdk/; pytest -vv -s

# SDK Release --------------------
##
sdk-release-test:		## Build and release sdk to testpypi
	@cd sdk/; $(MAKE) deploy-test

sdk-release:			## Build and release sdk to pypi
	@cd sdk/; $(MAKE) deploy

##
##----- UI -----
##
ui-setup:			## Setup npm required for the sdk
	@cd ui/; npm i -g next; npm ci

# UI Running --------------------
##
ui-run:				## Run the ui application
	@cd ui/; npm run

ui-run-dev:			## Run the ui application with hot reload
	@cd ui/; npm run dev

# UI Testing --------------------
##
ui-test:			## Test ui site
	@cd ui/; npm run test:all

# UI Release --------------------
##
ui-zip-and-release:		## Zip and release static ui site
	@cd ui/; $(MAKE) zip-contents; $(MAKE) upload-to-release

##
