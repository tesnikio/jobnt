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
    ):
        user_dict = {
            "_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),
            "company_name": company_name,
        }

        if not self.check_if_user_exists(user_id):
            self.users_collection.insert_one(user_dict)
