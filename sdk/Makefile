-include .env
export
PYTHON_VERSION=3.10.6

# Setup commands

python:
	pyenv install --skip-existing $(PYTHON_VERSION)
	echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
	pyenv local $(PYTHON_VERSION)

precommit:
	pre-commit install

venv:
	python3 -m venv .venv
	. .venv/bin/activate
	make reqs

reqs:
	pip install -r requirements.txt

setup: python precommit venv

test:
	pytest -vv -s

# Deploy the package
release:
	git checkout ${commit}
	git tag -a "${version}" -m "Release tag for version ${version}"
	git checkout -
	git push origin ${version}
	python get_latest_release_changelog.py
	@gh release create ${version} -F latest_release_changelog.md
	rm -rf latest_release_changelog.md

deploy/pypi:
	rm -rf ./dist
	python3 setup.py sdist
	twine upload dist/*

deploy/test:
	rm -rf ./dist
	python3 setup.py sdist
	twine upload --repository testpypi dist/*

documentation/build:
	cd ./docs && $(MAKE) html

documentation/serve:
	python -m http.server --directory ./docs/build/html
