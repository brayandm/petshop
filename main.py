import connection
from analytics.analytics_manager import AnalyticsManager
from analytics.analytics_querier import AnalyticsQuerier
from auction.auction_manager import AuctionManager 
from database_manager import DatabaseManager
from pet_shop import PetShop
from seeder import Seeder
from interactor import Interactor


def init():
    (cursor, conn) = connection.connect_to_postgres()
    
    database_manager = DatabaseManager(cursor, conn)
    database_manager.drop_tables()
    database_manager.create_tables()

    redis = connection.connect_to_redis()
    keys = redis.keys('petshop_*')
    for key in keys:
        redis.delete(key)

    pet_shop = PetShop(cursor=cursor, connection=conn)
    auction_manager = AuctionManager(pet_shop, redis)

    seeder = Seeder(pet_shop, auction_manager)

    seeder.seed()

    cursor.execute("SELECT * FROM petshop.users;")
    print(cursor.fetchall())


if __name__ == '__main__':
    (cursor, conn) = connection.connect_to_postgres()

    # init()

    pet_shop = PetShop(cursor=cursor, connection=conn)

    redis = connection.connect_to_redis()

    analytics_manager = AnalyticsManager(cursor=cursor, connection=conn, redis=redis, pet_shop=pet_shop)
    analytics_querier = AnalyticsQuerier(cursor=cursor, connection=conn)

    interactor = Interactor(pet_shop, redis, analytics_manager, analytics_querier)
    interactor.start_interaction()

    cursor.execute("SELECT * FROM petshop.events;")
    for e in cursor.fetchall():
        print(e)
