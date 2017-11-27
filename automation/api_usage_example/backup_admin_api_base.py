from api_base import ApiBase

class BackupAdminApiBase(ApiBase):

    def __init__(self, base_url, api_user, api_key):
        ApiBase.__init__(self, base_url, api_user, api_key)


    def get_all_mongo_snapshot_stores(self, assignable_only=False):
        url = "%s/admin/backup/snapshot/mongoConfigs?assignableOnly=%s" % (self.base_url, assignable_only)
        return self.get(url)

    def get_all_s3_snapshot_stores(self, assignable_only=False):
        url = "%s/admin/backup/snapshot/s3Configs?assignableOnly=%s" % (self.base_url, assignable_only)
        return self.get(url)

    def get_all_filesystem_snapshot_stores(self, assignable_only=False):
        url = "%s/admin/backup/snapshot/fileSystemConfigs?assignableOnly=%s" % (self.base_url, assignable_only)
        return self.get(url)

    def get_all_daemons(self):
        url = "%s/admin/backup/daemon/configs" % (self.base_url)
        return self.get(url)

    def create_daemon(self, machine_name, machine_head_directory):
        url = "%s/admin/backup/daemon/configs" % (self.base_url)
        daemon = {
          "assignmentEnabled" : True,
          "backupJobsEnabled" : True,
          "configured" : True,
          "garbageCollectionEnabled" : True,
          "headDiskType" : "some",
          "id" : "5991a422ad5df350005dd062",
          "labels" : [ "l1", "l2" ],
          "machine" : {
            "headRootDirectory" : machine_head_directory,
            "machine" : machine_name
          },
          "numWorkers" : 4,
          "resourceUsageEnabled" : True,
          "restoreJobsEnabled" : True,
          "restoreQueryableJobsEnabled" : True
        }
        return self.post(url, daemon)

    def create_mongo_snapshot_store(self, hostname, port):
        url = "%s/admin/backup/snapshot/mongoConfigs" % (self.base_url)
        mongo_snapshot_store = {
          "assignmentEnabled" : True,
          "encryptedCredentials" : False,
          "id" : "blockstore3",
          "labels" : [ "l1", "l2" ],
          "loadFactor" : 2,
          "maxCapacityGB" : 8,
          "uri" : "mongodb://%s:%s" % (hostname, port),
          "ssl" : False,
          "usedSize" : 223
        }
        return self.post(url, mongo_snapshot_store)
