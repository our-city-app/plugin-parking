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
# @@license_version:1.3@@

import webapp2

from framework.bizz.job import run_job
from framework.utils import guid
from plugins.parking.consts import PARKING_QUEUE
from plugins.parking.models import Settings


class ParkingSyncHandler(webapp2.RequestHandler):

    def get(self):
        uid = guid()
        run_job(_query_settings, [], _worker_settings, [uid], worker_queue=PARKING_QUEUE)


def _query_settings():
    return Settings.query()


def _worker_settings(settings_key, uid):
    from plugins.parking.backends.mycsn import sync as mycsn_sync
    settings = settings_key.get()
    b = settings.params.get('backend')
    if not b:
        return
    if b in ('mycsn'):
        mycsn_sync(uid, settings.params)
