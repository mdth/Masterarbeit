import re
from HelperMethods import add_quotes, compile_pattern, replace_brackets, replace_special_characters
from collections import namedtuple
from POSTagger import POSTagger
from nltk.tokenize import sent_tokenize
from nltk.tokenize import WhitespaceTokenizer


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
        self.tokenizer = WhitespaceTokenizer()

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
                snippet = self.__get_textsnippets(ind, ind, textlength, tokens)
                offsets = list(self.tokenizer.span_tokenize(snippet))
                offset_start = offsets[self.window_size][0]
                offset_end = offsets[self.window_size][1]
                SentObj = namedtuple('Sentence_Object', ['snippet', 'offset_start', 'offset_end'])
                textsnippets.append(SentObj(snippet=snippet, offset_start=offset_start, offset_end=offset_end))
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

    def __get_sentence_window(self, pattern, sentences, constraints):
        """Get a word window list with a specific number of sentences. size 0 will return the
        current sentence the pattern is found in. size n will return n sentences left and right
        from the initial sentence."""
        split_pattern = pattern.split()

        if len(split_pattern) > 1:
            textsnippets = self.__get_sentence_window_more_words(pattern, split_pattern, constraints)
        else:
            textsnippets = self.__get_sentence_window_one_word(pattern, sentences, constraints)
        return textsnippets

    def __get_sentence_window_one_word(self, pattern, sentences, constraints):
        """Get sentence snippets with pattern containing of only one words according to window size."""
        textsnippets = []
        for ind, sent in enumerate(sentences):
            tokens = self.tokenizer.tokenize(sent)
            for i, token in enumerate(tokens):
                if check_pattern(pattern, token):
                    if constraints is not None:
                        self.__check_constraints(constraints, i, ind, pattern, sent, sentences, textsnippets,
                                                 tokens)
                    else:
                        self.__get_sentence_window_one_word_help1(i, ind, sent, sentences, textsnippets)
        return textsnippets

    def __check_constraints(self, constraints, i, ind, pattern, sent, sentences, textsnippets, tokens):
        """Traverse the given list of constraints and find target words near the keyword. The number of word distance
        is given in the constraint list.
        add_info[0] is the keyword aka pattern.
        add_info[1] is the target_word aka the constraint.
        add_info[2] is the word distance from constraint to the pattern."""
        for add_info in constraints:
            # find pattern that matches target word
            if check_pattern(pattern, add_info[0]):
                # check if the constraint word is within specified number
                index = add_info[2]
                if (0 < i + index < len(tokens)) and check_pattern(add_info[1], tokens[i + index]):
                    self.__get_sentence_window_one_word_help1(
                        i, ind, sent, sentences, textsnippets)
                else:
                    while index != 0:
                        if index > 0:
                            index -= 1
                        else:
                            index += 1

                        if (0 < i + index < len(tokens)) and check_pattern(
                                add_info[1], tokens[i + index]):
                            self.__get_sentence_window_one_word_help1(
                                i, ind, sent, sentences, textsnippets)
                            break

    def __get_sentence_window_one_word_help1(self, i, ind, sent, sentences, textsnippets):
        sentence = self.__get_sentences(ind, sentences)
        # get offsets
        offsets = list(self.tokenizer.span_tokenize(sent))
        offset_start = offsets[i][0]
        offset_end = offsets[i][1]
        SentObj = namedtuple('Sentence_Object', ['snippet', 'offset_start', 'offset_end'])
        textsnippets.append(SentObj(snippet=sentence, offset_start=offset_start, offset_end=offset_end))

    def __get_sentence_window_more_words(self, split_pattern, sentences, constraints):
        """Get sentence snippets with pattern containing of more than 2 words according to window size."""
        textsnippets = []
        for ind, sent in enumerate(sentences):
            tokens = self.tokenizer.tokenize(sent)
            p_index = 0
            end_index = ind
            while p_index < len(split_pattern):
                if (end_index < len(tokens)) and check_pattern(split_pattern[p_index], tokens[end_index]):
                    p_index += 1
                    end_index += 1
                else:
                    break
            if p_index == len(split_pattern):
                if (ind - self.window_size) < 0:
                    sentence = sentences[0:ind+self.window_size]
                elif (ind + self.window_size) >= len(tokens):
                    # TODO Randfall -> decreasing window_size by one if it's bigger
                    sentence = sentences[ind-self.window_size:len(sentences)-1]
                else:
                    sentence = self.__get_sentences(ind, sentences)

                # get offsets
                offsets = list(self.tokenizer.span_tokenize(sent))
                offset_start = offsets[p_index][0]
                offset_end = offsets[end_index][1]
                SentObj = namedtuple('Sentence_Object', ['snippet', 'offset_start', 'offset_end'])
                textsnippets.append(SentObj(sentence=sentence, offset_start=offset_start, offset_end=offset_end))
        return textsnippets

    def __get_sentences(self, ind, sentences):
        if self.window_size > 0:
            sentence = sentences[ind - self.window_size:ind + self.window_size]
        else:
            sentence = sentences[ind]
        return sentence

    def find_text_window(self, text, text_id, constraints):
        """Finds text windows with variable size."""
        tokenized_text = self.tokenizer.tokenize(text)
        for pattern in self.postgre_db.get_data_from_table("single_pattern"):
            if self.sentence_mode:
                # this is only a quick and dirty fix: replace weird quotes to basic ones
                for ch in ['›', '‹', '»', '«']:
                    if ch in text:
                        text = text.replace(ch, '"')
                windows_objects = self.__get_sentence_window(
                    pattern['single_pattern'], sent_tokenize(text, language='german'), constraints)
            else:
                windows_objects = self.__get_word_window(pattern['single_pattern'], tokenized_text)

            # push found snippets onto database
            if len(windows_objects) > 0:
                single_pattern_id = pattern['id']
                for sent_obj in windows_objects:
                    # push snippets
                    self.__push_snippets(sent_obj.snippet)
                    snippet_id = self.postgre_db.get_id("snippets", "snippet=" + add_quotes(
                        replace_special_characters(sent_obj.snippet)))
                    # push relations
                    self.__push_texts_snippets(text_id, snippet_id)
                    self.__push_snippet_offsets(
                        single_pattern_id, snippet_id, sent_obj.offset_start, sent_obj.offset_end)

    def __push_snippets(self, snippet):
        """Push found snippets onto the snippets table in PostGre DB, if not already in the table.
        Afterwards push the single_pattern and snippets relation."""
        if not self.postgre_db.is_in_table("snippets", "snippet=" + add_quotes(
                replace_special_characters(snippet))):
            self.postgre_db.insert("snippets", {"snippet": snippet})

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
            self.postgre_db.update(
                "snippet_offsets", "offsets=" + add_quotes(replace_brackets(str(old_list))), "id=" + str(pid))

    def __push_relation(self, id1, id2, id1_name, id2_name, table):
        """Push a relation onto the PostGre DB. The relation has to have a primary key."""
        # case: No entry about relation is in DB yet
        if not self.postgre_db.is_in_table(table, id1_name + "=" + str(
                id1)):
            self.postgre_db.insert(table, {
                id1_name: id1, id2_name: [id2], "aggregation": 0})

        # case: Entry about single_pattern is in DB
        else:
            old_list = self.postgre_db.get(table, id1_name + "=" + str(
                id1), id2_name)
            new_list = list(set(old_list + [id2]))
            self.postgre_db.update(
                table, id2_name + "=" + add_quotes(replace_brackets(str(new_list))), id1_name + "=" + str(id1))

    def __push_aggregation_lowest_layer(self, aggregation_object, aggregation_name, table, id_name):
        """Push the aggregated snippet numbers onto corresponding the lower layer tables."""
        id = 0
        aggregation_value = 0
        for aggregation in aggregation_object:
            id = aggregation[aggregation_name][0]
            aggregation_value = aggregation[aggregation_name][1]
            self.postgre_db.update(table, "aggregation=" + str(aggregation_value), id_name + "=" + str(id))

    def __push_aggregation(self, table, sub_table, table_id, sub_table_id):
        """Calculate and push aggregation on the rest layer tables."""
        table_entries = self.postgre_db.get_data_from_table(table)
        for entry in table_entries:
            aggregation = 0
            entry_id = entry[table_id]
            entries_to_look_up = entry[sub_table_id]

            for look_up in entries_to_look_up:
                # calcutate aggregations differently depending on how the table structure is
                if len(entries_to_look_up) > 1:
                        stored_value = self.postgre_db.get(sub_table, sub_table_id + "=" + str(look_up), "aggregation")
                        if stored_value is None:
                            stored_value = 0
                        aggregation += stored_value

                else:
                    query = "SELECT SUM(aggregation) FROM " + sub_table + " WHERE " + sub_table_id + "=" + str(look_up)
                    aggregation = self.postgre_db.query(query)[0]['sum']
                    if aggregation is None:
                        aggregation = 0

            self.postgre_db.update(table, "aggregation=" + str(aggregation), table_id + "=" + str(entry_id))

    def get_snippets(self, constraints):
        """Get snippets for the whole corpus."""
        for ind, text in enumerate(self.mongo_db.get({"title": "Chapter 1"})):
            self.postgre_db.insert("texts", {"title": text['title']})
            self.find_text_window(text['text'], text['id'], constraints)
            print("Chapter " + str(text['id']) + " done.")

    def aggregation(self):
        """Calculate aggregation bottom-up and store the interim data onto the database."""
        aggregation_texts_snippets = self.postgre_db.query("SELECT aggregate_texts_snippets()")
        aggregation_snippet_offsets = self.postgre_db.query("SELECT aggregate_snippet_offsets()")

        # push 2 lowest levels of the hierarchy
        self.__push_aggregation_lowest_layer(
            aggregation_texts_snippets, str('aggregate_texts_snippets'), "texts_snippets", "text_id")
        self.__push_aggregation_lowest_layer(
            aggregation_snippet_offsets, str('aggregate_snippet_offsets'), "snippet_offsets", "id")

        # push rest of the hierarchy
        self.__push_aggregation(
            "pattern_single_pattern", "snippet_offsets", str('pattern_id'), str('single_pattern_id'))
        self.__push_aggregation("has_object", "pattern_single_pattern", str('bscale_id'), str('pattern_id'))
        self.__push_aggregation("has_attribute", "has_object", str('bsort_id'), str('bscale_id'))

    def pos_tagging(self):
        """POS tag all dialogues and monologues."""
        snippets = self.postgre_db.get_data_from_table("snippets")


def check_pattern(pattern, token):
    """Strip token and check if the token matches the defined pattern."""
    split_token = re.split('\W+', token, 1)
    if split_token[0] == '':
        split_token = split_token[1]
    else:
        split_token = split_token[0]
    return split_token == pattern