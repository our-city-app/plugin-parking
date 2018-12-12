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

from google.appengine.ext import ndb

from framework.models.common import NdbModel
from plugins.parking import consts


class Settings(NdbModel):
    NAMESPACE = consts.NAME

    name = ndb.StringProperty()
    params = ndb.JsonProperty()

    @classmethod
    def create_key(cls, uid):
        return ndb.Key(cls, uid, namespace=consts.NAME)

    @property
    def uid(self):
        return self.key.id().decode('utf-8')


class ParkingLocation(NdbModel):
    geo_location = ndb.GeoPtProperty()
    address = ndb.TextProperty()
    city = ndb.StringProperty()


class ParkingInfo(NdbModel):
    name = ndb.StringProperty()
    capacity = ndb.IntegerProperty()
    contact = ndb.TextProperty()
    opening_hours = ndb.TextProperty()
    location = ndb.LocalStructuredProperty(ParkingLocation)


class Parking(NdbModel):
    NAMESPACE = consts.NAME

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    visible = ndb.BooleanProperty()

    info = ndb.LocalStructuredProperty(ParkingInfo)

    @classmethod
    def create_key(cls, uid):
        return ndb.Key(cls, uid, namespace=consts.NAME)

    @property
    def uid(self):
        return self.key.id().decode('utf-8')

    def get_latest_stats(self):
        qry = ParkingStatistics.list_with_parent(self.key)
        qry = qry.order(-ParkingStatistics.created)
        return qry.get()


class ParkingStatistics(NdbModel):
    NAMESPACE = consts.NAME

    created = ndb.DateTimeProperty(auto_now_add=True)

    open = ndb.BooleanProperty()
    full = ndb.BooleanProperty()
    available_capacity = ndb.IntegerProperty()

    @classmethod
    def create_key(cls, uid, parent):
        return ndb.Key(cls, uid, parent=parent)

    @classmethod
    def list_with_parent(cls, key):
        qry = cls.query(ancestor=key)
        return qry
