from api_base import ApiBase

class BackupApiBase(ApiBase):

    def __init__(self, base_url, group_id, api_user, api_key):
        ApiBase.__init__(self, base_url, group_id, api_user, api_key)

    def get_restore_job_result_replica_set(self, replica_set_name, job_id):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)
        return self._get_restore_job_result(cluster_id, job_id=job_id)

    def get_restore_job_result_cluster(self, cluster_name, batch_id):
        cluster_id = self._get_cluster_id_from_cluster_name(cluster_name)
        return self._get_restore_job_result(cluster_id, batch_id=batch_id)

    def _get_restore_job_result(self, cluster_id, job_id=None, batch_id=None):
        url = "%s/groups/%s/clusters/%s/restoreJobs" % (self.base_url, self.group_id, cluster_id)

        if job_id:
            url = "%s/%s" % (url, job_id)

        if batch_id:
            url = "%s?batchId=%s" % (url, batch_id)

        return self.get(url)

    def request_restore_http_replica_set(self, replica_set_name, snapshot_id, max_downloads, expiration_hours):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)
        return self._request_restore(cluster_id, snapshot_id, max_downloads, expiration_hours)

    def request_restore_http_cluster(self, cluster_name, snapshot_id, max_downloads, expiration_hours):
        cluster_id = self._get_cluster_id_from_cluster_name(cluster_name)
        return self._request_restore(cluster_id, snapshot_id, max_downloads, expiration_hours)

    def _request_restore(self, cluster_id, snapshot_id, max_downloads, expiration_hours):
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
        return self._get_snapshots(cluster_id)

    def get_snapshots_cluster(self, cluster_name):
        cluster_id = self._get_cluster_id_from_cluster_name(cluster_name)
        return self._get_snapshots(cluster_id)

    def _get_snapshots(self, cluster_id):
        url = "%s/groups/%s/clusters/%s/snapshots" % (self.base_url, self.group_id, cluster_id)
        response = self.get(url)
        return response['results']

    def start_backup_replica_set(self, replica_set_name, storage_engine=None):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)
        return self._start_backup(cluster_id, storage_engine)

    def start_backup_cluster(self, cluster_name, storage_engine=None):
        cluster_id = self._get_cluster_id_from_cluster_name(cluster_name)
        return self._start_backup(cluster_id, storage_engine)

    def _start_backup(self, cluster_id, storage_engine):

        status = self._get_backup_configuration(cluster_id)
        if status['statusName'] == 'STARTED':
            return

        url = "%s/groups/%s/backupConfigs/%s" % (self.base_url, self.group_id, cluster_id)
        json_body = {
            'statusName': 'STARTED',
            "syncSource": "SECONDARY"
        }

        if storage_engine:
            json_body['storageEngineName'] = storage_engine

        self.patch(url, json_body)

    def get_backup_configuration_replica_set(self, replica_set_name):
        cluster_id = self._get_cluster_id_from_replica_set(replica_set_name)
        return self._get_backup_configuration(cluster_id)

    def get_backup_configuration_cluster(self, cluster_name):
        cluster_id = self._get_cluster_id_from_cluster_name(cluster_name)
        return self._get_backup_configuration(cluster_id)

    def _get_backup_configuration(self, cluster_id):
        url = "%s/groups/%s/backupConfigs/%s" % (self.base_url, self.group_id, cluster_id)
        return self.get(url)

    def _get_cluster_id_from_replica_set(self, replica_set_name):
        url = "%s/groups/%s/clusters" % (self.base_url, self.group_id)
        response = self.get(url)
        for cluster in response['results']:
            if cluster['replicaSetName'] == replica_set_name:
                return cluster['id']

        return None

    def _get_cluster_id_from_cluster_name(self, cluster_name):
        url = "%s/groups/%s/clusters" % (self.base_url, self.group_id)
        response = self.get(url)
        for cluster in response['results']:
            if cluster['clusterName'] == cluster_name and cluster['typeName'] == 'SHARDED_REPLICA_SET':
                return cluster['id']

        return None

    def get_replica_set_from_cluster_id(self, cluster_id):
        url = "%s/groups/%s/clusters" % (self.base_url, self.group_id)
        response = self.get(url)
        for cluster in response['results']:
            if cluster['id'] == cluster_id and cluster.get('replicaSetName'):
                return cluster['replicaSetName']

        return None

