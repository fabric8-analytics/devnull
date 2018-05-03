import argparse
import csv
import os
import json
import string
from google.cloud import bigquery
import datetime
from google.cloud.bigquery import SchemaField
import re


class BigQueryAdapter():
    """Wrapper Class responsible to fetch data by using Google BigQuery and manipulate it."""

    def __init__(self, select_columns):
        self._token = None
        self._select_columns = select_columns

    def query_big_query(self, bigquerysql):
        """
        Execute queries related to fetch data by using google big query.

        :bigquerysql: The query to run on bigquery
        :returns:  First set of results from bigquery, row count
        """
        bigquery_service = bigquery.Client()
        query = bigquery_service.run_sync_query(bigquerysql)
        query.timeout_ms = 60000
        query.use_legacy_sql = False
        query.use_query_cache = True
        query.run()
        self.query = query
        data, row_count, self._token = query.fetch_data()
        return BigQueryAdapter._bigquery_result_to_list(self._select_columns, data), row_count

    def next_result_set(self):
        """Return a new list of results, else return None

        :returns: A list of result JSONs if available, else None
        """
        if self._token is None:
            return None, 0
        else:
            data, row_count, self._token = self.query.fetch_data(page_token=self._token)
            return BigQueryAdapter._bigquery_result_to_list(self._select_columns, data), row_count

    @staticmethod
    def _bigquery_result_to_list(select_columns, result):
        """Convert bigquery result to list of dict"""
        result_transformed = []
        for result_row in result:
            result_transformed.append(dict(zip(select_columns, result_row[:len(select_columns)])))
        return result_transformed
