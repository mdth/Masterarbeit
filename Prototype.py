import re
import HelperMethods
from POSTagger import POSTagger


class Prototype:
    """Prototype system that searches for RDF pattern (aka Q-Calculus pattern) to find textsnippets."""

    def __init__(self, mongo_db, postgre_db, postagger="tree-tagger", sentence_mode=True, window_size=0):
        """Initialize a prototype system with a specified POS tagger, sentence or word mode and decide on the size
        for sentence or word windows size"""
        self.mongo_db = mongo_db
        self.postgre_db = postgre_db
        self.__postagger = postagger
        self.sentence_modus = sentence_mode
        self.window_size = window_size

    def get_word_window(self, pattern, tokens):
        """Get a word window list with a specific number of words."""
        split_pattern = pattern.split()
        if len(split_pattern) > 1:
            textsnippets = self.get_word_window_more_words_help(split_pattern, tokens)

        else:
            textsnippets = self.word_window_one_word_help(pattern, tokens)

        return textsnippets

    def get_word_window_more_words_help(self, split_pattern, tokens):
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
                textsnippets.append(self.get_textsnippets(ind, end_index - 1, len(tokens), tokens))
        return textsnippets

    def word_window_one_word_help(self, pattern, tokens):
        textsnippets = []
        textlength = len(tokens)
        for ind, token in enumerate(tokens):
            if check_pattern(pattern, token):
                textsnippets.append(self.get_textsnippets(ind, ind, textlength, tokens))
        return textsnippets

    def get_textsnippets(self, indl, indr, textlength, tokens):
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

    def get_sentence_window(self, pattern, tokens):
        """Get a word window list with a specific number of sentences. size 0 will return the
        current sentence the pattern is found in. size n will return n sentences left and right
        from the initial sentence."""
        split_pattern = pattern.split()
        if len(split_pattern) > 1:
            textsnippets = self.get_sentence_window_more_words_help(split_pattern, tokens)
        else:
            textsnippets = self.get_sentence_window_one_word_help(pattern, tokens)
        return textsnippets

    def get_sentence_window_more_words_help(self, split_pattern, tokens):
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
                textsnippets.append(self.get_textsnippets_sentence(tokens, ind, end_index - 1))
        return textsnippets

    def get_textsnippets_sentence(self, tokens, beg_index, end_index):
        sent_size = self.window_size + 1
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
                return " ".join(tokens[beg_index - l - 1:end_index + r])
            elif beg_index - l == 0:
                return " ".join(tokens[beg_index - l:end_index + r])
            elif find_left_sentence_boundary(tokens, beg_index, l):
                size2 += 1
            l += 1
        if size2 == sent_size:
            return " ".join(tokens[beg_index - l + 2:end_index + r])

    def get_sentence_window_one_word_help(self, pattern, tokens):
        textsnippets = []
        for ind, token in enumerate(tokens):
            if check_pattern(pattern, token):
                textsnippets.append(self.get_textsnippets_sentence(tokens, ind, ind))
        return textsnippets

    def find_text_window(self, text, text_id):
        """Finds text windows with variable size."""
        split_text = text.split()

        for pattern in self.postgre_db.get_data_from_table("single_pattern"):
            if self.sentence_modus:
                snippets = self.get_sentence_window(pattern['single_pattern'], split_text)
            else:
                snippets = self.get_word_window(pattern['single_pattern'], split_text)

            if len(snippets) > 0:
                single_pattern_id = pattern['id']
                # TODO push text_snippets
                self.push_snippets(snippets, single_pattern_id, text_id)

    def pos_tagging(self):
        snippets = self.postgre_db.get_data_from_table("snippets")
        for snippet in snippets:
            HelperMethods.search_for_dialog(snippet)

    def push_snippets(self, snippets, current_single_pattern_id, text_id):
        if len(snippets) > 0:
            for snippet in snippets:
                if not self.postgre_db.is_in_table("snippets", "snippet=" + HelperMethods.add_quotes(
                        HelperMethods.replace_special_characters(snippet))):
                    self.postgre_db.insert("snippets", {"snippet": snippet})
                snippet_id = self.postgre_db.get_id("snippets", "snippet=" + HelperMethods.add_quotes(
                    HelperMethods.replace_special_characters(snippet)))
                self.push_pattern_snippets(current_single_pattern_id, snippet_id)

    def push_pattern_snippets(self, current_single_pattern_id, current_snippet_id):
        """Push single_pattern & snippets relation onto PostGre DB."""

        # case: no entry about single_pattern is in db
        if not self.postgre_db.is_in_table("single_pattern_snippets", "single_pattern_id=" + str(
                current_single_pattern_id)):
            self.postgre_db.insert("single_pattern_snippets", {
                "single_pattern_id": current_single_pattern_id, "snippet_id": [current_snippet_id]})

        # case: entry about single_pattern is in db
        else:
            old_snippets = self.postgre_db.get("single_pattern_snippets", "single_pattern_id=" + str(
                current_single_pattern_id), "snippet_id")
            old_snippets.append(current_snippet_id)
            self.postgre_db.delete_from_table("single_pattern_snippets", {
                "single_pattern_id": current_single_pattern_id})
            self.postgre_db.insert("single_pattern_snippets", {
                "single_pattern_id": current_single_pattern_id, "snippet_id": old_snippets})

    def get_db_text(self):
        for ind, text in enumerate(self.mongo_db.get({})):
            # TODO postgre_db.insert("texts", {"title": "Chapter 1"})
            self.postgre_db.insert("texts", {"title": text['title']})
            self.find_text_window(text['text'], text['id'])
            print("Chapter " + str(text['id']) + " done.")


def find_right_sentence_boundary(tokens, ind, steps):
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