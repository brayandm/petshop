import connection
from analytics.analytics_manager import AnalyticsManager
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

    redis = connection.connect_to_redis()

    keys = redis.keys('petshop_*')

    for key in keys:
        redis.delete(key)


if __name__ == '__main__':
    (cursor, conn) = connection.connect_to_postgres()

    # init()

    pet_shop = PetShop(cursor=cursor, connection=conn)

    redis = connection.connect_to_redis()

    analytics_manager = AnalyticsManager(cursor=cursor, connection=conn, redis=redis, pet_shop=pet_shop)

    interactor = Interactor(pet_shop, redis, analytics_manager)
    interactor.start_interaction()

    cursor.execute("SELECT * FROM petshop.events;")
    for e in cursor.fetchall():
        print(e)
