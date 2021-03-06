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


from framework.plugin_loader import Plugin
from framework.utils.plugins import Handler
from plugins.parking.cron import ParkingSyncHandler
from plugins.parking.handlers import ParkingLoadHandler


class ParkingPlugin(Plugin):
    def __init__(self, configuration):
        super(ParkingPlugin, self).__init__(configuration)

    def get_handlers(self, auth):
        yield Handler(url='/app/load', handler=ParkingLoadHandler)
        if auth == Handler.AUTH_ADMIN:
            yield Handler(url='/admin/cron/parking/sync', handler=ParkingSyncHandler)

