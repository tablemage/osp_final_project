import werkzeug
import re
import requests
import timeit
import math
import argparse
import numpy
import operator
import json
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api, reqparse
from nltk.tokenize import word_tokenize

app = Flask(__name__)
api = Api(app)
# url을 get방식으로 변환하는것보다 post방식으로 변환한다음
# 반환하는 방법이 훨씬 편해서 사용하는 임시 데이터 변수입니다.
# 디비에 ID값과 같은 것으로 웹 - 서버 - 디비 연동되어야합니다. 
tempPostData = ''

# 모든 클래스는 각각의 url을 DB에 보내서 존재하는 값인지 확인해야함
# 존재하는 값이면 그 데이터를 불러와서 반환하고
# 존재하지 않는 값이면 프로그램을 통해 계산한 뒤에 데이터베이스에 입력해야함.

# 모든 데이터 베이스는 idx값을 등록해놓고 이를 사용하는것이 좋지만, url 값을 index값으로 사용하는 방식으로 짯음

# 전체적으로 index값을 기반으로 데이터를 주고받는게 좋아보입니다만, url 기반으로 하실거면 그렇게 해주세요

# 중복체크는 디비에서 검색해서 검색값이 NULL이나 공백이면 체크하는 방식으로 디비쪽에서 하는 게 좋아보입니다.
# url 을 받으면 그 url이랑 텍스트 분석결과를 디비에 저장하고 index 값을 반환해주셔야합니다.
# 그 index 값으로 호출하면, 반환받은 데이터를 분석



# 사용 할 함수들 
def cleansing(text):  # 특수문자 제거 함수
    pattern = '[(©).,0-9]'
    text = re.sub(pattern=pattern, repl='', string=text)
    text = text.lower().replace('[', '').replace(']', '').replace("'", "").replace('\n', '') \
        .replace('"', '').replace('-', '').replace('\t', '').replace('?', '').replace('@', '').replace('#', '').split()
    return text

# url  받아서 idx 값이나 db index값을 넘기세요. 그러면 그 index값을 반환해서 웹으로 넘깁니다.
#  웹에서 그 index 값을 가지고 페이지를 넘긴 다음에 이를 기반으로 데이터를 조회합니다.
# return 에 url이 아니고 index를 반환(중요)
class urlReceived(Resource):
    def post(self):
        global tempPostData
        parser = reqparse.RequestParser()
        parser.add_argument('urlName', type=str)
        args = parser.parse_args()
        tempPostData = args['urlName']

        return {'url': args['urlName']}

