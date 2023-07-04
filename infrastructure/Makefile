.PHONY: help

help: 		## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##
detect-secrets: 		## Check source code for possible secrets
	@./batect detect-secrets

ignore-secrets: 		## Mark detected non-secrets as ignored
	@./batect ignore-secrets

release:       ## Release
	@git checkout ${commit}
	@git tag -a "${version}" -m "Release tag for version ${version}"
	@git checkout -
	@git push origin ${version}
	@./batect generate_latest_changelog
	@gh release create ${version} -F latest_release_changelog.md
	@rm -rf latest_release_changelog.md
