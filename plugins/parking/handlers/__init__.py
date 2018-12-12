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

import json
import logging

import webapp2

from plugins.parking.models import Parking


class ParkingLoadHandler(webapp2.RequestHandler):

    def post(self):
        logging.debug(self.request.GET)
        logging.debug(self.request.POST)
        logging.info(self.request.body)

        headers = {}
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Content-Type'] = 'application/json'
        self.response.headers.update(headers)

        result = {'items': []}
        for p in Parking.query():
            stats = p.get_latest_stats()
            result['items'].append({
                'name': p.info.name,
                'open': stats.open,
                'full': stats.full,
                'capacity': {
                    'fee': stats.available_capacity,
                    'total': p.info.capacity
                },
                'contact': p.info.contact,
                'opening_hours': p.info.opening_hours,
                'location': {
                    'address':  p.info.location.address
                }
            })

        self.response.out.write(json.dumps(result))

    get = post
