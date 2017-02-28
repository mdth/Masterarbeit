import unittest
from PMI.Parser import Parser
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector


class TestGermanParser(unittest.TestCase):
    mongodb = MongoDBConnector()
    postgredb = PostGreDBConnector()
    parser = Parser()

    ## Unit test
    # german pos tagger is using universal tags !
    # getting the format of NLTK pos tags !
    # tags =[(t.orth_,t.pos_) for t in doc]

    @unittest.skip("need to break these up")
    def test1(self):
        # adjective as an attribute to a subject
        doc1 = self.parser.nlp("Schöne Mädchen und hübsche Jungen sitzen auf der gelben Bank.")
        doc2 = self.parser.nlp("Der kleine Hase heißt Max.")
        doc3 = self.parser.nlp("Mein kleiner Hase.")
        doc4 = self.parser.nlp("Der kleine, süße Hase war auf dem Weg nach Hause.")
        doc5 = self.parser.nlp("Der kleine und süße Hase war Marias Haustier.")
        doc6 = self.parser.nlp("Der kleine, aber freche Hase wusste wie er sich zu wehren hatte.")
        doc7 = self.parser.nlp("Der Hase ist klein, aber kein Kuscheltier.")
        doc8 = self.parser.nlp("Eine bahnbrechende physikalische Entdeckung wurde letztes Jahr auf der Messe X vorgestellt.")
        doc9 = self.parser.nlp("Ein kleiner Hase.")

        print(list(doc1.noun_chunks))
        print(list(doc2.noun_chunks))
        print(list(doc3.noun_chunks))
        print(list(doc4.noun_chunks))
        print(list(doc5.noun_chunks))
        print(list(doc6.noun_chunks))
        print(list(doc7.noun_chunks))
        print(list(doc8.noun_chunks))
        print(list(doc9.noun_chunks))
        print("-------------")

        print("1")
        for i in self.parser.nouns_adj_spacy(doc1):
            print(i)
        print("2")
        for i in self.parser.nouns_adj_spacy(doc2):
            print(i)
        print("3")
        for i in self.parser.nouns_adj_spacy(doc3):
            print(i)
        print("4")
        for i in self.parser.nouns_adj_spacy(doc4):
            print(i)
        print("5")
        for i in self.parser.nouns_adj_spacy(doc5):
            print(i)
        print("6")
        for i in self.parser.nouns_adj_spacy(doc6):
            print(i)
        print("7")
        for i in self.parser.nouns_adj_spacy(doc7):
            print(i)
        print("8")
        for i in self.parser.nouns_adj_spacy(doc8):
            print(i)
        print("9")
        for i in self.parser.nouns_adj_spacy(doc9):
            print(i)
        tags1 = [(t.orth_, t.pos_) for t in doc1]
        for i in self.parser.get_adjs(tags1):
            print(i)
        tags3 = [(t.orth_, t.pos_) for t in doc3]
        for i in self.parser.get_adjs(tags3):
            print(i)

    def test2(self):
        doc = self.parser.nlp("Der kleine Hase heißt Max.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        self.assertListEqual([{'noun': 'Hase', 'adj': 'klein'}], result_spacy)
        self.assertListEqual([{'noun': 'Hase', 'adj': 'klein'}], result_regex)

    def test3(self):
        doc = self.parser.nlp("Schöne Mädchen und hübsche Jungen sitzen auf der gelben Bank.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_regex_result = [{'noun': 'Mädchen', 'adj': 'schön'}, {'noun': 'Jungen', 'adj': 'hübsch'}, {'noun': 'Bank', 'adj': 'gelb'}]
        self.assertListEqual(expected_regex_result, result_spacy)
        # self.assertListEqual([{'noun': 'Hase', 'adj': 'kleine'}], result_regex)

    def test4(self):
        doc = self.parser.nlp("Der kleine, süße Hase war auf dem Weg nach Hause.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_regex_result = [{'noun': 'Hase', 'adj': 'süß'}, {'noun': 'Hase', 'adj': 'süß'}]
        self.assertListEqual(expected_regex_result, result_spacy)
        self.assertListEqual([{'noun': 'Hase', 'adj': 'kleine'}], result_regex)

    def test5(self):
        doc = self.parser.nlp("Der kleine und süße Hase war Marias Haustier.")
        result_spacy = list(self.parser.nouns_adj_spacy(doc))
        tags = [(t.orth_, t.pos_) for t in doc]
        result_regex = list(self.parser.get_adjs(tags))
        expected_regex_result = [{'noun': 'Hase', 'adj': 'klein'}, {'noun': 'Hase', 'adj': 'süß'}]
        self.assertListEqual(expected_regex_result, result_spacy)
        self.assertListEqual([{'noun': 'Hase', 'adj': 'kleine'}], result_regex)