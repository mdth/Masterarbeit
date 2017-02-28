import unittest

from Prototype import Prototype
from MongoDBConnector import MongoDBConnector
from PostGreDBConnector import PostGreDBConnector


class TestPrototype(unittest.TestCase):
    mongodb = MongoDBConnector()
    postgredb = PostGreDBConnector()

    def setUp(self):
        self.Prototype = Prototype(mongo_db=self.mongodb, postagger="spacy-tagger", postgre_db=self.postgredb,
                                   sentence_mode=False, window_size=1)

    def test_change_window_size(self):
        self.Prototype.change_window_size(4)
        self.assertEqual(self.Prototype.get_window_size(), 4)
        with self.assertRaises(ValueError):
            self.Prototype.change_window_size(-2)
        with self.assertRaises(ValueError):
            self.Prototype.change_window_size("a")

    def test_toggle_sentence_mode(self):
        self.Prototype.toggle_sentence_window_mode()
        self.assertTrue(self.Prototype.get_sentence_mode())
        self.Prototype.toggle_word_window_mode()
        self.assertFalse(self.Prototype.get_sentence_mode())

    @unittest.skip("doesn't work yet because of postagger initialization")
    def test_change_postagger(self):
        new_tagger = "spacy-tagger"
        self.Prototype.change_postagger(new_tagger)
        self.assertEqual(self.Prototype.get_postagger(), new_tagger)

    def test_get_word_window_simple(self):
        # no constraints, one word, window size 1
        pattern = "dog"
        text = "The brown dog is sleeping."
        tokenized_text = self.Prototype.tokenizer.tokenize(text)
        result = "brown dog is"
        test_result = self.Prototype.get_word_window(pattern, tokenized_text, None)
        self.assertEqual(test_result[0].snippet, result)

    def test_get_word_window_bigger_size(self):
        # no constraints, one word, window size 3
        self.Prototype.change_window_size(3)
        one_word_pattern = "dog"
        text = "The brown dog is sleeping on the couch."
        tokenized_text = self.Prototype.tokenizer.tokenize(text)
        result = "The brown dog is sleeping on"
        test_result = self.Prototype.get_word_window(one_word_pattern, tokenized_text, None)
        self.assertEqual(test_result[0].snippet, result)

    def test_get_word_window_three_word_pattern(self):
        # no constraints, three word pattern, window size 4
        self.Prototype.change_window_size(4)
        pattern = "old brown dog"
        text = "Our dear old brown dog is eating a lot."
        tokenized_text = self.Prototype.tokenizer.tokenize(text)
        result = "Our dear old brown dog is eating a lot."
        test_result = self.Prototype.get_word_window(pattern, tokenized_text, None)
        self.assertEqual(test_result[0].snippet, result)

    def test_get_word_window_constraint(self):
        # constraints, three word pattern, window size 2
        self.Prototype.change_window_size(2)
        pattern = "brown dog"
        text = "Our dear old brown dog is eating a lot."
        tokenized_text = self.Prototype.tokenizer.tokenize(text)
        constraint = [("brown dog", "old", -1)]
        result = "dear old brown dog is eating"
        test_result = self.Prototype.get_word_window(pattern, tokenized_text, constraint)
        self.assertEqual(test_result[0].snippet, result)

        # second test to see that due to the constraint, there is no snippet selected
        text2 = "Our brown dog is eating a lot."
        tokenized_text2 = self.Prototype.tokenizer.tokenize(text2)
        test_result2 = self.Prototype.get_word_window(pattern, tokenized_text2, constraint)
        self.assertListEqual(test_result2, [])

    def test_get_word_window_constraint2(self):
        # more constraints, three word pattern, window size 2
        self.Prototype.change_window_size(2)
        pattern = "dog"
        text = "Our dear old brown dog is eating a lot after dog obedience school."
        tokenized_text = self.Prototype.tokenizer.tokenize(text)
        constraint = [("dog", "brown", -1), ("dog", "school", 2)]
        result = ["old brown dog is eating", "lot after dog obedience school."]
        test_result = self.Prototype.get_word_window(pattern, tokenized_text, constraint)
        t_result = []
        for res in test_result:
            print(res.snippet)
            t_result.append(res.snippet)
        self.assertListEqual(t_result, result)

    def test_get_sentence_window_simple(self):
        # no constraints, one word, window size 0
        self.Prototype.toggle_sentence_window_mode()
        self.Prototype.change_window_size(0)
        pattern = "dog"
        text = ["The brown dog is sleeping."]
        result = "The brown dog is sleeping."
        test_result = self.Prototype.get_sentence_window(pattern, text, None)
        self.assertEqual(test_result[0].snippet, result)

    def test_get_sentence_window_bigger_size(self):
        # no constraints, one sentence, window size 3
        self.Prototype.toggle_sentence_window_mode()
        self.Prototype.change_window_size(2)
        pattern = "dog"
        text = ["The brown dog is sleeping on the couch.", "He is such a nice fluff ball."]
        result = "The brown dog is sleeping on the couch. He is such a nice fluff ball."
        test_result = self.Prototype.get_sentence_window(pattern, text, None)
        self.assertEqual(test_result[0].snippet, result)

    def test_get_sentence_window_two_word_pattern(self):
        # no constraints, three sentence pattern, window size 1
        self.Prototype.toggle_sentence_window_mode()
        self.Prototype.change_window_size(1)
        pattern = "große Stadt"
        text = ["Hallo.", "Eine große Stadt.", "Leckere Schokolade."]
        result = "Hallo. Eine große Stadt. Leckere Schokolade."
        test_result = self.Prototype.get_sentence_window(pattern, text, None)
        self.assertEqual(test_result[0].snippet, result)

    def test_get_sentence_window_constraint(self):
        # constraints, three sentence pattern, window size 2
        self.Prototype.toggle_sentence_window_mode()
        self.Prototype.change_window_size(0)
        pattern = "dog"
        text = ["Our dear old brown dog is eating a lot."]
        constraint = [("dog", "brown", -2)]
        result = "Our dear old brown dog is eating a lot."
        test_result = self.Prototype.get_sentence_window(pattern, text, constraint)
        self.assertEqual(test_result[0].snippet, result)

        # second test to see that due to the constraint, there is no snippet selected
        text2 = ["Our dog is eating a lot."]
        test_result2 = self.Prototype.get_sentence_window(pattern, text2, constraint)
        self.assertListEqual(test_result2, [])

    def test_get_sentence_window_constraint2(self):
        # more constraints, three sentence pattern, window size 2
        self.Prototype.toggle_sentence_window_mode()
        self.Prototype.change_window_size(0)
        pattern = "dog"
        text = ["Our dear old brown dog is great.", "The dog days are over."]
        constraint = [("dog", "brown", -2), ("dog", "days", 2)]
        result = ["Our dear old brown dog is great.", "The dog days are over."]
        test_result = self.Prototype.get_sentence_window(pattern, text, constraint)
        t_result = []
        for res in test_result:
            print(res.snippet)
            t_result.append(res.snippet)
        self.assertListEqual(t_result, result)


if __name__ == '__main__':
    unittest.main()
