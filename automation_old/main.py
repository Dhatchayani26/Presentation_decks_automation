from automation.fetch_sheet import fetch_updates


from automation.fetch_sheet import fetch_updates
from automation.processed import is_processed, mark_processed
from automation.registry import project_exists
from automation.create_project import create_project
from automation.update_project import update_project


def main():

    updates = fetch_updates()

    print(f"\nFound {len(updates)} response(s)\n")

    processed = 0
    skipped = 0

    for update in updates:

        if is_processed(update.timestamp):
            print(f"Skipping: {update.project_name}")
            skipped += 1
            continue

        try:
            if project_exists(update.project_name):
                print(f"Updating: {update.project_name}")
                update_project(update)
            else:
                print(f"Creating: {update.project_name}")
                create_project(update)

            mark_processed(update.timestamp)
            processed += 1

        except Exception as e:
            print(f"Error processing {update.project_name}: {e}")

    print("\n========== SUMMARY ==========")
    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")
    print("=============================")


if __name__ == "__main__":
    main()