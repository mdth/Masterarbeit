import re


def add_quotes(string):
    return "'" + string + "'"


def compile_pattern(string):
    """Compile a found pattern to search for it in text."""
    return re.compile(string)


def replace_special_characters(string):
    # TODO
    """Replaces special characters that cannot be stored by PostGre DB otherwise."""
    return string.replace("'", "''")


def replace_brackets(string):
    """Replaces brackets that cannot be stored by PostGre DB otherwise."""
    return string.replace("[", "{").replace("]", "}")