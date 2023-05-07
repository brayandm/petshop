import random
from typing import List


class PetShop:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def create_pet_type(self, name: str) -> None:
        create_type_query = """
            INSERT INTO petshop.types (name) VALUES (%s);
        """
        self.cursor.execute(create_type_query, (name,))
        self.connection.commit()

    def create_user(self, email: str, password: str, name: str, balance: float) -> None:
        create_user_query = """
            INSERT INTO petshop.users (email, password, name, balance) VALUES (%s, %s, %s, %s);
        """
        self.cursor.execute(create_user_query, (email, password, name, balance))
        self.connection.commit()

    def create_pet(self, owner_id: int, type_id: int, name: str, sex: str) -> None:
        create_pet_query = """
            INSERT INTO petshop.pets (owner_id, type_id, name, sex) VALUES (%s, %s, %s, %s);
        """
        self.cursor.execute(create_pet_query, (owner_id, type_id, name, sex))
        self.connection.commit()

    def purchase_pet(self, prev_owner_id: int, new_owner_id: int, pet_id: int, amount: float) -> None:
        # Set the transaction isolation level to SERIALIZABLE
        self.cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")

        # Start a transaction
        self.cursor.execute("BEGIN;")

        try:
            # Check if the previous owner is the actual owner of the pet
            self.cursor.execute("SELECT owner_id FROM petshop.pets WHERE id = %s;", (pet_id,))
            current_owner_id = self.cursor.fetchone()[0]

            if current_owner_id != prev_owner_id:
                raise ValueError("The previous owner is not the actual owner of the pet.")

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

    def reproduce_pets(self, mother_id: int, father_id: int, female_names: List[str] = None,
                       male_names: List[str] = None) -> None:
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
                self._get_name(sex, female_names, male_names),
                sex,
                father_id,
                mother_id
            )

        for _ in range(num_pets_father):
            sex = random.choice(['M', 'F'])
            self._create_pet_by_birth(
                father_owner_id,
                father_type_id,
                self._get_name(sex, female_names, male_names),
                sex,
                father_id,
                mother_id
            )

    def _create_pet_by_birth(self, owner_id: int, type_id: int, name: str, sex: str, father_id: int, mother_id: int):
        self.cursor.execute("BEGIN;")
        try:
            self.create_pet(owner_id, type_id, name, sex)
            self.cursor.execute("""
                INSERT INTO petshop.births (father_id, mother_id, children_id, time)
                VALUES (%s, %s, (SELECT max(id) FROM petshop.pets), NOW());
            """, (father_id, mother_id))
            self.connection.commit()
        except Exception as exception:
            self.cursor.execute("ROLLBACK;")
            raise exception

    @staticmethod
    def _get_name(sex: str, female_names: List[str], male_names: List[str]) -> str:
        if sex == 'F' and female_names:
            return female_names.pop()
        elif sex == 'M' and male_names:
            return male_names.pop()
        else:
            return f"Random {sex}-Pet-{random.randint(10000, 99999)}"
