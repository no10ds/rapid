-include .env
export

PYTHON_VERSION=3.10.6

.PHONY: help

help: 				## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

precommit:
	pre-commit install

security-check: detect-secrets detect-vulnerabilities

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
	@cd api; ./batect run-app

api-run-dev:			## Run the api application with hot reload
	@cd api; ./batect run-local-dev

# API Setup and Config --------------------
##
api-create-local-venv:		## Create the api local venv for deployment
	@cd api/; ./local-venv-setup.sh

api-create-image:		## Manually (re)create the api environment image
	@cd api/; ./batect --tag-image service-image=rapid-api-service-image runtime-environment

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

api-tag-and-upload-release-image:## Tag and upload the api release image
	@cd api/; $(MAKE) tag-and-upload-release-image

api-tag-prod-candidate:		## Tag the uploaded api image as a candidate for PROD deployment
	@cd api/; $(MAKE) tag-prod-candidate

api-tag-prod-failure: 		## Tag the PROD image with a fail flag
	@cd api/; $(MAKE) tag-prod-failure

api-app-live-in-prod:		## Deploy the latest version of the api
	@cd api/; $(MAKE) app-live-in-prod

api-check-app-is-running:
	@cd api/; $(MAKE) check-app-is-running

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

infra-scan:			## Print infrastructure output: make infra-output block=<infra-block>
	@cd infrastructure/; ./batect security-scan

##
##----- SDK -----
##
sdk-setup:			## Setup Python required for the sdk
	@cd sdk/; $(MAKE) venv; . .venv/bin/activate; $(MAKE) reqs

# SDK Testing --------------------
##
sdk-test:			## Run sdk unit tests
	@cd sdk/; . .venv/bin/activate && pytest -vv -s

# SDK Release --------------------
##
sdk-release-test:		## Build and release sdk to testpypi
	@cd sdk/; . .venv/bin/activate; $(MAKE) deploy-test

sdk-release:			## Build and release sdk to pypi
	@cd sdk/; . .venv/bin/activate; $(MAKE) deploy

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

ui-test-e2e:
	@cd ui/; npx playwright test ui/playwright

ui-test-e2e-headed:
	@cd ui/; npx playwright test ui/playwright --ui

# UI Release --------------------
##
ui-create-static-out:
	@cd ui/; $(MAKE) create-static-out

ui-zip-contents:
	@cd ui/; $(MAKE) zip-contents tag=${tag};

ui-release:
	@cd ui/; $(MAKE) upload-to-release-prod tag=${tag}

ui-zip-and-release: ui-zip-contents ui-release ## Zip and release prod static ui site

release-process:
	@python release.py --operation check --type ${type}
	# @git checkout ${commit}
	# @git tag -a "${version}" -m "Release tag for version ${version}"
	# @git checkout -
	# @git push origin ${version}
	@python release.py --operation create-changelog --type ${type}
	# @gh release create ${version} -F latest_release_changelog_${type}.md -t "${type} Release"
	@rm -rf latest_release_changelog_${type}.md

# Migration --------------------
##
migrate-v7:			## Run the migration
	@cd api/; ./batect migrate-v7 -- --layer ${layer} --all-layers ${all-layers}

serve-docs:
	mkdocs serve