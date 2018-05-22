import json
import sys
import os
import subprocess
import daiquiri
import logging
from bs4 import BeautifulSoup

daiquiri.setup(level=logging.INFO)
_logger = daiquiri.getLogger(__name__)

ecosystem = "maven"
list_of_manifest = []


def manifest_dep_collection(min_part_count=1, max_part_count=2):
    no_dep = 0
    error_pom = 0
    for i in range(min_part_count, max_part_count):
        with open(os.path.join('./manifests-EPV-{}'.format(ecosystem), 'manifests-{}-part-{}.json'.format(ecosystem, i))) as manifest_json:
            manifest_list = json.load(manifest_json)
        for repo_path in manifest_list.keys():
            try:
                pom_content = manifest_list[repo_path]
                soup = BeautifulSoup(pom_content, "xml")
                dependency_list = soup.find_all('dependency')
                if dependency_list is None:
                    continue
                dependencies = []
                for each_dependency in dependency_list:
                    scope = each_dependency.find('scope')
                    if scope is not None and scope.contents[0] == "test":
                        continue
                    else:
                        groupId = each_dependency.find('groupId')
                        artifactId = each_dependency.find('artifactId')
                        condition1 = groupId is not None and groupId.contents[
                            0][0].isalnum()
                        condition2 = artifactId is not None and artifactId.contents[
                            0][0].isalnum()
                        if condition1 and condition2:
                            dependencies.append(
                                groupId.contents[0] + ":" + artifactId.contents[0])
                if dependencies:
                    list_of_manifest.append(dependencies)
                    _logger.info(
                        "Processed successfully repo: {}".format(repo_path))
                else:
                    _logger.info(
                        "No deps found for repo: {}".format(repo_path))
                    no_dep += 1
            except Exception as e:
                _logger.error("File not a proper pom {}".format(repo_path))
                error_pom += 1
                continue
    print("No deps found for: {}".format(no_dep))
    print("Error poms found in: {}".format(error_pom))


def final_length():
    data = {"ecosystem": "maven", "package_list": list_of_manifest}
    data_file = [data]
    with open("manifest-{}.json".format(ecosystem), "w") as f:
        json.dump(data_file, f, indent=True)
    print("Final len of manifest.json: {}".format(len(list_of_manifest)))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        min_part_count = 1
        max_part_count = 2
    else:
        min_part_count = int(sys.argv[1])
        max_part_count = int(sys.argv[2])
    manifest_dep_collection(min_part_count, max_part_count)
    final_length()
