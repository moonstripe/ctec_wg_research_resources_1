import os
from datetime import datetime as dt
from requests import post, request
from dotenv import load_dotenv
import logging
from db import db

class Group:
    def __init__(self, name: str):
        load_dotenv()
        self.name: str = name
        self.id: int = 0
        self.posts: list = []

    def short_name_to_id(self):
        if self.id != 0:
            logging.info(f"ID has already been pulled for name: {self.name}.")
            return self.id

        base = "https://api.vk.com/method/groups.getById?v=5.131"
        params = f"&group_ids={self.name}&access_token={os.getenv('VK_APP_TOKEN')}"
        # print(base+params)
        
        try:
            res = request("POST", base+params)
        except Exception as e:
            logging.critical(e)

        # print('hello', res.json())

        feed = res.json()["response"]

        for i, e in enumerate(feed):
            self.id = e['id']
        
        logging.info(f"\tGroup: {self.name} has id: {self.id}.")
        return self.id

    def save_to_db(self, db):
        
        id = db.insert_group(self.name, self.id)
        logging.info(f'Saved {self.name} to DB with ID {id}')
        return

    def run(self):
        load_dotenv()

        # drop and create db
        database = db(table_name="groups")
        database.drop_tables()
        database.create_tables()

        pmcworld = Group('pmcworld')
        id = pmcworld.short_name_to_id()
        print(id)
        pmcworld.save_to_db(database)
        print(len(pmcworld.posts))
        return id



if __name__ == "__main__":
    load_dotenv()

    # drop and create db
    database = db(table_name="groups")
    database.drop_and_create()

    pmcworld = Group('pmcworld')
    pmcworld.short_name_to_id()
    pmcworld.save_to_db(database)
    print(len(pmcworld.posts))
