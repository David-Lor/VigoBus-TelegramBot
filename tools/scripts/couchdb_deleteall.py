"""COUCHDB DELETE ALL
Deletes all the documents in a CouchDB database.
"""

import argparse
from couchdb import Server


def confirm_action():
    while True:
        response = input("Are you sure you want to delete all documents in the database? (y/n): ").strip().lower()
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            print("Please respond with 'y' or 'n'.")


def delete_all_documents(url, username, password, db_name):
    try:
        server = Server(url)
        server.resource.credentials = (username, password)
        db = server[db_name]
        if confirm_action():
            for doc_id in db:
                del db[doc_id]
            print("All documents in the database '{}' have been successfully deleted.".format(db_name))
        else:
            print("Operation canceled.")
    except Exception as e:
        print("Error:", e.__class__.__name__, e)


def main():
    parser = argparse.ArgumentParser(description="Delete all documents in a CouchDB database.")
    parser.add_argument("--url", help="URL of the CouchDB database", required=True)
    parser.add_argument("--username", help="Username to access the database", required=True)
    parser.add_argument("--password", help="Password to access the database", required=True)
    parser.add_argument("--database", help="Name of the CouchDB database", required=True)
    args = parser.parse_args()

    delete_all_documents(args.url, args.username, args.password, args.database)


if __name__ == "__main__":
    main()
