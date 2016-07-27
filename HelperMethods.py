import re


def add_quotes(string):
    return "'" + string + "'"


def compile_pattern(string):
    """Compile a found pattern to search for it in text."""
    return re.compile(string)


def replace_special_characters(string):
    """Replaces special characters that cannot be stored by PostGre DB otherwise."""
    return string.replace("'", "''")


def search_for_dialog(snippet):
    dialog_boundary_begin = re.compile("(\»|\›)")
    dialog_boundary_end = re.compile("(\«|\‹)")
    #dialogs = sentence_window_one_word_help(0, dialog_boundary_begin)

