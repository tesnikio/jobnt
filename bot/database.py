import pymongo
import uuid
import config

from typing import Optional, Any
from datetime import datetime


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["jobnt_bot"]
        self.users_collection = self.db["users"]

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        if self.users_collection.count_documents({"_id": user_id}) > 0:
            return True
        else:
            if raise_exception:
                raise ValueError(f"User {user_id} does not exist")
            else:
                return False

    def add_new_user(
        self,
        user_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
        company_name: str = "",
        position_title: str = "",
    ):
        update_dict = {
            "$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "last_interaction": datetime.now(),
                "company_name": company_name,
                "position_title": position_title,
            },
            "$setOnInsert": {"first_seen": datetime.now()},
        }

        self.users_collection.update_one({"_id": user_id}, update_dict, upsert=True)

    def get_all_users(self):
        users_cursor = self.users_collection.find({})

        users_list = list(users_cursor)

        return users_list
