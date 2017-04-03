import re
from HelperMethods import add_quotes, compile_pattern, replace_brackets, replace_special_characters
from collections import namedtuple
from POSTagger import POSTagger
from nltk.tokenize import sent_tokenize
from nltk.tokenize import WhitespaceTokenizer
from PMI.Parser import Parser


class Prototype:
    """Prototype system that searches for RDF pattern (aka Q-Calculus pattern) to find textsnippets."""

    def __init__(self, mongo_db, postgre_db, postagger="spacy-tagger", sentence_mode=True, window_size=0):
        """Initialize a prototype with a specified configurations.

        Parameters:
        mongo_db -- Mongo DB connection
        postgre_db -- PostGre DB connection
        postagger -- POS Tagger (default "spacy-tagger")
        sentence_mode -- whether or not to use sentence window mode (default True)
        window_size -- the size of the sentence or word window (default 0)
        """
        self.__mongo_db = mongo_db
        self.__postgre_db = postgre_db
        self.__postagger = postagger
        #self.__postagger = POSTagger(postagger)
        self.__sentence_mode = sentence_mode
        self.__window_size = window_size
        self.tokenizer = WhitespaceTokenizer()
        self.parser = Parser()

    def exit(self):
        """Close down the prototype."""
        self.__mongo_db.close_connection()
        self.__postgre_db.close_connection()

    def get_postagger(self):
        """Gets the current POS Tagger in use."""
        return self.__postagger

    def get_window_size(self):
        """Gets the current window size."""
        return self.__window_size

    def get_sentence_mode(self):
        """Returns True if sentence window mode is activated, else False."""
        return self.__sentence_mode

    def change_postagger(self, name):
        """Change the current POS tagger to a new one."""
        self.__postagger = POSTagger(name)

    def change_window_size(self, size):
        """Change the current window size to a new size."""
        value = 0
        try:
            value = int(size)
        except ValueError:
            raise ValueError("Please type in a valid number.")

        if value >= 0:
            self.__window_size = value
        else:
            raise ValueError("Please type in a valid positive number.")

    def toggle_sentence_window_mode(self):
        """Activate sentence window mode."""
        self.__sentence_mode = True

    def toggle_word_window_mode(self):
        """De-activate sentence window mode."""
        self.__sentence_mode = False

    def get_word_window(self, pattern, tokens, constraints):
        """Get a word window list with a specific number of words.

        Parameters:
        pattern -- the pattern to search for
        tokens -- the tokens to search in
        constraints -- a constraint tuple list
        """
        split_pattern = pattern.split()
        if len(split_pattern) > 1:
            textsnippets = self.__get_word_window_more_words_help(split_pattern, tokens, constraints)
        else:
            textsnippets = self.__get_word_window_one_word_help(pattern, tokens, constraints)
        print(textsnippets)
        return textsnippets

    def __get_word_window_more_words_help(self, split_pattern, tokens, constraints):
        """Find pattern with more than one word.
        """
        textsnippets = []
        textlength = len(tokens)
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
                if constraints is not None:
                    self.__check_constraints(constraints, (ind, end_index - 1), ind, split_pattern, None, None, textsnippets, tokens)
                else:
                    self.__get_word_window_help((ind, end_index - 1), textsnippets, textlength, tokens)
        return textsnippets

    def __get_word_window_one_word_help(self, pattern, tokens, constraints):
        """Find pattern with only one word."""
        textsnippets = []
        textlength = len(tokens)
        for ind, token in enumerate(tokens):
            if check_pattern(pattern, token):
                if constraints is not None:
                    self.__check_constraints(constraints, (ind, ind), ind, pattern, None, None, textsnippets, tokens)
                else:
                    self.__get_word_window_help((ind, ind), textsnippets, textlength, tokens)
        return textsnippets

    def __get_word_window_help(self, token_pos, textsnippets, textlength, tokens):
        snippet = self.__get_textsnippets(token_pos[0], token_pos[1], textlength, tokens)
        offsets = list(self.tokenizer.span_tokenize(snippet))
        offset_start = offsets[self.__window_size][0]
        offset_end = offsets[self.__window_size][1]
        SentObj = namedtuple('Sentence_Object', ['snippet', 'offset_start', 'offset_end'])
        textsnippets.append(SentObj(snippet=snippet, offset_start=offset_start, offset_end=offset_end))

    def __get_textsnippets(self, indl, indr, textlength, tokens):
        if (indl - self.__window_size < 0) and (indr + self.__window_size > textlength):
            left_index = self.__window_size - 1
            while not (indl - left_index) == 0:
                left_index -= 1
            right_index = self.__window_size - 1
            while not (indr + right_index) == textlength:
                right_index -= 1
            return " ".join(tokens[indl - left_index:indr + right_index])

        elif indr + self.__window_size > textlength:
            right_index = self.__window_size - 1
            while not (indr + right_index) == textlength:
                right_index -= 1
            return " ".join(tokens[indl - self.__window_size:indr + right_index])

        elif indl - self.__window_size < 0:
            left_index = self.__window_size - 1
            while not (indl - left_index) == 0:
                left_index -= 1
            return " ".join(tokens[indl - left_index:indr + self.__window_size + 1])
        else:
            return " ".join(tokens[indl - self.__window_size:indr + (self.__window_size + 1)])

    def get_sentence_window(self, pattern, sentences, constraints):
        """Get a list with a specific number of sentences. size 0 will return the
        current sentence the pattern is found in. size n will return n sentences left and right
        from the initial sentence.

        Parameters:
        pattern -- the pattern to search for
        sentences -- the sentences to search in
        constraints -- the constraint tuple list
        """
        split_pattern = pattern.split()

        if len(split_pattern) > 1:
            textsnippets = self.__get_sentence_window_more_words(split_pattern, sentences, constraints)
        else:
            textsnippets = self.__get_sentence_window_one_word(pattern, sentences, constraints)
        print(textsnippets)
        return textsnippets

    def __get_sentence_window_one_word(self, pattern, sentences, constraints):
        """Get sentence snippets with pattern containing of only one words according to window size."""
        textsnippets = []
        for ind, sent in enumerate(sentences):
            tokens = self.tokenizer.tokenize(sent)
            for i, token in enumerate(tokens):
                if check_pattern(pattern, token):
                    if constraints is not None:
                        self.__check_constraints(constraints, (i, i), ind, pattern, sent, sentences, textsnippets, tokens)
                    else:
                        self.__get_sentence_window_help(i, ind, sentences, textsnippets)
        return textsnippets

    def __check_constraints(self, constraints, token_pos, sent_num, pattern, sent, sentences, textsnippets, tokens):
        """Traverse the given list of constraints and find target words near the keyword. The number of word distance
        is given in the constraint list.
        add_info[0] is the keyword aka pattern.
        add_info[1] is the target_word aka the constraint.
        add_info[2] is the word distance from constraint to the pattern."""
        pos = 0
        more_words_flag = False
        if token_pos[0] == token_pos[1]:
            pos = token_pos[0]
        else:
            more_words_flag = True

        for add_info in constraints:
            # find pattern that matches target word
            index = add_info[2]
            found_constraint_flag = True
            if more_words_flag:
                constraint = add_info[0].split()
                i = 0
                while found_constraint_flag and i < len(pattern) and i < len(constraint):
                    if check_pattern(pattern[i], constraint[i]):
                        pass
                    else:
                        found_constraint_flag = False
                        break
                    i += 1

            if found_constraint_flag or check_pattern(pattern, add_info[0]):
                # set token_pos depending if index is positive or negative
                if more_words_flag and index > 0:
                    pos = token_pos[1]
                elif more_words_flag and index < 0:
                    pos = token_pos[0]

                if self.__sentence_mode:
                    if (0 <= pos + index < len(tokens)) and check_pattern(add_info[1], tokens[pos + index]):
                        self.__get_sentence_window_help(pos, sent_num, sentences, textsnippets)
                    else:
                        while index != 0:
                            if index > 0:
                                index -= 1
                            else:
                                index += 1
                            if (0 < pos + index < len(tokens)) and check_pattern(add_info[1], tokens[pos + index]):
                                self.__get_sentence_window_help(pos, sent_num, sentences, textsnippets)
                                break
                else:
                    if (0 <= pos + index < len(tokens)) and check_pattern(add_info[1], tokens[pos + index]):
                        self.__get_word_window_help(token_pos, textsnippets, len(tokens), tokens)
                    else:
                        while index != 0:
                            if index > 0:
                                index -= 1
                            else:
                                index += 1
                            if (0 < pos + index < len(tokens)) and check_pattern(add_info[1], tokens[pos + index]):
                                self.__get_word_window_help(token_pos, textsnippets, sent, tokens)
                                break

    def __get_sentence_window_help(self, pos_token, ind, sentences, textsnippets):
        #TODO pos_token isn't right here at all
        sentence = self.__get_sentences(ind, sentences)
        # get offsets
        offsets = list(self.tokenizer.span_tokenize(sentence))
        offset_start = offsets[pos_token][0]
        offset_end = offsets[pos_token][1]
        SentObj = namedtuple('Sentence_Object', ['snippet', 'offset_start', 'offset_end'])
        textsnippets.append(SentObj(snippet=sentence, offset_start=offset_start, offset_end=offset_end))

    def __adjust_offset(self, offset):
        # TODO
        new_offset = offset - 1
        return new_offset

    def __get_sentence_window_more_words(self, split_pattern, sentences, constraints):
        """Get sentence snippets with pattern containing of more than 2 words according to window size."""
        textsnippets = []
        for ind, sent in enumerate(sentences):
            tokens = self.tokenizer.tokenize(sent)
            p_index = 0
            begin_index = ind
            end_index = ind
            while p_index < len(split_pattern):
                if (end_index < len(tokens)) and check_pattern(split_pattern[p_index], tokens[end_index]):
                    p_index += 1
                    end_index += 1
                else:
                    break
            if p_index == len(split_pattern):
                # search for constraints in sentence
                if constraints is not None:
                    self.__check_constraints(constraints, (begin_index, end_index), ind, split_pattern, sent, sentences,
                                             textsnippets, tokens)
                else:
                    # TODO end_index nicht genau genug für word_window
                    self.__get_sentence_window_help(end_index, ind, sentences, textsnippets)
        return textsnippets

    def __get_sentences(self, ind, sentences):
        if self.__window_size == 0:
            return sentences[ind]

        elif self.__window_size > 0:
            left_window_border = ind - self.__window_size
            right_window_border = ind + self.__window_size + 1
            if left_window_border < 0:
                left_window_border = 0
            if right_window_border >= len(sentences):
                # TODO does this need to be more precise?
                right_window_border = len(sentences)
            return " ".join(sentences[left_window_border:right_window_border])

    def find_text_window(self, text, text_id, constraints):
        """Finds text windows with variable size and pushes the found results in the PostGre database.

        Parameters:
        text -- text to search in
        text_id -- id of the text
        constraints -- the constraint tuple list"""

        # this is only a quick and dirty fix: replace weird quotes to basic ones
        for ch in ['›', '‹', '»', '«']:
            if ch in text:
                text = text.replace(ch, '"')

        tokenized_text = self.tokenizer.tokenize(text)
        for pattern in self.__postgre_db.get_data_from_table("single_pattern"):
            if self.__sentence_mode:
                windows_objects = self.get_sentence_window(
                    pattern['single_pattern'], sent_tokenize(text, language='german'), constraints)
            else:
                windows_objects = self.get_word_window(pattern['single_pattern'], tokenized_text, constraints)

            # push found snippets onto database
            if len(windows_objects) > 0:
                single_pattern_id = pattern['id']
                for sent_obj in windows_objects:
                    # push snippets
                    self.__push_snippets(sent_obj.snippet)
                    snippet_id = self.__postgre_db.get_id("snippets", "snippet=" + add_quotes(
                        replace_special_characters(sent_obj.snippet)))
                    # push relations
                    self.__push_texts_snippets(text_id, snippet_id)
                    self.__push_snippet_offsets(
                        single_pattern_id, snippet_id, sent_obj.offset_start, sent_obj.offset_end)

    

    def __push_snippets(self, snippet):
        """Push found snippets onto the snippets table in PostGre DB, if not already in the table.
        Afterwards push the single_pattern and snippets relation."""
        if not self.__postgre_db.is_in_table("snippets", "snippet=" + add_quotes(
                replace_special_characters(snippet))):
            self.__postgre_db.insert("snippets", {"snippet": snippet})

    def __push_texts_snippets(self, text_id, snippet_id):
        """Get all saved snippets that occur in a text and push them onto PostGre DB."""
        self.__push_relation(text_id, snippet_id, "text_id", "snippet_id", "texts_snippets")

    def __push_snippet_offsets(self, single_pattern_id, snippet_id, offset_start, offset_end):
        """Push found single_pattern in snippets and their respective offset."""
        if not self.__postgre_db.is_in_table(
                "snippet_offsets", "single_pattern_id=" + str(single_pattern_id) + " and snippet_id=" + str(
                    snippet_id)):
            self.__postgre_db.insert("snippet_offsets", {
                "single_pattern_id": single_pattern_id, "snippet_id": snippet_id, "offsets": [
                    [offset_start, offset_end]]})
        else:
            old_list = self.__postgre_db.get(
                "snippet_offsets", "single_pattern_id=" + str(single_pattern_id) + " and snippet_id=" + str(
                    snippet_id), "offsets")
            old_list.append([offset_start, offset_end])
            pid = self.__postgre_db.get_id(
                "snippet_offsets", "single_pattern_id=" + str(single_pattern_id) + " and snippet_id=" + str(
                    snippet_id))
            self.__postgre_db.update(
                "snippet_offsets", "offsets=" + add_quotes(replace_brackets(str(old_list))), "id=" + str(pid))

    def __push_relation(self, id1, id2, id1_name, id2_name, table):
        """Push a relation onto the PostGre DB. The relation has to have a primary key."""
        # case: No entry about relation is in DB yet
        if not self.__postgre_db.is_in_table(table, id1_name + "=" + str(
                id1)):
            self.__postgre_db.insert(table, {
                id1_name: id1, id2_name: [id2], "aggregation": 0})

        # case: Entry about single_pattern is in DB
        else:
            old_list = self.__postgre_db.get(table, id1_name + "=" + str(
                id1), id2_name)
            new_list = list(set(old_list + [id2]))
            self.__postgre_db.update(
                table, id2_name + "=" + add_quotes(replace_brackets(str(new_list))), id1_name + "=" + str(id1))

    def __push_aggregation_lowest_layer(self, aggregation_object, aggregation_name, table, id_name):
        """Push the aggregated snippet numbers onto corresponding the lower layer tables."""
        id = 0
        aggregation_value = 0
        for aggregation in aggregation_object:
            id = aggregation[aggregation_name][0]
            aggregation_value = aggregation[aggregation_name][1]
            self.__postgre_db.update(table, "aggregation=" + str(aggregation_value), id_name + "=" + str(id))

    def __push_aggregation(self, table, sub_table, table_id, sub_table_id):
        """Calculate and push aggregation on the rest layer tables."""
        table_entries = self.__postgre_db.get_data_from_table(table)
        for entry in table_entries:
            aggregation = 0
            entry_id = entry[table_id]
            entries_to_look_up = entry[sub_table_id]

            for look_up in entries_to_look_up:
                # calcutate aggregations differently depending on how the table structure is
                if len(entries_to_look_up) > 1:
                        stored_value = self.__postgre_db.get(sub_table, sub_table_id + "=" + str(look_up), "aggregation")
                        if stored_value is None:
                            stored_value = 0
                        aggregation += stored_value

                else:
                    query = "SELECT SUM(aggregation) FROM " + sub_table + " WHERE " + sub_table_id + "=" + str(look_up)
                    aggregation = self.__postgre_db.query(query)[0]['sum']
                    if aggregation is None:
                        aggregation = 0

            self.__postgre_db.update(table, "aggregation=" + str(aggregation), table_id + "=" + str(entry_id))

    def get_snippets(self, constraints):
        """Get snippets for the whole corpus.

        Parameter:
        constraints -- the constraint tuple list"""
        for ind, text in enumerate(self.__mongo_db.get({"title": "Chapter 1"})):
            self.__postgre_db.insert("texts", {"title": text['title']})
            self.find_text_window(text['text'], text['id'], constraints)
            print("Chapter " + str(text['id']) + " done.")

    def aggregation(self):
        """Calculate aggregation bottom-up and store the interim data onto the database."""
        aggregation_texts_snippets = self.__postgre_db.query("SELECT aggregate_texts_snippets()")
        aggregation_snippet_offsets = self.__postgre_db.query("SELECT aggregate_snippet_offsets()")

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


def check_pattern(pattern, token):
    """Strip token and check if the token matches the defined pattern.

    Parameter:
    pattern -- the pattern to search for
    token -- the token to match with the pattern
    """
    split_token = re.split('\W+', token, 1)
    if split_token[0] == '':
        split_token = split_token[1]
    else:
        split_token = split_token[0]
    return split_token == pattern
