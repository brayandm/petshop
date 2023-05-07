class DatabaseManager:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection
        self.create_schema()

    def create_schema(self):
        schema_query = "CREATE SCHEMA IF NOT EXISTS petshop;"
        self.cursor.execute(schema_query)
        self.connection.commit()

    def create_tables(self):
        users_table_query = """
        CREATE TABLE IF NOT EXISTS petshop.users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            balance NUMERIC(10, 2) NOT NULL
        );
        """

        types_table_query = """
        CREATE TABLE IF NOT EXISTS petshop.types (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """

        pets_table_query = """
        CREATE TABLE IF NOT EXISTS petshop.pets (
            id SERIAL PRIMARY KEY,
            owner_id INTEGER REFERENCES petshop.users(id),
            type_id INTEGER REFERENCES petshop.types(id),
            name VARCHAR(255) NOT NULL,
            sex VARCHAR(1) NOT NULL
        );
        """

        purchases_table_query = """
        CREATE TABLE IF NOT EXISTS petshop.purchases (
            prev_owner_id INTEGER REFERENCES petshop.users(id),
            new_owner_id INTEGER REFERENCES petshop.users(id),
            pet_id INTEGER REFERENCES petshop.pets(id),
            amount NUMERIC(10, 2) NOT NULL,
            date TIMESTAMP NOT NULL
        );
        """

        births_table_query = """
        CREATE TABLE IF NOT EXISTS petshop.births (
            father_id INTEGER REFERENCES petshop.pets(id),
            mother_id INTEGER REFERENCES petshop.pets(id),
            children_id INTEGER REFERENCES petshop.pets(id),
            time TIMESTAMP NOT NULL
        );
        """

        self.cursor.execute(users_table_query)
        self.cursor.execute(types_table_query)
        self.cursor.execute(pets_table_query)
        self.cursor.execute(purchases_table_query)
        self.cursor.execute(births_table_query)
        self.connection.commit()

    def drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS petshop.births;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.purchases;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.pets;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.types;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.users;")
        self.connection.commit()