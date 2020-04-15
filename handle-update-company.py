import json
import sys
import pymongo
import subprocess
import urllib.request
import urllib.parse
import os
import logging

DATABASE = "reviewcongty"
COMPANY_COLECTION = "company"
REVIEW_COLECTION = "review"
BASE_URL = "https://reviewcongty.com/"
IMAGE_DEST_FOLDER = "~/Desktop"



if __name__ == "__main__":
    comapny_file = sys.argv[1]

    logging.info("Reading company info and review from file")
    with open(comapny_file, 'r') as f:
        lines = [json.loads(l) for l in f.readlines()]

    company_info = lines[0]
    company_slug = company_info['slug']
    
    # print(company_info)
    # print(len(lines[1:]))

    with pymongo.MongoClient("mongodb://localhost:27017/") as client:
        db = client[DATABASE]
        comapny_collection = db[COMPANY_COLECTION]
        review_collection = db[REVIEW_COLECTION]


        if comapny_collection.count({'slug': company_slug}, limit=1) == 0:
            logging.info("Company is not created, create new one")

            image_url = urllib.parse.urljoin(BASE_URL, company_info["image_logo"])
            dest_image = os.path.join(IMAGE_DEST_FOLDER, f"{company_slug}-logo.png")

            logging.info("Download image")
            try:
                urllib.request.urlretrieve(image_url, dest_image)
            except Exception as e:
                logging.error("Cannot download {} cause {}".format(image_url, e))

            logging.info("Creating new company")
            comapny_collection.insert_one(company_info)
        
        logging.info("Getting company")
        company = comapny_collection.find_one({'slug': company_slug})

        logging.info("Delete all old reviews")
        delete_result = review_collection.delete_many({
            "company_id": company["_id"],
            "source": "crawler"
        })

        logging.info("Inserting new reviews")
        reviews = lines[1:]
        for r in reviews:
            r["company_id"] = company["_id"]
            r["source"] = "crawler"
        
        review_collection.insert_many(reviews)
