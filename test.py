import requests
import json

for i in range(2000):
    json_data = "{'category': 'aa','title': '" + str(i) + "','contents': 'cc','writer': 'dd','data': 'ff','ampm': 'gg','time': 'hh','company': 'ii','url': 'jj'}".encode('utf-8').decode('iso-8859-1')
    response = requests.post('http://localhost:9090/kafka', data=json_data)
    if response.text == "success":
        print('producer end!')
    else:
        print('[ERROR]producer Fail!!!!!!!!!!!!!!!!!!!!!!!')