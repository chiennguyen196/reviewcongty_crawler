import json
import sys
import pymongo
from bson.objectid import ObjectId
import urllib.parse
import requests
import os
import datetime
import logging
logging.basicConfig(level = logging.INFO)

# config in config.sh
MONGO_USERNAME = os.environ["MONGO_USERNAME"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = int(os.environ["MONGO_PORT"])
DATABASE = os.environ['DATABASE']
COMPANY_COLECTION = os.environ['COMPANY_COLECTION']
REVIEW_COLECTION = os.environ['REVIEW_COLECTION']
BASE_URL = os.environ['BASE_URL']
IMAGE_DEST_FOLDER = os.environ['IMAGE_DEST_FOLDER']

def convert_string_to_date(time_str):
    return datetime.datetime.strptime(time_str + "+0700", "%Y-%m-%d %H:%M:%S%z")

class UpdateCompany:
    def __init__(self):
        self.__db = None
        self.__company_collection = None
        self.__review_collection = None
        self.__company_id = None
        

    def process(self, data):
        self.new_company = data[0]
        self.new_reviews = data[1:]
        self.__process_raw_data()

        
        with pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USERNAME, password=MONGO_PASSWORD, authSource=DATABASE, authMechanism='SCRAM-SHA-256') as client:
            self.__db = client[DATABASE]
            self.__company_collection = self.__db[COMPANY_COLECTION]
            self.__review_collection = self.__db[REVIEW_COLECTION]

            is_existed = self.__check_company_is_existed()

            if not is_existed:
                self.__handle_new_company()
            else:
                self.__handle_old_company()
    
    def __process_raw_data(self):
        image_name = os.path.basename(self.new_company["image_logo"])
        self.new_company['image_name'] = image_name
        for r in self.new_reviews:
            r["created"] = ObjectId(r["review_id"]).generation_time
            for rely in r["replies"]:
                rely["created"] = convert_string_to_date(rely["created"])
    
    def __check_company_is_existed(self):
        return self.__company_collection.count({'_id': self.new_company['id']}, limit=1) != 0

    def __handle_new_company(self):
        self.__try_to_download_logo_image()
        self.__company_id = self.__insert_new_company()
        self.__insert_reviews()

    def __handle_old_company(self):
        self.__company_id = self.__get_company_id()
        self.__update_company()
        self.__delete_old_reviews()
        self.__insert_reviews()
    
    def __try_to_download_logo_image(self):
        image_url = urllib.parse.urljoin(BASE_URL, self.new_company["image_logo"])
        dest_image = os.path.join(IMAGE_DEST_FOLDER, self.new_company['image_name'])
        try:
            logging.info("Trying to download image from {}".format(image_url))
            r = requests.get(image_url)
            with open(dest_image, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            logging.error("Cannot download {} cause {}".format(image_url, e))
    
    def __insert_new_company(self):
        
        r = self.__company_collection.insert_one({
            "_id": self.new_company["id"],
            "image_name": self.new_company["image_name"],
            "name": self.new_company["name"],
            "rating": self.new_company["rating"],
            "rating_count": self.new_company["rating_count"],
            "company_type": self.new_company["company_type"],
            "size": self.new_company["size"],
            "address": self.new_company["address"],
            "last_updated": self.__get_last_updated()
        })
        return r.inserted_id

    def __get_company_id(self):
        company = self.__company_collection.find_one({'_id': self.new_company["id"]})
        return company["_id"]

    def __update_company(self):
        last_updated = self.__get_last_updated()
        rating = self.new_company["rating"]
        rating_count = self.new_company["rating_count"]
        self.__company_collection.update_one(
            {"_id": self.__company_id},
            {"$set": {
                "last_updated": last_updated,
                "rating": rating,
                "rating_count": rating_count
            }}
        )

    def __delete_old_reviews(self):
        self.__review_collection.delete_many({
            "company_id": self.__company_id,
            "source": "crawler"
        })

    def __get_last_updated(self):
        last_updated = max([r["created"] for r in self.new_reviews])
        return last_updated

    def __insert_reviews(self):
        for r in self.new_reviews:
            r["company_id"] = self.__company_id
            r["source"] = "crawler"
        self.__review_collection.insert_many(self.new_reviews)


if __name__ == "__main__":
    company_file = sys.argv[1]

    logging.info("Reading company info and review from file")
    with open(company_file, 'r') as f:
        lines = [json.loads(l) for l in f.readlines()]

    update_company = UpdateCompany()
    update_company.process(lines)