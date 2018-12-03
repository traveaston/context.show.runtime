# -*- coding: utf-8 -*-

from resources.lib import kodilogging
from resources.lib import context

import logging
import xbmcaddon

ADDON = xbmcaddon.Addon()
kodilogging.config()

context.run()
