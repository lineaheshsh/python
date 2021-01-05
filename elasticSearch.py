import pprint
import json
import pymysql.cursors
import multiprocessing
from elasticsearch import Elasticsearch

def selectData():

    # mysql ########################## 
    conn = pymysql.connect( host='localhost', user='root', password='1q2w3e4r5t', db='zzangho', charset='utf8', cursorclass=pymysql.cursors.DictCursor )
    curs = conn.cursor()

    sSql = "select contents_id, contents from view_news limit 0, 20"
    curs.execute(sSql)
    rows = curs.fetchall()

    return rows


def analysis(data):
    # open
    es = Elasticsearch('localhost:9200')

    #print(es.info())

    body= {
            'tokenizer': {
                'type': 'nori_tokenizer',
                'decompound_mode': 'mixed',
                'stoptags': [
                            "E",
                            "IC",
                            "J",
                            "MAG",
                            "MM",
                            "NA",
                            "NR",
                            "SC",
                            "SE",
                            "SF",
                            "SH",
                            "SL",
                            "SN",
                            "SP",
                            "SSC",
                            "SSO",
                            "SY",
                            "UNA",
                            "UNKNOWN",
                            "VA",
                            "VCN",
                            "VCP",
                            "VSV",
                            "VV",
                            "VX",
                            "XPN",
                            "XR",
                            "XSA",
                            "XSN",
                            "XSV"
                            ]
            }, 
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
        'keywords': keywords
    }

    print('id :: ' + str(id))
    res = es.index(index='nori_naver_news', id=id, body=body)

    return res

newsData = selectData()
f = open('test.txt', mode='wt', encoding='utf-8')

if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=2)
    pool.map(analysis, newsData)
    pool.close()
    pool.join()