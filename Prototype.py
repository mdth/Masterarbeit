import re
import HelperMethods
from collections import namedtuple
from POSTagger import POSTagger


class Prototype:
    """Prototype system that searches for RDF pattern (aka Q-Calculus pattern) to find textsnippets."""

    def __init__(self, mongo_db, postgre_db, postagger="tree-tagger", sentence_mode=True, window_size=0):
        """Initialize a prototype system with a specified POS tagger, sentence or word mode and decide on the size
        for sentence or word windows size"""
        self.mongo_db = mongo_db
        self.postgre_db = postgre_db
        self.postagger = postagger
        self.sentence_mode = sentence_mode
        self.window_size = window_size

    def change_postagger(self, name):
        """Change the current POS tagger to a new one."""
        self.postagger = POSTagger(name)

    def change_window_size(self, size):
        """Change the current window size to a new size."""
        self.window_size = size

    def toggle_sentence_mode(self):
        """Change the current setting of the sentence mode."""
        self.sentence_mode = not self.sentence_mode

    def __get_word_window(self, pattern, tokens):
        """Get a word window list with a specific number of words."""
        split_pattern = pattern.split()
        if len(split_pattern) > 1:
            textsnippets = self.__get_word_window_more_words_help(split_pattern, tokens)
        else:
            textsnippets = self.__get_word_window_one_word_help(pattern, tokens)

        return textsnippets

    def __get_word_window_more_words_help(self, split_pattern, tokens):
        """Find pattern with more than one word."""
        textsnippets = []
        for ind, token in enumerate(tokens):
            p_index = 0
            end_index = ind
            while p_index < len(split_pattern):
                if check_pattern(split_pattern[p_index], tokens[end_index]):
                    p_index += 1
                    end_index += 1
                else:
                    break
            if p_index == len(split_pattern):
                textsnippets.append(self.__get_textsnippets(ind, end_index - 1, len(tokens), tokens))
        return textsnippets

    def __get_word_window_one_word_help(self, pattern, tokens):
        textsnippets = []
        textlength = len(tokens)
        for ind, token in enumerate(tokens):
            if check_pattern(pattern, token):
                textsnippets.append(self.__get_textsnippets(ind, ind, textlength, tokens))
        return textsnippets

    def __get_textsnippets(self, indl, indr, textlength, tokens):
        if (indl - self.window_size < 0) and (indr + self.window_size > textlength):
            left_index = self.window_size - 1
            while not (indl - left_index) == 0:
                left_index -= 1
            right_index = self.window_size - 1
            while not (indr + right_index) == textlength:
                right_index -= 1
            return " ".join(tokens[indl - left_index:indr + right_index])

        elif indr + self.window_size > textlength:
            right_index = self.window_size - 1
            while not (indr + right_index) == textlength:
                right_index -= 1
            return " ".join(tokens[indl - self.window_size:indr + right_index])

        elif indl - self.window_size < 0:
            left_index = self.window_size - 1
            while not (indl - left_index) == 0:
                left_index -= 1
            return " ".join(tokens[indl - left_index:indr + self.window_size + 1])
        else:
            return " ".join(tokens[indl - self.window_size:indr + (self.window_size + 1)])

    def __get_sentence_window(self, pattern, tokens):
        """Get a word window list with a specific number of sentences. size 0 will return the
        current sentence the pattern is found in. size n will return n sentences left and right
        from the initial sentence."""
        split_pattern = pattern.split()
        if len(split_pattern) > 1:
            textsnippets = self.__get_sentence_window_more_words_help(pattern, split_pattern, tokens)
        else:
            textsnippets = self.__get_sentence_window_one_word_help(pattern, tokens)
        return textsnippets

    def __get_sentence_window_more_words_help(self, pattern, split_pattern, tokens):
        textsnippets = []
        for ind, token in enumerate(tokens):
            p_index = 0
            end_index = ind
            while p_index < len(split_pattern):
                if (end_index < len(tokens)) and check_pattern(split_pattern[p_index], tokens[end_index]):
                    p_index += 1
                    end_index += 1
                else:
                    break
            if p_index == len(split_pattern):
                textsnippets.append(self.__get_textsnippets_sentence(pattern, tokens, ind, end_index - 1))
        return textsnippets

    def __get_textsnippets_sentence(self, pattern, tokens, beg_index, end_index):
        sent_size = self.window_size + 1
        sentence = ""
        l = 1
        r = 0
        size1 = 0
        size2 = 0
        while size1 < sent_size:
            if end_index + r > len(tokens) - 1:
                break
            elif find_right_sentence_boundary(tokens, end_index, r):
                size1 += 1
            r += 1
        while size2 < sent_size:
            if beg_index - l < 0:
                sentence += " ".join(tokens[beg_index - l - 1:end_index + r])
                break
            elif beg_index - l == 0:
                sentence += " ".join(tokens[beg_index - l:end_index + r])
                break
            elif find_left_sentence_boundary(tokens, beg_index, l):
                size2 += 1
            l += 1
        if size2 == sent_size:
            sentence += " ".join(tokens[beg_index - l + 2:end_index + r])

        offset_start = sentence.index(pattern)
        offset_end = offset_start + len(pattern) - 1
        SentObj = namedtuple('Sentence_Object', ['sentence', 'offset_start', 'offset_end'])
        return SentObj(sentence=sentence, offset_start=offset_start, offset_end=offset_end)

    def __get_sentence_window_one_word_help(self, pattern, tokens):
        textsnippets = []
        for ind, token in enumerate(tokens):
            if check_pattern(pattern, token):
                textsnippets.append(self.__get_textsnippets_sentence(pattern, tokens, ind, ind))
        return textsnippets

    def find_text_window(self, text, text_id):
        """Finds text windows with variable size."""
        split_text = text.split()

        for pattern in self.postgre_db.get_data_from_table("single_pattern"):
            if self.sentence_mode:
                sentence_objects = self.__get_sentence_window(pattern['single_pattern'], split_text)
            else:
                sentence_objects = self.__get_word_window(pattern['single_pattern'], split_text)
            if len(sentence_objects) > 0:
                single_pattern_id = pattern['id']
                for sent_obj in sentence_objects:
                    # push snippets
                    self.__push_snippets(sent_obj.sentence)
                    snippet_id = self.postgre_db.get_id("snippets", "snippet=" + HelperMethods.add_quotes(
                        HelperMethods.replace_special_characters(sent_obj.sentence)))

                    # push relations
                    self.__push_pattern_snippets(single_pattern_id, snippet_id)
                    self.__push_texts_snippets(text_id, snippet_id)
                    self.__push_snippet_offsets(
                        single_pattern_id, snippet_id, sent_obj.offset_start, sent_obj.offset_end)

    def __push_snippets(self, snippet):
        """Push found snippets onto the snippets table in PostGre DB, if not already in the table.
        Afterwards push the single_pattern and snippets relation."""
        if not self.postgre_db.is_in_table("snippets", "snippet=" + HelperMethods.add_quotes(
                HelperMethods.replace_special_characters(snippet))):
            self.postgre_db.insert("snippets", {"snippet": snippet})

    def __push_pattern_snippets(self, current_single_pattern_id, current_snippet_id):
        """Push single_pattern & snippets relation onto PostGre DB."""
        self.__push_relation(
            current_single_pattern_id, current_snippet_id, "single_pattern_id", "snippet_id", "single_pattern_snippets")

    def __push_texts_snippets(self, text_id, snippet_id):
        """Get all saved snippets that occur in a text and push them onto PostGre DB."""
        self.__push_relation(text_id, snippet_id, "text_id", "snippet_id", "texts_snippets")

    def __push_snippet_offsets(self, single_pattern_id, snippet_id, offset_start, offset_end):
        """Push found single_pattern in snippets and their respective offset."""
        if not self.postgre_db.is_in_table(
                "snippet_offsets", "single_pattern_id=" + str(single_pattern_id) + " and snippet_id=" + str(
                    snippet_id)):
            self.postgre_db.insert("snippet_offsets", {
                "single_pattern_id": single_pattern_id, "snippet_id": snippet_id, "offsets": [
                    [offset_start, offset_end]]})
        else:
            old_list = self.postgre_db.get(
                "snippet_offsets", "single_pattern_id=" + str(single_pattern_id) + " and snippet_id=" + str(
                    snippet_id), "offsets")
            old_list.append([offset_start, offset_end])
            pid = self.postgre_db.get_id(
                "snippet_offsets", "single_pattern_id=" + str(single_pattern_id) + " and snippet_id=" + str(
                    snippet_id))
            self.postgre_db.delete_from_table("snippet_offsets", {"id": pid})
            self.postgre_db.insert("snippet_offsets", {
                "single_pattern_id": single_pattern_id, "snippet_id": snippet_id, "offsets": old_list})

    def __push_relation(self, id1, id2, id1_name, id2_name, table):
        """Push a relation onto the PostGre DB. The relation has to have a primary key."""
        # case: No entry about relation is in DB yet
        if not self.postgre_db.is_in_table(table, id1_name + "=" + str(
                id1)):
            self.postgre_db.insert(table, {
                id1_name: id1, id2_name: [id2]})

        # case: Entry about single_pattern is in DB
        else:
            old_list = self.postgre_db.get(table, id1_name + "=" + str(
                id1), id2_name)
            old_list.append(id2)
            self.postgre_db.delete_from_table(table, {
                id1_name: id1})
            self.postgre_db.insert(table, {
                id1_name: id1, id2_name: old_list})

    def get_snippets(self):
        """Get snippets for the whole corpus."""
        for ind, text in enumerate(self.mongo_db.get({})):
            self.postgre_db.insert("texts", {"title": text['title']})
            self.find_text_window(text['text'], text['id'])
            print("Chapter " + str(text['id']) + " done.")

    def pos_tagging(self):
        snippets = self.postgre_db.get_data_from_table("snippets")
        for snippet in snippets:
            HelperMethods.search_for_dialog(snippet)


