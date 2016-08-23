import treetaggerwrapper
import spacy
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize import StanfordTokenizer


class POSTagger:
    """POSTagger creates a POS tagger for german language. Different tagger are available to use."""
    STAN = "stanford-hgc-tagger"
    SFT = "stanford-fast-tagger"
    TT = "tree-tagger"
    SPACY = "spacy-tagger"

    # paths to Stanford tagger modules
    __path_to_jar = "C:/Users/din_m/MA/Stanford Tagger/stanford-postagger.jar"
    __model_file_name = "C:/Users/din_m/MA/Stanford Tagger/models/"

    def __init__(self, tagger):
        """Initialize a new POS tagger. Takes tagger parameter as an argument to define the kind of tagger."""
        self.__tokenizer = StanfordTokenizer(path_to_jar=POSTagger.__path_to_jar)
        if tagger == POSTagger.STAN:
            self.tagger_name = POSTagger.STAN
            self.__tagger = StanfordPOSTagger(path_to_jar=POSTagger.__path_to_jar,
                                              model_filename=POSTagger.__model_file_name + "german-hgc.tagger")
        elif tagger == POSTagger.SFT:
            self.tagger_name = POSTagger.SFT
            self.__tagger = StanfordPOSTagger(path_to_jar=POSTagger.__path_to_jar,
                                              model_filename=POSTagger.__model_file_name + "german-fast.tagger")
        elif tagger == POSTagger.TT:
            self.tagger_name = POSTagger.TT
            self.__tagger = treetaggerwrapper.TreeTagger(TAGLANG='de')

        # SpaCy takes really long to initialize (about 5-7 minutes), but performs well and fast afterwards
        elif tagger == POSTagger.SPACY:
            self.tagger_name = POSTagger.SPACY
            self.__tagger = spacy.load('de')
        else:
            raise Exception("Wrong tagger parameter.")

    def tag(self, text):
        """POS tag tokenized text."""
        if self.tagger_name == POSTagger.SFT or self.tagger_name == POSTagger.STAN:
            tokens = self.__tokenizer.tokenize(text)
            return self.__tagger.tag(tokens)
        elif self.tagger_name == POSTagger.TT:
            tags = self.__tagger.tag_text(text)
            tuple_list = []
            tag_list = treetaggerwrapper.make_tags(tags)
            for item in tag_list:
                tuple_list.append((item[0], item[1]))
            return tuple_list
        elif self.tagger_name == POSTagger.SPACY:
            tags = self.__tagger(text)
            tuple_list = []
            for word in tags:
                tuple_list.append((word.orth_, word.tag_))
            return tuple_list
        else:
            pass

#tagger = POSTagger("spacy-tagger")
#doc = tagger.tag(u"Bei mir zu Hause denken sie bestimmt, daß ich noch krank sei.")
#print(tagger.tag("Ich werde morgen in die Schule gehen."))
#print(tagger.tag("Hat Aglaja den Brief etwa der Alten gezeigt?«"))