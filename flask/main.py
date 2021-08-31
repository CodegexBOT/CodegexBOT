import json

from flask import Flask
from flask import render_template
from flask import request
import pymongo

app = Flask(__name__)

@app.route("/")
def default():
    return render_template("index.html")

@app.route('/json')
def hello_world():
    repo_name = request.args.get("repo")
    user_name = request.args.get("user")
    print(f"{repo_name} == {user_name}")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    localdb = myclient["local"]
    table = localdb["report"]
    pattern_table = localdb["pattern_dict"]
    result = table.find({"repo": repo_name, "user": user_name})
    re = {}
    pr_dict = set()
    arr = []
    problem_count = 0
    for x in result:
        print(x)
        del x["_id"]
        pr_dict.add(x["id"])
        problem_count += len(x["items"])
        for item in x["items"]:
            item["pattern_url"] = (pattern_table.find_one({"pattern_name": item["type"]})["pattern_href"])
            
        arr.append(x)
    re["pr_count"] = len(pr_dict)
    re["problem_count"] = problem_count
    re["data"] = arr
    return json.dumps(re)

if __name__ == '__main__':
    app.run(host="0.0.0.0")

