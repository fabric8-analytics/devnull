#!/usr/bin/env python3
from lda_maven_getdata import StackOverflowDataQuery
import json
import os
from nltk.tokenize import wordpunct_tokenize
import string

KEY_FILE = '/Users/avgupta/devnull/poc_tagging/key.json'

def process_package_name(pkg):
    stop_words = ['org','com','io','common']
    if pkg.find(':') != -1 and pkg.find('.') != '-1':
        tags_artifact = [tag for tag in wordpunct_tokenize(pkg) if
                tag not in string.punctuation and tag not in stop_words]
        return " ".join(tags_artifact)

def collect_data(package_name, real_name):
    sq = StackOverflowDataQuery()
    ans_q = sq.get_answer_query(package_name)
    ans_set = sq.query_big_query(KEY_FILE, ans_q)
    ans_set = [item[0] for item in ans_set.rows]

    ques_q = sq.get_question_query(package_name)
    ques_set = sq.query_big_query(KEY_FILE, ques_q)
    ques_set = [item[0] for item in ques_set.rows]

    dataset = ans_set + ques_set
    if dataset:
        with open(os.path.join('data_bigquery', real_name + '.json'), 'w') as outfile:
            outfile.write(json.dumps(dataset))
    return dataset


def dump_data_collated(dataset):
    with open('collated_dataset.json', 'w') as dumpfile:
        dumpfile.write(json.dumps(dataset))

def main():
    with open('has_github.json', 'r') as input_payload:
        pkg_list = json.loads(input_payload.read())
        dataset_agg = {}
    for pkg in pkg_list:
        print("Processing: " + pkg['real_name'])
        dataset_agg[pkg["real_name"]] = collect_data(pkg["search_query"], pkg['real_name'])
    dump_data_collated(dataset_agg)

if __name__ == '__main__':
    main()
