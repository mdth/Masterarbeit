import pymongo
import nltk
import parsing
from parsing import get_pattern_from_RDF

def connecting_to_DB():
    #os.system("start /wait cmd /c {C:/MongoDB/bin mongod}")
    
    '''Connecting to localhost MongoDB.'''
    # default host and port (localhost, 27017)
    client = MongoClient()
    
    db = client.database
    fackel_corpus = db.fackel_corpus #corpora collection
    text_snippets = db.text_snippets #text snippets collection


get_pattern_from_RDF("C:/Users/din_m/Google Drive/MA/Prototypen/test.rdf")
