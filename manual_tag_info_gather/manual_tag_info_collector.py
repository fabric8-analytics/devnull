"""
For all users assigned tagging work, check how many tags are left, and how many require pruning.
Also, generate an aggregate ecosystem_package_topic_map for PGM training.
"""
"""
To run the script:
Add the config parameters to env
cp config.py.template config.py
All the user_name as user_name = ["name1", "name2",...]
python manual_tag_info_collector.py
"""

import config
import requests
import json
import sys

# Update variables from config.
user_names = config.user_names
prefix_url = config.prefix_url
ecosystem = config.ecosystem
Authorization = config.Authorization

header = {'Authorization': Authorization}
user_data_not_found = []
final_data_list = []
for_each_ecosystem = {'ecosystem': ecosystem}
final_package_dict = {}

# For each user, collect the package_topic_map list
try:
    for name in user_names:
        url = prefix_url + name + "/" + ecosystem
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            user_data_not_found.append(name)
            continue
        response_data = json.loads(response.content)
        package_topic_map = response_data.get(
            'data', {}).get('package_topic_map', {})
        for package_name, tag_list in package_topic_map.items():
            if package_name in final_package_dict.keys():
                tag_list = tag_list.extend(final_package_dict[package_name])
            final_package_dict[package_name] = list(set(tag_list))
except Exception as e:
    raise e

if len(user_data_not_found) == len(user_names):
    print("Request unsuccessfull for all users")
    sys.exit(1)

if len(user_data_not_found) > 0:
    print("Request unsuccessfull for following users %s" % user_data_not_found)


for_each_ecosystem['package_topic_map'] = final_package_dict
final_list.append(for_each_ecosystem)

with open('package_topic.json', 'w') as f:
    json.dump(final_list, f, indent=4)

empty_count = 0  # No tags found.
need_prune_count = 0  # Need to prune tag list length to 4.

for package in final_package_dict:
    plen = len(final_package_dict[package])
    if plen == 0:
        empty_count += 1
    elif plen > 4:
        need_prune_count += 1

print("Total packages to tag in %s = %d" %
      (ecosystem, len(final_package_dict)))
print("Total untagged packages = %d" % empty_count)
print("Total packages that require tag pruining = %d" % need_prune_count)
