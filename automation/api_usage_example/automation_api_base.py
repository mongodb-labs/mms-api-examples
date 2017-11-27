import json
import logging
import time

from api_base import ApiBase

class AutomationApiBase(ApiBase):

    def __init__(self, base_url, machine_hostname, group_id, api_user, api_key):
        ApiBase.__init__(self, base_url, api_user, api_key)
        self.group_id = group_id
        self.machine_hostname = machine_hostname

    def clean(self):
        self.post_automation_config("configs/api_0_clean.json")

    def wait_for_goal_state(self):

        count = 0
        while True:
            continue_to_wait = False
            status = self.get_automation_status()
            goal_version = status['goalVersion']

            for process in status['processes']:
                logging.info("Round: %s GoalVersion: %s Process: %s (%s) LastVersionAchieved: %s Plan: %s "
                     % (count, goal_version, process['name'], process['hostname'], process['lastGoalVersionAchieved'], process['plan']))

                if process['lastGoalVersionAchieved'] < goal_version:
                    continue_to_wait = True

            if continue_to_wait:
                time.sleep(5)
            else:
                logging.info("All processes in Goal State. GoalVersionAchieved: %s" % goal_version)
                break

            count += 1

    def get_automation_config(self):
        url = "%s/groups/%s/automationConfig" % (self.base_url, self.group_id)
        return self.get(url)

    def get_automation_status(self):
        url = "%s/groups/%s/automationStatus" % (self.base_url, self.group_id)
        return self.get(url)

    def post_monitoring_agent_config(self, file_name):
        url = "%s/groups/%s/automationConfig/monitoringAgentConfig" % (self.base_url, self.group_id)
        json_body = self.load_config(file_name)
        return self.put(url, json_body)

    def post_backup_agent_config(self, file_name):
        url = "%s/groups/%s/automationConfig/backupAgentConfig" % (self.base_url, self.group_id)
        json_body = self.load_config(file_name)
        return self.put(url, json_body)

    def post_automation_config(self, file_name_or_json):
        url = "%s/groups/%s/automationConfig" % (self.base_url, self.group_id)
        if isinstance(file_name_or_json, basestring):
            json_body = self.load_config(file_name_or_json)
        else:
            json_body = file_name_or_json

        return self.put(url, json_body)

    def load_config(self, file_name):
        data = self.load_json(file_name)

        # Replace the Machine_hostname placeholders in the example configs
        # with real value.
        self.replace_machine_hostnames(data)
        self.replace_process_hostnames(data)
        self.replace_kerberos_principals(data)
        return data

    def load_json(self, file_name):
        with open(file_name) as data_file:
            data = json.load(data_file)
        return data

    def replace_machine_hostnames(self, data):
        if 'monitoringVersions' in data:
            for index, mv in enumerate(data['monitoringVersions']):
                data['monitoringVersions'][index]['hostname'] = self.machine_hostname

        if 'backupVersions' in data:
            for index, bv in enumerate(data['backupVersions']):
                data['backupVersions'][index]['hostname'] = self.machine_hostname

    def replace_process_hostnames(self, data):
        if 'processes' in data:
            for index, mv in enumerate(data['processes']):
                data['processes'][index]['hostname'] = self.machine_hostname
                if data['processes'][index].get('alias'):
                    data['processes'][index]['alias'] = self.machine_hostname

    def replace_kerberos_principals(self, data):
        if 'kerberosPrincipal' in data:
            data['kerberosPrincipal'] = data['kerberosPrincipal'].replace('Machine_hostname', self.machine_hostname)

        if 'auth' in data:
            if 'autoUser' in data['auth']:
                data['auth']['autoUser'] = data['auth']['autoUser'].replace('Machine_hostname', self.machine_hostname)

            for index, user in enumerate(data['auth']['usersWanted']):
                data['auth']['usersWanted'][index]['user'] = \
                    data['auth']['usersWanted'][index]['user'].replace('Machine_hostname', self.machine_hostname)
