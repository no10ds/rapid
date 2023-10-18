venv:
	python3 -m venv .venv
	. .venv/bin/activate

reqs:
	pip install -r requirements.txt
	@echo "========================"
	@echo "Virtual environment successfully created. To activate the venv:"
	@echo "	\033[0;32msource sdk/.venv/bin/activate"

cleanup:
	rm -rf ./dist

build:
	python3 setup.py sdist

deploy:
	$(MAKE) cleanup
	$(MAKE) build
	twine upload dist/*

deploy-test:
	$(MAKE) cleanup
	$(MAKE) build
	twine upload --repository testpypi dist/*
