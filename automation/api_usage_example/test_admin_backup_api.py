import argparse
import logging
import time

from backup_admin_api_base import BackupAdminApiBase

logging.basicConfig(
    level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

class TestAdminBackupApi:

    def __init__(self, base_url, api_user, api_key):
        self.backup_admin_api = BackupAdminApiBase(base_url, api_user, api_key)

    def run(self):
        logging.info("All Mongo Snapshot Stores")
        self.backup_admin_api.get_all_mongo_snapshot_stores()
        logging.info("All S3 Snapshot Stores")
        self.backup_admin_api.get_all_s3_snapshot_stores()
        logging.info("All Filesystem Snapshot Stores")
        self.backup_admin_api.get_all_filesystem_snapshot_stores()
        logging.info("All Daemons")
        self.backup_admin_api.get_all_daemons()
        #logging.info("Create A Daemon")
        #self.backup_admin_api.create_daemon("ip-10-0-1-142", "/backup/")
        logging.info("Create a Mongo Snapshot Store")
        self.backup_admin_api.create_mongo_snapshot_store("ip-10-0-1-142", 27018)

if __name__ == '__main__':

    # python test_admin_backup_api.py http://opsmanager.example.com john@xmple.com f0f88855-d211-4d4f-9461-e53b0822b505 59f7b8f954559e0cc0146094
    parser = argparse.ArgumentParser(description='Automated Restore API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")

    args = parser.parse_args()

    test = TestAdminBackupApi(
        args.base_url,
        args.api_user,
        args.api_key)

    test.run()

