from pathlib import Path


def update_section(file_path: Path, section: str, content: str):

    text = file_path.read_text(encoding="utf-8")

    start = f"<!-- {section}_START -->"
    end = f"<!-- {section}_END -->"

    start_idx = text.find(start)
    end_idx = text.find(end)

    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"{section} markers not found")

    start_idx += len(start)

    new_text = (
        text[:start_idx]
        + "\n"
        + content.strip()
        + "\n"
        + text[end_idx:]
    )

    file_path.write_text(new_text, encoding="utf-8")