import re
import csv

def add_quotes(string):
    return "'" + string + "'"


def compile_pattern(string):
    """Compile a found pattern to search for it in text."""
    return re.compile(string)


def replace_special_characters(string):
    """Replaces special characters that cannot be stored by PostGre DB otherwise."""
    return string.replace("'", "''")


def replace_brackets(string):
    """Replaces brackets that cannot be stored by PostGre DB otherwise."""
    return string.replace("[", "{").replace("]", "}")


def read_in_csv_file(filename):
    """Read in a csv_file with a specified file name."""
    if not filename.endswith(".csv"):
        raise Exception("Invalid file format")

    constraint_list = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        constraints = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        for row in constraints:
            if row:
                constraint_list.append((row[0], row[1], int(row[2])))
            else:
                return None
    return constraint_list


def read_in_txt_file(filename):
    """Read in file and return file content as string."""
    if not filename.endswith(".txt"):
        raise Exception("Invalid file format.")

    with open(filename, 'r', encoding="utf-8") as file:
        return file.read()
