import json
import pymysql.cursors
from pymongo import MongoClient

conn = pymysql.connect( host='localhost', user='root', password='1q2w3e4r5t', db='zzangho', charset='utf8', cursorclass=pymysql.cursors.DictCursor )
curs = conn.cursor()

sSql = "select * from tb_news"
curs.execute(sSql)
rows = curs.fetchall()

conn.close()

mongodb_URI = "mongodb://localhost:27020/"
client = MongoClient(mongodb_URI)

db = client.test
db.get_collection('news_20210717').insert_many(rows)