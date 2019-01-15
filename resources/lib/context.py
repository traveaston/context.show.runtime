# -*- coding: utf-8 -*-

import json
import sys
import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon()

def convert_time(runtime):
    return '{0} days {1} hours {2} minutes'.format(runtime/24/60, runtime/60%24, runtime%60)

# wrapper for dialog box, kodi function is not implemented correctly
# issue details here: https://github.com/xbmc/xbmc/issues/14824
def dialog(title, lines):
    line1 = lines.pop(0)
    line2 = lines.pop(0)
    remaining_lines = '\n'.join(lines)

    xbmcgui.Dialog().ok(title, line1, line2, remaining_lines)

def run():
    remaining_runtime, total_runtime, watched_runtime = 0, 0, 0
    query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "filter": { "field": "title", "operator": "is", "value": "" }, "limits": { "start": 0, "end": 1}, "properties": [ "title", "originaltitle", "playcount", "episode", "episodeguide", "watchedepisodes", "season"], "sort": { "order": "ascending", "method": "label"} }, "id": "libTvShows"}
    query = json.loads(json.dumps(query))
    query['params']['filter']['value'] = sys.listitem.getLabel()
    response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))

    if response['result']['limits']['total'] > 0:
        show_id = response['result']['tvshows'][0]['tvshowid']
        show_title = response['result']['tvshows'][0]['title']
        total_seasons = response['result']['tvshows'][0]['season']
        total_episodes = response['result']['tvshows'][0]['episode']
        watched_episodes = response['result']['tvshows'][0]['watchedepisodes']

        query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "filter": { "field": "tvshow", "operator": "is", "value": "" }, "limits": { "start" : 0, "end": total_episodes }, "properties": ["playcount", "runtime", "tvshowid", "streamdetails"], "sort": { "order": "ascending", "method": "label" } }, "id": "libTvShows"}
        query = json.loads(json.dumps(query))
        query['params']['filter']['value'] = show_title
        response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))

        for episode in response['result']['episodes']:
            if episode['playcount'] == 0:
                remaining_runtime += episode['runtime'] / 60
            else:
                watched_runtime += episode['runtime'] / 60

            total_runtime += episode['runtime'] / 60

        remaining_runtime = convert_time(remaining_runtime)
        total_runtime = convert_time(total_runtime)
        watched_runtime = convert_time(watched_runtime)

        if addon.getSetting('detailed_info') == 'true':
            percent = '{0}%'.format(str(round((float(watched_episodes)/total_episodes) * 100))[:-2])
            message = []
            message.append('Watched/Unwatched: {0}/{1} ({2})'.format(watched_episodes, total_episodes, percent))
            message.append('Remaining: ' + remaining_runtime)
            message.append('Watched: ' + watched_runtime)
            message.append('Total runtime: ' + total_runtime)

            dialog(show_title, message)
        else:
            xbmc.executebuiltin("Notification(Remaining runtime - {0}, {1})".format(show_title, remaining_runtime))
