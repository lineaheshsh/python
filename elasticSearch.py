import pprint
import json
import pymysql.cursors
import multiprocessing
import time
from elasticsearch import Elasticsearch

def selectData():

    # mysql ########################## 
    conn = pymysql.connect( host='localhost', user='root', password='1q2w3e4r5t', db='zzangho', charset='utf8', cursorclass=pymysql.cursors.DictCursor )
    curs = conn.cursor()

    sSql = "select contents_id, contents from view_news"
    curs.execute(sSql)
    rows = curs.fetchall()

    return rows


def analysis(data):
    # open
    es = Elasticsearch('localhost:9200')

    #print(es.info())

    body= {
            'tokenizer': 'nori_tokenizer',
            'filter': [
                'nori_part_of_speech_basic'
            ], 
            'text': data['CONTENTS']
    }

    r = es.indices.analyze(index='nori_naver_news', body=body)

    keywords = []

    for token in r['tokens']:
        if (len(token['token']) > 1):
            keywords.append(token['token'])

    dup_keyword = list(set(keywords))

    update(es, data['CONTENTS_ID'], dup_keyword)

    # close
    es.transport.close()

def update(es, id, keywords):
    body = {
        "doc" : {
            "keywords" : keywords
        }
    }

    #print('id :: ' + str(id))
    res = es.update(index='nori_naver_news', id=id, body=body, doc_type="_doc")

    return res

newsData = selectData()
f = open('test.txt', mode='wt', encoding='utf-8')

if __name__ == '__main__':
    secs = time.time()
    sTime = time.ctime(secs)
    print('start :: ' + sTime)
    pool = multiprocessing.Pool(processes=4)
    pool.map(analysis, newsData)
    pool.close()
    pool.join()
    eecs = time.time()
    eTime = time.ctime(eecs)
    print('end :: ' + eTime)