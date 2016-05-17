import argparse
import logging
import time

from automation_api_base import AutomationApiBase
from backup_api_base import BackupApiBase

logging.basicConfig(
    level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

class TestRestoreFromBackupReplicaSet:

    def __init__(self, base_url, machine_hostname, group_id, api_user, api_key, step_over):
        self.automation_api = AutomationApiBase(base_url, machine_hostname, group_id, api_user, api_key)
        self.backup_api = BackupApiBase(base_url, group_id, api_user, api_key)
        self.step_over = step_over

    def run(self):
        config_file = 'configs/api_3_create_replica_set.json'
        logging.info("Setting up a simple replica set")
        self.automation_api.post_automation_config(config_file)
        logging.info("Waiting for goal state")
        self.automation_api.wait_for_goal_state()
        logging.info("Enabling backup and waiting for restore link to be ready")
        restore_link = self.get_restore_link()

        automation_config = self.automation_api.load_config(config_file)
        for process in automation_config['processes']:
            process['backupRestoreUrl'] = restore_link

        logging.info("Initializing restore")
        self.automation_api.post_automation_config(automation_config)
        logging.info("Waiting for goal state")
        self.automation_api.wait_for_goal_state()

        logging.info("Removing restore URLs from config")
        self.automation_api.post_automation_config(config_file)
        logging.info("Waiting for goal state")
        self.automation_api.wait_for_goal_state()

    def get_restore_link(self):
        replica_set_name = 'blue'
        self.backup_api.start_backup_replica_set(replica_set_name)

        snapshot_id = None
        while True:
            snapshots = self.backup_api.get_snapshots_replica_set(replica_set_name)
            if snapshots:
                snapshot_id =  snapshots[0]['id']
                break

            logging.info("Snapshot not yet complete. Sleeping for 30 seconds")
            time.sleep(30)

        restore_job = self.backup_api.request_restore_http_replica_set('blue', snapshot_id, 6, 1)
        restore_link = None

        while True:
            restore_job_status = self.backup_api.get_restore_job_result_replica_set(replica_set_name, restore_job['id'])
            delivery_status = restore_job_status['delivery']['statusName']
            if delivery_status == 'READY':
                restore_link = restore_job_status['delivery']['url']
                break

            logging.info("Restore files not yet ready. Sleeping for 30 seconds")
            time.sleep(5)

        return restore_link

    def build_step_info(self, step, stepNumber):
        return "step {} ({})".format(stepNumber, step.description)


if __name__ == '__main__':

    # python test_restore_from_backup_replica_set.py http://mms.example.com:8080 mongo-01.example.com 54b5e4df9436322466a89a3e apple@johnandcailin.com 04e2aa59-d410-446f-aba9-70cf37010b7c
    parser = argparse.ArgumentParser(description='Automation API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('machine_hostname', help="Agent Hostname")
    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")
    parser.add_argument('--step', action='store_true', required=False)
    args = parser.parse_args()

    test = TestRestoreFromBackupReplicaSet(args.base_url, args.machine_hostname, args.group_id, args.api_user, args.api_key, args.step)
    test.run()

