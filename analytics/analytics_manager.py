import json
import time
from datetime import datetime

from redis.client import Redis

from pet_shop import PetShop


class AnalyticsManager:
    def __init__(self, cursor, connection, redis: Redis, pet_shop: PetShop):
        self.cursor = cursor
        self.connection = connection
        self.redis = redis
        self.pet_shop = pet_shop

    def populate_events_with_purchases(self):
        insert_query = """
            INSERT INTO petshop.events (
                event_type,
                original_event_id,
                prev_owner_id,
                new_owner_id,
                pet_id,
                amount,
                event_time,
                prev_owner_email,
                prev_owner_name,
                new_owner_email,
                new_owner_name,
                pet_name,
                pet_sex,
                type_id
            )
            SELECT 
                'PET_PURCHASED' AS event_type,
                p.id AS original_event_id,
                p.prev_owner_id,
                p.new_owner_id,
                p.pet_id,
                p.amount,
                p.date AS event_time,
                po.email AS prev_owner_email,
                po.name AS prev_owner_name,
                no.email AS new_owner_email,
                no.name AS new_owner_name,
                pt.name AS pet_name,
                pt.sex AS pet_sex,
                pt.type_id
            FROM 
                petshop.purchases p
            JOIN
                petshop.users po ON po.id = p.prev_owner_id
            JOIN
                petshop.users no ON no.id = p.new_owner_id
            JOIN
                petshop.pets pt ON pt.id = p.pet_id
            LEFT JOIN
                petshop.events e ON e.prev_owner_id = p.prev_owner_id AND e.new_owner_id = p.new_owner_id AND e.pet_id = p.pet_id
            WHERE
                e.id IS NULL
            ;
        """
        self.cursor.execute(insert_query)
        self.connection.commit()

    def populate_events_with_births(self):
        insert_query = """
            INSERT INTO petshop.events (
                original_event_id,
                event_type,
                father_id,
                mother_id,
                children_id,
                event_time,
                father_name,
                father_sex,
                mother_name,
                mother_sex,
                children_name,
                children_sex,
                type_id,
                type_name
            )
            SELECT 
                b.id AS original_event_id,
                'PETS_REPRODUCED' AS event_type,
                b.father_id,
                b.mother_id,
                b.children_id AS children_id,
                b.time AS event_time,
                father.name AS father_name,
                father.sex AS father_sex,
                mother.name AS mother_name,
                mother.sex AS mother_sex,
                child.name AS children_name,
                child.sex AS children_sex,
                child.type_id AS children_type_id,
                type.name AS type_name
            FROM 
                petshop.births b
            JOIN
                petshop.pets father ON father.id = b.father_id
            JOIN
                petshop.pets mother ON mother.id = b.mother_id
            JOIN
                petshop.pets child ON child.id = b.children_id
            JOIN
                petshop.types type ON type.id = child.type_id
            LEFT JOIN
                petshop.events e ON e.original_event_id = b.id
            WHERE
                e.id IS NULL
            ;
        """
        self.cursor.execute(insert_query)
        self.connection.commit()

    def process_logs_and_insert_to_mart(self):
        log_key = 'petshop_logs'
        # This counter keeps track of the last processed log in Redis
        last_processed_log = int(self.redis.get('petshop_last_processed_log') or -1)

        # Get new logs from Redis
        logs = self.redis.lrange(log_key, last_processed_log + 1, -1)

        for i in logs:
            # Decode log
            log = json.loads(i)

            event_type = log['type']
            data = log['data']
            timestamp = log['timestamp']

            if event_type == 'AUCTION_STARTED':
                # Extract the user's details
                pet_id = data['pet_id']
                minimum_bid = data['minimum_bid']
                self.insert_event('AUCTION_STARTED', pet_id=pet_id, amount=minimum_bid, timestamp=timestamp)

            elif event_type == 'BID':
                pet_id = data['pet_id']
                user_id = data['user_id']
                bid_amount = data['bid_amount']
                self.insert_event('BID', pet_id=pet_id, user_id=user_id, amount=bid_amount, timestamp=timestamp)

            elif event_type == 'AUCTION_ENDED':
                pet_id = data['pet_id']
                highest_bid = data['highest_bid']
                highest_bidder = data['highest_bidder']
                is_sold = data['sold']
                self.insert_event('AUCTION_ENDED', pet_id=pet_id, new_owner_id=highest_bidder, amount=highest_bid, pet_sold=is_sold, timestamp=timestamp)

            # Update the last processed log
            last_processed_log += 1
            self.redis.set('last_processed_log', last_processed_log)

    def insert_event(self, event_type, timestamp, pet_id=None, user_id=None, amount=None, new_owner_id=None, pet_sold=None):

        pet = None
        pet_type = None
        if pet_id:
            pet = self.pet_shop.get_pet(pet_id)
            pet_type = self.pet_shop.get_pet_type(pet.type_id)

        user = None
        if user_id:
            user = self.pet_shop.get_user(user_id)

        new_owner = None
        if new_owner_id:
            new_owner = self.pet_shop.get_user(new_owner_id)

        insert_query = """
            INSERT INTO petshop.events (
                event_type,
                pet_id,
                pet_name,
                pet_sex,
                type_id,
                type_name,
                user_id,
                user_name,
                user_email,
                new_owner_id,
                new_owner_name,
                new_owner_email,
                amount,
                pet_sold,
                event_time
            )
            VALUES (
                %(event_type)s,
                %(pet_id)s,
                %(pet_name)s,
                %(pet_sex)s,
                %(type_id)s,
                %(type_name)s,
                %(user_id)s,
                %(user_name)s,
                %(user_email)s,
                %(new_owner_id)s,
                %(new_owner_name)s,
                %(new_owner_email)s,
                %(amount)s,
                %(pet_sold)s,
                %(event_time)s
            );
        """

        pet_name = pet.name if pet else None

        self.cursor.execute(insert_query, {
            'event_type': event_type,
            'pet_id': pet_id,
            'pet_name': pet.name if pet else None,
            'pet_sex': pet.sex if pet else None,
            'type_id': pet.type_id if pet else None,
            'type_name': pet_type.name if pet_type else None,
            'user_id': user_id,
            'user_name': user.name if user else None,
            'user_email': user.email if user else None,
            'new_owner_id': new_owner_id,
            'new_owner_name': new_owner.name if new_owner else None,
            'new_owner_email': new_owner.email if new_owner else None,
            'amount': amount,
            'pet_sold': pet_sold,
            'event_time': datetime.fromtimestamp(timestamp)
        })
        self.connection.commit()

    def children_per_pet(self):

        query = """
            SELECT 
                father_id AS pet_id,
                father_name AS pet_name,
                COUNT(children_id) AS children_count
            FROM
                petshop.events
            WHERE
                event_type = 'PETS_REPRODUCED'
            GROUP BY
                father_id,
                father_name
            UNION
            SELECT 
                mother_id AS pet_id,
                mother_name AS pet_name,
                COUNT(children_id) AS children_count
            FROM
                petshop.events
            WHERE
                event_type = 'PETS_REPRODUCED'
            GROUP BY
                mother_id,
                mother_name
        """

        self.cursor.execute(query)
        print(self.cursor.fetchall())