# 파일 데이터를 받았을때 사용하는 클래스
# 파일 일단 저장하는 클래스, 원래는 파일이름 저장해서 파일을 반환해야함.
class fileReceived(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('userfile', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        urlFile = args['userfile']
        urlFile.save("urlList.txt")

        return {'status' : '200'}


#이 클래스를 이용해서 파일 리스트를 읽어서 데이터를 반납하면 됨
# 유사성 분석 프로그램 짜서 여기다 넣고 반환하세요 JSON으로하셔야합니다
class fileListTransfer(Resource):
    def post(self):
        whole_word_info = []  # 각 url 총단어 저장
        url = []
        status = []
        word_num = []  # 각 url 단어수 저장
        start_time = []
        stop_time = []
        result_time = []
        overlap_url = []  # url 중복 체크리스트
        url_index = 0
        try:
            f = open("urlList.txt", 'r')
            url_lines = f.readlines()
            f.close()
            for i in url_lines:
                url.append(i)
                url[url_index] = url[url_index].replace("\n", "")
                try:
                    res = requests.get(url[url_index])
                    tmp = 0
                    start_time.append(timeit.default_timer())
                    html = BeautifulSoup(res.content, "html.parser")
                    html_body = html.find_all('div')
                    dictionary = {}
                    for string in html_body:
                        word = str(string.text.split())
                        word = cleansing(word)
                        for element in word:
                            if element in dictionary.keys():  # 총 단어수 tmp (중복 허용)/ 단어 리스트는 중복 없이
                                dictionary[element] += 1
                                tmp += 1
                            else:
                                dictionary[element] = 1
                                tmp += 1
                    word_doc = []  # 딕셔너리에서 리스트로 단어 옮기기
                    for key in dictionary:
                        word_doc.append(key)
                    stop_time.append(timeit.default_timer())
                    whole_word_info[url_index] = [word_doc]  # 중복없는 단어 저장
                    word_num[url_index] = tmp  # 단어 수 저장
                    result_time.append(stop_time[url_index] - start_time[url_index])
                    status.append("O")
                    url_index += 1
                except:  # url 읽어오지 못할시 오류처리
                    status.append("X")
                    result_time.append("-")
            count = len(url)
            # 이 부분은 디비값이랑 연동
            for i in range(0, count):
                check = 0
                for j in range(0, count):
                    if url[i] == url[j] and i != j:
                        check = 1
                        break
                if check == 1:  # 중복일 경우
                    overlap_url.append("O")
                else:
                    overlap_url.append("X")


        except:  # 파일읽기 시 오류처리
            print("File Read Error!")    

        result = {
            'status' : '200',
            'list' : []
        }
                
        return result


# url 단일일때 사용하는 클래스
# 여기도 프로그램 돌려야함.
#  tempPostData는 웹으로 부터 받는 index 값이 여야 합니다.
# 디비로부터 데이터 주고받으면서 해야합니다.
# 단일이라 list 쓸 필요가 없는 부분
class urlOnlyTransfer(Resource):
    def post(self):
        global tempPostData
        print(tempPostData)
        url = tempPostData
        url = url.replace("\n", "")
        start_time = []
        stop_time = []
        result_time = []
        tmp = 0
        start_time.append(timeit.default_timer())
        res = requests.get(url)
        html = BeautifulSoup(res.content, "html.parser")
        html_body = html.find_all('div')
        dictionary = {}
        for string in html_body:
            word = str(string.text.split())
            word = cleansing(word)
            for element in word:
                if element in dictionary.keys():  # 총 단어수 tmp (중복 허용)/ 단어 리스트는 중복 없이
                    dictionary[element] += 1
                    tmp += 1
                else:
                    dictionary[element] = 1
                    tmp += 1
        word_doc = []  # 딕셔너리에서 리스트로 단어 옮기기
        for key in dictionary:
            word_doc.append(key)
        stop_time.append(timeit.default_timer())
        result_time.append(stop_time[0] - start_time[0])  # 총 소요시간 result_time[0]
        result = {
            'status' : '200',
            'list' : []
        }
        result['list'].append( { 'url' : url, 'doc' : word_doc, 'count' : tmp, 'resTime'  : result_time[0]})  
        # url : url , doc : 전체단어 리스트 , count : 전체 단어 개수 , resTime : 응답시간 
        # 전체 단어리스트 말고 사실은 TF-IDF 기반 함수로 상위 TOP10 주요 단어 리스트 생성한 것을 전달해주셔야 합니다.
        #그리고 여기다가 status 값을 넣어서 이걸로 중복 신규 처리불가 이걸 추가해줘야함.
        #유사성 분석 완성하면 FILE TRANSFER 쪽 배열에다 유사성 분석 데이터 첨부해서 넣어주세요.
        #json데이터형식이 DICTIONARY 형식입니다.
        return result


#단어 분석용
#여기도 돌리셈
#url 받아서 TF-IDF 기반 함수 정의 -> 상위 top10 주요 단어 리스트 생성 (단어 분석 버튼)

class wordAnalysis(Resource):
    def post(self):

        result = {
            'status' : '200',
            'list' : {}
        }

        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str)
        args = parser.parse_args()

        result['list']['url'] = args['url']



        return result

#localhost:5000/{{router}} 와 같은식으로 주소로 데이터를 받은경우 실행
api.add_resource(urlReceived, '/url')
api.add_resource(fileReceived, '/file')
api.add_resource(fileListTransfer, '/filelist') 
api.add_resource(urlOnlyTransfer, '/onlyurl')

api.add_resource(wordAnalysis, '/word')




if __name__ == '__main__':
    app.run(debug=True)
