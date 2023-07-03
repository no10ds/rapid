.PHONY: help

help: 		## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##
init-hooks:
	git config core.hooksPath .githooks

assume-role:	## assume role to perform infra tasks
	@./scripts/assume_role.sh

init:		## terraform init: make init block=<infra-block>
	@./scripts/infra_make_helper.sh run_init "${block}"

precommit-block: 	## tf format and validate: make precommit-blocks block=<infra-block>
	@./scripts/infra_make_helper.sh precommit "${block}" "${env}"

precommit-blocks: 	## .... for all the infra blocks
	@printf "infra validation auth: " && $(MAKE) precommit-block "block=auth"
	@printf "infra validation s3: " && $(MAKE) precommit-block "block=s3"
	@printf "infra validation iam-config: " && $(MAKE) precommit-block "block=iam-config"
	@printf "infra validation app-cluster: " && $(MAKE) precommit-block "block=app-cluster"
	@printf "infra validation ecr: " && $(MAKE) precommit-block "block=ecr"
	@printf "infra validation pipeline: " && $(MAKE) precommit-block "block=pipeline"
	@printf "infra validation vpc: " && $(MAKE) precommit-block "block=vpc"
	@printf "infra validation ui:" && $(MAKE) precommit-block "block=ui"

precommit-module: 	## tf docs: make precommit-module module=<infra-module>
	terraform-docs markdown table modules/"${module}" --output-file README.md

precommit-modules: 	## .... for all the infra blocks
	@printf "updating docs app-cluster: " && $(MAKE) precommit-module "module=app-cluster"
	@printf "updating docs auth: " && $(MAKE) precommit-module "module=auth"
	@printf "updating docs data-workflow: " && $(MAKE) precommit-module "module=data-workflow"
	@printf "updating docs rapid: " && $(MAKE) precommit-module "module=rapid"
	@printf "updating docs ui:" && $(MAKE) precommit-module "module=ui"

plan: 		## plan - view infra changes: make plan block=<infra-block>
	@./scripts/infra_make_helper.sh run_tf plan "${block}" "${env}"

apply: 		## apply infra changes: make apply block=<infra-block>
	@./scripts/infra_make_helper.sh run_tf apply "${block}" "${env}"

destroy: 		## destroy infra: make destroy block=<infra-block>
	@./scripts/infra_make_helper.sh run_tf destroy "${block}" "${env}"

output: 		## prints infra output: make output block=<infra-block>
	@./scripts/infra_make_helper.sh run_tf output "${block}" "${env}"

detect-secrets: 		## Check source code for possible secrets
	@./batect detect-secrets

ignore-secrets: 		## Mark detected non-secrets as ignored
	@./batect ignore-secrets

backend: 		## create terraform backend infrastructure
	@./scripts/infra_make_helper.sh create_backend

release:       ## Release
	@git checkout ${commit}
	@git tag -a "${version}" -m "Release tag for version ${version}"
	@git checkout -
	@git push origin ${version}
	@./batect generate_latest_changelog
	@gh release create ${version} -F latest_release_changelog.md
	@rm -rf latest_release_changelog.md
