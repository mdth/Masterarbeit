from pyparsing import alphanums, dblQuotedString, Forward, Literal, Group, OneOrMore, Optional, removeQuotes, Suppress, \
    Word
from HelperMethods import add_quotes


class RDFParser:
    """RDFParser is a parser to parse specified RDF files (aka ontologies) and pushing the found pattern onto the
    database."""

    def __init__(self, db):
        """Initialize a new RDF parser with pre-defined grammar. Takes database db as an argument."""
        self.__db = db

        # grammar definition
        # literals
        self.__word = self.__prefix = self.__suffix = Word(alphanums)
        self.__colon = Literal(':')
        self.__a = Literal('a')
        self.__quoted_string = dblQuotedString.setParseAction(removeQuotes)
        self.__l_paren = Suppress('(')
        self.__r_paren = Suppress(')')
        self.__dot = Suppress('.')
        self.__comma = Suppress(',')
        self.__semicolon = Suppress(';')

        # composites
        self.__get_suffix = Suppress(self.__prefix + self.__colon) + self.__suffix
        self.__get_object = Optional(self.__l_paren) + OneOrMore((self.__get_suffix | self.__quoted_string) +
                                                                 Optional(self.__comma)) + Optional(self.__r_paren)
        self.__is_a = (self.__get_suffix('subject') | self.__word) + self.__a('relation') + \
                      self.__get_suffix('object') + self.__dot
        self.__has_x = self.__get_suffix('subject') + self.__get_suffix('relation') + \
                       Group(self.__get_object)('object') + self.__dot

        # search term
        self.__search = Forward()
        self.__search << (self.__is_a | self.__has_x)

    def get_pattern_and_push(self, schema, filename):
        pattern = self.get_pattern_from_rdf(filename)
        self.push_data(schema, pattern[0], pattern[1], pattern[2], pattern[3])

    def get_pattern_from_rdf(self, filename):
        """Extract all needed pattern from a rdf file and then push them onto the database."""
        data = read_in_rdf_file(filename)
        pattern_list = dict()
        attribute_list = dict()
        object_list = dict()
        scale_list = dict()

        for statements in data:
            subject, relation, object = self.__search.parseString(statements)

            # filter relations
            if relation == 'hasPattern':
                pattern_list.update({subject: object})
            elif relation == 'hasAttribute':
                attribute_list.update({subject: object})
            elif relation == "hasObject":
                object_list.update({subject: object})
            elif relation == "hasScale":
                scale_list.update({subject: object})
            else:
                pass
        return pattern_list, attribute_list, object_list, scale_list

    def push_data(self, schema, pattern_list, attribute_list, object_list, scale_list):
        """Pushes found data onto the database."""
        self.__push_pattern(schema, pattern_list)
        self.__push_attribute(schema, attribute_list)
        self.__push_objects(schema, object_list)
        self.__push_scales(schema, scale_list)

    def __push_pattern(self, schema, pattern_list):
        """Push found rdf pattern onto the database."""
        for key in pattern_list:
            pattern = pattern_list[key]

            # push pattern
            new_s_pattern = []
            if not self.__db.is_in_table(schema, "pattern", "pattern=" + add_quotes(key)):
                self.__db.insert(schema, "pattern", {"pattern": key})

            # push single pattern
            for single_pattern in pattern:
                if not self.__db.is_in_table(schema, "single_pattern", "single_pattern=" + add_quotes(single_pattern)):
                    self.__db.insert(schema, "single_pattern", {"single_pattern": single_pattern})
                single_pattern_id = self.__db.get_id(schema, "single_pattern", "single_pattern=" + add_quotes(single_pattern))
                new_s_pattern.append(single_pattern_id)

            pattern_id = self.__db.get_id(schema, "pattern", "pattern=" + add_quotes(key))
            self.__db.insert(schema, "pattern_single_pattern", {
                "pattern_id": pattern_id, "single_pattern_id": new_s_pattern, "aggregation": 0})

    def __push_attribute(self, schema, attribute_list):
        """Push found rdf attributes onto the database."""
        for key in attribute_list:
            attributes = attribute_list[key]

            # push bsort
            new_attributes = []
            self.__db.insert(schema, "bsort", {"bsort": key})

            # push bscale and has_attribute relation
            for attribute in attributes:
                # look out for duplicates
                if not self.__db.is_in_table(schema, "bscale", "bscale=" + add_quotes(attribute)):
                    self.__db.insert(schema,
                        "bscale", {"bscale": attribute, "nominal": False, "ordinal": False, "interval": False})
                new_attributes.append(self.__db.get_id(schema, "bscale", "bscale=" + add_quotes(attribute)))

            bsort_id = self.__db.get_id(schema, "bsort", "bsort=" + add_quotes(key))
            self.__db.insert(schema, "has_attribute", {"bsort_id": bsort_id, "bscale_id": new_attributes, "aggregation": 0})

    def __push_objects(self, schema, object_list):
        """Push found rdf objects onto the database."""
        for key in object_list:
            objects = object_list[key]
            new_attributes = []

            # push bscale x pattern relation
            for object in objects:
                new_attributes.append(self.__db.get_id(schema, "pattern", "pattern=" + add_quotes(object)))
            bscale_id = self.__db.get_id(schema, "bscale", "bscale=" + add_quotes(key))
            self.__db.insert(schema, "has_object", {"bscale_id": bscale_id, "pattern_id": new_attributes, "aggregation": 0})

    def __push_scales(self, schema, scale_list):
        """Push found rdf bscale attributes onto the database."""
        for key in scale_list:
            #
            scale = scale_list[key][0]
            if scale == 'nominal':
                row = "nominal"
            elif scale == 'ordinal':
                row = "ordinal"
            elif scale == 'interval':
                row = "interval"
            else:
                raise Exception("Invalid scale attribute.")

            if self.__db.is_in_table(schema, "bscale", "bscale=" + add_quotes(key)):
                bscale_id = self.__db.get_id(schema, "bscale", "bscale=" + add_quotes(key))
                self.__db.update(schema, "bscale", row + "=" + add_quotes('True'), "id=" + str(bscale_id))


def read_in_rdf_file(filename):
    """Read in a rdf_file with a specified file name."""
    if not filename.endswith(".rdf"):
        raise Exception("Invalid file format")

    cleaned_rdf = []
    with open(filename, 'r', encoding="utf-8") as file:
        data = file.read()
        rdf_data = data.splitlines()
        for data in rdf_data:
            if data != '':
                cleaned_rdf.append(data)
        return cleaned_rdf
