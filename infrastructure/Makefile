.PHONY: help

help: 		## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##
assume-role:	## assume role to perform infra tasks
	@./scripts/assume_role.sh

init:		## terraform init: make init block=<infra-block>
	@./scripts/infra_make_helper.sh run_init "${block}"

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
