ECS_SERVICE=rapid-preprod-ecs-service
ECS_CLUSTER=rapid-preprod-cluster
LATEST_COMMIT_HASH=$(shell git rev-parse --short HEAD)
ACCOUNT_ECR_URI=$(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com
IMAGE_NAME=data-f1-registry
PUBLIC_URI=public.ecr.aws
PUBLIC_IMAGE=no10-rapid/api

# Deployment -------------------------
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

# Clean up and reset --------------------
clean-docker: 		## Clean up docker images, containers, volumes
	@docker system prune -a

clean-env: 		## Clean up environment
	@docker image rm -f rapid-api-service-image &&\
	  rm -rf .pytest_cache &&\
	  rm -rf .coverage &&\
	  rm -rf venv

clean-slate: 		## Runs clean-env  and clean-docker
	@$(MAKE) clean-docker && $(MAKE) clean-env
