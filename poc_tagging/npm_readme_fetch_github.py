#!/usr/bin/env python3
"""Gets the readme for the most popular NPM packages from github and stores it and the description
against the repository name in a formatted JSON.

Usage: ./npm_readme_fetch_github
"""
import github3
import daiquiri
import logging
import json

daiquiri.setup(level=logging.DEBUG)
_logger = daiquiri.getLogger(__name__)

gh = github3.GitHub()
search_result = gh.search_repositories(query="language:javascript stars:>10000",
                                       sort="stars", number=100)

json_dump = {}

for search_hit in search_result:
    # check if file is a valid npm package
    package_json_content = search_hit.repository.file_contents('package.json')
    if isinstance(package_json_content, github3.null.NullObject):
        _logger.warning("No action taken for package {} as it's not a valid NPM package".format(
                        search_hit))
        continue
    readme = search_hit.repository.readme()
    repo_name = search_hit.as_dict().get('full_name')
    json_dump[repo_name] = {
        "readme": readme.decoded.decode('utf-8'),
        "description": search_hit.repository.description
    }


with open('npm_data.json', 'w') as npm_data_json:
    npm_data_json.write(json.dumps(json_dump))
