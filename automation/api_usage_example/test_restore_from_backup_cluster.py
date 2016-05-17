import argparse
import logging
import time

from automation_api_base import AutomationApiBase
from backup_api_base import BackupApiBase

logging.basicConfig(
    level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

class TestRestoreFromBackupCluster:

    def __init__(self, base_url, machine_hostname, group_id, api_user, api_key, step_over):
        self.automation_api = AutomationApiBase(base_url, machine_hostname, group_id, api_user, api_key)
        self.backup_api = BackupApiBase(base_url, group_id, api_user, api_key)
        self.step_over = step_over

    def run(self):
        config_file = 'configs/mongo32_csrs_cluster.json'
        logging.info("Setting up a MongoDB 3.2.5 CSRS cluster")
        self.automation_api.post_automation_config(config_file)
        logging.info("Waiting for goal state")
        self.automation_api.wait_for_goal_state()

        logging.info("Enabling backup and waiting for restore link to be ready")
        restore_links = self.get_restore_links()

        automation_config = self.automation_api.load_config(config_file)
        # For each non-mongos process, add the appropriate restoreUrl
        for process in automation_config['processes']:
            if process['processType'] == 'mongod':
                process['backupRestoreUrl'] = restore_links[process['args2_6']['replication']['replSetName']]

        logging.info("Initializing restore")
        self.automation_api.post_automation_config(automation_config)
        logging.info("Waiting for goal state")
        self.automation_api.wait_for_goal_state()

        logging.info("Removing restore URLs from config")
        self.automation_api.post_automation_config(config_file)
        logging.info("Waiting for goal state")
        self.automation_api.wait_for_goal_state()

    def get_restore_links(self):
        logging.info("Sleeping for 60 seconds to wait for monitoring agent data")
        time.sleep(60)

        cluster_name = 'blueCluster'
        self.backup_api.start_backup_cluster(cluster_name, "WIRED_TIGER")

        # Wait for a snapshot to be taken for all components in the cluster
        snapshot_id = None
        while True:
            snapshots = self.backup_api.get_snapshots_cluster(cluster_name)
            # There will be two parts, one for the shard, and one for the config server replica set
            if snapshots and len(snapshots[0].get('parts',[])) == 2:
                snapshot_id = snapshots[0]['id']
                break

            logging.info("Snapshot not yet complete. Sleeping for 30 seconds")
            time.sleep(30)

        # Request a restore for this snapshot.  Be sure to specify an adequate number of
        # downloads for each snapshot, and a generous expriation time.  The Automation Agents will
        # need to download the snapshot _once per mongod process_.  In this case, a value of 3 should
        # be sufficient (3 processes in each replica set), but we'll use 6, just in case there are any
        # network glitches or other transient failures

        max_downloads = 6
        expiration_hours = 24
        restore_job = self.backup_api.request_restore_http_cluster(
            cluster_name,
            snapshot_id,
            max_downloads,
            expiration_hours)
        batch_id = restore_job['batchId']
        restore_links = {}

        while True:
            restore_job_statuses = self.backup_api.get_restore_job_result_cluster(cluster_name, batch_id)

            # Wait for a restore job to be created for both components of the cluster
            if len(restore_links) == 2:
                break

            logging.info("Restore files not yet ready. Sleeping for 15 seconds")
            time.sleep(15)

            # And then wait for the deliveryUrls to be complete for both components
            for restore_job_status in restore_job_statuses['results']:
                delivery_status = restore_job_status['delivery']['statusName']
                if delivery_status == 'READY':
                    restore_link = restore_job_status['delivery']['url']
                    cluster_id = restore_job_status['clusterId']
                    # Keep a dictionary of the restore links for each component in the cluster
                    # Identify the component by it's replica set id
                    restore_links[self.backup_api.get_replica_set_from_cluster_id(cluster_id)] = restore_link

        return restore_links


if __name__ == '__main__':

    # USAGE:
    # python test_restore_from_backup_cluster.py CLOUD_OR_OPS_MANAGER_URL HOSTNAME GROUP_ID USER_NAME USER_API_KEY
    # python test_restore_from_backup_cluster.py http://mms.example.com:8080 mongo-01.example.com 54b5e4df9436322466a89a3e apple@johnandcailin.com 04e2aa59-d410-446f-aba9-70cf37010b7c
    parser = argparse.ArgumentParser(description='Automation API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('machine_hostname', help="Agent Hostname")
    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")
    args = parser.parse_args()

    test = TestRestoreFromBackupCluster(args.base_url, args.machine_hostname, args.group_id, args.api_user, args.api_key, args.step)
    test.run()

