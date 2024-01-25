from setuptools import setup, find_packages
import os

setup(
    name="rapid-sdk",
    version=os.getenv("TEST_SDK_VERSION", "0.1.6"),
    description="A python sdk for the rAPId API",
    url="https://github.com/no10ds/rapid/tree/main/sdk",  # Originally pointed to a deprecated repo, have updated
    author="Lewis Card",
    author_email="lcard@no10.gov.uk",
    license="MIT",
    packages=find_packages(include=["rapid", "rapid.*"], exclude=["tests"]),
    install_requires=["pandas", "requests", "deepdiff", "pyarrow", "pydantic"],
    include_package_data=True,
)
