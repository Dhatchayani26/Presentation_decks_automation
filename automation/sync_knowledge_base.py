import os
import re
import subprocess
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


# ============================================================
# CONFIG
# ============================================================

# Only the document ID, NOT the full URL
GOOGLE_DOC_ID = "1L1nzyLF2CkZ4POnhI-WNUUiGKfuXlGGQp_ZLW0SAgv8"

SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

ROOT = Path(__file__).resolve().parent.parent

CREDENTIALS = ROOT / "credentials.json"

OUTPUT_DIR = ROOT / "knowledge_base"

OUTPUT_FILE = OUTPUT_DIR / "ACKOInsurance.md"

STATE_FILE = OUTPUT_DIR / "logs" / "ACKOInsurance.modified_time.txt"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# GOOGLE AUTH
# ============================================================

def get_credentials():

    return service_account.Credentials.from_service_account_file(
        CREDENTIALS,
        scopes=SCOPES
    )


def get_docs_service():

    return build(
        "docs",
        "v1",
        credentials=get_credentials(),
        cache_discovery=False
    )


# ============================================================
# GOOGLE DOC
# ============================================================

def fetch_document():

    drive = build(
        "drive",
        "v3",
        credentials=get_credentials(),
        cache_discovery=False
    )

    file = drive.files().get(
        fileId=GOOGLE_DOC_ID,
        fields="id,name,mimeType,modifiedTime"
    ).execute()

    document = get_docs_service().documents().get(
        documentId=GOOGLE_DOC_ID
    ).execute()

    document["title"] = file.get("name", document.get("title", ""))
    document["modifiedTime"] = file.get("modifiedTime", "")

    return document


def load_last_modified_time():

    if not STATE_FILE.exists():
        return ""

    return STATE_FILE.read_text(encoding="utf-8").strip()


def save_last_modified_time(modified_time):

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(modified_time, encoding="utf-8")

# ============================================================
# MARKDOWN HELPERS
# ============================================================

def clean_text(text):

    return (
        text.replace("\v", "")
            .replace("\r", "")
            .rstrip()
    )


def apply_text_style(text, style):

    if not text:
        return ""

    if style.get("bold"):
        text = f"**{text}**"

    if style.get("italic"):
        text = f"*{text}*"

    if style.get("strikethrough"):
        text = f"~~{text}~~"

    if style.get("underline"):
        text = f"<u>{text}</u>"

    if style.get("link"):

        url = style["link"]["url"]

        text = f"[{text}]({url})"

    return text


def paragraph_text(paragraph):

    text = ""

    for element in paragraph.get("elements", []):

        run = element.get("textRun")

        if not run:
            continue

        content = clean_text(run.get("content", ""))

        if not content:
            continue

        style = run.get("textStyle", {})

        text += apply_text_style(content, style)

    return text


def heading_prefix(style):

    mapping = {
        "TITLE": "# ",
        "SUBTITLE": "## ",
        "HEADING_1": "# ",
        "HEADING_2": "## ",
        "HEADING_3": "### ",
        "HEADING_4": "#### ",
        "HEADING_5": "##### ",
        "HEADING_6": "###### "
    }

    return mapping.get(style, "")

# ============================================================
# TABLES
# ============================================================

def table_to_markdown(table):

    rows = []

    for row in table.get("tableRows", []):

        cols = []

        for cell in row.get("tableCells", []):

            value = ""

            for content in cell.get("content", []):

                if "paragraph" not in content:
                    continue

                value += paragraph_to_markdown(
                    content["paragraph"]
                ).strip()

            cols.append(value)

        rows.append(cols)

    if not rows:
        return ""

    md = []

    md.append("| " + " | ".join(rows[0]) + " |")

    md.append(
        "| "
        + " | ".join(["---"] * len(rows[0]))
        + " |"
    )

    for row in rows[1:]:

        md.append("| " + " | ".join(row) + " |")

    return "\n".join(md)


# ============================================================
# PARAGRAPH -> MARKDOWN
# ============================================================

def paragraph_to_markdown(paragraph):

    text = paragraph_text(paragraph).strip()

    if not text:
        return ""

    style = paragraph.get(
        "paragraphStyle",
        {}
    ).get(
        "namedStyleType",
        "NORMAL_TEXT"
    )

    prefix = heading_prefix(style)

    if prefix:
        return prefix + text

    if "bullet" in paragraph:

        level = paragraph["bullet"].get(
            "nestingLevel",
            0
        )

        return ("  " * level) + "- " + text

    return text


# ============================================================
# GOOGLE DOC -> MARKDOWN
# ============================================================

def document_to_markdown(document):

    markdown = []

    body = document["body"]["content"]

    for element in body:

        # Paragraphs
        if "paragraph" in element:

            line = paragraph_to_markdown(
                element["paragraph"]
            )

            if line:

                markdown.append(line)
                markdown.append("")

        # Tables
        elif "table" in element:

            markdown.append(
                table_to_markdown(
                    element["table"]
                )
            )

            markdown.append("")

        # Horizontal separator
        elif "sectionBreak" in element:

            markdown.append("---")
            markdown.append("")

    while markdown and markdown[-1] == "":
        markdown.pop()

    return "\n".join(markdown)


# ============================================================
# SAVE MARKDOWN
# ============================================================

def save_markdown(document):

    markdown = document_to_markdown(
        document
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(markdown)

    print(f"Saved: {OUTPUT_FILE}")

# ============================================================
# GIT
# ============================================================

def push_to_github():

    try:

        subprocess.run(
            ["git", "add", "."],
            check=True
        )

        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"]
        )

        if diff.returncode == 0:

            print("No changes detected.")

            return

        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "Knowledge Base Sync"
            ],
            check=True
        )

        subprocess.run(
            ["git", "push"],
            check=True
        )

        print("GitHub updated successfully.")

    except subprocess.CalledProcessError as e:

        print("Git operation failed.")

        print(e)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("Knowledge Base Sync")
    print("=" * 60)

    print("Fetching Google Document...")

    document = fetch_document()

    modified_time = document.get("modifiedTime", "")
    last_modified_time = load_last_modified_time()

    if modified_time and modified_time == last_modified_time:
        print("No document changes detected.")
        return

    print(f"Title : {document.get('title', document.get('name', ''))}")

    print("Converting to Markdown...")

    save_markdown(document)

    print("Uploading to GitHub...")

    push_to_github()

    if modified_time:
        save_last_modified_time(modified_time)

    print("\nDone.")


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()