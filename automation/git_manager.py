import subprocess


def commit_and_push():

    subprocess.run(["git", "add", "."])

    subprocess.run(["git", "commit", "-m", "Knowledge Base Update"])

    subprocess.run(["git", "push"])