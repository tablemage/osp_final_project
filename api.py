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

tempPostData = ''
PostData  = ""
tfidf_result = ""





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


class urlReceived(Resource):
    def post(self):
        print("urlReceived")
        global tempPostData
        parser = reqparse.RequestParser()
        parser.add_argument('urlName', type=str)
        args = parser.parse_args()
        tempPostData = args['urlName']

        return {'url': args['urlName']}

 
class fileReceived(Resource):
    def post(self):
        print("fileReceived")
        parse = reqparse.RequestParser()
        parse.add_argument('userfile', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        urlFile = args['userfile']
        urlFile.save("urlList.txt")

        return {'status' : '200'}



class fileListTransfer(Resource):
    def post(self):
        print("fileListTransfer")
        global PostData, tfidf_result
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

        #sim 계산
        sim_mat = np.zeros((tfidf.shape[0],tfidf.shape[0]))
        for i in range(tfidf.shape[0]):
            for j in range(tfidf.shape[0]):
                sim_mat[i][j] = np.dot(tfidf[i], tfidf[j])/(np.linalg.norm(tfidf[i])*np.linalg.norm(tfidf[j]))

        result = {
            'status' : '200',
            'list' : []
        }

        for i in range(count):
            token_idx_list = np.flip(np.argsort(tfidf[i]))[:10]
            tmp = []
            for idx in token_idx_list:
                tmp.append(vocab[idx])

            sim_tmp = []
            sim_value = []
            sim_idx_list = np.flip(np.argsort(sim_mat[i]))[1:4]
            for idx in sim_idx_list:
                sim_tmp.append(url[idx])
                sim_value.append(sim_mat[i][idx])


            result['list'].append( { 'url' : url[i], 'doc' : tmp,'simurl':sim_tmp,'sim':sim_value, 'count' : word_num[i], 'resTime'  : result_time[i]})  

        PostData=result
        tfidf_result = tfidf

        return result



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

        return result




class wordAnalysis(Resource):
    def post(self):
        global PostData
        print("wordAnalysis")
        result = {
            'status' : '200',
            'list' : {}
        }

        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        print(args)
        print(args['url'])
        for data in PostData['list']:
            if data["url"] == args['url']:
                result['list'] = data["doc"]

        return result

class simAnalysis(Resource):
    def post(self):
        global tfidf_result
        print("simAnalysis")
        result = {
            'status' : '200',
            'list' : []
        }

        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        idx = 1

        for data in PostData['list']:
            if data["url"] == args['url']:
                for i, u in enumerate(data["simurl"]):
                    result['list'].append({'index':idx, 'data':data["sim"][i], 'url':u})
                    idx += 1

        return result



#localhost:5000/{{router}} 와 같은식으로 주소로 데이터를 받은경우 실행
api.add_resource(urlReceived, '/url')
api.add_resource(fileReceived, '/file')
api.add_resource(fileListTransfer, '/filelist') 
api.add_resource(urlOnlyTransfer, '/onlyurl')
api.add_resource(simAnalysis,'/sim')
api.add_resource(wordAnalysis, '/word')




if __name__ == '__main__':
    app.run(debug=True)
