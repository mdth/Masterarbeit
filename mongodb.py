################################
#
# MongoDB Initialisation
#
################################

import pymongo
import os
from pymongo import MongoClient

id = 0


def connecting_to_db():
    # os.system("start /wait cmd /c {C:/MongoDB/bin mongod}")

    """Connecting to localhost (default host and port [localhost, 27017]) MongoDB and initializing needed data
    base and collections."""
    client = MongoClient()

    print("DB connection sucessfully built...")

    global db
    db = client.database
    db.dostojewski.create_index([('id', pymongo.ASCENDING)], unique=True)
    db.snippets.create_index([('text_snippet_id', pymongo.ASCENDING)], unique=True)
    db.pattern.create_index([('pattern_id', pymongo.ASCENDING)], unique=True, sparse=True)
    db.single_pattern.create_index([('single_pattern_id', pymongo.ASCENDING)], unique=True, sparse=True)


def read_in_file(filename):
    """Read in file and return file content as string."""
    with open(filename, 'r') as file:
        return file.read()


def add_articles(file_directory):
    """Add one article into database."""
    for file in os.listdir(file_directory):
        if file.endswith(".txt"):
            global id
            article = {"id": id,
                       "title": os.path.splitext(os.path.basename(file))[0],
                       "text": read_in_file(file_directory + file)}
            db.dostojewski.insert_one(article)
            id += 1


def delete_previous_results():
    db.dostojewski.delete_many({})

connecting_to_db()
delete_previous_results()
add_articles("C:/Users/din_m/PycharmProjects/Masterarbeit/Der Idiot/")
print("Successfully added files into the database.")
