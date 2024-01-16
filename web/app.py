from flask import *
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

Client = MongoClient("mongodb://db:27017")
db = Client.aNewDb
users = db["users"]

def UserExists(username):
    if users.count_documents({"username": username}) == 0:
        return False
    else:
        return True

def ret(status, message):
    retjson = {
        "Status": status,
        "Message": message
    }
    return jsonify(retjson)
def retr(status, message,username):
    own = users.find({"username": username})[0]["own"]
    retjson = {
        "Status": status,
        "Message": message,
        "Remaining Balance":own
    }
    return jsonify(retjson)

def verify_pw(username, password):
    correct_pw = users.find({"username": username})[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), correct_pw) == correct_pw:
        return True
    else:
        return False

class Registration(Resource):
    def post(self):
        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["password"]

        if UserExists(username):
            return ret(301, "User Already Found")

        hashpw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        users.insert_one({
            "username": username,
            "password": hashpw,
            "own": 0,
            "debt": 0
        })
        return retr(200, "You Have Successfully Signed up",username)

class Add(Resource):
    def post(self):
        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["password"]
        amount = posteddata["amount"]

        if not UserExists(username):
            return ret(301, "User Does not Exists")

        if not verify_pw(username, password):
            return ret(302, "Incorrect password")

        own = users.find({"username": username})[0]["own"]
        t_amount = own + amount
        users.update_one({"username": username}, {"$set": {"own": t_amount}})
        return retr(200, "Amount Successfully added!!!!!",username)

class Takeloan(Resource):
    def post(self):
        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["password"]
        amount = posteddata["amount"]

        if not UserExists(username):
            return ret(301, "User Does not Exists")

        if not verify_pw(username, password):
            return ret(302, "Incorrect password")

        own = users.find({"username": username})[0]["own"]
        t_amount = own + amount
        users.update_one({"username": username}, {"$set": {"own": t_amount}})
        return retr(200, "Amount Successfully added!!!!!",username)

class Payloan(Resource):
    def post(self):
        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["password"]
        LP_amount = posteddata["amount"]

        if not UserExists(username):
            return ret(301, "User Does not Exists")

        if not verify_pw(username, password):
            return ret(302, "Incorrect password")

        # checking if enough amount is there
        # NOTE: There was an error in the indentation here
        amount = users.find({"username": username})[0]["own"]

        if amount < LP_amount:
            return ret(303, "Not enough amount to pay the loan")

        rem_amount = amount - LP_amount
        users.update_one({"username": username}, {"$set": {"own": rem_amount}})
        return retr(200,"Loan Payment Successfully",username)

class Checkbalance(Resource):
    def post(self):
        posteddata = request.get_json()
        username = posteddata["username"]
        password = posteddata["password"]

        if not UserExists(username):
            return ret(301, "User Does not Exists")

        if not verify_pw(username, password):
            return ret(302, "Incorrect password")

        amount = users.find({"username": username})[0]["own"]
        retjson = {
            "Balance": amount,
            "Message": "this is your total balance"
        }
        return jsonify(retjson)
api.add_resource(Registration,"/register")
api.add_resource(Takeloan,"/takeloan")
api.add_resource(Payloan,"/payloan")
api.add_resource(Checkbalance,"/checkbalance")
api.add_resource(Add,"/add")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
