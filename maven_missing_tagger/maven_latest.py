#!/usr/bin/python3
# This script was used to list untagged packages during initial tagger run.
# These packages are sent to jobs API endpoint that triggers tagging again.
#
# Versions are received from JSON that was created from maven index checker.

# Bucket copied using:
#   aws s3 cp s3://prod-keywords-summary prod-keywords-summary --recursive

import os
import yaml
import sys
import json
import logging
import requests


logger = logging.getLogger(__name__)


_VERSION_FILE = 'maven_latest.json'
_JOBS_ENDPOINT = 'http://bayesian-jobs-bayesian-production.09b5.dsaas.openshiftapps.com/api/v1/jobs/selective-flow-scheduling?state=running'
_JOBS_TOKEN = 'TBD'

with open(_VERSION_FILE, 'r') as f:
    version_content = yaml.load(f)


def dict2json(dict_):
    return json.dumps(dict_, sort_keys=True, separators=(',', ': '), indent=2)


def is_empty_result(result_file):
    with open(result_file, 'r') as f:
        content = yaml.load(f)

    return len(content['tags']['_sorted']) == 0 or \
           len(content['_all']['package']) == 0 or \
           len(content['_all']['versions']) == 0


def get_version(package_name):
    version = version_content.get(package_name)
    if not version:
        raise ValueError("No version found for package '%s'" % package_name)

    return version


def get_untagged():
    flow_arguments = []
    for dirpath, _, filenames in os.walk('maven'):
        for filename in filenames:
            result_file = os.path.join(dirpath, filename)
            package_name = filename[:-len('.json')]

            if not is_empty_result(result_file):
                continue

            try:
                package_version = get_version(package_name)
            except ValueError as exc:
                logger.warning("Failed to get version for package '%s': %s" % (package_name, str(exc)))
                continue

            flow_arguments.append({
                'ecosystem': 'maven',
                'name': package_name,
                'version': package_version,
                'force': True,
            })

    return flow_arguments


def main():
    flow_arguments = get_untagged()
    payload = {
        'flow_arguments': flow_arguments,
        'flow_name': 'bayesianFlow',
        'task_names': [
            'keywords_tagging',
            'package_keywords_tagging',
            'ResultCollector',
            'PackageResultCollector',
            'GraphImporterTask',
            'PackageGraphImporterTask'
        ]
    }

    response = requests.post(_JOBS_ENDPOINT, headers={'auth_token': _JOBS_TOKEN}, json=payload)
    print("Request HTTP status code: %d" % response.status_code)
    print("Request result: %s" % response.text)


if __name__ == '__main__':
    sys.exit(main())
