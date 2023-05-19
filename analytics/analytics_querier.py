class AnalyticsQuerier:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

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

    def total_money_transfer_last_week(self):

        query = """
            SELECT sum(amount) AS total_money_transfer_last_week
            FROM petshop.events
            WHERE event_time >= CURRENT_TIMESTAMP - INTERVAL '1 week';
        """

        self.cursor.execute(query)
        print(self.cursor.fetchall())