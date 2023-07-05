IMAGE_NAME=ui-f1-registry
LATEST_COMMIT_HASH=$(shell git rev-parse --short HEAD)
ZIP_PATH=$(IMAGE_NAME)-$(LATEST_COMMIT_HASH)

LATEST_TAG=$(shell gh api /repos/no10ds/rapid-ui/releases/latest | jq -r ".tag_name")
ifeq ($(LATEST_TAG), null)
	TAG_NAME="$(IMAGE_NAME)-$(LATEST_COMMIT_HASH)"
else
	TAG_NAME="$(LATEST_TAG)-dev-$(LATEST_COMMIT_HASH)"
endif

help:	## List targets and description
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

zip-contents:		## Zip contents of the built static html files
ifdef tag
	@zip -r "${tag}.zip" ./out
	@zip -r "${tag}-router-lambda.zip" ./lambda/lambda.js
else
	@zip -r "$(ZIP_PATH).zip" ./out
	@zip -r "$(ZIP_PATH)-router-lambda.zip" ./lambda/lambda.js
endif

upload-to-release:	## Upload the zipped built static files to a Github draft release
	@gh release create [] "$(ZIP_PATH).zip" --draft --title "$(TAG_NAME)" --notes ""
	@gh release create [] "$(ZIP_PATH)-router-lambda.zip" --draft --title "$(TAG_NAME)" --notes ""

upload-to-release-prod:	## Upload the zipped built static files to a production Github release
	@gh release upload ${tag} "${tag}.zip" --clobber
	@gh release upload ${tag} "${tag}-router-lambda.zip" --clobber

create-static-out: 	## Manually create the static files
	@npm run build:static
