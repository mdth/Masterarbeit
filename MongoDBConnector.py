import pymongo
import os
from pymongo import MongoClient
from HelperMethods import read_in_txt_file


class MongoDBConnector:
    """MongoDBConnector opens a Mongo DB connection. Different functions allow you to add, delete or update documents
    in Mongo DB."""

    def __init__(self):
        """Connecting to localhost (default host and port [localhost, 27017]) MongoDB and initializing needed data
            base and collections."""
        self.__id = 1
        try:
            print("Connecting to Mongo DB...")
            self.__client = MongoClient()
            print("Mongo DB connection successfully built.")
        except ConnectionError:
            print("Mongo DB connection could not be built.")

        self.__db = self.__client.database
        self.delete_all("dostojewski")
        self.delete_all("storm")
        self.delete_all("storm_word_window")
        self.delete_all("storm_punctuation")
        self.add_articles("dostojewski", os.getcwd() + "/Der Idiot/")
        self.add_articles("storm_word_window", os.getcwd() + "/Posthuma/")
        self.add_articles("storm_punctuation", os.getcwd() + "/Posthuma/")
        self.add_articles("storm", os.getcwd() + "/Posthuma/")

    def add_articles(self, collection, file_directory):
        """Add one article into database."""
        for file in os.listdir(file_directory):
            if file.endswith(".txt"):
                article = {"id": self.__id,
                           "title": os.path.splitext(os.path.basename(file))[0],
                           "text": read_in_txt_file(file_directory + file)}
                self.__db[collection].insert_one(article)
                self.__id += 1

    def delete_all(self, collection):
        """Delete all db entries in a specific collection."""
        self.__db[collection].delete_many({})

    def get(self, collection, search_term):
        """Get all db entries in a specific collection and the specified search_term."""
        return self.__db[collection].find(search_term)

    def create_collection(self, collection_name):
        self.__db[collection_name].create_index([('id', pymongo.ASCENDING)], unique=True)

    def close_connection(self):
        self.__client.close()
