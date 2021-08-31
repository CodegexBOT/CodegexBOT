# transport pattern descriptions to mondodb
import json
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017")
localdb= myclient["local"]
table = localdb["pattern_dict"]
with open("pattern_dict.json", "r") as f:
    data = json.loads(f.read())
    for item in data:
        data[item]["pattern_name"] = item
        print(data[item])
        print("============")
        table.insert_one(data[item])

