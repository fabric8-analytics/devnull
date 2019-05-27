import six
from google.cloud import bigquery

client = bigquery.Client()


query = """
 SELECT
    C.id, content
  FROM (
  SELECT id, content FROM
    [bigquery-public-data:github_repos.contents]
  WHERE
    content like '%k8s%' or content like '%docker' or content like '%kubernetes%'
    GROUP BY ID, CONTENT
  ) AS C
INNER JOIN (
  SELECT
    id, repo_name, path
  FROM
    [bigquery-public-data:github_repos.files]
  WHERE
    LOWER(path) LIKE '%{}' and path not LIKE '%vendor%'
  GROUP BY
    path, id, repo_name) AS F
ON
      C.id = F.id
""".format(package_filename)

query_results = client.run_sync_query(query)
query_results.use_legacy_sql = False

query_results.run()

# The query might not complete in a single request. To account for a
# long-running query, force the query results to reload until the query
# is complete.
while not query_results.complete:
  query_iterator = query_results.fetch_data()
  try:
     six.next(iter(query_iterator))
  except StopIteration:
      pass

rows = query_results.fetch_data()
for row in rows:
    print(row)
