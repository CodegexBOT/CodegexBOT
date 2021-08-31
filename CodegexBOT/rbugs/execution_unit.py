from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from exp_pull_requests import get_modified_patchset
import json
import os
import sys
import time

import pymongo

sys.path.append(os.path.dirname(__file__))

if __name__ == '__main__':
    global repo_user
    global repo_name
    global pr_id
    repo_user, repo_name, pr_id =sys.argv[1].split('/')
    context = Context()
    engine = DefaultEngine(context)
    patch_set = get_modified_patchset()
    engine.context.update_repo_name(repo_name)
    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    localdb = myclient["local"]
    table = localdb["report"]
    bugs_json = dict()
    bugs_json['repo'] = repo_name
    bugs_json['user'] = repo_user
    bugs_json['id'] = pr_id
    bugs_json['time'] = int(time.time())
    if patch_set:
        engine.visit(*patch_set)
        bugs = engine.filter_bugs()
        if bugs:
            bugs_json['total'] = len(bugs)
            bugs_json['items'] = [bug.__dict__ for bug in bugs]
        else:
            bugs_json['total'] = 0
            bugs_json['items'] = []
    else:
        bugs_json['total'] = 0
        bugs_json['items'] = []
    table.insert_one(bugs_json)
print("Happy~")
