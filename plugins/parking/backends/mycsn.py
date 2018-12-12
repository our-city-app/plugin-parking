# -*- coding: utf-8 -*-
# Copyright 2018 Mobicage NV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @@license_version:1.5@@
import base64
import json
import logging

from google.appengine.api import urlfetch

from mcfw.rpc import returns, arguments


@returns(dict)
@arguments(params=dict)
def get_api_headers(params):
    credentials = base64.encodestring('%s:%s' % (params['auth_username'], params['auth_password']))[:-1]
    return {
        'Authorization': 'Basic %s' % credentials
    }


@returns(dict)
@arguments(params=dict)
def get_data(params):
    headers = get_api_headers(params)
    result = urlfetch.fetch(url=params['url'], method=urlfetch.GET, headers=headers, deadline=5)
    if result.status_code != 200:
        logging.info(result.content)
        logging.error('failed to call %s, code: %d', params['url'], result.status_code)
        raise Exception('Failed to call mycsn backend')

    return json.loads(result.content)


def sync(params):
    data = get_data(params)
    latest = json.loads(data['snapshots'][unicode(data['upperCutoffMillis'])])
    logging.info(latest)
