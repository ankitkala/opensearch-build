
import os
from contextlib import contextmanager

from test_workflow.perf_test.perf_test_cluster import PerfTestCluster


class PerfMultiNodeCluster(PerfTestCluster):
    """
    Represents a performance test cluster. This class deploys the opensearch bundle with CDK. Supports both single
    and multi-node clusters
    """
    def __init__(self, bundle_manifest, config, stack_name, cluster_config, current_workspace):
        assert not cluster_config.is_single_node_cluster(), "Cluster is a single node configuration"
        work_dir = os.path.join(current_workspace, "opensearch-cluster", "cdk", "multi-node")
        super().__init__(bundle_manifest, config, stack_name, cluster_config, current_workspace, work_dir)

    def create_endpoint(self, cdk_output):
        scheme = "https://" if self.cluster_config.security else "http://"
        host = cdk_output[self.stack_name]["LoadBalancerEndpoint"]
        self.is_endpoint_public = True
        if host is not None:
            self.endpoint = host
            self.cluster_endpoint_with_port = "".join([scheme, host, ":", str(self.port)])

    def setup_cdk_params(self, config):
        return {
            "url": self.manifest.build.location,
            "security_group_id": config["Constants"]["SecurityGroupId"],
            "vpc_id": config["Constants"]["VpcId"],
            "account_id": config["Constants"]["AccountId"],
            "region": config["Constants"]["Region"],
            "cluster_stack_name": self.stack_name,
            "security": "enable" if self.cluster_config.security else "disable",
            "architecture": self.manifest.build.architecture,
            "master_node_count": int(self.cluster_config.master_nodes),
            "data_node_count": int(self.cluster_config.data_nodes),
            "ingest_node_count": int(self.cluster_config.ingest_nodes),
            "client_node_count": int(self.cluster_config.client_nodes)
        }

    @classmethod
    @contextmanager
    def create(cls, *args):
        """
        Set up the cluster. When this method returns, the cluster must be available to take requests.
        Throws ClusterCreationException if the cluster could not start for some reason. If this exception is thrown, the caller does not need to call "destroy".
        """
        cluster = cls(*args)

        try:
            cluster.start()
            yield cluster
        finally:
            cluster.terminate()
