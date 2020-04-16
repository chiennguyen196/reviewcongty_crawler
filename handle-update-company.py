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
DATABASE = os.environ['DATABASE']
COMPANY_COLECTION = os.environ['COMPANY_COLECTION']
REVIEW_COLECTION = os.environ['REVIEW_COLECTION']
BASE_URL = os.environ['BASE_URL']
IMAGE_DEST_FOLDER = os.environ['IMAGE_DEST_FOLDER']

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

        with pymongo.MongoClient("mongodb://localhost:27017/") as client:
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
            r["created"] = datetime.datetime.strptime(r["created"] + "+0700", "%Y-%m-%d %H:%M:%S.%f%z")
    
    def __check_company_is_existed(self):
        return self.__company_collection.count({'slug': self.new_company['slug']}, limit=1) != 0

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
            r = requests.get(image_url)
            with open(dest_image, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            logging.error("Cannot download {} cause {}".format(image_url, e))
    
    def __insert_new_company(self):
        
        r = self.__company_collection.insert_one({
            "image_name": self.new_company["image_name"],
            "name": self.new_company["name"],
            "slug": self.new_company["slug"],
            "rating": self.new_company["rating"],
            "rating_count": self.new_company["rating_count"],
            "company_type": self.new_company["company_type"],
            "size": self.new_company["size"],
            "address": self.new_company["address"],
            "last_updated": self.__get_last_updated()
        })
        return r.inserted_id

    def __get_company_id(self):
        company = self.__company_collection.find_one({'slug': self.new_company["slug"]})
        return company["_id"]

    def __update_company(self):
        last_updated = self.__get_last_updated()
        rating = self.new_company["rating"]
        rating_count = self.new_company["rating_count"]
        self.__company_collection.update_one(
            {"_id": ObjectId(self.__company_id)},
            {"$set": {
                "last_updated": last_updated,
                "rating": rating,
                "rating_count": rating_count
            }}
        )

    def __delete_old_reviews(self):
        self.__review_collection.delete_many({
            "company_id": ObjectId(self.__company_id),
            "source": "crawler"
        })

    def __get_last_updated(self):
        last_updated = max([r["created"] for r in self.new_reviews])
        return last_updated

    def __insert_reviews(self):
        company_id = ObjectId(self.__company_id)
        for r in self.new_reviews:
            r["company_id"] = company_id
            r["source"] = "crawler"
        self.__review_collection.insert_many(self.new_reviews)


if __name__ == "__main__":
    company_file = sys.argv[1]

    logging.info("Reading company info and review from file")
    with open(company_file, 'r') as f:
        lines = [json.loads(l) for l in f.readlines()]

    update_company = UpdateCompany()
    update_company.process(lines)