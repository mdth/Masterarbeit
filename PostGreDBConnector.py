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
        self.create_schema("dostojewski")
        self.create_schema("storm")

    def close_connection(self):
        self.__db.close()

    def create_schema(self, schema_name):
        self.__db.query("CREATE SCHEMA " + schema_name)
        self.__create_tables(schema_name)
        self.__create_functions(schema_name)

    def __create_tables(self, schema):
        """Create needed tables for RDF parsing."""
        schema += "."
        self._add_table("CREATE TABLE " + schema + "texts (id serial primary key, title text)")
        self._add_table(
            "CREATE TABLE " + schema + "bscale (id serial primary key, bscale text, nominal bool, ordinal bool, interval bool)")
        self._add_table("CREATE TABLE " + schema + "bsort (id serial primary key, bsort text)")
        self._add_table("CREATE TABLE " + schema + "pattern (id serial primary key, pattern text)")
        self._add_table("CREATE TABLE " + schema + "single_pattern (id serial primary key, single_pattern text)")
        self._add_table("CREATE TABLE " + schema + "snippets (id serial primary key, snippet text)")

        # relations
        self._add_table("CREATE TABLE " + schema + "has_attribute (bsort_id int, bscale_id integer[], aggregation int)")
        self._add_table("CREATE TABLE " + schema + "has_object (bscale_id int, pattern_id integer[], aggregation int)")
        self._add_table(
            "CREATE TABLE " + schema + "pattern_single_pattern (pattern_id int, single_pattern_id integer[], aggregation int)")
        self._add_table("CREATE TABLE " + schema + "texts_snippets (text_id int primary key, snippet_id integer[], aggregation int)")
        self._add_table(
            "CREATE TABLE " + schema + "snippet_offsets (id serial primary key,"
            " single_pattern_id int, snippet_id int, offsets integer[][], aggregation int)")

        # adjective and verb extractions
        self._add_table("CREATE TABLE " + schema + "subject_occ (id serial primary key, subject text, count int)")
        self._add_table("CREATE TABLE " + schema + "adjective_occ (id serial primary key, adjective text, count int)")
        self._add_table("CREATE TABLE " + schema + "verb_occ (id serial primary key, verb text, count int)")
        self._add_table("CREATE TABLE " + schema + "object_occ (id serial primary key, object text, count int)")
        self._add_table("CREATE TABLE " + schema + "subject_adjective_occ (id serial primary key, subject int, adjective int, count int, pmi float)")
        self._add_table("CREATE TABLE " + schema + "subject_object_occ (id serial primary key, subject int, object int, count int, pmi float)")
        self._add_table("CREATE TABLE " + schema + "object_verb_occ (id serial primary key, object int, verb int, count int, pmi float)")
        self._add_table("CREATE TABLE " + schema + "subject_verb_occ (id serial primary key, subject int, verb int, count int, pmi float)")

    def __create_functions(self, schema):
        """Create all necessary functions to aggregate the results saved in the database."""
        schema += schema + "."
        self.add_function(schema + "aggregate_texts_snippets", "SELECT text_id, array_length(snippet_id, 1) FROM texts_snippets")
        self.add_function(schema + "aggregate_snippet_offsets", "SELECT id, array_length(offsets, 1) FROM snippet_offsets")

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
