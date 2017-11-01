import argparse
import csv
import os
import json
import string
from google.cloud import bigquery
import datetime
from google.cloud.bigquery import SchemaField
import re


class StackOverflowDataQuery():
    """
    The Class is responsible to fetch StackOverflow data by using Google BigQuery.
    """
    def __init__(self):
        pass

    def get_latest_comment_query(self, pkg_name):
        latest_comment_query = "SELECT  text, creation_date FROM `bigquery-public-data.stackoverflow.comments` \
        where text like '%" + pkg_name + "%' ORDER BY creation_date desc LIMIT 1"
        return latest_comment_query

    def get_comment_query(self, pkg_name):
        comment_query = "SELECT text FROM `bigquery-public-data.stackoverflow.comments` \
        where text like '%" + pkg_name + "%'"
        return comment_query
        
    def get_question_query(self, pkg_name):
        question_query = "SELECT body FROM `bigquery-public-data.stackoverflow.posts_questions` \
        where body like '%" + pkg_name.replace(' ', '%') + "%'"
        return question_query

    def get_answer_query(self, pkg_name):
        answer_query = "SELECT body FROM `bigquery-public-data.stackoverflow.posts_answers` \
        where body like '%" + pkg_name.replace(' ', '%') + "%'"
        return answer_query

    def get_stackoverflow_query(self, pkg_name):
        stackoverflow_query = "SELECT body FROM `bigquery-public-data.stackoverflow.stackoverflow_posts` \
        where body like '%" + pkg_name + "%'"
        return stackoverflow_query

    def query_big_query(self, key_file, bigquerysql):
        """
        Execute queries related to fetch StackOverflow data by using google big query
        :param key_file:
        :param bigquerysql:
        :return: Query response
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_file
        bigquery_service = bigquery.Client()
        query = bigquery_service.run_sync_query(bigquerysql)
        query.timeout_ms = 60000
        query.use_legacy_sql = False
        query.use_query_cache = True
        query.run()
        return query
