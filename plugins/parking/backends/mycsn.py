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
import hashlib
import json
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from framework.utils import put_in_chunks
from mcfw.rpc import returns, arguments
from plugins.parking.models import Parking, ParkingInfo, ParkingLocation, \
    ParkingStatistics


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


def create_parking_uid(city, name):
    key = u'mycsn_%s_%s' % (city, name)
    return hashlib.sha256(key).hexdigest().upper()


def sync(uid, params):
    data = get_data(params)
    latest = json.loads(data['snapshots'][unicode(data['upperCutoffMillis'])])
    
    to_put = []
    for p in latest['parkings']:
        logging.debug(p)
        pk = Parking.create_key(create_parking_uid(data['municipality'], p['name']))
        parking = pk.get()
        if not parking:
            parking = Parking(key=pk)
            parking.visible = True
            parking.info = ParkingInfo()
            parking.info.name = p['name']
            parking.info.capacity = p['totalCapacity']
            parking.info.contact = p['contactInfo']
            parking.info.opening_hours = p['openingHours']
            parking.info.location = ParkingLocation()
            parking.info.location.geo_location = ndb.GeoPt(p['latitude'],
                                                           p['longitude'])
            parking.info.location.address = p['address']
            parking.info.location.city = data['municipality']
            to_put.append(parking)

        parking_stats = ParkingStatistics(key=ParkingStatistics.create_key(uid, pk))
        parking_stats.open = p['open'] or True
        parking_stats.full = p['full'] or False
        try:
            parking_stats.available_capacity = long(p['availableCapacity'])
        except:
            parking_stats.available_capacity = parking.info.capacity
        to_put.append(parking_stats)

    if to_put:
        logging.info('put %s items', len(to_put))
        put_in_chunks(to_put, is_ndb=True)
