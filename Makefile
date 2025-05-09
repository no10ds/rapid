-include .env
export

# Versions
PYTHON_VERSION=3.12.6
NODE_VERSION=lts/iron

# Git references
GITHUB_SHA=$$(git rev-parse HEAD)
GITHUB_SHORT_SHA=$$(git rev-parse --short HEAD)
RELEASE_TAG=$$(git describe --exact-match --tags HEAD)

# API Build variables
API_ACCOUNT_ECR_URI=$(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
API_PUBLIC_URI=public.ecr.aws
API_PUBLIC_IMAGE=no10-rapid/api

# UI Build variables
UI_ZIP_PATH=$(UI_IMAGE_NAME)-$(GITHUB_SHORT_SHA)
ifeq ($(RELEASE_TAG), null)
	TAG_NAME="$(UI_IMAGE_NAME)-$(GITHUB_SHORT_SHA)"
else
	TAG_NAME="$(RELEASE_TAG)-dev-$(GITHUB_SHORT_SHA)"
endif

setup: brew precommit

brew:				## Brew install all the dependencies
	brew bundle

.PHONY: help
help: 				## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

precommit:			## Setup the pre-commits
	pre-commit install

security-check: detect-secrets detect-vulnerabilities	## Run the security checks

detect-secrets:		## Detect secrets
	@git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline

ignore-secrets:		## Ignore secrets
	detect-secrets scan > .secrets.baseline

detect-vulnerabilities:		##Detect the vulnerabilities
	bandit -qr api/api sdk/rapid

python-setup:			## Setup python to run the sdk and api
	pyenv install --skip-existing $(PYTHON_VERSION)
	pyenv local $(PYTHON_VERSION)

node-setup:				## Setup node to run the UI
	. ${HOME}/.nvm/nvm.sh && nvm install $(NODE_VERSION)
	. ${HOME}/.nvm/nvm.sh && nvm use $(NODE_VERSION)

##
##----- API -----
##

# API Testing --------------------
.PHONY: api/test
api/test:			## Run api python unit tests
	@cd api/; . .venv/bin/activate; pytest test/api -vv -s

api/test-coverage:		## Run api python unit tests with coverage report
	@cd api/; . .venv/bin/activate; pytest --durations=5 --cov=api --cov-report term-missing test/api

api/test-focus:			## Run api python tests marked with `@pytest.mark.focus`
	@cd api/; . .venv/bin/activate; pytest test/api -vv -s -m focus

api/test-e2e:			## Run api python e2e tests
	@cd api/; . .venv/bin/activate; pytest test/e2e -v  --order-scope=module 

api/test-e2e-focus:		## Run api python e2e tests marked with `@pytest.mark.focus`
	@cd api/; . .venv/bin/activate; pytest test/e2e -v -s -m focus

# API Security --------------------
##
api/scan-for-vulns-and-tag:	## Scan api ecr for latest image and tag as vulnerable
	@cd api/; ./image-utils.sh "pipeline_post_scanning_processing"

api/scheduled-prod-scan:	## Handle api scheduled scan result for production image
	@cd api/; ./image-utils.sh "scheduled_scan_result_check" "PROD"

# API Running --------------------
##
api/run:			## Run the api application with hot reload
	@cd api && . .venv/bin/activate && uvicorn api.entry:app --host 0.0.0.0 --port 8000 --reload

# API Setup and Config --------------------
##
api/venv:		## Create the api local venv for deployment
	@cd api/; python3 -m venv .venv

api/reqs:
	@cd api/; . .venv/bin/activate; pip install -r requirements-dev.txt

api/setup:	api/venv api/reqs

api/create-image:		## Manually (re)create the api environment image
	@cd api/; docker build --build-arg commit_sha=$(GITHUB_SHA) --build-arg version=$(GITHUB_SHORT_SHA) -t rapid-api/service-image .

api/lint:			## Run the api lint checks with flake8
	@cd api/; . .venv/bin/activate; flake8 api test

api/format:			## Run the api code format with black
	@cd api/; . .venv/bin/activate; black api test

# API Release --------------------
##

pull: api/docker-login
	@docker pull $(API_ACCOUNT_ECR_URI)/$(API_IMAGE_NAME):$(GITHUB_SHORT_SHA)

api/tag-image:		## Tag the image with the latest commit hash
	@cd api/; docker tag rapid-api/service-image:latest $(API_ACCOUNT_ECR_URI)/$(API_IMAGE_NAME):$(GITHUB_SHORT_SHA)

api/docker-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(API_ACCOUNT_ECR_URI)

api/upload-image: api/docker-login	## Upload the tagged image to the image registry
	@docker push $(API_ACCOUNT_ECR_URI)/$(API_IMAGE_NAME):$(GITHUB_SHORT_SHA)

api/tag-and-upload:	api/tag-image api/upload-image	## Tag and upload the latest api image

api/tag-release-image:			## Tag the image with the tag name
	@cd api/; docker tag rapid-api/service-image:latest $(API_PUBLIC_URI)/$(API_PUBLIC_IMAGE):${RELEASE_TAG}

api/upload-release-image:	## Upload the tagged release image to the image registry
	@aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(API_PUBLIC_URI) && docker push $(API_PUBLIC_URI)/$(API_PUBLIC_IMAGE):${RELEASE_TAG}

api/tag-and-upload-release-image: api/tag-release-image api/upload-release-image## Tag and upload the api release image

api/tag-prod-candidate:		## Tag the uploaded api image as a candidate for PROD deployment
	@cd api/; ./image-utils.sh "tag_prod_image"

api/tag-prod-failure: 		## Tag the PROD image with a fail flag
	@cd api/; ./image-utils.sh "tag_prod_failure"

api/app-live-in-prod:		## Deploy the latest version of the api
	@aws ecs update-service --region $(AWS_REGION) --force-new-deployment --service $(ECS_SERVICE) --cluster $(ECS_CLUSTER)

api/check-app-is-running:
	@echo "starting wait services to be stable"
	@aws ecs wait services-stable --region $(AWS_REGION) --services $(ECS_SERVICE) --cluster $(ECS_CLUSTER)
	@echo "finished waiting for services to be stable"

api/clean-docker:
	@docker system prune -a

##
##----- Infrastructure -----
##

infra/assume-role:		## Assume role to perform infrastructure tasks
	@cd infrastructure/; ./scripts/assume_role.sh

infra/backend:			## Create terraform backend for infrastructure
	@cd infrastructure/; ./scripts/infra_make_helper.sh create_backend

infra/init:			## Terraform init: make infra/init block=<infra/block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_init "${block}"

infra/plan:			## Terraform view infrastructure changes: make infra/plan block=<infra/block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf plan "${block}" "${env}"

infra/apply:			## Terraform apply infrastructure changes: make infra/apply block=<infra/block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf apply "${block}" "${env}"

infra/destroy:			## Terraform destory entire infrastructure: make infra/destroy block=<infra/block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf destroy "${block}" "${env}"

infra/output:			## Print infrastructure output: make infra/output block=<infra/block>
	@cd infrastructure/; ./scripts/infra_make_helper.sh run_tf output "${block}" "${env}"

infra/scan:			## Print infrastructure output: make infra/output block=<infra/block>
	@cd infrastructure/; checkov -d ./blocks --quiet

##
##----- SDK -----
##

sdk/venv:		## Create the Python virtual environment for the sdk
	@cd sdk/; python3 -m venv .venv


sdk/reqs:		## Install the necessary Python requirements
	@cd sdk/; . .venv/bin/activate; pip install -r requirements.txt

sdk/setup:	sdk/venv sdk/reqs			## Setup Python required for the sdk


# SDK Testing --------------------
##
sdk/test:			## Run sdk unit tests
	@cd sdk/; . .venv/bin/activate; pytest -vv -s

# SDK Release --------------------
##

sdk/clean:		## Clean the environment, removing the previous build
	@cd sdk/; rm -rf ./dist

sdk/build:	sdk/clean		## Re-builds the sdk package
	@cd sdk/; .venv/bin/activate; python setup.py sdist

sdk/release-test:	sdk/build	## Build and release sdk to testpypi
	@cd sdk/; . .venv/bin/activate; twine upload --repository testpypi dist/*

sdk/release:	sdk/build		## Build and release sdk to pypi
	@cd sdk/; . .venv/bin/activate; twine upload dist/*

##
##----- UI -----
##
ui/setup:			## Setup npm required for the sdk
	@cd ui/; npm i -g next; npm ci

ui/run:			## Run the ui application with hot reload
	@cd ui/; npm run dev

# UI Testing --------------------
##
ui/test:			## Test ui site
	@cd ui/; npm run test:all

ui/test-e2e:
	@cd ui/; npx playwright test ui/playwright

ui/test-e2e-headed:
	@cd ui/; npx playwright test ui/playwright --ui

# UI Release --------------------
##
ui/create-static-out:
	@cd ui/; npm run build:static

ui/zip-contents:		## Zip contents of the built static html files
ifdef tag
	@cd ui/; zip -r "${tag}.zip" ./out
	@cd ui/; zip -r "${tag}-router-lambda.zip" ./lambda/lambda.js
else
	@cd ui/; zip -r "$(UI_ZIP_PATH).zip" ./out
	@cd ui/; zip -r "$(UI_ZIP_PATH)-router-lambda.zip" ./lambda/lambda.js
endif

ui/release:		## Upload the zipped built static files to a production Github release
	@gh release upload ${tag} "./ui/${tag}.zip" --clobber
	@gh release upload ${tag} "./ui/${tag}-router-lambda.zip" --clobber

ui/zip-and-release: ui/zip-contents ui/release ## Zip and release prod static ui site

RELEASE_TYPE_UC=$(shell echo ${type} | tr  '[:lower:]' '[:upper:]')
release:
	@python release.py --operation check --type ${type}
	@git checkout ${commit}
	@git tag -a "${version}" -m "Release tag for version ${version}"
	@git checkout -
	@git push origin ${version}
	@python release.py --operation create-changelog --type ${type}
	@gh release create ${version} -F latest_release_changelog_${type}.md -t "$(RELEASE_TYPE_UC): ${version}"
	@rm -rf latest_release_changelog_${type}.md

# Migration --------------------
##
migrate-v7:			## Run the migration
	@cd api/; . .venv/bin/activate; python migrations/scripts/v7_layer_migration.py --layer ${layer} --all-layers ${all-layers}

serve-docs:
	mkdocs serve
