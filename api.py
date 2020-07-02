import werkzeug
import re
import requests
import timeit
import math
import argparse
import numpy as np
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
# 제발 디비에 ID값과 같은 것으로 웹 - 서버 - 디비 연동되어야합니다. 
tempPostData = ''

# 모든 클래스는 각각의 url을 DB에 보내서 존재하는 값인지 확인해야함
# 존재하는 값이면 그 데이터를 불러와서 반환하고
# 존재하지 않는 값이면 프로그램을 통해 계산한 뒤에 데이터베이스에 입력해야함.

# 모든 데이터 베이스는 idx값을 등록해놓고 이를 사용하는것이 좋음
# 근데 idx값을 사용할지 안할지 모르니 url 값을 index값으로 사용하는 방식으로 짯음

# 전체적으로 index값을 기반으로 데이터를 주고받는게 좋아보이나 할수없으면 걍 url  로 하셈

# 그리고 중복체크는 제발 디비에서 검색해서 검색값이 NULL이나 공백이면 체크하는방식으로 디비쪽에서 해야함
# 안읽는거같아서 쓰는데 일단 url 을 받으면 그 url이랑 텍스트 분석결과를 디비에 저장하고 index 값을 반환해주는거임
# 그 index 값으로 호출하면 반환받은 데이터를 다시 분석돌리는거



# 사용 할 함수들 
def cleansing(text):  # 특수문자 제거 함수
    pattern = '[(©).,0-9]'
    text = re.sub(pattern=pattern, repl='', string=text)
    text = text.lower().replace('[', '').replace(']', '').replace("'", "").replace('\n', '') \
        .replace('"', '').replace('-', '').replace('\t', '').replace('?', '').replace('@', '').replace('#', '').split()
    return text

def tfidf_weighting(docs):
    vocab = set()
    for doc in docs:
        for token in doc:
            vocab.add(token)
    vocab = list(vocab)
    print(len(vocab))

    def tf(v, doc):
        tf_result = np.zeros((len(doc),len(v)))
        print(tf_result.shape)
        for i, t in enumerate(v):
            for j, d in enumerate(doc):
                tf_result[j][i] = d.count(t)
        return tf_result
    def idf(v, doc):
        idf_result = np.zeros((len(doc),len(v)))
        for i, t in enumerate(v):
            df = 0
            for j, d in enumerate(doc):
                if t in d:
                    df += 1
            for j, d in enumerate(doc):
                idf_result[j][i] = math.log(len(doc)/(df+1))
        return idf_result
    
    tfs = tf(vocab, docs)
    idfs = idf(vocab, docs)

    tfidf = tfs*idfs

    return vocab, tfidf

# 모두다 설명해 드림 url  받아서 idx 값이나 db index값을 넘기세요
#그러면 그 index값을 반환해서 웹으로 넘겨요 
# 그럼 웹에서 그 index 값을 가지고 페이지를 넘긴다음에 이를 기반으로 데이터를 조회할 거예요
# return 에 url이 아니고 index를 반환해줘야해요
class urlReceived(Resource):
    def post(self):
        print("urlReceived")
        global tempPostData
        parser = reqparse.RequestParser()
        parser.add_argument('urlName', type=str)
        args = parser.parse_args()
        tempPostData = args['urlName']

        return {'url': args['urlName']}

# 파일 데이터를 받았을때 사용하는 클래스
# 파일 일단 저장하는 클래스임
# 원래라면 파일이름 저장해서 이걸 반환해야하는데 
class fileReceived(Resource):
    def post(self):
        print("fileReceived")
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
        print("fileListTransfer")
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
                    url_wordlist = []
                    for string in html_body:
                        word = str(string.text.split())
                        word = cleansing(word)
                        url_wordlist += word
                        tmp += len(url_wordlist)
                    stop_time.append(timeit.default_timer())
                    whole_word_info.append(url_wordlist) # 각 url별 토큰을 저장하는 리스트
                    word_num.append(tmp)  # 단어 수 저장
                    result_time.append(stop_time[url_index] - start_time[url_index])
                    status.append("O")
                    url_index += 1
                except:  # url 읽어오지 못할시 오류처리
                    status.append("X")
                    result_time.append("-")
            count = len(url)
            print(count)
            # 이건 디비값이랑 연동해서 돌리셈
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

        #tf-idf 계산
        vocab, tfidf = tfidf_weighting(whole_word_info)
        print(len(vocab))
        print(tfidf.shape)


        result = {
            'status' : '200',
            'list' : []
        }
        for i in range(count):
            token_idx_list = np.argsort(tfidf[i])[:10]
            tmp = []
            for idx in token_idx_list:
                tmp.append(vocab[idx])
            result['list'].append( { 'url' : url[i], 'doc' : tmp, 'count' : word_num[i], 'resTime'  : result_time[i]})  

                
        return result


# url 단일일때 사용하는 클래스
# 여기도 프로그램 돌려야함.
# 운래는 tempPostData는 웹으로 부터 받는 index 값이 여야 합니다.
# 제발 이거보고 이거 기준으로 코드 짜세요 그리고 변수 전역으로 쓰지마세요 제발.. 
# 디비로부터 데이터 주고받으면서 해야합니다.
# 그리고 여기는 단일인데 리스트를 쓸필요가있나?
class urlOnlyTransfer(Resource):
    def post(self):
        print("urlOnlyTransfer")
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
        word_doc = list(dictionary.keys())  # 딕셔너리에서 리스트로 단어 옮기기
        stop_time.append(timeit.default_timer())
        result_time.append(stop_time[0] - start_time[0])  # 총 소요시간 result_time[0]
        result = {
            'status' : '200',
            'list' : []
        }
        result['list'].append( { 'url' : url, 'doc' : word_doc, 'count' : tmp, 'resTime'  : result_time[0]}) 
        
        # url : url , doc : 전체단어 리스트 , count : 전체 단어 개수 , resTime : 응답시간 
        # 전체 단어리스트가 원래는 TF-IDF 기반 함수로 상위 TOP10 주요 단어 리스트 생성한거여야함.
        # 전체 단어리스트 웹으로 출력하라는 내용이 있었나?
        #그리고 여기다가 status 값을 넣어서 이걸로 중복 신규 처리불가 이걸 추가해줘야함.
        #유사성 분석 완성하면 FILE TRANSFER 쪽 배열에다 유사성 분석 데이터 첨부해서 넣으세요
        #json데이터형식이 DICTIONARY 형식인데 그정돈 할줄알잖아요 안그래요?
        return result


#단어 분석용
#여기도 돌리셈
#url 받아서 TF-IDF 기반 함수 정의 -> 상위 top10 주요 단어 리스트 생성 (단어 분석 버튼)

class wordAnalysis(Resource):
    def post(self):

        print("wordAnalysis")
        result = {
            'status' : '200',
            'list' : {}
        }

        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        print(args)
        result['list']['url'] = args['url']

        print(result)



        return result

#localhost:5000/{{router}} 와 같은식으로 주소로 데이터를 받은경우 실행
api.add_resource(urlReceived, '/url')
api.add_resource(fileReceived, '/file')
api.add_resource(fileListTransfer, '/filelist') 
api.add_resource(urlOnlyTransfer, '/onlyurl')

api.add_resource(wordAnalysis, '/word')




if __name__ == '__main__':
    app.run(debug=True)
