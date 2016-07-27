import pymongo
import os
from pymongo import MongoClient


class MongoDBConnector:
    """MongoDBConnector opens a Mongo DB connection. Different functions allow you to add, delete or update documents
    in Mongo DB."""

    def __init__(self):
        """Connecting to localhost (default host and port [localhost, 27017]) MongoDB and initializing needed data
            base and collections."""
        self.__id = 1
        try:
            self.__client = MongoClient()
            # TODO only throws exception if system can't access database...
            print("Mongo DB connection successfully built...")
        except Exception:
            # TODO own exception
            print("Mongo DB connection could not be built...")

        self.__db = self.__client.database
        self.delete_all()
        self.add_articles("C:/Users/din_m/PycharmProjects/Masterarbeit/Der Idiot/")
        self.__db.dostojewski.create_index([('id', pymongo.ASCENDING)], unique=True)

    def add_articles(self, file_directory):
        """Add one article into database."""
        for file in os.listdir(file_directory):
            if file.endswith(".txt"):
                article = {"id": self.__id,
                           "title": os.path.splitext(os.path.basename(file))[0],
                           "text": read_in_txt_file(file_directory + file)}
                self.__db.dostojewski.insert_one(article)
                self.__id += 1

    def delete_all(self):
        self.__db.dostojewski.delete_many({})

    def get(self, search_term):
        return self.__db.dostojewski.find(search_term)


def read_in_txt_file(filename):
    """Read in file and return file content as string."""
    if not filename.endswith(".txt"):
        raise Exception("Invalid file format.")

    with open(filename, 'r') as file:
        return file.read()