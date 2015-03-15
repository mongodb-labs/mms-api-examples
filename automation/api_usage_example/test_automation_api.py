import argparse
import logging

from automation_api_base import AutomationApiBase

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

class TestAutomationApi(AutomationApiBase):

    def __init__(self, base_url, machine_hostname, group_id, api_user, api_key, step_over):
        AutomationApiBase.__init__(self, base_url, machine_hostname, group_id, api_user, api_key)
        self.step_over = step_over

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


if __name__ == '__main__':

    # python test_automation_api.py http://mms.example.com:8080 mongo-01.example.com 54b5e4df9436322466a89a3e apple@johnandcailin.com da5f6890-1ee4-49db-83ca-ece9b2dbe5c0
    parser = argparse.ArgumentParser(description='Automation API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('machine_hostname', help="Agent Hostname")
    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")
    parser.add_argument('--clean', action='store_true', required=False)
    parser.add_argument('--step', action='store_true', required=False)
    args = parser.parse_args()

    test = TestAutomationApi(args.base_url, args.machine_hostname, args.group_id, args.api_user, args.api_key, args.step)
    if args.clean:
        test.clean()
    else:
        test.run()

