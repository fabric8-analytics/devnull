#!/usr/bin/env python3
import pathlib
import json

cwd = pathlib.Path.cwd()

repo_to_owner_list = {}

for jf in cwd.glob("schemakube_*.json"):
    with open(jf) as json_list:
        jc = json.load(json_list)
        for repo in jc:
            repo_user, repo_name = repo['repo_name'].split('/')
            prev_owner_list = repo_to_owner_list.get(repo_name, [])
            prev_owner_list.append(repo_user)
            repo_to_owner_list[repo_name] = prev_owner_list

with open('repo_names.json', 'w') as f:
    f.write(json.dumps(repo_to_owner_list, sort_keys=True, indent=4))