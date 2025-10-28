import re


def clean_column_name(value: str) -> str:
    """
    AWS Glue has particular requirements for column header formats
    (https://docs.aws.amazon.com/glue/latest/dg/add-classifier.html)

    1. Remove all special characters except underscores
    2. Strip any leading or trailing whitespace
    3. Replace spaces with underscores
    4. Lowercase the text

    """
    return re.sub("[^\\w\\s\\d]+", "", value).strip().replace(" ", "_").lower()
