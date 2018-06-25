#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import daiquiri
import logging
from bigquery_utils import *


bq_master = BigQueryAdapter(['repo_name', 'pom_path', 'content'])
daiquiri.setup(level=logging.INFO)
_logger = daiquiri.getLogger(__name__)

ecosystem = "maven"


def setup():
    if not os.path.exists('./manifests-EPV' + ecosystem):
        os.makedirs('./manifests-EPV' + ecosystem)


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def get_list_from_bq():
    """Get the file content from bigquery."""
    query = "SELECT A.repo_name as repo_name, A.path as pom_path, B.content as content FROM `bigquery-public-data.github_repos.files` as A JOIN  `bigquery-public-data.github_repos.contents` as B ON A.id=B.id WHERE A.path like '%pom.xml%'"
    _logger.info("--Query complete!--")
    response, row_count = bq_master.query_big_query(query)
    if row_count == 0:
        _logger.info("The query did not return any results")
        return
    part = 1
    while response is not None:
        print("Processing {} rows in part {}".format(row_count, part))
        queue = {}
        for manifest in response:
            queue[manifest['repo_name'] + "::_::" +
                  manifest['pom_path']] = manifest['content']
        with open(os.path.join('./manifests-EPV-{}'.format(ecosystem), 'manifests-{}-part-{}.json'.format(ecosystem, part)), 'w') as f:
            f.write(json.dumps(queue, indent=True))
        response, row_count = bq_master.next_result_set()
        part += 1
    _logger.info("Total parts processed {}".format(part - 1))


if __name__ == "__main__":
    setup()
    get_list_from_bq()
