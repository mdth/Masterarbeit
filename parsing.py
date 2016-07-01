import time
import re
import RDFParser
import POSTagger
from pg import DB
from pymongo import MongoClient

snippet_id = 0


def connecting_to_db():
    """Connecting to localhost MongoDB."""
    # default host and port (localhost, 27017)
    client = MongoClient()
    print("DBMongo connection sucessfully built...")
    global db
    db = client.database


def connecting_postgre_db():
    """Connecting to localhost PostGreDB."""
    # default host and port (localhost)
    global pdb
    pdb = DB(dbname='testdb', user='postgre', passwd='superuser')
    print("PostGre DB connection sucessfully built...")


def compile_pattern(string):
    """Compile a found pattern to search for it in text."""
    return re.compile(string)


def strip_token(pattern, token):
    split_token = re.split('\W+', token, 1)
    if split_token[0] == '':
        split_token = split_token[1]
    else:
        split_token = split_token[0]
    return split_token == pattern


def word_window(size, pattern, tokens):
    """Get a word window list with a specific number of words."""
    split_pattern = pattern.split()
    if len(split_pattern) > 1:
        textsnippets = word_window_more_words_help(size, split_pattern, tokens)

    else:
        textsnippets = word_window_one_word_help(size, pattern, tokens)

    return textsnippets


def word_window_more_words_help(size, split_pattern, tokens):
    textsnippets = []
    for ind, token in enumerate(tokens):
        p_index = 0
        end_index = ind
        while p_index < len(split_pattern):
            if strip_token(split_pattern[p_index], tokens[end_index]):
                p_index += 1
                end_index += 1
            else:
                break
        if p_index == len(split_pattern):
            textsnippets.append(get_textsnippets(ind, end_index - 1, size, len(tokens), tokens))
    return textsnippets


def word_window_one_word_help(size, pattern, tokens):
    textsnippets = []
    textlength = len(tokens)
    for ind, token in enumerate(tokens):
        if strip_token(pattern, token):
            textsnippets.append(get_textsnippets(ind, ind, size, textlength, tokens))
    return textsnippets


def get_textsnippets(indl, indr, size, textlength, tokens):
    if (indl - size < 0) and (indr + size > textlength):
        left_index = size - 1
        while not (indl - left_index) == 0:
            left_index -= 1
        right_index = size - 1
        while not (indr + right_index) == textlength:
            right_index -= 1
        return " ".join(tokens[indl - left_index:indr + right_index])

    elif indr + size > textlength:
        right_index = size - 1
        while not (indr + right_index) == textlength:
            right_index -= 1
        return " ".join(tokens[indl - size:indr + right_index])

    elif indl - size < 0:
        left_index = size - 1
        while not (indl - left_index) == 0:
            left_index -= 1
        return " ".join(tokens[indl - left_index:indr + size + 1])
    else:
        return " ".join(tokens[indl - size:indr + (size + 1)])


def find_right_sentence_boundary(tokens, ind, steps):
    sentence_boundary = compile_pattern('(\w)*(\.|!|\?)+(?!.)')
    sentence_boundary_special = compile_pattern('(\w)*(\.|!|\?)\S(?!,)')
    next_token = compile_pattern('(\W)*(\w+)(,)*')
    found_boundary = False

    if re.search(sentence_boundary, tokens[ind + steps]):
        found_boundary = True
    elif re.search(sentence_boundary_special, tokens[ind + steps]):
        next_index = ind + steps + 1
        if next_index <= (len(tokens) - 1):
            found_boundary = re.search(next_token, tokens[ind + steps + 1])
    return found_boundary


def find_left_sentence_boundary(tokens, ind, steps):
    sentence_boundary = compile_pattern('(\w)*(\.|!|\?)+(?!.)')
    sentence_boundary_special = compile_pattern('(\w)*(\.|!|\?)\S')
    next_token = compile_pattern('(\W(\w+)(,)*)')
    found_boundary = False

    if re.search(sentence_boundary, tokens[ind - steps]):
        found_boundary = True
    elif re.search(sentence_boundary_special, tokens[ind - steps]):
        next_index = ind - steps + 1
        if next_index >= 0:
            found_boundary = re.search(next_token, tokens[ind - steps + 1])

    return found_boundary


def sentence_window(size, pattern, tokens):
    """Get a word window list with a specific number of sentences. size 0 will return the
    current sentence the pattern is found in. size n will return n sentences left and right
    from the initial sentence."""
    sent_size = size + 1
    split_pattern = pattern.split()
    if len(split_pattern) > 1:
        textsnippets = sentence_window_more_words_help(sent_size, split_pattern, tokens)
    else:
        textsnippets = sentence_window_one_word_help(sent_size, pattern, tokens)
    return textsnippets


