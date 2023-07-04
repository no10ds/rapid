release:       ## Release
	@git checkout ${commit}
	@git tag -a "${version}" -m "Release tag for version ${version}"
	@git checkout -
	@git push origin ${version}
	@./batect generate_latest_changelog
	@gh release create ${version} -F latest_release_changelog.md
	@rm -rf latest_release_changelog.md
