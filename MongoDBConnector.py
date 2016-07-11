import pymongo
import os
from pymongo import MongoClient


class MongoDBConnector:
    """MongoDBConnector opens a Mongo DB connection. Different functions allow you to add, delete or update documents
    in Mongo DB."""

    def __init__(self):
        """Connecting to localhost (default host and port [localhost, 27017]) MongoDB and initializing needed data
            base and collections."""
        self.__id = 0
        try:
            self.__client = MongoClient()
            print("Mongo DB connection successfully built...")
        except Exception:
            # TODO own exception
            print("Mongo DB connection could not be built...")

        self.__db = self.__client.database
        self.delete_previous_results()
        self.__db.dostojewski.create_index([('id', pymongo.ASCENDING)], unique=True)
        self.__db.snippets.create_index([('text_snippet_id', pymongo.ASCENDING)], unique=True)
        self.__db.pattern.create_index([('pattern_id', pymongo.ASCENDING)], unique=True, sparse=True)
        self.__db.single_pattern.create_index([('single_pattern_id', pymongo.ASCENDING)], unique=True, sparse=True)

    def read_in_file(self, filename):
        """Read in file and return file content as string."""
        with open(filename, 'r') as file:
            return file.read()

    def add_articles(self, file_directory):
        """Add one article into database."""
        for file in os.listdir(file_directory):
            if file.endswith(".txt"):
                article = {"id": self.__id,
                           "title": os.path.splitext(os.path.basename(file))[0],
                           "text": self.read_in_file(file_directory + file)}
                self.__db.dostojewski.insert_one(article)
                self.__id += 1

    def delete_previous_results(self):
        self.__db.snippets.delete_many({})
        self.__db.pattern.delete_many({})
        self.__db.single_pattern.delete_many({})
        self.__db.single_pattern_snippets.delete_many({})
        self.__db.aggregation.delete_many({})

    def delete_all(self):
        self.__db.dostojewski.delete_many({})
        self.delete_previous_results()

