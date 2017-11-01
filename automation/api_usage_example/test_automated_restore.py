import argparse
import logging
import time

from automation_api_base import AutomationApiBase
from backup_api_base import BackupApiBase

logging.basicConfig(
    level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

class TestRestoreFromBackupReplicaSet:

    def __init__(self, base_url, api_user, api_key, group_id, cluster_name, target_group_id, target_cluster_name):
        self.backup_api = BackupApiBase(base_url, group_id, api_user, api_key)
        self.backup_api_target = BackupApiBase(base_url, target_group_id, api_user, api_key)
        self.cluster_name = cluster_name
        self.target_group_id = target_group_id
        self.target_cluster_name = target_cluster_name

    def run(self):
        cluster_id = self.backup_api.get_cluster_id_from_cluster_name(self.cluster_name)
        target_cluster_id = self.backup_api_target.get_cluster_id_from_cluster_name(self.target_cluster_name)
        snapshots = self.backup_api._get_snapshots(cluster_id)
        snapshot_id = snapshots[0]['id']
        self.backup_api.request_automated_restore(cluster_id, snapshot_id, self.target_group_id, target_cluster_id)

if __name__ == '__main__':

    # python test_automated_restore.py http://opsmanager.example.com john@xmple.com f0f88855-d211-4d4f-9461-e53b0822b505 59f7b8f954559e0cc0146094 red 59f77d0254559e0cc0138ba0 blue
    parser = argparse.ArgumentParser(description='Automated Restore API Demo')
    parser.add_argument('base_url', help="Base URL")

    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")

    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('cluster_name', help="Cluster Name")
    parser.add_argument('target_group_id', help="Target Group ID")
    parser.add_argument('target_cluster_name', help="Target Cluster Name")

    args = parser.parse_args()

    test = TestRestoreFromBackupReplicaSet(
        args.base_url,
        args.api_user,
        args.api_key,
        args.group_id,
        args.cluster_name,
        args.target_group_id,
        args.target_cluster_name)

    test.run()

