#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

ecosystem = "npm"

epv_json = {}
list_of_manifests = []


def main():
    for i in range(1, 64):
        with open("manifests-{}-part-{}.json".format(ecosystem, i)) as manifest_json:
            manifest_list = json.load(manifest_json)
            for repo_name in manifest_list.keys():
                if type(manifest_list[repo_name]) is not dict:
                    print(manifest_list[repo_name])
                    continue
                list_of_manifests.append(list(manifest_list[repo_name].keys()))
                append_to_epv_json(manifest_list[repo_name], repo_name)
        # print(epv_json)
    save_list_of_manifest_list()
    save_epv_json()


def filter_list():
    pass
    # TODO


def append_to_epv_json(manifest_list, repo_name):
    for (package_name, package_version) in manifest_list.items():
        if type(package_version) != str:
            continue
        #if package_version.startswith('^'):
        #    package_version = package_version[1:]
        epv_json[package_name] = epv_json.get(package_name, set()).union(set([package_version]))


def save_list_of_manifest_list():
    print("Number of manifests: {}".format(len(list_of_manifests)))
    with open("manifests.json", 'w') as manifests_list:
        manifests_list.write(json.dumps(list_of_manifests))


def save_epv_json():
    epv_json_ser = {package_name: list(package_versions)
                    for (package_name, package_versions) in epv_json.items()}
    print("EPV count: %d" % len(epv_json.values()))
    with open('epv_to_ingest.json', 'w') as epv_json_op:
        epv_json_op.write(json.dumps(epv_json_ser))


if __name__ == "__main__":
    main()
