from redis.client import Redis

from auction.auction_interactor import AuctionInteractor
from pet_shop import PetShop

class Interactor:

    def __init__(self, pet_shop: PetShop, redis: Redis):
        self.user_id = None
        self.pet_shop = pet_shop
        self.redis = redis

    def start_interaction(self):

        while True:

            self.user_id = int(input("Enter your user id: "))

            if not self.pet_shop.user_exists(id=self.user_id):
                print("No user with that id. Try again.")
                continue

            break
        
        while True:
            print("1: Go to auctions")
            print("2: Reproduce pets")
            print("3: Exit")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                AuctionInteractor(self.pet_shop, self.redis, user_id=self.user_id).start_interaction()
                continue
            elif choice == 2:
                print("Reproducing pets...");
                continue
            elif choice == 3:
                break