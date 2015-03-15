import argparse
import logging
import os

from automation_api_base import AutomationApiBase

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

class TestAutomationApi(AutomationApiBase):

    def __init__(self, base_url, machine_hostname, group_id, api_user, api_key, config_name, cluster):
        AutomationApiBase.__init__(self, base_url, machine_hostname, group_id, api_user, api_key)
        self.config_name = config_name
        self.cluster = cluster

    def clean(self):
        self.post_automation_config("configs/api_0_clean.json")

    def run(self):
        if self.cluster:
            self.post_automation_config("configs/%s_cluster.json" % self.config_name)
        else:
            self.post_automation_config("configs/%s.json" % self.config_name)

        if os.path.exists("configs/%s_monitoring_agent.json" % self.config_name):
            self.post_monitoring_agent_config("configs/%s_monitoring_agent.json" % self.config_name)

        if os.path.exists("configs/%s_backup_agent.json" % self.config_name):
            self.post_backup_agent_config("configs/%s_backup_agent.json" % self.config_name)

        #self.wait_for_goal_state()


if __name__ == '__main__':

    # automation-agent/ec2-52-5-170-235.compute-1.amazonaws.com@MMS.COM
    # /opt/automation-agent.keytab

    # python test_enterprise_advanced.py http://localhost:8080 ec2-52-5-170-235.compute-1.amazonaws.com 541ed2009436399a1f54e01b cailin.nelson@10gen.com 0db80617-1cab-44d6-b858-a84496194f43 security_kerberos
    parser = argparse.ArgumentParser(description='Automation API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('machine_hostname', help="Agent Hostname")
    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")
    parser.add_argument('config_name', help="ConfigName")
    parser.add_argument('--cluster', action='store_true', required=False)
    parser.add_argument('--clean', action='store_true', required=False)
    args = parser.parse_args()

    test = TestAutomationApi(
        args.base_url,
        args.machine_hostname,
        args.group_id,
        args.api_user,
        args.api_key,
        args.config_name,
        args.cluster
    )

    if args.clean:
        test.clean()
    else:
        test.run()

