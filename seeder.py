from pet_shop import PetShop 
from faker import Faker
import random

class Seeder:

    def __init__(self, petShop: PetShop):
        self.petShop = petShop
        self.petTypes = ["Dog", "Cat", "Bird"]
        self.numberOfUsers = 10
        self.numberOfPets = 30
        self.numberOfBirths = 20
        self.maxMoney = 1000
        self.pets = {}

    def seed(self):

        self.seedTypes()
        self.seedUsers()
        self.seedPets()
        self.seedBirths()

    def seedTypes(self):

        for type in self.petTypes:
            self.petShop.create_pet_type(type)

    def seedUsers(self):
        fake = Faker()

        for _ in range(self.numberOfUsers):
            self.petShop.create_user(
                email=fake.unique.email(),
                password=fake.password(),
                name=fake.name(),
                balance=random.randint(0, self.maxMoney)
            )

    def seedPets(self):
        fake = Faker()

        for i in range(self.numberOfPets):

            type_id = random.randint(1, len(self.petTypes))
            sex = random.choice(["M", "F"])

            if type_id not in self.pets:
                self.pets[type_id] = {"M": [], "F": []}

            self.pets[type_id][sex].append(i+1)

            self.petShop.create_pet(
                owner_id=random.randint(1, self.numberOfUsers),
                type_id=type_id,
                name=fake.first_name_female() if sex == 'F' else fake.first_name_male(),
                sex=sex,
            )

    def seedBirths(self):
        
        for _ in range(self.numberOfBirths):

            while True:

                type_id = random.randint(1, len(self.petTypes))

                if type_id not in self.pets:
                    continue

                if len(self.pets[type_id]["M"]) == 0 or len(self.pets[type_id]["F"]) == 0:
                    continue

                father_id = self.pets[type_id]["M"][random.randint(1, len(self.pets[type_id]["M"])) - 1]
                mother_id = self.pets[type_id]["F"][random.randint(1, len(self.pets[type_id]["F"])) - 1]

                self.petShop.reproduce_pets(
                    mother_id=mother_id,
                    father_id=father_id
                )

                break
