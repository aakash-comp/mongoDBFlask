from pymongo import MongoClient

client = MongoClient("mongodb+srv://aakashdb:<password>@assignment3.qgvar1x.mongodb.net/?retryWrites=true&w=majority")
db = client["Sensors"]

ret = db.env.find()
print(ret)