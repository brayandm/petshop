from redis.client import Redis

from analytics.analytics_manager import AnalyticsManager
from auction.auction_interactor import AuctionInteractor
from pet_shop import PetShop

class Interactor:

    def __init__(self, pet_shop: PetShop, redis: Redis, analytics_manager: AnalyticsManager):
        self.user_id = None
        self.pet_shop = pet_shop
        self.redis = redis
        self.analytics_manager = analytics_manager

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
            print("3: Sync events table for analytics")
            print("4: Exit")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                AuctionInteractor(self.pet_shop, self.redis, user_id=self.user_id).start_interaction()
                continue
            elif choice == 2:
                self.reproduce_pets()
                continue
            elif choice == 3:
                self.analytics_manager.populate_events_with_purchases()
                self.analytics_manager.populate_events_with_births()
                self.analytics_manager.process_logs_and_insert_to_mart()
                continue
            elif choice == 4:
                break

    def reproduce_pets(self):
        
        pets = self.pet_shop.get_user_pets(self.user_id)

        if len(pets) < 2:
            print("You need to have at least 2 pets to reproduce.")
            return

        print("Your pets:")
        for pet in pets:
            print(f"ID: {pet.id}, Name: {pet.name}, Type: {pet.type_id}, Sex: {pet.sex}")

        pet1_id = int(input("Enter first pet id: "))
        pet2_id = int(input("Enter second pet id: "))

        if pet1_id not in [pet.id for pet in pets] or pet2_id not in [pet.id for pet in pets]:
            print("No pet with that id.")
            return

        if pet1_id == pet2_id:
            print("You can't reproduce a pet with itself.")
            return

        pet1 = self.pet_shop.get_pet(id=pet1_id)
        pet2 = self.pet_shop.get_pet(id=pet2_id)

        if pet1.type_id != pet2.type_id:
            print("You can't reproduce pets of different types.")
            return
        
        if pet1.sex == pet2.sex:
            print("You can't reproduce pets of equal sex.")
            return
        
        mother_id = (pet1.id if pet1.sex == 'F' else pet2.id)
        father_id = (pet1.id if pet1.sex == 'M' else pet2.id)

        self.pet_shop.reproduce_pets(mother_id=mother_id, father_id=father_id)
        print("Your pets reproduced successfully.")