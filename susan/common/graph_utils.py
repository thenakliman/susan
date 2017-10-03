# Copyright 2017 <thenakliman@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


def traverse(graph, curr_app, visited):
    for app in graph[curr_app].get('goto', []):
        if app not in visited:
            visited.add(app)
            traverse(graph, app, visited)


def get_apps(graph):
    # NOTE(thenakliman): For storing the apps, set is used not list. it does
    # not matter if applications are small, but if they are around 10**5 then
    # it matters. Searching in list is O(n) operation but addition is O(1)
    # we are making up search queries a lot of time therefor using set.
    # Insertion and lookup takes O(logn) time therefore set is being used here.
    apps = set(['susan'])
    traverse(graph, 'susan', apps)
    # Converted to list for ease of processing and set are not ordered.
    return list(apps)
