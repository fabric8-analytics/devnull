import json
import sys
import os
import subprocess
import daiquiri
import logging

daiquiri.setup(level=logging.INFO)
_logger = daiquiri.getLogger(__name__)

ecosystem = "maven"
unique_packages = set()


def package_collection():
    with open("manifest-{}.json".format(ecosystem), "r")as f:
        manifest_data = json.load(f)
    manifest_data = manifest_data[0]['package_list']

    for each_dependency_list in manifest_data:
        for each_package in each_dependency_list:
            unique_packages.add(each_package)
    _logger.info("Total unique packages found {}".format(len(unique_packages)))


def save_unique_packages():
    data_list = {'ecosystem': ecosystem,
                 'unique_packages': list(unique_packages)}
    data = [data_list]
    with open("unique_packages-{}.json".format(ecosystem), "w") as f:
        json.dump(data, f, indent=True)


if __name__ == "__main__":
    package_collection()
    save_unique_packages()