def sentence_window_more_words_help(sent_size, split_pattern, tokens):
    textsnippets = []
    for ind, token in enumerate(tokens):
        p_index = 0
        end_index = ind
        while p_index < len(split_pattern):
            if (end_index < len(tokens)) and strip_token(split_pattern[p_index], tokens[end_index]):
                p_index += 1
                end_index += 1
            else:
                break
        if p_index == len(split_pattern):
            textsnippets.append(get_textsnippets_sentence(sent_size, tokens, ind, end_index - 1))
    return textsnippets


def get_textsnippets_sentence(sent_size, tokens, beg_index, end_index):
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


def sentence_window_one_word_help(sent_size, pattern, tokens):
    textsnippets = []
    for ind, token in enumerate(tokens):
        if strip_token(pattern, token):
            textsnippets.append(get_textsnippets_sentence(sent_size, tokens, ind, ind))
    return textsnippets


def find_text_window(sentence, text, text_id, size):
    """Finds text windows with variable size."""
    split_text = text.split()

    for pattern in db.single_pattern.find():
        if sentence:
            snippets = sentence_window(size, pattern['single_pattern'], split_text)
        else:
            snippets = word_window(size, pattern['single_pattern'], split_text)
        if len(snippets) > 0:
            single_pattern_id = pattern['single_pattern_id']
            push_snippets(snippets, single_pattern_id)
            push_aggregation(text_id, single_pattern_id)


def push_aggregation(text_id, single_pattern_id):
    global db
    if not db.aggregation.find_one({"id": text_id}):
        db.aggregation.insert_one({"id": text_id, "single_pattern_id": [single_pattern_id]})
    else:
        saved_relation = db.aggregation.find_one({"id": text_id})
        old_pattern = saved_relation["single_pattern_id"]
        old_pattern.append(single_pattern_id)
        db.aggregation.find_and_modify({"id": text_id}, {"$set": {"single_pattern_id": old_pattern}})


def push_snippets(snippets, current_single_pattern_id):
    global db, snippet_id
    if len(snippets) > 0:
        for snippet in snippets:
            if not db.snippets.find_one({"text_snippet": snippet}):
                f_snippet = {"snippet_id": snippet_id, "text_snippet": snippet}
                push_pattern_snippets(current_single_pattern_id, snippet_id)
                snippet_id += 1
                db.snippets.insert_one(f_snippet)


def push_pattern_snippets(current_single_pattern_id, current_snippet_id):
    global db
    if not db.single_pattern_snippets.find_one({"single_pattern_id": current_single_pattern_id}):
        db.single_pattern_snippets.insert_one({"single_pattern_id": current_single_pattern_id, "snippet_id": [current_snippet_id]})
    else:
        saved_relation = db.single_pattern_snippets.find_one({"single_pattern_id": current_single_pattern_id})
        old_snippets = saved_relation["snippet_id"]
        old_snippets.append(snippet_id)
        db.single_pattern_snippets.find_and_modify({"single_pattern_id": current_single_pattern_id},
                                                   {"$set": {"snippet_id": old_snippets}})


def get_db_text(sentence, size):
    for ind, text in enumerate(db.dostojewski.find({"title": "Chapter 7"})):
        find_text_window(sentence, text['text'], text['id'], size)
        print("Chapter " + str(ind + 1) + " done.")


def aggregation():
    for pattern in db.aggregation.find():
        num_of_snippets = 0
        single_pattern = pattern['single_pattern_id']

        for spattern_id in single_pattern:
            for snippets in db.single_pattern_snippets.find({"single_pattern_id": spattern_id}):
                num_of_snippets += len(snippets['snippet_id'])
        print("Number of Snippets for text with id " + str(pattern['id']) + ": " + str(num_of_snippets))


def debug_pretty_print():
    global db

    print()
    print("------------------- Number of chapters in the DB -------------------")
    print(db.dostojewski.count())
    print()
    print("------------------- Pattern in the DB -------------------")
    for p in db.pattern.find({}, {"_id": 0}):
        print(p)
    print()
    print("------------------- Snippets in the DB -------------------")
    for p in db.snippets.find({}, {"_id": 0}):
        print(p)
    print()
    print("------------------- Single pattern & Snippet relation in the DB -------------------")
    for relation in db.single_pattern_snippets.find({}, {"_id": 0}):
        print(relation)
    print()
    print("------------------- Aggregation of found pattern in the DB -------------------")
    for relation in db.aggregation.find({}, {"_id": 0}):
        print(relation)
    print()


def delete_previous_results():
    db.snippets.delete_many({})
    db.pattern.delete_many({})
    db.single_pattern.delete_many({})
    db.single_pattern_snippets.delete_many({})
    db.aggregation.delete_many({})

print("Begin: " + str(time.time()))
connecting_to_db()
delete_previous_results()
parser = RDFParser(db)
parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/persons.rdf")
get_db_text(True, 0)  # Sentence mode

# debug print
debug_pretty_print()
aggregation()

print("End: " + str(time.time()))
