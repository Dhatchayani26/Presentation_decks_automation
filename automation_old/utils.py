import re


def slugify(name: str) -> str:

    name = name.lower().strip()

    name = re.sub(r"[^a-z0-9]+", "-", name)

    return name.strip("-")