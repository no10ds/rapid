-include .env
export

.PHONY: help

help: 				## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

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
api-security:			## Run api security checks
	@$(MAKE) api-detect-secrets
	@$(MAKE) api-detect-vulns

api-detect-secrets:		## Check api source code for possible secrets
	@cd api/; ./batect detect-secrets

api-ignore-secrets:		## Mark api detected non-secrets as ignored
	@cd api/; ./batect ignore-secrets

api-detect-vulns:		## Check api source code for common vulnerabilities
	@cd api/; ./batect detect-vulnerabilities

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

infra-init:			## Terraform init: make infra-init block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_init "${block}"

infra-plan:			## Terraform view infrastructure changes: make infra-plan block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf plan "${block}" "${env}"

infra-apply:			## Terraform apply infrastructure changes: make infra-apply block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf apply "${block}" "${env}"

infra-destroy:			## Terraform destory entire infrastructure: make infra-destroy block=<infra-block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf destroy "${block}" "${env}"

infra-output:			## Print infrastructure output: make infra-output block=<infra-block>
	@cd infrastructure/: ./scripts/infra_make_helper.sh run_tf output "${block}" "${env}"
