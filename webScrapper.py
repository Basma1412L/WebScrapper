from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium.webdriver.chrome.options import Options
import pymongo
from pymongo import MongoClient

#Instead of waiting for each element to load, used this method to save time
class wait_for_all(object):
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, driver):
        try:
            for method in self.methods:
                if not method(driver):
                    return False
            return True
        except StaleElementReferenceException:
            return False


options = Options()
options.headless = True
PATH = os.path.join(os.path.dirname(__file__), "chromedriver")
driver=webdriver.Chrome(PATH,options=options)
driver.get("https://www.rrpcanada.org/#/")
jsonPosts=[]

try:
    methods = []
    lefts = EC.presence_of_all_elements_located((By.CLASS_NAME,"line-item-left"))
    rights =EC.presence_of_all_elements_located((By.CLASS_NAME,"line-item-right"))
    methods.append(lefts)
    methods.append(rights)
    method = wait_for_all(methods)
    main= WebDriverWait(driver, 10).until(method)
    lefts =driver.find_elements_by_class_name("line-item-left")
    rights =driver.find_elements_by_class_name("line-item-right")
    count=0
    for item,available in zip(lefts,rights):
        postDist = {}
        postDist["_id"]=count
        postDist["Product Name"] = item.text
        postDist["Total Available"] = available.text
        jsonPosts.append(postDist)
        count+=1
finally:
    driver.quit()


#Connecting to the database and updating it
cluster = MongoClient("mongodb+srv://dbUser:12345abc@textbooks.3gxa8.mongodb.net/dbUser?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = cluster["products_availability"]
collection= db["product"]
#Checking for duplicates and searching on each element by its name to update it would take more time than removing all then inserting all. That is only because the data size is not large and there are only two fields.
collection.delete_many({})
collection.insert_many(jsonPosts)

# Testing the content on the database
# getContent=collection.find()
# for p in getContent:
#     print(p)
