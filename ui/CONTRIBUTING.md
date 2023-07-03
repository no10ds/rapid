# Contributing

## Developing 🤓

To maintain a consistent version of node across machines we use node version manager. Once this is installed you can install the correct version of node for this project using the command

```
nvm use
```

By default the application checks for a valid rAPId access token (rat) cookie, if this is not available you will be redirected to the login page. When developing locally to bypass this you need to generate a valid rat token and place this as a cookie in both the frontend and in the api.

## Testing

By default precommit hooks are setup using husky to automatically lint the project and run the ui unit tests.

To run them all you can use the command `make test`

## Releasing

### Context

The product of the rAPId UI is a set of complete static HTML files that using the provided [infrastructure](https://github.com/no10ds/rapid-infrastructure) can be deployed and served alongside the API.

Performing a release requires tagging the repository with the specific version and then building a zip of the static html files that can be served within a GitHub release. 

⚠️ When releasing a new version of the service, you must also release a version of
the [api](https://github.com/no10ds/rapid-api) [infrastructure](https://github.com/no10ds/rapid-infrastructure) and vice versa. All versions should be the same (
i.e.: all vX.Y.Z). If there are no changes in one or the others repo, it should still be released along with the other
and a tag added to the same commit as the previous release. This ensures that the version numbers signal the
compatibility between all the elements.

### Steps

1. Decide on the new version number following the [semantic versioning approach](https://semver.org)
2. Update and commit the [Changelog](CHANGELOG.md) (you can follow the [template](changelog_release_template.md))
3. Run `make release commit=<commit_hash> version=vX.X.X`

> ⚠️ Ensure the version number follows the format `vX.X.X` with full-stops in the same places.

Now the release pipeline will run automatically, this will build the static html files, zip them and upload them to the release tag in GitHub.