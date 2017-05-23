import re
from HelperMethods import add_quotes, replace_brackets, replace_special_characters
from collections import Counter, namedtuple
from POSTagger import POSTagger
from nltk.tokenize import sent_tokenize
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import word_tokenize
from PMI.Parser import Parser
from math import log2
from pprint import pprint
from nltk import bigrams
from nltk import trigrams


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

    def create_new_collection(self, schema_name):
        self.__mongo_db.create_collection(schema_name)
        self.__postgre_db.create_schema(schema_name)

    def create_new_schema(self, schema_name):
        self.__postgre_db.create_schema(schema_name)

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
                if self.check_pattern(split_pattern[p_index], tokens[end_index]):
                    p_index += 1
                    end_index += 1
                else:
                    break
            if p_index == len(split_pattern):
                if constraints is not None:
                    self.__check_constraints(constraints, (ind, end_index - 1), ind, split_pattern, None, None, textsnippets, tokens)
                else:
                    pattern = " ".join(item for item in split_pattern)
                    self.__get_word_window_help((ind, end_index - 1), textsnippets, textlength, tokens, pattern)
        return textsnippets

    def __get_word_window_one_word_help(self, pattern, tokens, constraints):
        """Find pattern with only one word."""
        textsnippets = []
        textlength = len(tokens)
        for ind, token in enumerate(tokens):
            if self.check_pattern(pattern, token):
                if constraints is not None:
                    self.__check_constraints(constraints, (ind, ind), ind, pattern, None, None, textsnippets, tokens)
                else:
                    self.__get_word_window_help((ind, ind), textsnippets, textlength, tokens, pattern)
        return textsnippets

    def __get_word_window_help(self, token_pos, textsnippets, textlength, tokens, pattern):
        snippet = self.__get_textsnippets(token_pos[0], token_pos[1], textlength, tokens)
        offset_start = re.search(pattern, snippet).span()[0]
        offset_end = offset_start + (len(pattern) - 1)
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
        return textsnippets

    def __get_sentence_window_one_word(self, pattern, sentences, constraints):
        """Get sentence snippets with pattern containing of only one words according to window size."""
        textsnippets = []
        for ind, sent in enumerate(sentences):
            tokens = self.tokenizer.tokenize(sent)
            for i, token in enumerate(tokens):
                if self.check_pattern(pattern, token):
                    if constraints is not None:
                        self.__check_constraints(constraints, (i, i), ind, pattern, sent, sentences, textsnippets, tokens)
                    else:
                        self.__get_sentence_window_help(ind, sentences, textsnippets, pattern)
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
                    if self.check_pattern(pattern[i], constraint[i]):
                        pass
                    else:
                        found_constraint_flag = False
                        break
                    i += 1

            if found_constraint_flag or self.check_pattern(pattern, add_info[0]):
                # set token_pos depending if index is positive or negative
                if more_words_flag and index > 0:
                    pos = token_pos[1]
                elif more_words_flag and index < 0:
                    pos = token_pos[0]

                if self.__sentence_mode:
                    if (0 <= pos + index < len(tokens)) and self.check_pattern(add_info[1], tokens[pos + index]):
                        self.__get_sentence_window_help(sent_num, sentences, textsnippets, pattern)
                    else:
                        while index != 0:
                            if index > 0:
                                index -= 1
                            else:
                                index += 1
                            if (0 < pos + index < len(tokens)) and self.check_pattern(add_info[1], tokens[pos + index]):
                                self.__get_sentence_window_help(sent_num, sentences, textsnippets, pattern)
                                break
                else:
                    if (0 <= pos + index < len(tokens)) and self.check_pattern(add_info[1], tokens[pos + index]):
                        self.__get_word_window_help(token_pos, textsnippets, len(tokens), tokens, pattern)
                    else:
                        while index != 0:
                            if index > 0:
                                index -= 1
                            else:
                                index += 1
                            if (0 < pos + index < len(tokens)) and self.check_pattern(add_info[1], tokens[pos + index]):
                                self.__get_word_window_help(token_pos, textsnippets, sent, tokens, pattern)
                                break

    def __get_sentence_window_help(self, ind, sentences, textsnippets, pattern):
        sentence = self.__get_sentences(ind, sentences)
        # get offsets
        offset_start = re.search(pattern, sentence).span()[0]
        offset_end = offset_start + (len(pattern) - 1)
        SentObj = namedtuple('Sentence_Object', ['snippet', 'offset_start', 'offset_end'])
        textsnippets.append(SentObj(snippet=sentence, offset_start=offset_start, offset_end=offset_end))

    def __get_sentence_window_more_words(self, split_pattern, sentences, constraints):
        """Get sentence snippets with pattern containing of more than 2 words according to window size."""
        textsnippets = []
        for ind, sent in enumerate(sentences):
            tokens = self.tokenizer.tokenize(sent)
            p_index = 0
            begin_index = 0
            end_index = 0
            while p_index < len(split_pattern):
                if (end_index < len(tokens)) and self.check_pattern(split_pattern[p_index], tokens[end_index]):
                    if p_index == 0:
                        begin_index = end_index
                    else:
                        begin_index = begin_index + end_index - end_index
                    p_index += 1
                    end_index += 1
                else:
                    break
            end_index -= 1
            if p_index == len(split_pattern):
                # search for constraints in sentence
                if constraints is not None:
                    self.__check_constraints(constraints, (begin_index, end_index), ind, split_pattern, sent, sentences,
                                             textsnippets, tokens)
                else:
                    pattern = " ".join(item for item in split_pattern)
                    self.__get_sentence_window_help(ind, sentences, textsnippets, pattern)
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
                right_window_border = len(sentences)
            return " ".join(sentences[left_window_border:right_window_border])

    def find_text_window(self, schema, text, text_id, constraints=None):
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
        for pattern in self.__postgre_db.get_data_from_table(schema, "single_pattern"):
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
                    self.__push_snippets(schema, sent_obj.snippet)
                    snippet_id = self.__postgre_db.get_id(schema,"snippets", "snippet=" + add_quotes(
                        replace_special_characters(sent_obj.snippet)))
                    # push relations
                    self.__push_texts_snippets(schema, text_id, snippet_id)
                    self.__push_snippet_offsets(schema,
                        single_pattern_id, snippet_id, sent_obj.offset_start, sent_obj.offset_end)

    def __push_snippets(self, schema, snippet):
        """Push found snippets onto the snippets table in PostGre DB, if not already in the table.
        Afterwards push the single_pattern and snippets relation."""
        if not self.__postgre_db.is_in_table(schema, "snippets", "snippet=" + add_quotes(
                replace_special_characters(snippet))):
            self.__postgre_db.insert(schema,"snippets", {"snippet": snippet})

    def __push_texts_snippets(self, schema, text_id, snippet_id):
        """Get all saved snippets that occur in a text and push them onto PostGre DB."""
        self.__push_relation(schema, text_id, snippet_id, "text_id", "snippet_id", "texts_snippets")

    def __push_snippet_offsets(self, schema, single_pattern_id, snippet_id, offset_start, offset_end):
        """Push found single_pattern in snippets and their respective offset."""
        if not self.__postgre_db.is_in_table(
                schema, "snippet_offsets", "single_pattern_id=" + str(single_pattern_id) + " and snippet_id=" + str(
                    snippet_id)):
            self.__postgre_db.insert(schema, "snippet_offsets", {
                "single_pattern_id": single_pattern_id, "snippet_id": snippet_id, "offsets": [
                    [offset_start, offset_end]]})
        else:
            old_list = self.__postgre_db.get(schema, "snippet_offsets", "single_pattern_id=" + str(
                single_pattern_id) + " and snippet_id=" + str(snippet_id), "offsets")
            old_list.append([offset_start, offset_end])
            pid = self.__postgre_db.get_id(schema, "snippet_offsets", "single_pattern_id=" + str(
                single_pattern_id) + " and snippet_id=" + str(snippet_id))
            self.__postgre_db.update(schema, "snippet_offsets", "offsets=" + add_quotes(replace_brackets(str(
                old_list))), "id=" + str(pid))

    def __push_relation(self, schema, id1, id2, id1_name, id2_name, table):
        """Push a relation onto the PostGre DB. The relation has to have a primary key."""
        # case: No entry about relation is in DB yet
        if not self.__postgre_db.is_in_table(schema, table, id1_name + "=" + str(
                id1)):
            self.__postgre_db.insert(schema, table, {
                id1_name: id1, id2_name: [id2], "aggregation": 0})

        # case: Entry about single_pattern is in DB
        else:
            old_list = self.__postgre_db.get(schema, table, id1_name + "=" + str(
                id1), id2_name)
            new_list = list(set(old_list + [id2]))
            self.__postgre_db.update(schema, table, id2_name + "=" + add_quotes(replace_brackets(str(
                new_list))), id1_name + "=" + str(id1))

    def __push_aggregation_lowest_layer(self, schema, aggregation_object, aggregation_name, table, id_name):
        """Push the aggregated snippet numbers onto corresponding the lower layer tables."""
        for aggregation in aggregation_object:
            id = aggregation[aggregation_name][0]
            aggregation_value = aggregation[aggregation_name][1]
            self.__postgre_db.update(schema, table, "aggregation=" + str(aggregation_value), id_name + "=" + str(id))

    def __push_aggregation(self, schema, table, sub_table, table_id, sub_table_id):
        """Calculate and push aggregation on the rest layer tables."""
        table_entries = self.__postgre_db.get_data_from_table(schema, table)
        for entry in table_entries:
            aggregation = 0
            entry_id = entry[table_id]
            entries_to_look_up = entry[sub_table_id]

            for look_up in entries_to_look_up:
                query = "SELECT SUM(aggregation) FROM " + schema + "." + sub_table + " WHERE " + sub_table_id + "=" + str(look_up)
                stored_value = self.__postgre_db.query(query)[0]['sum']
                if stored_value is None:
                    stored_value = 0
                aggregation += stored_value
            self.__postgre_db.update(schema, table, "aggregation=" + str(aggregation), table_id + "=" + str(entry_id))

    def get_snippets(self, schema, constraints):
        """Get snippets for the whole corpus.

        Parameter:
        constraints -- the constraint tuple list"""
        for ind, text in enumerate(self.__mongo_db.get(schema, {})):
            self.__postgre_db.insert(schema, "texts", {"title": text['title']})
            self.find_text_window(schema, text['text'], text['id'], constraints)
            print("Finished extracting snippets from chapter " + str(text['id']) + ".")

    def aggregation(self, schema):
        """Calculate aggregation bottom-up and store the interim data onto the database."""
        aggregation_texts_snippets = self.__postgre_db.query("SELECT " + schema + ".aggregate_texts_snippets()")
        aggregation_snippet_offsets = self.__postgre_db.query("SELECT " + schema + ".aggregate_snippet_offsets()")

        # push 2 lowest levels of the hierarchy
        self.__push_aggregation_lowest_layer(schema,
            aggregation_texts_snippets, str('aggregate_texts_snippets'), "texts_snippets", "text_id")
        self.__push_aggregation_lowest_layer(schema,
            aggregation_snippet_offsets, str('aggregate_snippet_offsets'), "snippet_offsets", "id")

        # push rest of the hierarchy
        self.__push_aggregation(schema,
            "pattern_single_pattern", "snippet_offsets", str('pattern_id'), str('single_pattern_id'))
        self.__push_aggregation(schema, "has_object", "pattern_single_pattern", str('bscale_id'), str('pattern_id'))
        self.__push_aggregation(schema, "has_attribute", "has_object", str('bsort_id'), str('bscale_id'))

    def aggregate_bscale(self, schema, new_bscale, bsort, *args):
        pattern_info = self.__add_new_bscale(schema, new_bscale, bsort, *args)
        if pattern_info is not None:
            pattern_ids = pattern_info[0]
            new_bscale_id = pattern_info[1]
            new_pattern_list = list(set.union(*[set(item) for item in pattern_ids]))
            aggregation = 0
            for item in new_pattern_list:
                aggregation += self.__postgre_db.get(schema, "pattern_single_pattern", "pattern_id=" + str(item), "aggregation")
            self.__postgre_db.insert(schema, "has_object", {"bscale_id": new_bscale_id, "pattern_id": new_pattern_list, "aggregation": aggregation})

    def intersect_bscale(self, schema, new_bscale, bsort, *args):
        pattern_info = self.__add_new_bscale(schema, new_bscale, bsort, *args)
        if pattern_info is not None:
            pattern_ids = pattern_info[0]
            new_bscale_id = pattern_info[1]
            new_pattern_list = list(set.intersection(*[set(item) for item in pattern_ids]))
            aggregation = 0
            for item in new_pattern_list:
                aggregation += self.__postgre_db.get(schema, "pattern_single_pattern", "pattern_id=" + str(item), "aggregation")
            self.__postgre_db.insert(schema, "has_object", {"bscale_id": new_bscale_id, "pattern_id": new_pattern_list, "aggregation": aggregation})

    def __add_new_bscale(self, schema, new_bscale, bsort, *args):
        if args is not None:
            bscale_table = self.__postgre_db.get_data_from_table(schema, "bscale")
            bscale_ids = []
            for scale in args:
                scale_found = False
                for bscale in bscale_table:
                    if scale == bscale['bscale']:
                        bscale_ids.append(bscale['id'])
                        scale_found = True
                if not scale_found:
                    raise Exception("Chosen Bscale does not exist.")
            if not self.__postgre_db.is_in_table(schema, "bscale", "bscale=" + add_quotes(new_bscale)):
                self.__postgre_db.insert(schema, "bscale", {"bscale": new_bscale})
                #TODO nominal, ordinal, interval
            new_bscale_id = self.__postgre_db.get_id(schema, "bscale", "bscale=" + add_quotes(new_bscale))
            bsort_id = self.__postgre_db.get_id(schema, "bsort", "bsort=" + add_quotes(bsort))
            if self.__postgre_db.is_in_table(schema, "has_attribute", "bsort_id=" + str(bsort_id)):
                old_list = self.__postgre_db.get(schema, "has_attribute", "bsort_id=" + str(bsort_id), "bscale_id")
                old_list.append(new_bscale_id)
                self.__postgre_db.update(schema, "has_attribute", "bscale_id=" + add_quotes(
                    replace_brackets(str(old_list))), "bsort_id=" + str(bsort_id))
            else:
                self.__postgre_db.insert(schema, "has_attribute",
                                         {"bsort_id": bsort_id, "bscale_id": [new_bscale_id], "aggregation": 0})

            scale_obj = self.__postgre_db.get_data_from_table(schema, "has_object")
            pattern_ids = []
            for scale_id in bscale_ids:
                for item in scale_obj:
                    if scale_id == item['bscale_id']:
                        pattern_ids.append(item['pattern_id'])

            return (pattern_ids, new_bscale_id)

    def find_correlating_pattern(self, schema):
        all_snippets_table = self.__postgre_db.get_data_from_table(schema, "snippets")
        all_snippets = [snippet['snippet'] for snippet in all_snippets_table]
        all_bscales_table = self.__postgre_db.get_data_from_table(schema, "bscale")
        all_bscales = [bscale['id'] for bscale in all_bscales_table]

        # TODO temporary
        self.__postgre_db.delete_data_in_table(schema, "bscale_single_pattern")
        self.__postgre_db.delete_data_in_table(schema, "correlating_bscales")

        for bscale_id in all_bscales:
            pattern_list = self.__postgre_db.get(schema, "has_object", "bscale_id=" + str(bscale_id), "pattern_id")
            for pattern_id in pattern_list:
                single_pattern_id_list = self.__postgre_db.get(
                    schema, "pattern_single_pattern", "pattern_id=" + str(pattern_id), "single_pattern_id")
                for single_pattern_id in single_pattern_id_list:
                    single_pattern = self.__postgre_db.get(schema, "single_pattern", "id=" + str(single_pattern_id), "single_pattern")
                    self.__postgre_db.insert(schema, "bscale_single_pattern", {"bscale_id": bscale_id, "single_pattern_id": single_pattern_id, "single_pattern": single_pattern , "count": 0})
        for snippet in self.parser.nlp.pipe(all_snippets, batch_size=3000, n_threads=-1):
            correlating_pattern = self.parser.get_correlating_nouns_and_adjectives(snippet)
            for ind, item in enumerate(correlating_pattern):
                if self.__postgre_db.is_in_table(schema, "bscale_single_pattern",
                                                 "single_pattern=" + add_quotes(item)):
                    bscale_item_id = self.__postgre_db.get_id(schema, "bscale_single_pattern", "single_pattern=" + str(add_quotes(item)))
                    index = ind + 1
                    while index < len(correlating_pattern):
                        next_item = correlating_pattern[index]
                        if self.__postgre_db.is_in_table(schema, "bscale_single_pattern",
                                                 "single_pattern=" + add_quotes(next_item)):
                            bscale_next_item_id = self.__postgre_db.get_id(schema, "bscale_single_pattern", "single_pattern=" + str(add_quotes(next_item)))
                            if bscale_item_id != bscale_next_item_id:
                                if not self.__postgre_db.is_in_table(
                                        schema, "correlating_bscales", "bscale_a=" + str(bscale_item_id) + " and bscale_b=" + str(bscale_next_item_id)):
                                    self.__postgre_db.insert(schema, "correlating_bscales", {
                                        "bscale_a": bscale_item_id, "bscale_b": bscale_next_item_id,"count":1})
                                else:
                                    old_count = self.__postgre_db.get(schema, "correlating_bscales", "bscale_a=" + str(bscale_item_id) + " and bscale_b=" + str(bscale_next_item_id), "count")
                                    new_count = old_count + 1
                                    self.__postgre_db.update(schema, "correlating_bscales", "count=" + str(new_count), "bscale_a=" + str(bscale_item_id) + " and bscale_b=" + str(bscale_next_item_id))
                        index += 1

    def find_spo_and_adjectives(self, schema):
        all_snippets_table = self.__postgre_db.get_data_from_table(schema, "snippets")
        all_snippets = [snippet['snippet'] for snippet in all_snippets_table]
        for snippet in self.parser.nlp.pipe(all_snippets, batch_size=3000, n_threads=-1):
            spo = self.parser.get_SVO(snippet)
            for item in spo:
                if item is not None:
                    # subject is pattern
                    if self.__postgre_db.is_in_table(schema, "single_pattern", "single_pattern=" + add_quotes(item.subject)):
                        if item.object != '':
                            self.push_parser_items(schema, item.subject, "subject_occ", "subject")
                            self.push_parser_items(schema, item.object, "object_occ", "object")
                            self.push_parser_items(schema, item.verb, "verb_occ", "verb")
                            self.push_parser_item_relationship(schema,
                                    item.subject, item.verb, "subject_verb_occ", "subject", "verb")
                            self.push_parser_item_relationship(schema,
                                    item.subject, item.object, "subject_object_occ", "subject", "object")
                    #object is pattern
                    elif self.__postgre_db.is_in_table(schema, "single_pattern", "single_pattern=" + add_quotes(item.object)):
                        if item.subject != '':
                            self.push_parser_items(schema, item.subject, "subject_occ", "subject")
                            self.push_parser_items(schema, item.object, "object_occ", "object")
                            self.push_parser_items(schema, item.verb, "verb_occ", "verb")
                            self.push_parser_item_relationship(schema,
                                    item.subject, item.object, "subject_object_occ", "subject", "object")
                            self.push_parser_item_relationship(schema,
                                    item.object, item.verb, "object_verb_occ", "object", "verb")

            noun_adjectives = self.parser.nouns_adj_spacy(snippet)
            for item in noun_adjectives:
                subject = item['noun']
                adjective = item['adj']
                if self.__postgre_db.is_in_table(
                        schema, "single_pattern", "single_pattern=" + add_quotes(item['noun'])):
                    self.push_parser_items(schema, subject, "subject_occ", "subject")
                    self.push_parser_items(schema, adjective, "adjective_occ", "adjective")
                    self.push_parser_item_relationship(
                        schema, subject, adjective, "subject_adjective_occ", "subject", "adjective")

    def push_parser_items(self, schema, word, table, word_type):
        if not self.__postgre_db.is_in_table(schema, table, word_type + "=" + add_quotes(word)):
            self.__postgre_db.insert(schema, table, {word_type: word, "count": 0})

    def push_parser_item_relationship(self, schema, word1, word2, table, word_type1, word_type2):
        word1_id = self.__postgre_db.get_id(schema, word_type1 + "_occ", word_type1 + "=" + add_quotes(word1))
        word2_id = self.__postgre_db.get_id(schema, word_type2 + "_occ", word_type2 + "=" + add_quotes(word2))

        if not self.__postgre_db.is_in_table(schema, table, word_type1 + "=" + str(
                word1_id) + " and " + word_type2 + "=" + str(word2_id)):
            self.__postgre_db.insert(schema, table, {word_type1: word1_id, word_type2: word2_id, "count": 1})
        else:
            table_id = self.__postgre_db.get_id(schema, table, word_type1 + "=" + str(word1_id) + " and " + word_type2 + "=" + str(word2_id))
            old_count = self.__postgre_db.get(schema, table, "id=" + str(table_id), "count")
            self.__postgre_db.update(schema, table, "count=" + str(old_count + 1), "id=" + str(table_id))

    def aggregate_occurences_help(self, text_counter, word):
        count = text_counter[word]
        if count == 0:
            return 1
        else:
            return count

    def calculate_pmi(self, schema):
        print("Calculating PMI for " + schema)
        corpus_count = 0
        for item in self.__mongo_db.get(schema, {}):
            corpus_count += len(word_tokenize(item['text']))
        print(corpus_count)
        print("Lemmatizing corpus.")
        lemmatized_text = []
        for ind, text in enumerate(self.__mongo_db.get(schema, {})):
            doc = text['text']
            for ch in ['›', '‹', '»', '«']:
                if ch in doc:
                    doc = doc.replace(ch, '"')
            lemmatized_text += self.parser.lemmatize_chunk(doc)
            print("Part " + str(ind) + " lemmatized.")
        self.aggregate_occurences(schema, "subject", lemmatized_text)
        self.aggregate_occurences(schema, "object", lemmatized_text)
        self.aggregate_occurences(schema, "adjective", lemmatized_text)
        self.aggregate_occurences(schema, "verb", lemmatized_text)
        print("Finished aggregating occurences.")
        self.calculate_pmi_helper(schema, corpus_count, "subject_adjective_occ", "subject", "adjective")
        self.calculate_pmi_helper(schema, corpus_count, "subject_verb_occ", "subject", "verb")
        self.calculate_pmi_helper(schema, corpus_count, "subject_object_occ", "subject", "object")
        self.calculate_pmi_helper(schema, corpus_count, "object_verb_occ", "object", "verb")

    def aggregate_occurences(self, schema, word_table, lemmatized_text):
        table = self.__postgre_db.get_data_from_table(schema, word_table + "_occ")
        for item in table:
            word = item[word_table]
            split_word = word.split(" ")
            length = len(split_word)
            if length > 1:
                if length == 2:
                    counter = list(bigrams(lemmatized_text))
                    word_tuple = (split_word[0], split_word[1])
                elif length == 3:
                    counter = list(trigrams(lemmatized_text))
                    word_tuple = (split_word[0], split_word[1], split_word[2])
                else:
                    counter = []
                count = counter.count(word_tuple)
            else:
                word = item[word_table]
                count = self.aggregate_occurences_help(Counter(lemmatized_text), word)
            print(word, str(count))
            self.__postgre_db.update(schema, word_table + "_occ", "count=" + str(count), "id=" + str(item['id']))

    def calculate_pmi_helper(self, schema, corpus_count, co_occurence, word1, word2):
        co_occ_table = self.__postgre_db.get_data_from_table(schema, co_occurence)
        for item in co_occ_table:
            item_id = item['id']
            co_occ_freq = float(item['count'] / corpus_count)
            word1_id = item[word1]
            word2_id = item[word2]
            word1_occ = self.__postgre_db.get(schema, word1 + "_occ", "id=" + str(word1_id), "count")
            word2_occ = self.__postgre_db.get(schema, word2 + "_occ", "id=" + str(word2_id), "count")
            pmi = log2(co_occ_freq / (float(word1_occ / corpus_count) * float(word2_occ / corpus_count)))
            self.__postgre_db.update(schema, co_occurence, "pmi=" + str(pmi), "id=" + str(item_id))

    def check_pattern(self, pattern, token):
        """Strip token and check if the token matches the defined pattern.

        Parameter:
        pattern -- the pattern to search for
        token -- the token to match with the pattern
        """
        split_token = re.split('\W+', token)
        if split_token[0] == '':
            split_token = split_token[1]
        else:
            split_token = split_token[0]
        return split_token == pattern

    def get_result(self, schema):
        pprint(self.__postgre_db.query("""SELECT S.subject, V.verb, SV.pmi FROM """ + schema + """.subject_verb_occ SV, """ + schema + """.subject_occ S, """ + schema + """.verb_occ V WHERE SV.subject = S.id AND SV.verb = V.id ORDER BY subject DESC, pmi DESC"""))
        pprint(self.__postgre_db.query("""SELECT O.object, V.verb, OV.pmi FROM """ + schema + """.object_verb_occ OV, """ + schema + """.object_occ O, """ + schema + """.verb_occ V WHERE OV.object = O.id AND OV.verb = V.id ORDER BY object DESC, pmi DESC"""))
        pprint(self.__postgre_db.query("""SELECT O.object, S.subject, SO.pmi FROM """ + schema + """.subject_object_occ SO, """ + schema + """.subject_occ S, """ + schema + """.object_occ O WHERE SO.object = O.id AND SO.subject = S.id ORDER BY subject DESC, pmi DESC"""))
        pprint(self.__postgre_db.query("""SELECT S.subject, A.adjective, SA.pmi FROM """ + schema + """.subject_adjective_occ SA, """ + schema + """.subject_occ S, """ + schema + """.adjective_occ A WHERE SA.subject = S.id AND SA.adjective = A.id ORDER BY subject DESC, pmi DESC"""))