from setuptools import setup, find_packages
import os

TEST_SDK_VERSION = os.getenv("TEST_SDK_VERSION")
version = "0.1.7"
setup(
    name="rapid-sdk",
    version=version if TEST_SDK_VERSION is None else f"{version}.{TEST_SDK_VERSION}",
    description="A python sdk for the rAPId API",
    url="https://github.com/no10ds/rapid/tree/main/sdk",  # Originally pointed to a deprecated repo, have updated
    author="Lewis Card",
    author_email="lcard@no10.gov.uk",
    license="MIT",
    packages=find_packages(include=["rapid", "rapid.*"], exclude=["tests"]),
    install_requires=["pandas", "requests", "deepdiff", "pyarrow", "pydantic"],
    include_package_data=True,
)
