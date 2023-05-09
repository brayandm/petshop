import connection
from database_manager import DatabaseManager
from pet_shop import PetShop
from seeder import Seeder

if __name__ == '__main__':
    (cursor, connection) = connection.connect()
    database_manager = DatabaseManager(cursor, connection)
    database_manager.drop_tables()
    database_manager.create_tables()

    petShop = PetShop(cursor, connection)

    seeder = Seeder(petShop)

    seeder.seed()

    cursor.execute("SELECT * FROM petshop.types;")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM petshop.users;")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM petshop.pets;")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM petshop.births;")
    print(cursor.fetchall())


