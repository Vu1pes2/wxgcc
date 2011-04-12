#!/bin/env python
# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------
# Name:         gtkwin.py
# Purpose:      A virtual terminal window.
#
# Author:       Zechao Wang <zwang@ucrobotics.com>
#
# Created:      2011-04-12
# RCS-ID:       
# Copyright:    (c) 2011 by Zechao Wang
# Licence:      GPLV2
#----------------------------------------------------------------------------

import gtk
import vte

class GtkWin(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("destroy", lambda window: gtk.main_quit())
        self.set_default_size(600, 600)
        self.vt = vte.Terminal ()
        self.vt.connect ("child-exited", lambda term: gtk.main_quit())
        self.vt.fork_command()
        self.add(self.vt)
        self.show_all()

    def RunComm(self, comm):
        self.comm = comm
        self.vt.feed_child(self.comm + '\n')

