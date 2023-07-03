import re
from typing import List


def parse_categorisation(
    path: str, categories: List[str], category_name: str = "categorisation"
) -> str:
    match = re.findall(rf"({'|'.join(categories)})", path)
    if match:
        return match[0]
    else:
        raise ValueError(f"Could not find {category_name}")
