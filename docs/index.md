# Welcome to rAPId

Project rAPId aims to create consistent, secure, interoperable data storage and sharing interfaces (APIs) that enable departments to discover, manage and share data and metadata amongst themselves.

Pioneered by 10 Downing Street rAPId aims to improve the government's use of data by making it more scalable, secure, and resilient, helping to match the rising demand for good-quality evidence in the design, delivery, and evaluation of public policy.

The project aims to deliver a replicable template for simple data storage infrastructure in AWS, a RESTful API and custom frontend UI to ingest and share named, standardised datasets.

# rAPId Structure

rAPId aims to deliver a suite of products that can be used together to deliver a replicable template for simple data storage infrastructure in AWS, a RESTful API and custom frontend UI to ingest and share named, standardised datasets.

Alongside this a Python sdk to make interacting with the API using common data manipulation tools such as Pandas easier.

rAPId is a monorepo containing all the different rapid services and products. Each standalone product is developed separately but then released together as the entire rAPId ecosystem.

## API

The rAPId API is a RESTful API built using FastAPI and Python. It handles all the serving for user management, schema definitions and data storage and retrieval. The overarching API functionality includes:

- Upload a schema (i.e.: creating a new dataset definition)
- Uploading data to any version of a dataset
- Listing available data
- Querying data from any version of a dataset
- Deleting data
- Creating users and clients
- Managing user and client permissions

## Infrastructure

The rAPId infrastructure is a set of Terraform modules that creates all the initial AWS resources required to deploy a rAPId instance. This service can deploy a rAPId service either on top of your existing AWS infrastructure or from scratch typically in a new AWS account.

## UI

Whilst rAPId is designed to be a RESTful API, a UI is provided to make it easier to interact with the API. The UI is built using NextJS and Typescript and is designed to be deployed as a static site and hosted through a Cloud Delivery Network (CDN) deployed from the infrastructure.

## SDK

The rAPId SDK is a lightweight Python wrapper around the API. It provides easy programmatic access to the core rAPId functionality and provides a set of common patterns when using rAPId with common data manipulation tools such as Pandas.
