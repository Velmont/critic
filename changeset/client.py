# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import configuration
import socket
from textutils import json_encode, json_decode, indent

def requestChangesets(requests):
    try:
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.connect(configuration.services.CHANGESET["address"])
        connection.send(json_encode(requests))
        connection.shutdown(socket.SHUT_WR)

        data = ""

        while True:
            received = connection.recv(4096)
            if not received: break
            data += received

        connection.close()
    except socket.error, error:
        raise Exception, "Changeset background service failed: %s" % error[1]

    try:
        results = json_decode(data)
    except:
        raise Exception, "Changeset background service failed: returned an invalid response (%r)" % data

    if type(results) != list:
        raise Exception, "Changeset background service failed: %s" % str(results)

    if len(results) != len(requests):
        raise Exception, "Changeset background service failed: didn't process all requested changesets"

    errors = []

    for result in results:
        if "error" in result:
            errors.append(result["error"])

    if errors:
        raise Exception, "Changeset background service failed: one or more requests failed\n%s" % "\n".join(map(indent, errors))
