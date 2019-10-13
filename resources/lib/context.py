# -*- coding: utf-8 -*-

import json
import xbmc
import xbmcgui
from resources.lib import kodiutils

def format_time(seconds):
    time = ''

    if kodiutils.get_setting('show_days') == 'true':
        divisions = {
            'days': seconds / 60 / 60 / 24,
            'hours': seconds / 60 / 60 % 24,
            'minutes': seconds / 60 % 60
        }
    else:
        divisions = {
            'hours': seconds / 60 / 60,
            'minutes': seconds / 60 % 60
        }

    for division, value in sorted(divisions.items()):
        # remove empty divisions and make singular if necessary
        if value == 1:
            division = division[:-1]
        elif value is 0:
            continue

        time += '{} {}, '.format(value, division)

    if time == '':
        return 'none'

    return time.strip(', ')

# wrapper for dialog box, kodi function is not implemented correctly
# issue details here: https://github.com/xbmc/xbmc/issues/14824
def dialog(title, lines):
    line1 = lines.pop(0)
    line2 = lines.pop(0)
    remaining_lines = '\n'.join(lines)

    xbmcgui.Dialog().ok(title, line1, line2, remaining_lines)

def notify(title, message='empty'):
    if message is 'empty':
        message = title
        title = "Notification:"

    xbmc.executebuiltin('Notification("{}", "{}")'.format(title, message))

def show_runtime(series):
    remaining_runtime, total_runtime, watched_runtime = 0, 0, 0
    query = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetTVShows",
        "params": {
            "filter": {
                "field": "title",
                "operator": "is",
                "value": series
            },
            "limits": {
                "start": 0,
                "end": 1
            },
            "properties": [
                "episode",
                "watchedepisodes"
            ]
        },
        "id": "libTvShows"
    }

    response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))

    if response['result']['limits']['total'] > 0:
        total_episodes = response['result']['tvshows'][0]['episode']
        watched_episodes = response['result']['tvshows'][0]['watchedepisodes']

        query = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetEpisodes",
            "params": {
                "filter": {
                    "field": "tvshow",
                    "operator": "is",
                    "value": series
                },
                "limits": {
                    "start" : 0,
                    "end": total_episodes
                },
                "properties": [
                    "playcount",
                    "runtime"
                ]
            },
            "id": "libTvShows"
        }

        response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))

        for episode in response['result']['episodes']:
            if episode['playcount'] == 0:
                remaining_runtime += episode['runtime']
            else:
                watched_runtime += episode['runtime']

            total_runtime += episode['runtime']

        remaining_runtime = format_time(remaining_runtime)
        total_runtime = format_time(total_runtime)
        watched_runtime = format_time(watched_runtime)

        if kodiutils.get_setting('detailed_info') == 'true':
            percent = '{}%'.format(str(round((float(watched_episodes)/total_episodes) * 100))[:-2])
            message = []
            message.append('Watched episodes: {}/{} ({})'.format(watched_episodes, total_episodes, percent))
            message.append('Total runtime: {}'.format(total_runtime))
            message.append('Watched: {}'.format(watched_runtime))
            message.append('Remaining: {}'.format(remaining_runtime))

            dialog(series, message)
        else:
            notify('Remaining runtime - {}'.format(series), remaining_runtime)
