import json
import logging
import pprint
import requests

from requests.auth import HTTPDigestAuth

class ApiBase:
    def __init__(self, base_url, group_id, api_user, api_key):
        self.base_url = base_url + "/api/public/v1.0"
        self.group_id = group_id
        self.api_user = api_user
        self.api_key = api_key

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

        return r.json()

    def patch(self, url, json_body):
        logging.info("Executing PATCH: %s" % url)
        headers = {'content-type': 'application/json'}
        r = requests.patch(
            url,
            auth=HTTPDigestAuth(self.api_user, self.api_key),
            data=json.dumps(json_body),
            headers=headers
        )
        self.check_response(r)
        logging.debug("%s" % pprint.pformat(r.json()))

        return r.json()

    def post(self, url, json_body):
        logging.info("Executing POST: %s" % url)
        headers = {'content-type': 'application/json'}
        r = requests.post(
            url,
            auth=HTTPDigestAuth(self.api_user, self.api_key),
            data=json.dumps(json_body),
            headers=headers
        )
        self.check_response(r)
        logging.debug("%s" % pprint.pformat(r.json()))

        return r.json()

    def check_response(self, r):
        if r.status_code not in [requests.codes.ok, 202]:
            logging.error("Response Error Code: %s Detail: %s" % (r.status_code, r.json()['detail']))
            raise ValueError(r.json()['detail'])