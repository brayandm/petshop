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
            id SERIAL PRIMARY KEY,
            prev_owner_id INTEGER REFERENCES petshop.users(id),
            new_owner_id INTEGER REFERENCES petshop.users(id),
            pet_id INTEGER REFERENCES petshop.pets(id),
            amount NUMERIC(10, 2) NOT NULL,
            date TIMESTAMP NOT NULL
        );
        """

        births_table_query = """
        CREATE TABLE IF NOT EXISTS petshop.births (
            id SERIAL PRIMARY KEY,
            father_id INTEGER REFERENCES petshop.pets(id),
            mother_id INTEGER REFERENCES petshop.pets(id),
            children_id INTEGER REFERENCES petshop.pets(id),
            time TIMESTAMP NOT NULL
        );
        """

        events_table_query = """
        CREATE TABLE IF NOT EXISTS petshop.events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(255) NOT NULL,
            original_event_id BIGINT,
            user_id INTEGER,
            user_email VARCHAR(255),
            user_name VARCHAR(255),
            prev_owner_id INTEGER,
            prev_owner_email VARCHAR(255),
            prev_owner_name VARCHAR(255),
            new_owner_id INTEGER,
            new_owner_email VARCHAR(255),
            new_owner_name VARCHAR(255),
            father_id INTEGER,
            father_name VARCHAR(255),
            father_sex VARCHAR(1),
            mother_id INTEGER,
            mother_name VARCHAR(255),
            mother_sex VARCHAR(1),
            pet_id INTEGER,
            pet_name VARCHAR(255),
            pet_sex VARCHAR(1),
            children_id INTEGER,
            children_name VARCHAR(255),
            children_sex VARCHAR(1),
            type_id INTEGER,
            type_name VARCHAR(255),
            pet_sold BOOLEAN,
            amount NUMERIC(10, 2),
            event_time TIMESTAMP NOT NULL
        );
        """

        self.cursor.execute(users_table_query)
        self.cursor.execute(types_table_query)
        self.cursor.execute(pets_table_query)
        self.cursor.execute(purchases_table_query)
        self.cursor.execute(births_table_query)
        self.cursor.execute(events_table_query)
        self.connection.commit()

    def drop_tables(self):
        self.cursor.execute("DROP TABLE IF EXISTS petshop.events;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.births;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.purchases;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.pets;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.types;")
        self.cursor.execute("DROP TABLE IF EXISTS petshop.users;")
        self.connection.commit()