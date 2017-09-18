#!/usr/bin/env python3
import boto3
import botocore
from botocore.exceptions import ClientError
from nltk.stem import PorterStemmer
import json
import os
import sys


class tagging_accuracy_report():

    def __init__(self,
                 manual_tags_bucket,
                 automated_tags_bucket,
                 ecosystem='maven'):
        self.manual_tags_bucket_name = manual_tags_bucket
        self.automated_tags_bucket_name = automated_tags_bucket
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", None)
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
        if aws_access_key_id is None or aws_secret_access_key is None:
            print("No AWS credentials set in environment")
            sys.exit(1)
        self.session = boto3.session.Session(
            aws_access_key_id, aws_secret_access_key)
        self.s3_resource = self.session.resource(
            's3', config=botocore.client.Config(signature_version='s3v4'))
        self.stemmer = PorterStemmer()
        self.ecosystem = ecosystem

    def load_manual_tags_json(self, manual_tags_filename):
        manual_tags_file = self.s3_resource.Object(
            self.manual_tags_bucket_name, manual_tags_filename
        ).get()['Body'].read().decode('utf-8')
        manual_tags_json = json.loads(manual_tags_file)
        for tag_data in manual_tags_json:
            if tag_data['ecosystem'] == self.ecosystem:
                self.package_topic_json = tag_data['package_topic_map']
                break

    def get_automated_tags_for_package(self, package_name):
        tags_file_path = "{}/{}.json".format(self.ecosystem, package_name)
        automated_tags_file = self.s3_resource.Object(
            self.automated_tags_bucket_name, tags_file_path
        ).get()['Body'].read().decode('utf-8')
        automated_tags_json = json.loads(automated_tags_file)
        return automated_tags_json

    def match_tags(self):
        no_tags = man_tags_not_in_result = man_tags_not_collected = 0
        for package_name in self.package_topic_json:
            # print("Package: " + package_name)
            manual_tags = set(self.package_topic_json[package_name])
            # print(manual_tags)
            try:
                automated_tags = self.get_automated_tags_for_package(
                    package_name)
            except ClientError:
                print("No tags collected for " + package_name)
                no_tags += 1
                continue
            if 'tags' not in automated_tags \
                or len(automated_tags['tags']) == 0 \
                    or len(automated_tags['tags']['_sorted']) == 0:
                    print(
                        "No tags available for package {}".format(package_name)
                    )
                    no_tags += 1
                    continue
            # First check if all manual tags are present in result
            result = set()
            for tag_data in automated_tags['tags']['result']:
                tag_name, tag_score = tag_data
                result.add(tag_name)
            # print(result)
            tags_not_found = manual_tags - result
            if len(tags_not_found) > 0:
                print(
                    """{} not found in result for package {} in automated"""
                    """ tagging""".format(tags_not_found, package_name)
                )
                man_tags_not_in_result += 1
            else:
                print("Manual tags of {} are in result".format(package_name))
                continue
            # if not, check if all manual tags are present in collected tags
            all_tags = set()
            for tag_data in automated_tags['tags']['_sorted']:
                tag_name, tag_score = tag_data
                all_tags.add(tag_name)
            tags_not_found = manual_tags - all_tags
            if len(tags_not_found) > 0:
                print("{} not found in all tags of package {} in automated """
                      """tagging""".format(tags_not_found, package_name))
                man_tags_not_collected += 1
            else:
                print("Collected manual tags for {}".format(package_name))
        return no_tags, man_tags_not_in_result, man_tags_not_collected


def main():
    if len(sys.argv) < 4:
        print("Usage: ./tagging_accuracy_report manual_tags_bucket """
              """automated_tags_bucket manual_tags_json""")
        sys.exit(0)
    tar = tagging_accuracy_report(sys.argv[1], sys.argv[2])
    tar.load_manual_tags_json(
        sys.argv[3])
    no_tags, not_in_res, not_collected = tar.match_tags()
    print("{} packages did not have tags available for them.".format(no_tags))
    print("{} packages did not have all manual tags """
          """in the result""".format(not_in_res))
    print("{} packages did not have all manual tags """
          """collected""".format(not_collected))


if __name__ == '__main__':
    main()
