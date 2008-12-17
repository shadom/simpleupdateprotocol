#!/usr/bin/env python
#
# Copyright 2008 FriendFeed
# Author: Paul Buchheit
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""
SUP (Simple Update Protocol) is to a simple and compact "ping feed" that
web services can produce in order to alert the consumers of their feeds when
a feed has been updated. This reduces update latency and improves efficiency
by eliminating the need for frequent polling.

This validator is used to verify that SUP feeds are well-formed. It is
available on the web at http://friendfeed.com/api/sup-validator

See http://code.google.com/p/simpleupdateprotocol/ to learn more about SUP.
"""

import datetime
import simplejson
import re

ERROR = 'error'
SUGGESTION = 'suggestion'

def validate(sup_data):
    try:
        sup = simplejson.loads(sup_data)
    except Exception, e:
        return ERROR, "Invalid JSON: %s" % e

    required = ["since_time", "updated_time", "period", "updates"]
    for key in required:
        if key not in sup:
            return ERROR, "Missing attribute %r" % key

    for key in ["since_time", "updated_time"]:
        try:
            sup[key] = _parse_3339_date(sup[key])
        except ValueError, e:
            return ERROR, "Invalid %s: %s" % (key, e)

    try:
        sup["period"] = int(sup["period"])
    except ValueError, e:
        return ERROR, "Invalid period: %s" % e
    
    update_window = (sup["updated_time"] - sup["since_time"]).seconds
    if update_window < sup["period"]:
        return ERROR, \
            "updated_time - since_time (%d sec) does not cover period (%d sec)" % (
            update_window, sup["period"])

    if sup["period"] < 1:
        return ERROR, "Invalid period: %d" % sup["period"]

    if type(sup["updates"]) != list:
        return ERROR, "'updates' should be a list of lists"

    for u in sup["updates"]:
        if type(u) != list or len(u) != 2 or \
           not isinstance(u[0], basestring) or not isinstance(u[1], basestring):
            return ERROR, "Bad update '%r'. Each entry in 'updates' must be" \
                   " a two element list of strings" % u

        if not re.match(r"^[a-zA-Z0-9-]+\Z", u[0]):
            return ERROR, "Bad SUP-ID: %r. Valid SUP-IDs are composed " \
                "exclusively of ASCII letters, numbers, or hyphens" % str(u[0])
    
        if not u[1]:
            return ERROR, "Missing update-id on update '%r'" % u

    available = sup.get("available_periods")
    if available:
        if type(available) != dict:
            return ERROR, "'available_periods' must be a map (object)"
        for period, url in available.iteritems():
            try:
                int(period)
            except ValueError, e:
                return ERROR, "Invalid available_period: %s" % e
            if not re.match(r"^https?://[0-9a-zA-Z-\.]+/[^\s]*\Z", url):
                return ERROR, "Bad url in available_periods: %s" % url
            
            
    if sup["period"] < 10 or sup["period"] > 120:
        return SUGGESTION, \
            "The default period should be between 10 and 120 seconds"

    if update_window == sup["period"]:
        return SUGGESTION, "updated_time - since_time (%d sec)" \
               " equals period (%d sec). It is recommended that you include" \
               " some overlap (e.g. an extra 10 seconds of updates)" % (
               update_window, sup["period"])
    
    if not available or len(available) < 2:
        return SUGGESTION, "It is better to include multiple available_periods"

    return None, None

def _validate_doctests():
    """ A bunch of doctests for validate(). Move apart from validate() because
    they are a little bulky.

    >>> validate("{")
    ('error', 'Invalid JSON: Expecting property name: line 1 column 1 (char 1)')
    >>> validate("{3:3}")
    ('error', 'Invalid JSON: Expecting property name: line 1 column 1 (char 1)')
    >>> validate("{}")
    ('error', "Missing attribute 'since_time'")
    >>> validate('{"since_time":"2008/11/12", "updated_time":"bad", "period":3, "updates":[]}')
    ('error', 'Invalid since_time: Unrecognized RFC 3339 date timezone format')
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:20Z", "period":"bad", "updates":[]}')
    ('error', "Invalid period: invalid literal for int() with base 10: 'bad'")
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"30", "updates":[]}')
    ('error', 'updated_time - since_time (20 sec) does not cover period (30 sec)')
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":{}}')
    ('error', "'updates' should be a list of lists")
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[[2,3]]}')
    ('error', "Bad update '[2, 3]'. Each entry in 'updates' must be a two element list of strings")
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[["id1", "v1"], ["id%bad", "v2"]]}')
    ('error', "Bad SUP-ID: 'id%bad'. Valid SUP-IDs are composed exclusively of ASCII letters, numbers, or hyphens")
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[["id1", "v1"], ["id2", ""]]}')
    ('error', "Missing update-id on update '[u'id2', u'']'")
    >>> validate('{"since_time":"2008-11-12T22:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[], "available_periods":[3]}')
    ('error', "'available_periods' must be a map (object)")
    >>> validate('{"since_time":"2008-11-12T22:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[], "available_periods":{"bad": "http://x.com/test"}}')
    ('error', "Invalid available_period: invalid literal for int() with base 10: 'bad'")
    >>> validate('{"since_time":"2008-11-12T22:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[], "available_periods":{"10": "mysuptest"}}')
    ('error', u'Bad url in available_periods: mysuptest')
    >>> validate('{"since_time":"2008-11-12T22:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"300", "updates":[]}')
    ('suggestion', 'The default period should be between 10 and 120 seconds')
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"20", "updates":[]}')
    ('suggestion', 'updated_time - since_time (20 sec) equals period (20 sec). It is recommended that you include some overlap (e.g. an extra 10 seconds of updates)')
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[["id1", "v1"], ["id2", "v1"]]}')
    ('suggestion', 'It is better to include multiple available_periods')
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[["id1", "v1"], ["id2", "v1"]], "available_periods":{"10":"http://site.com/sup?10"}}')
    ('suggestion', 'It is better to include multiple available_periods')
    >>> validate('{"since_time":"2008-11-12T23:51:20Z", "updated_time":"2008-11-12T23:51:40Z", "period":"10", "updates":[["id1", "v1"], ["id2", "v1"]], "available_periods":{"10":"http://site.com/sup?10", "300":"http://site.com/sup?30"}}')
    (None, None)

    """
    pass


def _parse_3339_date(date):
    """
    Simple RFC 3339 date parser. The standard python libraries can't parse
    this format for some reason. The "Universal feed parser" can, but I didn't
    want to include it here.

    This code is not correct because it discards timezone info.

    >>> _parse_3339_date("2008-11-13T01:55:05-00:00")
    datetime.datetime(2008, 11, 13, 1, 55, 5)
    >>> _parse_3339_date("2008-11-13T01:55:05Z")
    datetime.datetime(2008, 11, 13, 1, 55, 5)
    >>> _parse_3339_date("2008-11-13T01:55:05")
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized RFC 3339 date timezone format
    >>> _parse_3339_date("2008-11-13T01:5505Z")
    Traceback (most recent call last):
    ...
    ValueError: time data did not match format:  data=2008-11-13T01:5505Z  fmt=%Y-%m-%dT%H:%M:%SZ
    """

    if not date:
        raise ValueError

    if date[-1] == 'Z':
        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    elif date[-6] in ['-', '+']:
        # handle 2008-11-13T01:55:05+00:00
        # TODO handle timezone instead of discarding
        return datetime.datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S")
    else:
        raise ValueError("Unrecognized RFC 3339 date timezone format")


if __name__ == "__main__":
    import doctest
    doctest.testmod()

