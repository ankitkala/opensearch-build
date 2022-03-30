import os
import subprocess
import json
from system.working_directory import WorkingDirectory


class PerfTestSuite:
    """
    Represents a performance test suite. This class runs rally test on the deployed cluster with the provided IP.
    """

    def __init__(self, bundle_manifest, endpoint, security, current_workspace, args, owner="opensearch-devops", scenario="DEFAULT"):
        print(current_workspace)
        self.manifest = bundle_manifest
        self.work_dir = current_workspace + "/mensor/"
        self.endpoint = endpoint
        self.security = security
        self.current_workspace = current_workspace
        self.args = args
        endpoint_arg = ""
        # Pass the cluster endpoints with -t for multi-cluster usecases(e.g. cross-cluster-replication)
        if type(self.endpoint) is dict:
            endpoint_arg = "-t '{}'".format(json.dumps(self.endpoint))
        else:
            endpoint_arg = "-e {self.endpoint}"
        self.command = (
            f"pipenv run python test_config.py {endpoint_arg} -b {self.manifest.build.id}"
            f" -a {self.manifest.build.architecture} -p {self.current_workspace}"
            f" --workload {self.args.workload} --workload-options '{self.args.workload_options}'"
            f" --warmup-iters {self.args.warmup_iters} --test-iters {self.args.test_iters}"
            f" --scenario-type {scenario} --owner {owner}"
        )

    def execute(self):
        try:
            with WorkingDirectory(self.work_dir):
                dir = os.getcwd()
                subprocess.check_call("python3 -m pipenv install", cwd=dir, shell=True)
                subprocess.check_call("pipenv install", cwd=dir, shell=True)

                if self.security:
                    subprocess.check_call(f"{self.command} -s", cwd=dir, shell=True)
                else:
                    subprocess.check_call(f"{self.command}", cwd=dir, shell=True)
        finally:
            os.chdir(self.current_workspace)
