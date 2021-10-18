from pymongo import MongoClient


client = MongoClient("localhost:27017")
db = client.get_database("rest")
collection = db.get_collection("Repsol")
