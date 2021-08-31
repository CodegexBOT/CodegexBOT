from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from exp_pull_requests import get_modified_patchset
import re
import json
import os
import sys
import csv
import time
import ast
import random
import requests

user_agent = 'Mozilla/5.0 ven(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/69.0.3497.100 Safari/537.36 '
token = '8ceea3ee741bbfb004e76405ae956fcca7369c1d'
RE_SHA = re.compile(r'https://github\.com/[^/]+/[^/]+/blob/(\w+)/')
report_save_path = 'autoComment/report.json'
pull_save_path = 'autoComment/file.json'
records_save_path = 'autoComment/config/records.csv'

sys.path.append(os.path.dirname(__file__))

PATTERN_DICT_PATH = './autoComment/config/pattern_dict.json'
RECORDS_PATH = './autoComment/config/records.csv'
PROXIES_PATH = './autoComment/config/proxy_pool.txt'

pattern_dict = None


def get_pull_file():
    headers = {'User-Agent': user_agent, 'Authorization': f'token {token}'}
    r = requests.get(query_download_url, headers=headers)
    file_object = open(pull_save_path, 'w')
    file_object.write(r.text)
    file_object.close()
    return r.text


def generate_records():
    headers = ['relative_path', 'html_url', 'path', 'commit_id', 'line', 'bug_type', 'priority', 'comment_or_not',
               'token']
    with open(report_save_path, 'r') as f:
        tmp_record = json.load(f)
        rows = []
        for row_data in tmp_record['items']:
            rows.append([row_data['file_name'], query_download_url, row_data['file_name'], row_data['commit_sha'],
                         row_data['line_no'],
                         row_data['type'], row_data['priority'], 'TRUE', f'{token}'])
        with open(records_save_path, 'w')as f_record:
            f_csv = csv.writer(f_record)
            f_csv.writerow(headers)
            f_csv.writerows(rows)
            f_record.close()
        f.close()


def parse_html(pr_url: str):
    url_parts = pr_url.split('/')
    return url_parts[3], url_parts[4], url_parts[6]


def load_pattern_dict():
    global pattern_dict
    pattern_dict = json.load(open(PATTERN_DICT_PATH, 'r'))


def get_body(pattern_name):
    category_name = pattern_dict[pattern_name]['category_name']
    category_href = pattern_dict[pattern_name]['category_href']
    des_title = pattern_dict[pattern_name]['des_title']
    des_detail = pattern_dict[pattern_name]['des_detail']
    pattern_href = pattern_dict[pattern_name]['pattern_href']
    body = '''I detect that this code is problematic. According to the [{category_name}]\
({category_href}), [{des_title}]({pattern_href}).
{des_detail}'''.format(category_name=category_name,
                       category_href=category_href,
                       des_title=des_title,
                       des_detail=des_detail,
                       pattern_href=pattern_href)
    return body


def read_csv():
    csv_table = [line for line in csv.reader(open(RECORDS_PATH, 'r'))]
    comments_info = []
    flag = False
    for line_no, row in enumerate(csv_table):
        if line_no == 0:
            continue
        comment = dict()
        html_url = row[1]
        owner, repo, pull_number = parse_html(html_url)
        path = row[2]
        commit_id = row[3]
        line = row[4]
        bug_type = row[5]
        comment_or_not = row[7]
        token = row[8]
        if comment_or_not == 'TRUE':
            body = get_body(bug_type)
            comment["owner"] = owner
            comment["repo"] = repo
            comment["pull_number"] = pull_number
            comment["commit_id"] = commit_id
            comment["path"] = path
            comment["line"] = int(line)
            comment["type"] = bug_type
            comment["body"] = body
            comment['token'] = token
            comments_info.append(comment)
    return comments_info


def create_comment_from_comments_info(comments_info):
    for comment in comments_info:
        # owner: str, repo: str, pull_number: int, body: str, commit_id: str, path: str, line: int
        create_comment(comment['body'], comment['commit_id'], comment['path'], comment['line'], comment['token'],
                       )
        print('time sleep for 10s.')
        time.sleep(10)


def create_comment(body: str, commit_id: str, path: str, line: int, token: str, ):
    query_url = "https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments".format(owner=repo_user,
                                                                                                  repo=repo_name,
                                                                                                  pull_number=
                                                                                                  pr_id)
    comment_url = "https://github.com/{owner}/{repo}/pull/{pull_number}".format(owner=repo_user,
                                                                                repo=repo_name,
                                                                                pull_number=pr_id)
    params = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "side": "RIGHT",
        "line": line,
    }
    headers = {'Authorization': f'token {token}', 'accept': "application/vnd.github.v3+json"}
    # print(query_url)
    r = requests.post(query_url, data=json.dumps(params), headers=headers)
    print(r.text)
    if r.status_code == 201:
        print('link:', comment_url)
        return comment_url
    else:
        print("status_code", r.status_code, 'link', comment_url, 'content', r.content)


if __name__ == '__main__':
    args_list = sys.argv
    global repo_user
    global repo_name
    global pr_id
    global query_download_url
    repo_user, repo_name, pr_id = parse_html(sys.argv[1])
    query_download_url = f'https://api.github.com/repos/{repo_user}/{repo_name}/pulls/{pr_id}/files'
    context = Context()
    engine = DefaultEngine(context)
    # get_pull_file()
    load_pattern_dict()
    patch_set = get_modified_patchset(pull_save_path)
    engine.context.update_repo_name(repo_name)
    if patch_set:
        engine.visit(*patch_set)
        bugs = engine.filter_bugs()
        if bugs:
            with open(report_save_path, 'w') as out:
                bugs_json = dict()
                bugs_json['repo'] = repo_name
                bugs_json['id'] = pr_id
                bugs_json['total'] = len(bugs)
                bugs_json['items'] = [bug.__dict__ for bug in bugs]
                json.dump(bugs_json, out)
        generate_records()
        comments_info = read_csv()
        print('start auto-commenting for {} items.'.format(str(len(comments_info))))
        create_comment_from_comments_info(comments_info)
