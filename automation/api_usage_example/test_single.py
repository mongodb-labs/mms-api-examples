import argparse
import logging
import os

from automation_api_base import AutomationApiBase

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

class TestAutomationApi(AutomationApiBase):

    def __init__(self, base_url, machine_hostname, group_id, api_user, api_key, config_name):
        AutomationApiBase.__init__(self, base_url, machine_hostname, group_id, api_user, api_key)
        self.config_name = config_name

    def clean(self):
        self.post_automation_config("configs/api_0_clean.json")

    def run(self):

        self.post_automation_config("configs/%s.json" % self.config_name)


if __name__ == '__main__':

    # python test_enterprise_advanced.py http://localhost:8080 cailinmac 541ed2009436399a1f54e01b cailin.nelson@10gen.com da5f6890-1ee4-49db-83ca-ece9b2dbe5c0 mongo32_csrs_cluster
    parser = argparse.ArgumentParser(description='Automation API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('machine_hostname', help="Agent Hostname")
    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")
    parser.add_argument('config_name', help="ConfigName")
    parser.add_argument('--clean', action='store_true', required=False)
    args = parser.parse_args()

    test = TestAutomationApi(
        args.base_url,
        args.machine_hostname,
        args.group_id,
        args.api_user,
        args.api_key,
        args.config_name
    )

    if args.clean:
        test.clean()
    else:
        test.run()

