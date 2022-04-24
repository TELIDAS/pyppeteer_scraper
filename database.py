import psycopg2.extras
import config


class Database:
    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
        )
        self.cursor = self.connection.cursor()

    def insert_data(self, data: list) -> None:
        queryText = """
        INSERT INTO auto 
        (url, title, usd_price, mile_age, username, phone_number, img_url, img_total_count, car_number, car_vin_code) 
        VALUES %s
        """

        psycopg2.extras.execute_values(
            self.cursor,
            queryText,
            tuple(
                data,
            ),
        )
        self.connection.commit()

    def close_connection(self) -> None:
        self.cursor.close()
        self.connection.close()