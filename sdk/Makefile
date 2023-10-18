venv:
	pyenv install --skip-existing $(PYTHON_VERSION)
	echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
	pyenv local $(PYTHON_VERSION)
	pyenv exec python -m venv .venv
	. ./.venv/bin/activate

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
