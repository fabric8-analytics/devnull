#!/usr/bin/env python3
"""Check for missing maven packages and automatically suggest changes in package name correction."""
# Copy prod bucket:
#   aws s3 cp s3://prod-keywords-summary prod-keywords-summary --recursive
#
# The version file is file containing mapping package-name to package version, e.g.:
#   'log4j:log4j': '1.0.0'
#
# Example run:
#   why_missing_maven.py -v --no-tagged prod-keywords-summary/maven --version-file maven_latest.json

import json
import logging
import os
import re
import sys

import click
import daiquiri
import requests
import yaml

daiquiri.setup(level=logging.INFO)
_logger = daiquiri.getLogger(__name__)


def iter_files(path):
    """Yield each file in a directory tree.

    :param path: path to a directory tree to yield files
    :return: file
    """
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


def _create_flow_args(names, versions):
    """Create flow arguments that can be directly fed into jobs service."""
    flow_arguments = []

    for name in names:
        version = versions.get(name)

        if not version:
            _logger.warning("No version information found for package '%s'", name)
            continue

        flow_arguments.append({
            'ecosystem': 'maven',
            'name': name,
            'recursive_limit': 0,
            'force': True,
            'version': version
        })

    return flow_arguments


def _has_tags(tagging_result):
    """Check whether tagging result has tags."""
    return len(tagging_result['tags']['result']) != 0


def _create_maven_central_url(name):
    """Construct URL to Maven Central Repository for the given package."""
    name_parts = re.split('[:.]', name)
    return 'https://repo1.maven.org/maven2/' + "/".join(name_parts)


def _create_maven_repository_url(name):
    """Construct URL to Maven Repository for the given package."""
    # Let's use only group id and artifact id, assuming the suspicious names are already flagged.
    name_parts = name.split(':')
    # There is a possibility of key error, but it never occurred on testing set, leave as is for now.
    return 'http://mvnrepository.com/artifact/{group_id}/{artifact_id}'. \
        format(group_id=name_parts[0], artifact_id=name_parts[1])


def _create_tagged_result_entry(name, tagging_result):
    """Create entry in tagged listing."""
    tagging_result.pop('_audit', None)
    tagging_result['name'] = name
    return tagging_result


def _create_untagged_result_entry(name):
    """Create entry in untagged list - check for reasoning why tags were not found."""
    name_parts = name.split(':')
    maven_central_url = _create_maven_central_url(name)
    maven_repository_url = _create_maven_repository_url(name)

    _logger.debug("Checking maven central for package '%s', URL: %s", name, maven_central_url)
    maven_central_status_code = requests.head(maven_central_url).status_code
    _logger.debug("Response from maven central: %d", maven_central_status_code)

    _logger.debug("Checking maven repository for package '%s', URL: %s", name, maven_repository_url)
    maven_repository_status_code = requests.head(maven_repository_url).status_code
    _logger.debug("Response from maven repository: %d", maven_repository_status_code)

    return {
        'name': name,
        'suspicious_package_name': len(name_parts) != 2,
        'maven_central_url': maven_central_url,
        'maven_repository_url': maven_repository_url,
        'maven_repository_status_code': maven_repository_status_code,
        'maven_central_status_code': maven_central_status_code,
        'suggested_name': ":".join(name_parts[:2]) if maven_repository_status_code == 200 else None
    }


def _create_untagged_summary(untagged_packages, versions):
    """Add summary about untagged packages."""
    result = dict.fromkeys(('non_existing', 'to_inspect', 'no_version'), [])

    for file_path, untagged_info in untagged_packages.items():
        if untagged_info['maven_central_status_code'] == 404 and \
                        untagged_info['maven_repository_status_code'] == 404:
            result['non_existing'].append(file_path)
        elif not versions.get(untagged_info['name']):
            result['no_version'].append(file_path)
        else:
            result['to_inspect'].append(file_path)

    # ... and add some nice to have stats
    result['non_existing_count'] = len(result['non_existing'])
    result['to_inspect_count'] = len(result['to_inspect'])
    result['no_version_count'] = len(result['no_version'])

    return result


def check_why_missing(path, tagged=True, untagged=True, version_file=None):
    """Check for packages that are missing.

    :param path: path to directory containing JSON files
    :param tagged: collect tagged packages
    :type tagged: bool
    :param untagged: collect untagged packages
    :type untagged: bool
    :param version_file: version file to be used
    :type: str
    :return: a dict containing information about tagged and untagged packages
    :rtype: dict
    """
    result = {}
    if tagged:
        result['tagged'] = {}

    if untagged:
        result['untagged'] = {}

    _logger.debug("Listing JSON files in '%s'", path)
    for file_path in iter_files(path):

        if not file_path.endswith('.json'):
            _logger.warning("Ignoring file '%s' - not a JSON file", file_path)
            continue

        _logger.debug("Parsing JSON file in '%s'", file_path)
        with open(file_path, 'r') as f:
            content = json.load(f)

        package_name = os.path.basename(file_path[:-len('.json')])

        if not _has_tags(content) and untagged:
            result['untagged'][file_path] = _create_untagged_result_entry(package_name)
        elif _has_tags(content) and tagged:
            result['tagged'][file_path] = _create_tagged_result_entry(package_name, content)
        else:
            _logger.debug("Package '%s' (from file '%s') will not be part of output (package %s tags)",
                          package_name, file_path, 'has no' if not untagged else 'has')

    if untagged:
        _logger.debug("Parsing version file")
        with open(version_file, 'r') as f:
            versions = yaml.load(f)
        _logger.debug("Computing untagged summary and preparing flow arguments")
        result['_untagged_summary'] = _create_untagged_summary(result['untagged'], versions)
        result['flow_arguments'] = _create_flow_args(
            [entry['name'] for entry in result['untagged'].values()],
            versions
        )
        result['flow_arguments_count'] = len(result['flow_arguments'])
        result['untagged_count'] = len(result['untagged'])

    if tagged:
        result['tagged_count'] = len(result['tagged'])

    return result


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option('--verbose', '-v', is_flag=True,
              help='Turn on debug messages.')
@click.option('--pretty/--no-pretty', default=True,
              help='Turn on/off pretty formatted output.')
@click.option('--tagged/--no-tagged', default=True,
              help='Turn on/off collecting tagged projects.')
@click.option('--untagged/--no-untagged', default=True,
              help='Turn on/off collecting untagged projects.')
@click.option('--output', type=click.File(mode='w'))
@click.option('--version-file', type=click.Path(file_okay=True, exists=True),
              help='Path to version file containing package version information.')
def main(path, verbose=False, pretty=True, output=None, tagged=True, untagged=True, version_file=None):
    # pylint: disable=too-many-arguments
    """Check maven tagged and untagged packages."""
    if verbose:
        _logger.setLevel(logging.DEBUG)

    if untagged and not version_file:
        raise ValueError("No version file provided to suggest analysis parameters.")

    result = check_why_missing(path, tagged, untagged, version_file)

    json_kwargs = {}
    if pretty:
        json_kwargs = {
            'sort_keys': True,
            'separators': (',', ': '),
            'indent': 2
        }

    _logger.debug("Dumping result to '%s'", (output or sys.stdout).name)
    json.dump(result, output or sys.stdout, **json_kwargs)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
