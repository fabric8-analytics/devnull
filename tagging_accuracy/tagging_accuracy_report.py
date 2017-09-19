#!/usr/bin/env python3
import boto3
import botocore
from botocore.exceptions import ClientError
import json
import os
import sys
import click


class TaggingAccuracyReport():

    def __init__(self,
                 manual_tags_bucket,
                 automated_tags_bucket,
                 manual_tags_filename,
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
        self.ecosystem = ecosystem
        self.package_topic_json = self.load_manual_tags_json(
            manual_tags_filename)

    def load_manual_tags_json(self, manual_tags_filename):
        manual_tags_file = self.s3_resource.Object(
            self.manual_tags_bucket_name, manual_tags_filename
        ).get()['Body'].read().decode('utf-8')
        manual_tags_json = json.loads(manual_tags_file)
        for tag_data in manual_tags_json:
            if tag_data['ecosystem'] == self.ecosystem:
                return tag_data['package_topic_map']
            else:
                return {}

    def get_automated_tags_for_package(self, package_name):
        tags_file_path = "{}/{}.json".format(self.ecosystem, package_name)
        try:
            automated_tags_file = self.s3_resource.Object(
                self.automated_tags_bucket_name, tags_file_path
            ).get()['Body'].read().decode('utf-8')
        except ClientError:
            print("No tags collected for " + package_name)
            return {}
        automated_tags_json = json.loads(automated_tags_file)
        if 'tags' not in automated_tags_json or \
            len(automated_tags_json['tags']) == 0 \
                or len(automated_tags_json['tags']['_sorted']) == 0:
            print(
                "No tags available for package {}".format(package_name)
            )
            return {}
        return automated_tags_json['tags']

    def match_tags(self):
        total_packages = correctly_tagged = partially_correct = \
            no_tags = man_tags_not_in_result = man_tags_not_collected = 0
        no_tags_list = []
        for package_name in self.package_topic_json:
            total_packages += 1
            manual_tags = set(self.package_topic_json[package_name])
            automated_tags = self.get_automated_tags_for_package(package_name)
            if len(automated_tags) == 0:
                no_tags_list.append(":".join(package_name.split(':')[:2]))
                no_tags += 1
                continue
            # First check if all manual tags are present in result
            result = set()
            for tag_data in automated_tags['result']:
                tag_name, tag_score = tag_data
                result.add(tag_name)
            tags_not_found = manual_tags - result
            if len(tags_not_found) > 0:
                print(
                    """{} not found in result for package {} in automated"""
                    """ tagging""".format(tags_not_found, package_name)
                )
                man_tags_not_in_result += 1
            else:
                print("Manual tags of {} are in result".format(package_name))
                correctly_tagged += 1
                partially_correct += 1
                continue
            # if not, check if all manual tags are present in collected tags
            all_tags = set()
            for tag_data in automated_tags['_sorted']:
                tag_name, tag_score = tag_data
                all_tags.add(tag_name)
            tags_not_found = manual_tags - all_tags
            if len(tags_not_found) > 0:
                print("{} not found in all tags of package {} in automated """
                      """tagging""".format(tags_not_found, package_name))
                man_tags_not_collected += 1
            else:
                print("Collected manual tags for {}".format(package_name))
                partially_correct += 1
        with open('no_tags.json', 'w') as f:
            f.write(json.dumps(no_tags_list))
        return no_tags, man_tags_not_in_result, man_tags_not_collected, total_packages, correctly_tagged, partially_correct


@click.command()
@click.option('--automated-tags-bucket',
              help='The bucket in which automated tags are stored',
              required=True)
@click.option('--manual-tags-bucket',
              help='The bucket in which manual tags are stored',
              required=True)
@click.option('--manual-tags-json',
              help='The path to json on s3 bucket containing the manual tags',
              required=True)
def main(automated_tags_bucket, manual_tags_bucket, manual_tags_json):
    tar = TaggingAccuracyReport(
        manual_tags_bucket, automated_tags_bucket, manual_tags_json)
    no_tags, not_in_res, not_collected, total, correct, partially_correct = \
        tar.match_tags()
    print("{} packages did not have tags available for them.".format(no_tags))
    print("{} packages did not have all manual tags """
          """in the result""".format(not_in_res))
    print("{} packages did not have all manual tags """
          """collected""".format(not_collected))
    tags_found = total - no_tags
    print("Tagged {}% packages correctly".format(correct / tags_found * 100))
    print("Successfully extracted all manual tags for {}% packages".format(
        partially_correct / tags_found * 100))


if __name__ == '__main__':
    main()
