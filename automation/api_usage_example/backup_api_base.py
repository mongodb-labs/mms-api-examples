from api_base import ApiBase

class BackupApiBase(ApiBase):

    def __init__(self, base_url, group_id, api_user, api_key):
        ApiBase.__init__(self, base_url, group_id, api_user, api_key)

    def get_restore_job_result(self, replica_set_name, job_id):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)
        url = "%s/groups/%s/clusters/%s/restoreJobs/%s" % (self.base_url, self.group_id, cluster_id, job_id)
        return self.get(url)

    def request_restore_http_replica_set(self, replica_set_name, snapshot_id, max_downloads, expiration_hours):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)
        url = "%s/groups/%s/clusters/%s/restoreJobs" % (self.base_url, self.group_id, cluster_id)
        json_body = {
            'snapshotId': snapshot_id,
            'delivery': {
                'methodName': 'HTTP',
                'maxDownloads': max_downloads,
                'expirationHours': expiration_hours
            }
        }

        response = self.post(url, json_body)
        return response['results'][0]

    def get_snapshots_replica_set(self, replica_set_name):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)

        url = "%s/groups/%s/clusters/%s/snapshots" % (self.base_url, self.group_id, cluster_id)
        response = self.get(url)
        return response['results']

    def start_backup_replica_set(self, replica_set_name):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)

        status = self.get_backup_configuration_replica_set(replica_set_name)
        if status['statusName'] == 'STARTED':
            return

        url = "%s/groups/%s/backupConfigs/%s" % (self.base_url, self.group_id, cluster_id)
        json_body = {
            'statusName': 'STARTED'
        }
        self.patch(url, json_body)

    def get_backup_configuration_replica_set(self, replica_set_name):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)
        url = "%s/groups/%s/backupConfigs/%s" % (self.base_url, self.group_id, cluster_id)
        return self.get(url)

    def _get_cluster_id_from_replica_set(self, replica_set_name):
        url = "%s/groups/%s/clusters" % (self.base_url, self.group_id)
        response = self.get(url)
        for cluster in response['results']:
            if cluster['replicaSetName'] == replica_set_name:
                return cluster['id']

        return None

