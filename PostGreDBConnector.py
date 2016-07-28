from pg import DB
from RDFParser import RDFParser


class PostGreDBConnector():
    """PostGreDBConnector opens a PostGre DB connection. Different functions allow you to add, delete or update documents
     in PostGre DB."""

    def __init__(self):
        """Connecting to localhost (default host and port [localhost, 4532]) PostGre DB and initializing needed data
            base and tables."""
        try:
            self.__db = DB(dbname='testdb', host='localhost', port=5432, user='postgres', passwd='superuser')
            print("PostGre DB connection successfully built...")
        except Exception:
            print("PostGre DB connection could not be built...")

        self.delete_all_data()
        self.drop_all_tables()
        self.create_tables()

    def create_tables(self):
        """Create needed tables for RDF parsing."""
        self._add_table("CREATE TABLE texts (id serial primary key, title text)")
        self._add_table("CREATE TABLE bscale (id serial primary key, bscale text)")
        self._add_table("CREATE TABLE bsort (id serial primary key, bsort text)")
        self._add_table("CREATE TABLE pattern (id serial primary key, pattern text)")
        self._add_table("CREATE TABLE single_pattern (id serial primary key, single_pattern text)")
        self._add_table("CREATE TABLE snippets (id serial primary key, snippet text)")

        # relations
        self._add_table("CREATE TABLE has_attribute (bsort_id int, bscale_id integer[])")
        self._add_table("CREATE TABLE has_object (bscale_id int, pattern_id integer[])")
        self._add_table("CREATE TABLE pattern_single_pattern (pattern_id int, single_pattern_id integer[])")
        self._add_table(
            "CREATE TABLE single_pattern_snippets (single_pattern_id int primary key, snippet_id integer[])")
        self._add_table("CREATE TABLE texts_snippets (text_id int primary key, snippet_id integer[])")

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

    def get(self, table, where_clause, key):
        """Search for a chosen key of a specific item in a table."""
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
        """Search for a specific id of an item in a table. If found return id number of found item, else None."""
        select = "SELECT id FROM "
        where = " WHERE "
        q = select + table + where + where_clause
        result = self.__db.query(q).dictresult()
        if len(result) > 0:
            return result[0]['id']
        else:
            return None

    def update(self, table, row, **kw):
        """Update a already existing row for a table."""
        return self.__db.update(table, row, **kw)

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
        for ind, table in enumerate(tables):
            if ind == 0:
                table_names = str(table.split('.')[1])
            else:
                table_names = table_names + ", " + str(table.split('.')[1])
        self.__db.query("DROP TABLE " + table_names)

    def get_all(self, table, attribute):
        """Gets one or more attributes of all entries from a specified table."""
        select = "SELECT "
        _from = " FROM "
        query = select + attribute + _from + table
        return self.__db.query(query).dictresult()

    def query(self, query):
        return self.__db.query(query).dictresult()

#db = PostGreDBConnector()
#parser = RDFParser(db)
#parser.get_pattern_from_rdf("C:/Users/din_m/PycharmProjects/Masterarbeit/persons.rdf")
#str = "Rogoshin"
#key = "MainCharacter"
#print(db.insert("bsort", {"bsort": "Maincharacter"}))
#db.drop_table("test")
#db.add_table1("CREATE TABLE integer (id serial primary key, title integer[])")
#print(db.insert("single_pattern_snippets", {"single_pattern_id": 59, "snippet_id": [1,2,3]}))
#print(db.insert("single_pattern_snippets", {"single_pattern_id": 57, "snippet_id": [3,4,5]}))
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
#print(db.is_in_table("snippets", "snippet='»Nun, wenn''s so ist«, rief Rogoshin, »so bist du ja ein richtiger Gottesnarr, Fürst, und solche Menschen wie dich liebt Gott.«'"))
#print(db.insert("snippets", {"snippet": "»Nun, wenn's so ist«, rief Rogoshin, »so bist du ja ein richtiger Gottesnarr, Fürst, und solche Menschen wie dich liebt Gott.«"}))
