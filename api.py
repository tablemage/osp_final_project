from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import werkzeug


app = Flask(__name__)
api = Api(app)
# url을 get방식으로 변환하는것보다 post방식으로 변환한다음
# 반환하는 방법이 훨씬 편해서 사용하는
# 임시 temp data
tempPostData = ''

# 모든 클래스는 각각의 url을 DB에 보내서 존재하는 값인지 확인해야함
# 존재하는 값이면 그 데이터를 불러와서 반환하고
# 존재하지 않는 값이면 프로그램을 통해 계산한 뒤에 데이터베이스에 입력해야함.

# 모든 데이터 베이스는 idx값을 등록해놓고 이를 사용하는것이 좋음
# 근데 idx값을 사용할지 안할지 모르니 url 값을 index값으로 사용하는 방식으로 짯음


# 테스트용 클래스

class urlReceived(Resource):
    def post(self):
        global tempPostData
        parser = reqparse.RequestParser()
        parser.add_argument('urlName', type=str)
        args = parser.parse_args()
        tempPostData = args['urlName']

        return {'url': args['urlName']}
# 파일 데이터를 받았을때 사용하는 클래스
class fileReceived(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('userfile', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        urlFile = args['userfile']
        urlFile.save("urlList.txt")

        return {'status' : '200'}


#이 클래스를 이용해서 파일 리스트를 읽어서 데이터를 반납하면 됨
class fileListTransfer(Resource):
    def post(self):
        result = {
            'status' : '200',
            'list' : []
        }
        f = open("urlList.txt", 'r')
        lines = f.readlines()
        f.close()
        for i in lines:
            result["list"].append({"url" : lines[i]})
        return result


# url 단일일때 사용하는 클래스
# 여기도 프로그램 돌려야함.
class urlOnlyTransfer(Resource):
    def post(self):

        result = {
            'status' : '200',
            'list' : {}
        }



        result['list']['url'] = tempPostData

        return result

#url 추가용
#여기도 분석프로그램 돌려야함.
class addUrl(Resource):
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

#유사성 분석용
# 분석 프로그램 돌릴 곳

class simAnalysis(Resource):
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

#단어 분석용
#분석 프로그램 돌릴 곳

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
api.add_resource(addUrl, '/addurl')
api.add_resource(simAnalysis, '/sim')
api.add_resource(wordAnalysis, '/word')




if __name__ == '__main__':
    app.run(debug=True)
