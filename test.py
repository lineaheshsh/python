from pymongo import MongoClient
import re
import datetime

collection_json = [
    {
        "col_name" : "ticket_goods",
        "count" : 0,
        "list": ""
    },
    {
        "col_name" : "ticket_man",
        "count" : 0,
        "list": ""
    }
]
collection_arr = ["ticket_goods", "ticket_man"]

# 방법1 - URI
mongodb_URI = "mongodb://localhost:27017/"
client = MongoClient(mongodb_URI)

db = client.test
collections = db.list_collection_names()

for col_json in collection_json:
    for collection in collections:
        if str(collection).find(col_json['col_name']) > -1:
            print(col_json['col_name'] + ": " + collection)
            col_json['count'] = col_json['count'] + 1
            if str(collection) != "ticket_goods_inc":
                col_json['list'] = col_json['list'] + str(collection) + ","

print(collection_json)

for collection in collection_json:
    if collection['count'] > 3:
        remove_list = collection['list'].split(",")
        for num in range(0, len(remove_list) - 4):
            now = datetime.datetime.now()
            nowDate = now.strftime('%Y%m%d')
            print(nowDate)
            print(now - datetime.timedelta(1))
            print(now - datetime.timedelta(2))
            #db.drop_collection(remove_list[num])