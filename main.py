import connection
from database_manager import DatabaseManager
from pet_shop import PetShop

if __name__ == '__main__':
    (cursor, connection) = connection.connect()
    database_manager = DatabaseManager(cursor, connection)
    database_manager.drop_tables()
    database_manager.create_tables()

    petShop = PetShop(cursor, connection)
    petShop.create_pet_type("Dog")
    petShop.create_pet_type("Cat")

    petShop.create_user(
        email="user1@example.com",
        password="password",
        name="User 1",
        balance=100.0
    )
    petShop.create_user(
        email="user2@example.com",
        password="password",
        name="User 1",
        balance=100.0
    )

    petShop.create_pet(1, 1, "Dog 1", "M")
    petShop.create_pet(1, 1, "Dog 2", "F")

    petShop.reproduce_pets(mother_id=2, father_id=1, female_names=["Laika"], male_names=["Buddy"])

    cursor.execute("SELECT * FROM petshop.types;")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM petshop.users;")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM petshop.pets;")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM petshop.births;")
    print(cursor.fetchall())


