#!/usr/bin/env python
#
# BitBake Graphical GTK User Interface
#
# Copyright (C) 2011        Intel Corporation
#
# Authored by Joshua Lock <josh@linux.intel.com>
# Authored by Dongxiao Xu <dongxiao.xu@intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import gobject
import gtk
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    import bb
except RuntimeError as exc:
    sys.exit(str(exc))
from bb.ui import uihelper
from bb.ui.crumbs.hoblistmodel import RecipeListModel, PackageListModel
from bb.ui.crumbs.hobeventhandler import HobHandler
from bb.ui.crumbs.builder import Builder

extraCaches = ['bb.cache_extra:HobRecipeInfo']

def event_handle_idle_func(eventHandler, hobHandler):
    # Consume as many messages as we can in the time available to us
    if not eventHandler:
        return False
    event = eventHandler.getEvent()
    while event:
        hobHandler.handle_event(event)
        event = eventHandler.getEvent()
    return True

def main (server = None, eventHandler = None):
    bitbake_server = None
    client_addr = None
    server_addr = None

    if not eventHandler:
        helper = uihelper.BBUIHelper()
        server, eventHandler, server_addr, client_addr = helper.findServerDetails()
    bitbake_server = server

    gobject.threads_init()

    # That indicates whether the Hob and the bitbake server are
    # running on different machines
    # recipe model and package model
    recipe_model = RecipeListModel()
    package_model = PackageListModel()

    hobHandler = HobHandler(bitbake_server, server_addr, client_addr, recipe_model, package_model)
    if hobHandler.kick() == False:
        return 1
    builder = Builder(hobHandler, recipe_model, package_model)

    # This timeout function regularly probes the event queue to find out if we
    # have any messages waiting for us.
    gobject.timeout_add(10, event_handle_idle_func, eventHandler, hobHandler)

    try:
        gtk.main()
    except EnvironmentError as ioerror:
        # ignore interrupted io
        if ioerror.args[0] == 4:
            pass
    finally:
        hobHandler.cancel_build(force = True)

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(15)
    sys.exit(ret)
