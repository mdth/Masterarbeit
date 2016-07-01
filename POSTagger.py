import treetaggerwrapper
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize import StanfordTokenizer


class POSTagger:
    """POSTagger creates a POS tagger for german language. Different tagger are available to use."""
    # parameter for Stanford HGC tagger
    STAN = "stanford-hgc-tagger"
    # parameter for Stanford fast tagger
    SFT = "stanford-fast-tagger"
    # parameter for Tree Tagger
    TT = "tree-tagger"

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
        else:
            raise Exception("Wrong tagger parameter.")


    def tag(self, text):
        """POS tag tokenized text."""
        if self.tagger_name == (POSTagger.STAN or POSTagger.SFT):
            tokens = self.__tokenizer.tokenize(text)
            return self.__tagger.tag(tokens)
        elif self.tagger_name == POSTagger.TT:
            tags = self.__tagger.tag_text(text)
            tuple_list = []
            tag_list = self.__tagger.make_tags(tags)
            for item in tag_list:
                tuple_list.append(item[0], item[1])
            return tuple_list
        else:
            pass
