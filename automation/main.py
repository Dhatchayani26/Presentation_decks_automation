from automation.fetch_sheet import fetch_updates


def main():

    updates = fetch_updates()

    print(f"\nFound {len(updates)} responses\n")

    for update in updates:

        print("=" * 60)
        print(f"Project Name : {update.project_name}")
        print(f"Client Name  : {update.client_name}")
        print(f"Team Lead    : {update.team_lead}")
        print(f"Project Type : {update.project_type}")
        print(f"New Project? : {update.is_new_project}")
        print(f"Objective    : {update.objective[:80]}...")


if __name__ == "__main__":
    main()