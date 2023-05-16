import connection
from database_manager import DatabaseManager
from pet_shop import PetShop
from seeder import Seeder
from interactor import Interactor


def init():
    (cursor, conn) = connection.connect_to_postgres()
    database_manager = DatabaseManager(cursor, conn)
    database_manager.drop_tables()
    database_manager.create_tables()

    pet_shop = PetShop(cursor=cursor, connection=conn)

    seeder = Seeder(pet_shop)

    seeder.seed()

    cursor.execute("SELECT * FROM petshop.users;")
    print(cursor.fetchall())


if __name__ == '__main__':
    (cursor, conn) = connection.connect_to_postgres()

    pet_shop = PetShop(cursor=cursor, connection=conn)

    redis = connection.connect_to_redis()

    interactor = Interactor(pet_shop, redis)
    interactor.start_interaction()