def find_right_sentence_boundary(tokens, ind, steps):
    # TODO in höhere Ebene bringen -> boundaries austauschbar
    sentence_boundary = HelperMethods.compile_pattern('(\w)*(\.|!|\?)+(?!.)')
    sentence_boundary_special = HelperMethods.compile_pattern('(\w)*(\.|!|\?)\S(?!,)')
    next_token = HelperMethods.compile_pattern('(\W)*(\w+)(,)*')
    found_boundary = False

    if re.search(sentence_boundary, tokens[ind + steps]):
        found_boundary = True
    elif re.search(sentence_boundary_special, tokens[ind + steps]):
        next_index = ind + steps + 1
        if next_index <= (len(tokens) - 1):
            found_boundary = re.search(next_token, tokens[ind + steps + 1])
    return found_boundary


def find_left_sentence_boundary(tokens, ind, steps):
    # TODO in höhere Ebene bringen -> boundaries austauschbar
    sentence_boundary = HelperMethods.compile_pattern('(\w)*(\.|!|\?)+(?!.)')
    sentence_boundary_special = HelperMethods.compile_pattern('(\w)*(\.|!|\?)\S')
    next_token = HelperMethods.compile_pattern('(\W(\w+)(,)*)')
    found_boundary = False

    if re.search(sentence_boundary, tokens[ind - steps]):
        found_boundary = True
    elif re.search(sentence_boundary_special, tokens[ind - steps]):
        next_index = ind - steps + 1
        if next_index >= 0:
            found_boundary = re.search(next_token, tokens[ind - steps + 1])
    return found_boundary


def check_pattern(pattern, token):
    """Strip token and check if the token matches the defined pattern."""
    split_token = re.split('\W+', token, 1)
    if split_token[0] == '':
        split_token = split_token[1]
    else:
        split_token = split_token[0]
    return split_token == pattern