from pg import DB
from HelperMethods import add_quotes


class PostGreDBConnector:
    """PostGreDBConnector opens a PostGre DB connection. Different functions allow you to add, delete or update
    documents in PostGre DB."""

    def __init__(self):
        """Connecting to localhost (default host and port [localhost, 4532]) PostGre DB and initializing needed data
            base and tables."""
        try:
            print("Connecting to PostGre DB...")
            self.__db = DB(dbname='testdb', host='localhost', port=5432, user='postgres', passwd='superuser')
            print("PostGre DB connection successfully built.")
        except ConnectionError:
            print("PostGre DB connection could not be built.")

        self.delete_all_data()
        self.drop_all_tables()
        self.__create_tables()
        # self.__create_functions()

    def close_connection(self):
        self.__db.close()

    def __create_tables(self):
        """Create needed tables for RDF parsing."""
        self._add_table("CREATE TABLE texts (id serial primary key, title text)")
        self._add_table(
            "CREATE TABLE bscale (id serial primary key, bscale text, nominal bool, ordinal bool, interval bool)")
        self._add_table("CREATE TABLE bsort (id serial primary key, bsort text)")
        self._add_table("CREATE TABLE pattern (id serial primary key, pattern text)")
        self._add_table("CREATE TABLE single_pattern (id serial primary key, single_pattern text)")
        self._add_table("CREATE TABLE snippets (id serial primary key, snippet text)")

        # relations
        self._add_table("CREATE TABLE has_attribute (bsort_id int, bscale_id integer[], aggregation int)")
        self._add_table("CREATE TABLE has_object (bscale_id int, pattern_id integer[], aggregation int)")
        self._add_table(
            "CREATE TABLE pattern_single_pattern (pattern_id int, single_pattern_id integer[], aggregation int)")
        self._add_table("CREATE TABLE texts_snippets (text_id int primary key, snippet_id integer[], aggregation int)")
        self._add_table(
            "CREATE TABLE snippet_offsets (id serial primary key,"
            " single_pattern_id int, snippet_id int, offsets integer[][], aggregation int)")

        # adjective and verb extractions
        self._add_table("CREATE TABLE subject_occ (id serial primary key, subject text, count int)")
        self._add_table("CREATE TABLE adjective_occ (id serial primary key, adjective text, count int)")
        self._add_table("CREATE TABLE verb_occ (id serial primary key, verb text, count int)")
        self._add_table("CREATE TABLE object_occ (id serial primary key, object text, count int)")
        self._add_table("CREATE TABLE subject_adjective_occ (id serial primary key, subject int, adjective int, count int)")
        self._add_table("CREATE TABLE subject_object_occ (id serial primary key, subject int, object int, count int)")
        self._add_table("CREATE TABLE object_verb_occ (id serial primary key, object int, verb int, count int)")
        self._add_table("CREATE TABLE subject_verb_occ (id serial primary key, subject int, verb int, count int)")

    def __create_functions(self):
        """Create all necessary functions to aggregate the results saved in the database."""
        self.add_function("aggregate_texts_snippets", "SELECT text_id, array_length(snippet_id, 1) FROM texts_snippets")
        self.add_function("aggregate_snippet_offsets", "SELECT id, array_length(offsets, 1) FROM snippet_offsets")

    def add_function(self, name, function):
        """Create a new function in the db."""
        create_function = "CREATE FUNCTION "
        returns = "() RETURNS SETOF RECORD AS "
        lang = " LANGUAGE SQL"
        query = create_function + name + returns + add_quotes(function) + lang
        self.__db.query(query)

    def _add_table(self, query):
        """Create a new table with a query."""
        self.__db.query(query)

    def add_table(self, name, rows):
        """Create a new table with a name and rows given in query form."""
        create_table = "CREATE TABLE "
        query = create_table + name + rows
        self.__db.query(query)

    def insert(self, table, row):
        """Insert a new row element into a specified table."""
        return self.__db.insert(table, row)

    def is_in_table(self, table, where_clause):
        """Returns whether a row already exists in a table or not."""
        select = "SELECT * FROM "
        where = " WHERE "
        q = select + table + where + where_clause
        result = self.__db.query(q).dictresult()
        if len(result) > 0:
            return True
        else:
            return False

    def update(self, table, values, where_clause):
        """Update an entry in a specified table."""
        UPDATE = "UPDATE "
        SET = " SET "
        WHERE = " WHERE "
        query = UPDATE + table + SET + values + WHERE + where_clause
        self.query(query)

    def get(self, table, where_clause, key):
        """Return the key of a specific item in a table."""
        select = "SELECT "
        _from = " FROM "
        where = " WHERE "
        q = select + key + _from + table + where + where_clause
        result = self.__db.query(q).dictresult()
        if len(result) > 0:
            return result[0][key]
        else:
            return None

    def get_data_from_table(self, table):
        """Gets all data available in a specific table."""
        return self.__db.query("SELECT * FROM " + table).dictresult()

    def get_id(self, table, where_clause):
        """Return the id of an item in a table. If found return id number of found item, else None."""
        select = "SELECT id FROM "
        where = " WHERE "
        q = select + table + where + where_clause
        result = self.__db.query(q).dictresult()
        if len(result) > 0:
            return result[0]['id']
        else:
            return None

    def delete_from_table(self, table, row):
        """Delete a row element form a specific table."""
        return self.__db.delete(table, row)

    def delete_data_in_table(self, table):
        """Delete all data in a specific table."""
        self.__db.truncate(table, restart=True, cascade=True, only=False)

    def delete_all_data(self):
        """Deletes all data from all existing tables."""
        tables = self.get_tables()
        for table in tables:
            table_name = str(table.split('.')[1])
            self.delete_data_in_table(table_name)

    def get_tables(self):
        """Get all available tables in the database."""
        return self.__db.get_tables()

    def get_attributes(self, table):
        """Get all attributes of a specified table."""
        return self.__db.get_attnames(table)

    def drop_table(self, table):
        """Drops a specified table."""
        query = "DROP TABLE "
        self.__db.query(query + table)

    def drop_all_tables(self):
        """Drops all existing tables."""
        tables = self.get_tables()
        table_names = ""
        if len(tables) > 0 :
            for ind, table in enumerate(tables):
                if ind == 0:
                    table_names = str(table.split('.')[1])
                else:
                    table_names = table_names + ", " + str(table.split('.')[1])
            self.__db.query("DROP TABLE " + table_names)
        else:
            print("Nothing to delete.")

    def get_all(self, table, attribute):
        """Gets one or more attributes of all entries from a specified table."""
        select = "SELECT "
        _from = " FROM "
        query = select + attribute + _from + table
        return self.__db.query(query).dictresult()

    def query(self, query):
        """Sends a query to the database."""
        result = self.__db.query(query)
        if result is not None:
            if not isinstance(result, str):
                return result.dictresult()
        else:
            return result

