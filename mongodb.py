################################
#
# MongoDB Initialisation
#
################################

import pymongo
import os
import codecs
from pymongo import MongoClient

id = 0


def connecting_to_db():
    # os.system("start /wait cmd /c {C:/MongoDB/bin mongod}")

    """Connecting to localhost MongoDB and initializing needed data base and collections."""
    # default host and port (localhost, 27017)
    client = MongoClient()

    print("DB connection sucessfully built...")

    global db
    db = client.database
    fackel_corpus = db.fackel_corpus #collection
    db.fackel_corpus.create_index([('id', pymongo.ASCENDING)], unique=True)
    
    text_snippets = db.text_snippets
    db.text_snippets.create_index([('text_snippet_id', pymongo.ASCENDING)], unique=True)  
    
    pattern = db.pattern
    db.pattern.create_index([('pattern_id', pymongo.ASCENDING)], unique=True, sparse=True)
    
    single_pattern = db.single_pattern
    db.single_pattern.create_index([('single_pattern_id', pymongo.ASCENDING)], unique=True, sparse=True)
    
    # pattern_snippets = db.pattern_snippets
    single_pattern_snippets = db.single_pattern_snippets
    aggregation = db.aggregation


def read_in_file(filename):
    """Read in file and return file content as string."""
    with open(filename, 'rb') as file:
        return file.read()


def add_articles(file_directory):
    """Add one article into database."""
    for file in os.listdir(file_directory):
        if file.endswith(".txt"):
            global id
            article = {"id": id,
                       "title": os.path.splitext(os.path.basename(file))[0],
                       "text": read_in_file(file_directory + file)}
            db.fackel_corpus.insert_one(article)
            id += 1


connecting_to_db()
add_articles("C:/Users/din_m/PycharmProjects/Masterarbeit/test/")

for a in db.fackel_corpus.find():
    print(a)