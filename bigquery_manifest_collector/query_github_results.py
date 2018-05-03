#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import subprocess
import daiquiri
import logging
import envoy

from bigquery_utils import *


bq_master = BigQueryAdapter(['repo_name', 'content'])
daiquiri.setup(level=logging.INFO)
_logger = daiquiri.getLogger(__name__)

ecosystem = "npm"

def setup():
    import os
    if not os.path.exists('./manifests-' + ecosystem):
        os.makedirs('./manifests-' + ecosystem)


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def get_list_from_bq():
    """Get the file content from bigquery."""
    query = "SELECT A.repo_name as repo_name, B.content as content FROM `bigquery-public-data.github_repos.files` as A JOIN  `bigquery-public-data.github_repos.contents` as B ON A.id=B.id WHERE A.path like 'package.json'"
    response, row_count = bq_master.query_big_query(query)
    if row_count == 0:
        _logger.info("The query did not return any results")
        return
    part = 1
    while response is not None:
        print("Processing {} rows in part {}".format(row_count, part))
        queue = {}
        for manifest in response:
            try:
                queue[manifest['repo_name']] = json.loads(manifest['content'])
            except (json.decoder.JSONDecodeError, TypeError) as e:
                _logger.error("Cound not parse package.json from {}, error: {}".format(manifest['repo_name'], e))
                continue
        process_response(queue, part=part)
        response, row_count = bq_master.next_result_set()
        _logger.info("Processed part {}".format(part))
        part += 1


def process_response(queue, part=0):
    """Get the manifest"""
    manifest_list = {}
    for repo in queue.keys():
        try:
            dependencies = queue[repo].get('dependencies', {})
        except AttributeError:
            _logger.error("content for {} is not a dict".format(repo))
        if not dependencies:
            _logger.info('No dependencies for {}'.format(repo))
            continue
        manifest_list[repo] = dependencies
    _logger.info("Processed {} dependencies in part {}".format(len(manifest_list), part))
    with open('manifests-{}-part-{}.json'.format(ecosystem, part), 'w') as f:
        f.write(json.dumps(manifest_list))


if __name__ == "__main__":
    setup()
    get_list_from_bq()