#db = PostGreDBConnector()

#parser = RDFParser(db)
#parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/bscale_test.rdf")
#db.insert("bscale", {"bscale": "test", "nominal": True})
#print(db.get("bscale", "id=1", "id"))
#db.update("bscale", "interval='False'","id=1")
#str = "Rogoshin"
#key = "MainCharacter"
#print(db.insert("bsort", {"bsort": "Maincharacter"}))
#db.drop_table("test")
#db.add_table1("CREATE TABLE integer (id serial primary key, title integer[])")
#print(db.is_in_table("snippet_offsets", "single_pattern_id=59 and snippet_id=1"))
#print(db.insert("snippet_offsets", {"single_pattern_id": 59, "snippet_id": 1, "offsets": [[3, 8], [14,17]]}))
#print(db.insert("snippet_offsets", {"single_pattern_id": 59, "snippet_id": 5, "offsets": [[9, 14]]}))
#print(db.insert("snippet_offsets", {"single_pattern_id": 57, "snippet_id": 57, "offsets": [[3, 8], [9, 14], [67, 71]]}))
#print(db.insert("single_pattern_snippets", {"single_pattern_id": 1, "snippet_id": [3,4,5]}))
#print(db.insert("single_pattern_snippets", {"single_pattern_id": 2, "snippet_id": [6,8,9,10]}))
#print(db.insert("pattern_single_pattern", {"pattern_id": 1, "single_pattern_id": [3,4,5]}))
#print(db.insert("pattern_single_pattern", {"pattern_id": 2, "single_pattern_id": [6,8,9,10]}))
#print(db.get_all("single_pattern_snippets", "snippet_id"))
#print(db.get_id("bsort", "bsort='Maincharacter'"))
#print(db.get("pattern_single_pattern", "pattern_id=3", "single_pattern_id"))
#print(db.is_in_table("pattern_single_pattern", "pattern_id=" + str(3)))
#pattern = db.get_all("single_pattern")
#for patter in pattern:
#    print(patter['single_pattern'])
#print(db.is_in_table("pattern_single_pattern", "pattern_id=58"))
#print(db.insert('fruits', {"name": "kirsche"}))
#print(db.get_attributes('fruits'))
#print(db.get_tables())
#print(db.insert("single_pattern_snippets", {"single_pattern_id": 1}))
#print(db.is_in_table("single_pattern_snippets", "single_pattern_id=1"))
#db.insert("texts", {"title": "Chapter 1"})
#print(db.insert("snippets", {"snippet": "»Nun, wenn's so ist«, rief Rogoshin, »so bist du ja ein richtiger Gottesnarr, Fürst, und solche Menschen wie dich liebt Gott.«"}))

#print(db.query("""CREATE FUNCTION arraycount() RETURNS int AS 'SELECT table.snippet_id.COUNT FROM single_pattern_snippets table WHERE single_pattern_id = 57' LANGUAGE SQL"""))
#print(db.query("SELECT arraycount() AS answer"))

# TODO use with for loop if only snippet_offsets relation is used
#print(db.create_function("counting", "'SELECT COUNT(single_pattern_id) FROM single_pattern_snippets WHERE single_pattern_id=57'"))

#print(db.query("SELECT single_pattern_id, array_length(offsets, 1) FROM snippet_offsets"))
#print(db.query("SELECT single_pattern_id, array_length(snippet_id, 1) FROM single_pattern_snippets"))
#print(db.query("""CREATE FUNCTION OR REPLACE double_salary(single_pattern_snippets) RETURNS integer[] AS $$ SELECT $COUNT(snippet_id) AS newid $$ LANGUAGE SQL"""))
#print(db.query("""SELECT double_salary(single_pattern_snippets) FROM single_pattern_snippets WHERE single_pattern_snippets.single_pattern_id = 57"""))
#print(db.query("CREATE FUNCTION array_lengths() RETURNS SETOF RECORD AS 'SELECT single_pattern_id, array_length(snippet_id, 1) FROM single_pattern_snippets' LANGUAGE SQL"))
#snippet_no = db.query("SELECT array_lengths()")
#print(snippet_no[1]['array_lengths']) # can extract the tuple like this.
#print(db.query("SELECT unnest_pattern_single_pattern()"))
#print(db.update("single_pattern_snippets", "aggregation=3", "single_pattern_id=1"))
#print(db.get_data_from_table("single_pattern_snippets"))
