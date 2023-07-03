# rAPId UI

<img src="https://github.com/no10ds/rapid-api/blob/main/logo.png?raw=true" display=block margin-left=auto margin-right=auto width=60%;/>

The rAPId service allows users to ingest, validate and query data via an API. This repo provides the user interface service for rAPId version >= 5.0

<br />
<p align="center">
<a href="https://ukgovernmentdigital.slack.com/archives/C03E5GV2LQM"><img src="https://user-images.githubusercontent.com/609349/63558739-f60a7e00-c502-11e9-8434-c8a95b03ce62.png" width=160px; /></a>
</p>

# About

Since rAPId version 5.0 the user interface to interact with the API was seperated into it's own service. The user interface is compiled and built to static html files and hosted through a Cloud Delivery Network (CDN).

# Tech Stack 🍭

- Typescript
- NodeJs
- NextJs

# Developing

This is a quick guide to running the rAPId UI locally for development. For greater details please see the [Contributing README](CONTRIBUTING.md)

## Prerequisites

Install all the required tools

- [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm#installing-and-updating)
- Install and use the required version of node `nvm use`

Install the packages and pre-commit hooks.

1. Install packages & husky `make npm-setup`

## Running Locally 🏃‍♂️

Copy over the `.env.example` file into a seperate `.env.local` file and then populate the environment variable to point the api url to your current running rAPId api. To get authentication working you will need the relevant `rat` cookie stored in the browser.

To run the app locally you can then run `make dev`.

## Local environment variables

Use the below to proxy to a third party auth server

```
NEXT_PUBLIC_API_URL=/myapi
NEXT_PUBLIC_API_URL_PROXY=https://some-apiurl-from-another-server #optional for local development only
```
