from pyparsing import alphas, dblQuotedString, Forward, Literal, Group, OneOrMore, Optional, removeQuotes, Suppress, \
    Word

class RDFParser:
    """RDFParser is a parser to parse RDF files (aka ontologies) and pushing the found pattern onto the database."""

    def __init__(self, db):
        """Initialize a new RDF parser with pre-defined grammar. Takes database db as an argument."""
        self.__db = db
        self.__pattern_id = 0
        self.__single_pattern_id = 0

        # grammar definition
        # literals
        self.__word = self.__prefix = self.__suffix = Word(alphas)
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

    def read_in_rdf_file(self, filename):
        """Read in a rdf_file with a specified file name."""
        cleaned_rdf = []
        with open(filename, 'r') as file:
            data = file.read()
            rdf_data = data.splitlines()
            for data in rdf_data:
                if data != '':
                    cleaned_rdf.append(data)
            return cleaned_rdf

    def get_pattern_from_rdf(self, filename):
        """Extract all needed pattern from a rdf file and then push them onto the database."""
        data = self.read_in_rdf_file(filename)
        pattern_list = dict()
        for statements in data:
            parser_result = self.__search.parseString(statements)
            subject, relation, object = parser_result

            # filter pattern
            if relation == 'hasPattern':
                pattern_list.update({subject: object})
                # TODO debug line
                # print "%s %s %s" % (subject, has_pattern, object)

        self.__push_pattern(pattern_list)

    def __push_pattern(self, pattern_list):
        """Push found rdf pattern onto the database."""
        for key in pattern_list:
            pattern = pattern_list[key]

            # push pattern
            f_pat = {"pattern_id": self.__pattern_id, "pattern": key, "single_pattern": []}
            self.__pattern_id += 1
            new_s_pattern = []
            self.__db.pattern.insert_one(f_pat)
            for single_pattern in pattern:

                # push single pattern
                f_pattern = {"single_pattern_id": self.__single_pattern_id, "single_pattern": single_pattern}
                new_s_pattern.append(self.__single_pattern_id)
                self.__single_pattern_id += 1
                self.__db.single_pattern.insert_one(f_pattern)

                # modify already saved pattern with new list of single pattern, if necessary
                self.__db.pattern.find_and_modify(query={"pattern_id": self.__pattern_id - 1},
                                                  update={"$set": {"single_pattern": new_s_pattern}})
