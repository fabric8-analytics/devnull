import json
import sys
import os
import subprocess
import daiquiri
import logging

daiquiri.setup(level=logging.INFO)
_logger = daiquiri.getLogger(__name__)

os.environ['MERCATOR_JAVA_RESOLVE_POMS'] = "true"
ecosystem = "maven"


def setup():
    if not os.path.exists('./manifests-{}'.format(ecosystem)):
        os.makedirs('./manifests-{}'.format(ecosystem))


def manifest_dep_collection(min_part_count=1, max_part_count=2):
    for i in range(min_part_count, max_part_count):
        manifests_dependencies = {}
        manifest_list = {}
        with open(os.path.join('./manifests-EPV-{}'.format(ecosystem), 'manifests-{}-part-{}.json'.format(ecosystem, i))) as f:
            manifest_list = json.load(f)
        for repo_path in manifest_list.keys():
            all_required_dep = {}
            pom_content = manifest_list[repo_path]
            try:
                with open("pom.xml", "w") as f:
                    f.write(pom_content)
                mercator_result = subprocess.check_output(
                    ["mercator pom.xml"], env=dict(os.environ), shell=True)
                dependencies = json.loads(mercator_result).get("items", [{}])[0].get(
                    "result", {}).get("pom.xml", {}).get("dependencies", {})
                all_required_dep = dependencies.get("compile", {})
                all_required_dep.update(dependencies.get("run", {}))
                all_required_dep.update(dependencies.get("provided", {}))
                all_required_dep = all_required_dep.keys()
                if all_required_dep:
                    package_list = [get_pruned_name(
                        package) for package in all_required_dep]
                    manifests_dependencies[repo_path] = package_list
                else:
                    manifests_dependencies[repo_path] = []
                _logger.info(
                    "Successfully resolving dependencies for {}".format(repo_path))
            except Exception as e:
                _logger.error(
                    "Could not parse dependencies for {}".format(repo_path))
                continue
        with open(os.path.join('./manifests-{}'.format(ecosystem), 'manifests-{}-part-{}.json'.format(ecosystem, i)), "w") as f:
            json.dump(manifests_dependencies, f, indent=True)


def get_pruned_name(name):
    return ':'.join(name.split(":")[:2])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        max_part_count = 2
        min_part_count = 1
    else:
        min_part_count = int(sys.argv[1])
        max_part_count = int(sys.argv[2])
    setup()
    manifest_dep_collection(min_part_count, max_part_count)
