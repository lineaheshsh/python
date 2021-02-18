import time
from json import dumps
import pymysql.cursors
import multiprocessing
from selenium import webdriver
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from kafka import KafkaProducer

docs = []
producer = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=lambda x: dumps(x).encode('utf-8'))

def init(pCode):
    driver = webdriver.Chrome('driver/chromedriver.exe')
    time.sleep(2)

    crawling(driver, pCode)

def getNewsCode():
    # mysql ########################## 
    conn = pymysql.connect( host='localhost', user='root', password='1q2w3e4r5t', db='zzangho', charset='utf8', cursorclass=pymysql.cursors.DictCursor )
    curs = conn.cursor()

    sSql = "select category_nm, category_code from tb_news_code"
    curs.execute(sSql)
    rows = curs.fetchall()

    conn.close()
    
    print(rows)
    return rows


def crawling(pDriver, pCode):

    # mysql ########################## 
    # conn = pymysql.connect( host='localhost', user='root', password='1q2w3e4r5t', db='zzangho', charset='utf8' )
    # curs = conn.cursor()

    i = 1
    while True:
        print("pagenum :: " + str(i))
        pDriver.get("https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=" + pCode['category_code'] + "#&date=%2000:00:00&page=" + str(i))

        html = pDriver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        #링크
        hrefs = soup.select(
            '#section_body > ul > li > dl > dt:nth-child(1) > a'
        )

        #제목
        titles = soup.select(
            '#section_body > ul > li > dl > dt:nth-child(2) > a'
        )

        #신문사
        companies = soup.select(
            '#section_body > ul > li > dl > dd > span.writing'
        )

        if len(hrefs) <= 0: 
            break
        

        contents = []
        dates = []
        ampms = []
        times = []

        ## 상세페이지 수집(본문내용, 작성일)
        for href in hrefs:
            sub_url = 'https://news.naver.com' + href.attrs['href']

            pDriver.get(sub_url)

            sub_html = pDriver.page_source
            sub_soup = BeautifulSoup(sub_html, 'html.parser')
            content = sub_soup.select_one('div#articleBodyContents').get_text()
            fullDate = sub_soup.select_one('span.t11').get_text()
            date = fullDate.split(" ")[0]
            ampm = fullDate.split(" ")[1]
            time = fullDate.split(" ")[2]

            contents.append(content)
            dates.append(date[:-1])
            ampms.append(ampm)
            times.append(time)

        for item in zip(hrefs, titles, companies, contents, dates, ampms, times):

            # kafka producer
            data = {'category' : pCode['category_code'], 
                    'title': item[1].text, 
                    'contents': item[3], 
                    'writer': '', 
                    'date': item[4],
                    'ampm': item[5],
                    'time': item[6],
                    'company': item[2].text,
                    'url': 'https://news.naver.com' + item[0].attrs['href']}
            print(data)
            producer.send('test', value=data)
            print('producer end!')

            # sSql = "select * from tb_news where CATEGORY=%s and TITLE=%s and CONTENTS=%s"
            # curs.execute(sSql, (pCode['category_code'], item[1].text, item[3]))
            # rows = curs.fetchall()

            # if len(rows) == 0:
            #     iSql = "insert into tb_news(CATEGORY, TITLE, CONTENTS, WRITER, DATE, AMPM, TIME, COMPANY, URL, CRAWLER_DT, UDT_DT) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())"
            #     curs.execute(iSql, (pCode['category_code'] ,item[1].text , item[3], '', item[4], item[5], item[6], item[2].text, 'https://news.naver.com' + item[0].attrs['href']))

            #     keywords = analysis(item)

            #     docs.append({
            #         '_index': 'nori_naver_news',
            #         '_source': {
            #             'category_nm': pCode['category_nm'],
            #             'title': item[1].text,
            #             'contents': item[3],
            #             'writer': '',
            #             'date': item[4],
            #             'ampm': item[5],
            #             'time': item[6],
            #             'company': item[2].texxt,
            #             'url': 'https://news.naver.com' + item[0].attrs['href'],
            #             'keywords': keywords
            #         }
            #     })

        # conn.commit()

        # 페이지 증가
        i += 1
        
    # close(pDriver)
    # conn.close()

    # index(docs)

def close(pDriver):
    pDriver.quit()

def analysis(data):
    # open
    es = Elasticsearch('localhost:9200')

    body= {
            'tokenizer': 'nori_tokenizer',
            'filter': [
                'nori_part_of_speech_basic'
            ], 
            'text': data[3]
    }

    r = es.indices.analyze(index='nori_naver_news', body=body)

    keywords = []

    for token in r['tokens']:
        if (len(token['token']) > 1):
            keywords.append(token['token'])

    dup_keyword = list(set(keywords))

    #index(es, data, dup_keyword)

    # close
    es.transport.close()

    return dup_keyword

def index(dataArrays):
    es = Elasticsearch('localhost:9200')

    es.bulk(es, dataArrays)
    
#news_code = ['100','101','102','103','104','105']

if __name__ == '__main__':
    news_code = getNewsCode()
    pool = multiprocessing.Pool(processes=4)
    pool.map(init, news_code)
    pool.close()
    pool.join()