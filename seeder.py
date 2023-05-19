from pet_shop import PetShop
from auction.auction_manager import AuctionManager 
from faker import Faker
import random

class Seeder:

    def __init__(self, pet_shop: PetShop, auction_manager: AuctionManager):
        self.pet_shop = pet_shop
        self.auction_manager = auction_manager
        self.pet_types = ["Dog", "Cat", "Bird"]
        self.number_of_users = 10
        self.number_of_pets = 30
        self.number_of_births = 20
        self.number_of_purchases = 20
        self.number_of_auctions = 10
        self.number_max_bids = 10
        self.max_money = 1000
        self.pets = {}

    def seed(self):

        self.seed_types()
        self.seed_users()
        self.seed_pets()
        self.seed_births()
        self.seed_purchases()
        self.seed_auctions()

    def seed_types(self):

        for type in self.pet_types:
            self.pet_shop.create_pet_type(type)

    def seed_users(self):
        fake = Faker()

        for _ in range(self.number_of_users):
            self.pet_shop.create_user(
                email=fake.unique.email(),
                password=fake.password(),
                name=fake.name(),
                balance=random.randint(0, self.max_money)
            )

    def seed_pets(self):
        fake = Faker()

        for i in range(self.number_of_pets):

            type_id = random.randint(1, len(self.pet_types))
            sex = random.choice(["M", "F"])

            if type_id not in self.pets:
                self.pets[type_id] = {"M": [], "F": []}

            self.pets[type_id][sex].append(i+1)

            self.pet_shop.create_pet(
                owner_id=random.randint(1, self.number_of_users),
                type_id=type_id,
                name=fake.first_name_female() if sex == 'F' else fake.first_name_male(),
                sex=sex,
            )

    def seed_births(self):
        
        for _ in range(self.number_of_births):

            while True:

                type_id = random.randint(1, len(self.pet_types))

                if type_id not in self.pets:
                    continue

                if len(self.pets[type_id]["M"]) == 0 or len(self.pets[type_id]["F"]) == 0:
                    continue

                father_id = self.pets[type_id]["M"][random.randint(1, len(self.pets[type_id]["M"])) - 1]
                mother_id = self.pets[type_id]["F"][random.randint(1, len(self.pets[type_id]["F"])) - 1]

                self.pet_shop.reproduce_pets(
                    mother_id=mother_id,
                    father_id=father_id
                )

                break

    def seed_purchases(self):

        for _ in range(self.number_of_purchases):

            while True:
            
                pet = self.pet_shop.get_pet(random.randint(1, self.number_of_pets))

                user = self.pet_shop.get_user(random.randint(1, self.number_of_users))

                if pet.owner_id == user.id:
                    continue

                price = random.randint(0, user.balance)

                self.pet_shop.purchase_pet(
                    new_owner_id=user.id,
                    pet_id=pet.id,
                    amount=price
                )

                break

    def seed_auctions(self):

        for _ in range(self.number_of_auctions):

            pets = self.pet_shop.get_pets()
            users = self.pet_shop.get_users()

            pet = pets[random.randint(1, len(pets)) - 1]

            user = self.pet_shop.get_user(pet.owner_id)

            if user.balance == 0:
                continue

            current_price = random.randint(1, user.balance)

            self.auction_manager.start_auction(pet.id, current_price)

            for _ in range(random.randint(1, self.number_max_bids)):

                bidder = users[random.randint(1, len(users)) - 1]

                if bidder.id == user.id:
                    continue

                if bidder.balance <= current_price:
                    continue

                new_price = random.randint(current_price + 1, bidder.balance)

                self.auction_manager.handle_bid(pet.id, bidder.id, new_price)

                current_price = new_price

            self.auction_manager.end_auction(pet.id)