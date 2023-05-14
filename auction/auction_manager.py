import psycopg2
from redis.client import Redis

from pet_shop import PetShop


class AuctionManager:
    def __init__(self, pet_shop: PetShop, redis: Redis):
        self.pet_shop = pet_shop
        self.redis = redis
        self.pubsub = self.redis.pubsub()

    def publish_message_and_print(self, message: str):
        """Publishes message to petshop_auction_updates channel and prints it to console"""
        self.redis.publish("petshop_auction_updates", message)
        print(message)

    def start_auction(self, pet_id: int, minimum_bid: int):
        """Starts auction for pet with pet_id and minimum bid"""
        # Add pet_id to petshop_auctions set
        self.redis.sadd("petshop_auctions", pet_id)

        self.publish_message_and_print(f"Auction started for pet with id: {pet_id}, minimum bid: {minimum_bid}")

        # Set highest_bid and highest_bidder to 0
        self.redis.hset("petshop_auction_{}_data".format(pet_id), "highest_bid", minimum_bid - 1)
        self.redis.hset("petshop_auction_{}_data".format(pet_id), "highest_bidder", 0)

    def handle_bid(self, pet_id: int, user_id: int, bid_amount: int):
        """Handles bid from user_id for bid_amount"""
        highest_bid = int(self.redis.hget("petshop_auction_{}_data".format(pet_id), "highest_bid").decode())

        # Check if bid_amount is higher than highest_bid
        if bid_amount > highest_bid:
            # Update highest_bid and highest_bidder
            highest_bid = bid_amount
            highest_bidder = user_id

            self.publish_message_and_print(f"New highest bid from user id {user_id} for amount {bid_amount} for pet with id {pet_id}")

            # Save highest_bid and highest_bidder to Redis
            self.redis.hset("petshop_auction_{}_data".format(pet_id), "highest_bid", highest_bid)
            self.redis.hset("petshop_auction_{}_data".format(pet_id), "highest_bidder", highest_bidder)
        else:
            self.publish_message_and_print(f"User id {user_id} bid of {bid_amount} for pet with id {pet_id} is not high enough")

    def end_auction(self, pet_id: int):
        """Ends auction for pet with pet_id selling the pet if there is a highest_bidder"""
        # Get highest_bid and highest_bidder from Redis
        highest_bid = int(self.redis.hget("petshop_auction_{}_data".format(pet_id), "highest_bid").decode())
        highest_bidder = int(self.redis.hget("petshop_auction_{}_data".format(pet_id), "highest_bidder").decode())

        if highest_bidder:
            # Purchase pet
            try:
                self.pet_shop.purchase_pet(highest_bidder, pet_id, highest_bid)
                self.publish_message_and_print(f"Auction ended. Pet with id {pet_id} sold to user id {highest_bidder} for amount {highest_bid}")
            except (ValueError, psycopg2.Error) as e:
                self.publish_message_and_print(f"Auction ended. Pet with id {pet_id} not sold. Error: {e}")
        else:
            self.publish_message_and_print(f"Auction ended for pet with id: {pet_id}. No bids received.")

        # Remove pet_id from petshop_auctions set
        self.redis.srem("petshop_auctions", pet_id)

    def subscribe_to_updates(self):
        """Subscribes to petshop_auction_updates channel and prints updates to console, it is blocking"""
        self.pubsub.subscribe("petshop_auction_updates")

        print("Subscribed to auction updates. Press Ctrl+C to stop.")

        try:
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    print(message['data'].decode())
        except KeyboardInterrupt:
            self.pubsub.unsubscribe("petshop_auction_updates")
            print("Unsubscribed from auction updates.")