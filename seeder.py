from pet_shop import PetShop 

class Seeder:

    def __init__(self, petShop: PetShop):
        self.petShop = petShop

    def seed(self):
        self.petShop.create_pet_type("Dog")
        self.petShop.create_pet_type("Cat")

        self.petShop.create_user(
            email="user1@example.com",
            password="password",
            name="User 1",
            balance=100.0
        )
        self.petShop.create_user(
            email="user2@example.com",
            password="password",
            name="User 1",
            balance=100.0
        )

        self.petShop.create_pet(1, 1, "Dog 1", "M")
        self.petShop.create_pet(1, 1, "Dog 2", "F")

        self.petShop.reproduce_pets(mother_id=2, father_id=1, female_names=["Laika"], male_names=["Buddy"])