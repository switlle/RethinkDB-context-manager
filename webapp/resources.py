from webapp import app
from flask_restful import Resource

class Main(Resource):
    def get(self):
        return {"GET message": "Hello, World!"}
        
    def post(self):
        return {"POST message": "Hello, World!"}
