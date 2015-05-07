
import argparse
import json
import logging
import pprint
import requests
import time

from requests.auth import HTTPDigestAuth

logging.basicConfig(
    level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')


class Step:

    def __init__(self, config_path, description):
        self.config_path = config_path
        self.description = description

steps = [
    Step("configs/api_0_clean.json",
         "Start with empty automation config"),

    Step("configs/api_1_define_versions.json",
         "Setup desired MongoDB versions"),

    Step("configs/api_2_install_other_agents.json",
         "Install Backup and Monitoring agents"),

    Step("configs/api_3_create_replica_set.json",
         "Create a Replica Set"),

    Step("configs/api_4_upgrade_replica_set.json",
         "Upgrade the Replica Set"),

    Step("configs/api_5_replica_set_to_cluster.json",
         "Convert Replica Set to Cluster"),

    Step("configs/api_6_enable_auth.json",
         "Enable Authentication"),
]


class TestAutomationApi:

    def __init__(self, base_url, machine_hostname, group_id, api_user, api_key, step_over):
        self.base_url = base_url + "/api/public/v1.0"
        self.machine_hostname = machine_hostname
        self.group_id = group_id
        self.api_user = api_user
        self.api_key = api_key
        self.step_over = step_over

    def clean(self):
        self.run_step(steps[0], 0, False)

    def run(self):
        for (i, step) in enumerate(steps):
            self.run_step(step, i)

    def run_step(self, step, stepNumber, wait=True):
        step_info = self.build_step_info(step, stepNumber)
        logging.info("Running %s..." % step_info)
        self.post_automation_config(step.config_path)
        if wait:
            self.wait_for_goal_state()
        if self.step_over:
            raw_input("\nFinished %s. Hit enter to continue...\n" % step_info)

    def build_step_info(self, step, stepNumber):
        return "step {} ({})".format(stepNumber, step.description)

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
                time.sleep(1)
            else:
                logging.info(
                    "All processes in Goal State. GoalVersionAchieved: %s" % goal_version)
                break

            count += 1

    def get_automation_config(self):
        url = "%s/groups/%s/automationConfig" % (self.base_url, self.group_id)
        return self.get(url)

    def get_automation_status(self):
        url = "%s/groups/%s/automationStatus" % (self.base_url, self.group_id)
        return self.get(url)

    def post_automation_config(self, file_name):
        url = "%s/groups/%s/automationConfig" % (self.base_url, self.group_id)
        json_body = self.load_config(file_name)
        return self.put(url, json_body)

    def get(self, url):
        logging.info("Executing GET: %s" % url)
        r = requests.get(url, auth=HTTPDigestAuth(self.api_user, self.api_key))
        self.check_response(r)
        logging.debug("%s" % pprint.pformat(r.json()))
        return r.json()

    def put(self, url, json_body):
        logging.info("Executing PUT: %s" % url)
        headers = {'content-type': 'application/json'}
        r = requests.put(
            url,
            auth=HTTPDigestAuth(self.api_user, self.api_key),
            data=json.dumps(json_body),
            headers=headers
        )
        self.check_response(r)
        logging.debug("%s" % pprint.pformat(r.json()))

        return r

    def check_response(self, r):
        if r.status_code != requests.codes.ok:
            logging.error("Response Error Code: %s Detail: %s" %
                          (r.status_code, r.json()['detail']))
            raise ValueError(r.json()['detail'])

    def load_config(self, file_name):
        data = self.load_json(file_name)
        # Replace the MACHINE_HOSTNAME placeholders in the example configs
        # with real value.
        self.replace_agent_hostnames(data)
        self.replace_process_hostnames(data)
        return data

    def load_json(self, file_name):
        with open(file_name) as data_file:
            data = json.load(data_file)
        return data

    def replace_agent_hostnames(self, data):
        for index, mv in enumerate(data['monitoringVersions']):
            data['monitoringVersions'][index][
                'hostname'] = self.machine_hostname

        for index, bv in enumerate(data['backupVersions']):
            data['backupVersions'][index]['hostname'] = self.machine_hostname

    def replace_process_hostnames(self, data):
        for index, mv in enumerate(data['processes']):
            data['processes'][index]['hostname'] = self.machine_hostname
            if data['processes'][index].get('alias'):
                data['processes'][index]['alias'] = self.machine_hostname

if __name__ == '__main__':

    '''python test_automation_api.py https://mms.mongodb.com saturn-0.automabot.6351.mongodbdns.com 554ba356e4b09f341d2f3f5e botbotson@sky.net 51277c3a-51c0-42fb-9d2c-07cd4b0d1608'''
    parser = argparse.ArgumentParser(description='Automation API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('machine_hostname', help="Machine Hostname")
    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")
    parser.add_argument('--clean', action='store_true', required=False)
    parser.add_argument('--step', action='store_true', required=False)
    args = parser.parse_args()

    test = TestAutomationApi(
        args.base_url, args.machine_hostname, args.group_id, args.api_user, args.api_key, args.step)
    if args.clean:
        test.clean()
    else:
        test.run()
