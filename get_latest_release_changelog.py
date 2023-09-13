import re

with open("./docs/changelog.md", "r") as changelog_file:
    changelog_lines = changelog_file.readlines()

parsed_lines = []

adding = False

for line in changelog_lines:
    if re.match(
        # Match for the release version number e.g. ## v7.0.0
        f"##\s+v\d+\.\d+\.\d+",  # noqa: F541
        line,
    ):
        adding = not adding
    if adding:
        parsed_lines.append(line)

if not parsed_lines:
    raise Exception(
        "It looks like there is no release information in the changelog. Please check it."
    )
else:
    with open("latest_release_changelog.md", "w+") as latest_changelog:
        latest_changelog.writelines(parsed_lines)
