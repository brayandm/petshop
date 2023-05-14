from redis.client import Redis

from auction.auction_manager import AuctionManager
from pet_shop import PetShop


class AuctionInteractor:
    def __init__(self, pet_shop: PetShop, redis: Redis):
        self.pet_shop = pet_shop
        self.redis = redis
        self.auction_manager = AuctionManager(pet_shop=pet_shop, redis=redis)
        self.user_id = None

    def start_auction(self):
        pets = self.pet_shop.get_user_pets(id=self.user_id)

        if not pets:
            print("You don't own any pets to sell.")
            return

        print("Your pets:")
        for pet in pets:
            print(f"ID: {pet.id}, Name: {pet.name}")

        pet_id = int(input("Enter pet id to auction: "))

        if pet_id not in [pet.id for pet in pets]:
            print("You don't own a pet with that id.")
            return

        if pet_id in [pet.id for pet in self.__get_pets_in_auctions()]:
            print("Pet is already in auction.")
            return

        minimum_bid = int(input("Enter minimum bid: "))

        self.auction_manager.start_auction(pet_id, minimum_bid)

    def place_a_bid(self):
        pets_in_auction = self.__get_pets_in_auctions()

        for pet in pets_in_auction:
            print(f"ID: {pet.id}, Name: {pet.name}")

        pet_id = int(input("Enter pet id to bid on: "))

        if pet_id not in [pet.id for pet in pets_in_auction]:
            print("No pet with that id is in auction.")
            return

        if self.pet_shop.get_pet(id=pet_id).owner_id == self.user_id:
            print("You can't bid on your own pet.")
            return

        bid_amount = int(input("Enter bid amount: "))

        user = self.pet_shop.get_user(id=self.user_id)
        if user.balance < bid_amount:
            print("You don't have enough balance to bid that amount.")
            return

        self.auction_manager.handle_bid(pet_id=pet_id, user_id=self.user_id, bid_amount=bid_amount)

    def end_auction(self):
        pets_in_auction = self.__get_pets_in_auctions()

        for pet in pets_in_auction:
            print(f"ID: {pet.id}, Name: {pet.name}")

        pet_id = int(input("Enter pet id to end auction: "))

        if pet_id not in [pet.id for pet in pets_in_auction]:
            print("No pet with that id is in auction.")
            return

        self.auction_manager.end_auction(pet_id=pet_id)

    def start_interaction(self):
        self.user_id = int(input("Enter your user id: "))
        while True:
            print("1: Start an auction")
            print("2: Place a bid")
            print("3: End an auction")
            print("4: Subscribe to auction updates")
            print("5: Exit")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                self.start_auction()
                continue
            elif choice == 2:
                self.place_a_bid()
                continue
            elif choice == 3:
                self.end_auction()
                continue
            elif choice == 4:
                self.auction_manager.subscribe_to_updates()
                continue
            elif choice == 5:
                break

    def __get_pets_in_auctions(self):
        """Returns a list of pets that are in auction."""
        set_members = self.redis.smembers("petshop_auctions")
        pet_ids = [int(member.decode()) for member in set_members]
        pets = [self.pet_shop.get_pet(id=pet_id) for pet_id in pet_ids]
        return pets
