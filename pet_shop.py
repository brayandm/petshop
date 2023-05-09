import random
from typing import List
from faker import Faker


class User:
    def __init__(self, id: int, email: str, password: str, name: str, balance: float):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.balance = balance


class Pet:
    def __init__(self, id: int, owner_id: int, type_id: int, name: str, sex: str):
        self.id = id
        self.owner_id = owner_id
        self.type_id = type_id
        self.name = name
        self.sex = sex


class PetShop:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def login_user(self, email: str, password: str) -> User | None:
        login_user_query = """
            SELECT * FROM petshop.users WHERE email = %s AND password = %s;
        """
        self.cursor.execute(login_user_query, (email, password))
        if self.cursor.rowcount == 0:
            return None
        return User(*self.cursor.fetchone())

    def create_pet_type(self, name: str, with_commit: bool = True) -> None:
        create_type_query = """
            INSERT INTO petshop.types (name) VALUES (%s);
        """
        self.cursor.execute(create_type_query, (name,))
        if with_commit:
            self.connection.commit()

    def create_user(self, email: str, password: str, name: str, balance: float, with_commit: bool = True) -> None:
        create_user_query = """
            INSERT INTO petshop.users (email, password, name, balance) VALUES (%s, %s, %s, %s);
        """
        self.cursor.execute(create_user_query, (email, password, name, balance))
        if with_commit:
            self.connection.commit()

    def create_pet(self, owner_id: int, type_id: int, name: str, sex: str, with_commit: bool = True) -> None:
        create_pet_query = """
            INSERT INTO petshop.pets (owner_id, type_id, name, sex) VALUES (%s, %s, %s, %s);
        """
        self.cursor.execute(create_pet_query, (owner_id, type_id, name, sex))
        if with_commit:
            self.connection.commit()

    def purchase_pet(self, new_owner_id: int, pet_id: int, amount: float) -> None:

        self.connection.commit()

        # Set the transaction isolation level to SERIALIZABLE
        self.cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")

        # Start a transaction
        self.cursor.execute("BEGIN;")

        try:
            # Check if the previous owner is the actual owner of the pet
            self.cursor.execute("SELECT owner_id FROM petshop.pets WHERE id = %s;", (pet_id,))
            prev_owner_id = self.cursor.fetchone()[0]

            if prev_owner_id == new_owner_id:
                raise ValueError("The new owner is already the owner of the pet.")

            # Check if the new owner has enough balance
            self.cursor.execute("SELECT balance FROM petshop.users WHERE id = %s;", (new_owner_id,))
            new_owner_balance = self.cursor.fetchone()[0]

            if new_owner_balance < amount:
                raise ValueError("The new owner does not have enough balance to purchase the pet.")

            # Update the pet's owner
            self.cursor.execute("UPDATE petshop.pets SET owner_id = %s WHERE id = %s;", (new_owner_id, pet_id))

            # Update the previous owner's balance
            self.cursor.execute("UPDATE petshop.users SET balance = balance + %s WHERE id = %s;",
                                (amount, prev_owner_id))

            # Update the new owner's balance
            self.cursor.execute("UPDATE petshop.users SET balance = balance - %s WHERE id = %s;",
                                (amount, new_owner_id))

            # Insert the purchase record
            self.cursor.execute(
                "INSERT INTO petshop.purchases (prev_owner_id, new_owner_id, pet_id, amount, date) VALUES (%s, %s, %s, %s, NOW());",
                (prev_owner_id, new_owner_id, pet_id, amount)
            )

            # Commit the transaction
            self.connection.commit()

        except Exception as e:
            # If any error occurs, rollback the transaction
            self.cursor.execute("ROLLBACK;")
            raise e

    def reproduce_pets(self, mother_id: int, father_id: int) -> None:
        self.cursor.execute("""
            SELECT p1.type_id, p1.sex, p1.owner_id, p2.type_id, p2.sex, p2.owner_id
            FROM petshop.pets p1, petshop.pets p2
            WHERE p1.id = %s AND p2.id = %s;
        """, (mother_id, father_id))

        mother_type_id, mother_sex, mother_owner_id, father_type_id, father_sex, father_owner_id = self.cursor.fetchone()

        if mother_type_id != father_type_id:
            raise ValueError("Mother and father pets should be of the same type.")
        if mother_sex != 'F':
            raise ValueError("The mother pet should be female.")
        if father_sex != 'M':
            raise ValueError("The father pet should be male.")

        # Generate new pets with random sex
        num_pets = random.randint(1, 4)
        num_pets_mother = ((num_pets + 1) // 2)  # Equivalent to ceil(n/2)
        num_pets_father = num_pets // 2

        for _ in range(num_pets_mother):
            sex = random.choice(['M', 'F'])
            self._create_pet_by_birth(
                mother_owner_id,
                mother_type_id,
                self._get_name(sex),
                sex,
                father_id,
                mother_id
            )

        for _ in range(num_pets_father):
            sex = random.choice(['M', 'F'])
            self._create_pet_by_birth(
                father_owner_id,
                father_type_id,
                self._get_name(sex),
                sex,
                father_id,
                mother_id
            )

    def _create_pet_by_birth(self, owner_id: int, type_id: int, name: str, sex: str, father_id: int, mother_id: int):
        self.cursor.execute("BEGIN;")
        try:
            self.create_pet(owner_id, type_id, name, sex, with_commit=False)
            self.cursor.execute("""
                INSERT INTO petshop.births (father_id, mother_id, children_id, time)
                VALUES (%s, %s, (SELECT max(id) FROM petshop.pets), NOW());
            """, (father_id, mother_id))
            self.connection.commit()
        except Exception as exception:
            self.cursor.execute("ROLLBACK;")
            raise exception

    @staticmethod
    def _get_name(sex: str) -> str:

        fake = Faker()

        if sex == 'F':
            return fake.first_name_female()
        elif sex == 'M':
            return fake.first_name_male()
        else:
            assert False, "The gender should be either 'M' or 'F'"

    def get_user(self, id: int) -> User:
        self.cursor.execute("SELECT * FROM petshop.users WHERE id = %s;", (id,))
        return User(*self.cursor.fetchone())
    
    def get_user_pets(self, id: int) -> List[Pet]:
        self.cursor.execute("SELECT * FROM petshop.pets WHERE owner_id = %s;", (id,))
        return [Pet(*pet) for pet in self.cursor.fetchall()]
    
    def get_pet(self, id: int) -> Pet:
        self.cursor.execute("SELECT * FROM petshop.pets WHERE id = %s;", (id,))
        return Pet(*self.cursor.fetchone())