import re
import argparse


def create_changelog(type):
    with open(f"./docs/changelog/{type}.md", "r") as changelog_file:
        changelog_lines = changelog_file.readlines()

    parsed_lines = []

    adding = False

    for line in changelog_lines:
        if re.match(
            # Match for the release version number e.g. ## v7.0.0
            f"##\s+v\d+\.\d+\.\d+",  # noqa: F541, W605
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
        with open(f"latest_release_changelog_{type}.md", "w+") as latest_changelog:
            latest_changelog.writelines(parsed_lines)


def ask_yes_no_question(question):
    while True:
        answer = input(f"{question} (yes/no): ").strip().lower()
        if answer == "yes" or answer == "y":
            return True
        elif answer == "no" or answer == "n":
            print("Please fix this before continuing.")
            exit(1)
        else:
            print("Please answer yes or no.")


def check(type):
    if type == "api":
        ask_yes_no_question("Have you updated the API, UI and Terraform version?")
        ask_yes_no_question("Have you updated the changelog for this release?")
    elif type == "sdk":
        ask_yes_no_question("Have you updated the changelog for this release?")
        ask_yes_no_question("Have you updated the SDK?")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--operation",
        help="The operation to carry out",
        required=True,
        choices=["check", "create-changelog"],
    )

    parser.add_argument(
        "--type",
        help="What are you releasing?",
        required=True,
        choices=["api", "sdk"],
    )

    args = parser.parse_args()

    match args.operation:
        case "create-changelog":
            create_changelog(args.type)
        case "check":
            check(args.type)
