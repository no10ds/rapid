import re

with open("CHANGELOG.md", "r", encoding="utf-8") as changelog_file:
    changelog_lines = changelog_file.readlines()

parsed_lines = []

adding = False

for line in changelog_lines:
    if re.match(
        f"##\\sv\\d+\\.\\d+\\.\\d+\\s-\\s_\\d{{4}}-\\d{{2}}-\\d{{2}}_$",  # noqa: F541
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
    with open(
        "latest_release_changelog.md", "w+", encoding="utf-8"
    ) as latest_changelog:
        latest_changelog.writelines(parsed_lines[4:])
