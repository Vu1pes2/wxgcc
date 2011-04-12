#!/bin/env python
# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------
# Name:         wxgcc.py
# Purpose:      A GUI toolkit for GCC based wxPython.
#
# Author:       Zechao Wang <zwang@ucrobotics.com>
#
# Created:      2011-03-12
# RCS-ID:       
# Copyright:    (c) 2011 by Zechao Wang
# Licence:      GPLV2
#----------------------------------------------------------------------------

import os
import sys
import wx
import wx.aui
import wx.richtext as rt
from wx import stc
from wx.lib.wordwrap import wordwrap
import webbrowser

#import threading

if not wx.Platform == "__WXMSW__":
    from gtkwin import GtkWin

if wx.Platform == "__WXMSW__":
    TmpBin = "C:\\foo"
    TmpLog = "C:\\foo.log"
    #TmpRes = "C:\\foo.res"
else:
    TmpBin = "/tmp/foo"
    TmpLog = "/tmp/foo.log"
    #TmpRes = "/tmp/foo.res"

# convert tab to TabLen spaces
TabLen = 8

# macro definition colour
DefColor = (205, 0, 205, 255)
# key word colour
KeyColor = (0, 205, 0, 255)
# string clour
StrColor = (205, 0, 0, 255)
# comment colour
ComColor = (0, 0, 205, 255)

ID_MB_NEW_C           = 11
ID_MB_NEW_CPP         = 12
ID_MB_OPEN            = 13
ID_MB_REPLACE         = 14
ID_MB_RUN             = 15

ID_TB_NEW_C           = 21
ID_TB_NEW_CPP         = 22
ID_TB_OPEN            = 23
ID_TB_REPLACE         = 24
ID_TB_RUN             = 25

ID_MB_LIST = [ID_MB_NEW_C, ID_MB_NEW_CPP, ID_MB_OPEN, wx.ID_UNDO, wx.ID_REDO, wx.ID_CUT, wx.ID_PASTE, ID_MB_REPLACE, ID_MB_RUN]

ID_TB_LIST = [ID_TB_NEW_C, ID_TB_NEW_CPP, ID_TB_OPEN, wx.ID_UNDO, wx.ID_REDO, ID_TB_REPLACE, ID_TB_RUN]

LicenseText = """
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

# keywords for c/c++
KeyWords = "and and_eq asm auto bitand bitor bool break case catch char class compl const const_cast continue default delete do double dynamic_cast else enum explicit export extern false float for friend goto if inline int long mutable namespace new not not_eq operator or or_eq private protected public register reinterpret_cast return short signed sizeof static static_cast struct switch template this throw true try typedef typeid typename union unsigned using virtual void volatile wchar_t while xor xor_eq"

ArrList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Version = "Wxgcc V1.8.6"

#----------------------------------------------------------------------

class WxgccFrame(wx.Frame):
    def __init__(self, parent, id=-1):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=Version, size=(600, 600), style = wx.DEFAULT_FRAME_STYLE)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        # Will not works on windows if Bind here
        #self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        # set the frame icon
        self.SetIcon(wx.Icon('./icon/wxgcc.ico', wx.BITMAP_TYPE_ICO))

        # set the window center
        #self.Center()

        self.FileFlag = 0
        self.FileTxt = ""
        self.lock = False
        self.FullScreen = False

        # If create a rtc and log based panel, then will not works well on windows, cursor will swith from rtc to log when Enter.
        ## self.panel = wx.Panel(self, wx.ID_ANY)

        self.mgr = wx.aui.AuiManager()
        ## self.mgr.SetManagedWindow(self.panel)
        self.mgr.SetManagedWindow(self)

        self.MakeMenuBar()
        self.MakeToolBar()
        self.StatusBar = self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(2)
        #self.StatusBar.SetStatusWidths([-3,-2])

        # create log box, wx.TE_RICH2 can enable to set the text colour in Windows
        ## self.log = wx.TextCtrl(self.panel, -1, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL, size=(-1,200))
        self.log = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.TE_RICH2, size=(-1,200))

        # create richText box and init: http://docs.wxwidgets.org/stable/wx_wxrichtextctrl.html
	## self.rtc = rt.RichTextCtrl(self.panel, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER, size=(-1,300))
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER, size=(-1,300))
        self.rtc.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        wx.CallAfter(self.rtc.SetFocus)
        self.OnNewC(True)

        # create a new thread to set syntax highlight 
        #th = MyThread(self.rtc)
        #th.setDaemon(True)
        #th.start()

        # for detail: http://docs.wxwidgets.org/stable/wx_wxauipaneinfo.html
        self.mgr.AddPane(self.rtc,
                         wx.aui.AuiPaneInfo().
                         CenterPane().BestSize((-1, 300)).
                         #MinSize((-1, 200)).
                         Floatable(False).
                         Caption("Edit").
                         CloseButton(False).
                         Name("EditWin"))
        self.mgr.AddPane(self.log,
                         wx.aui.AuiPaneInfo().
                         Bottom().BestSize((-1, 200)).
                         MinSize((-1, 100)).
                         Gripper(True).
                         Floatable(False).
                         Caption("Log").
                         CloseButton(False).
                         Name("LogWin"))
        self.mgr.Update()

        # add find/replace event
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplace)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAll)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)

    def InitC(self):
        self.rtc.Freeze()

        self.rtc.SetBackgroundColour((236,248,224))
        self.log.SetBackgroundColour((236,248,224))

        self.rtc.WriteText("/*")
        self.rtc.Newline()

        self.rtc.WriteText(" * This is the demo code of C language.")
        self.rtc.Newline()

        self.rtc.WriteText(" * Just modify me when programing.")
        self.rtc.Newline()

        self.rtc.WriteText(" */")
        self.rtc.Newline()

        self.rtc.WriteText("#include <stdio.h>")
        self.rtc.Newline()

        self.rtc.WriteText("int main()")
        self.rtc.Newline()

        self.rtc.WriteText("{")
        self.rtc.Newline()

        self.rtc.WriteText("        printf(\"Hello C !\\n\");")
        self.rtc.Newline()

        self.rtc.WriteText("        return 0;")
        self.rtc.Newline()

        self.rtc.WriteText("}")

        self.rtc.Thaw()

    def InitCpp(self):
        self.rtc.Freeze()

        self.rtc.SetBackgroundColour((224,236,248))
        self.log.SetBackgroundColour((224,236,248))

        self.rtc.WriteText("/*")
        self.rtc.Newline()

        self.rtc.WriteText(" * This is the demo code of C++ language.")
        self.rtc.Newline()

        self.rtc.WriteText(" * Just modify me when programing.")
        self.rtc.Newline()

        self.rtc.WriteText(" */")
        self.rtc.Newline()

        self.rtc.WriteText("#include<iostream>")
        self.rtc.Newline()

        self.rtc.WriteText("int main()")
        self.rtc.Newline()

        self.rtc.WriteText("{")
        self.rtc.Newline()

        self.rtc.WriteText("        std::cout << \"Hello C++ !\\n\";")
        self.rtc.Newline()

        self.rtc.WriteText("        return 0;")
        self.rtc.Newline()

        self.rtc.WriteText("}")

        self.rtc.Thaw()

    def OnNewC(self, evt):
        if self.WarningDlg(evt):
            self.rtc.Clear()
            self.log.Clear()
            self.InitC()
            self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
            self.FileFlag = 0
            self.rtc.SetFilename("")
            self.rtc.SetInsertionPoint(0)
            self.SyntaxHighlight()
            #self.TabToSpace()
            titleTxt = "[Untitled C File] - " + Version
            wx.CallAfter(self.UpdateTitle, titleTxt)
            #wx.CallAfter(self.UpdateStatus, "")

    def OnNewCpp(self, evt):
        if self.WarningDlg(evt):
            self.rtc.Clear()
            self.log.Clear()
            self.InitCpp()
            self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
            self.FileFlag = 1
            self.rtc.SetFilename("")
            self.rtc.SetInsertionPoint(0)
            self.SyntaxHighlight()
            #self.TabToSpace()
            titleTxt = "[Untitled C++ File] - " + Version
            wx.CallAfter(self.UpdateTitle, titleTxt)
            #wx.CallAfter(self.UpdateStatus, "New C++ file")

    def WarningDlg(self, evt):
        path = self.rtc.GetFilename()
        FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")

        if FileTxt != self.FileTxt:
            dlg = wx.MessageDialog(self, "Do you want to save the file ?", "Warning", wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
            warnFlag = dlg.ShowModal()
            if warnFlag == wx.ID_YES:
                self.OnFileSave(evt)
                return True
            elif warnFlag == wx.ID_CANCEL:
                return False
        return True

    def OnFileOpen(self, evt):
        # This gives us a string suitable for the file dialog based on
        # the file handlers that are loaded
        ## wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
        wildcard = "Files (*.c;*.cpp)|*.c;*.cpp"
        dlg = wx.FileDialog(self, "Choose a filename", wildcard=wildcard, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                if self.WarningDlg(evt):
                    #fileType = types[dlg.GetFilterIndex()]
                    #self.rtc.LoadFile(path, fileType)
                    f = file(path, "r")
                    fv = f.read()
                    self.rtc.SetValue(fv)
                    f.close()
                    self.rtc.SetFilename(path)
                    self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
                    titleTxt = "[" + path + "] - " + Version
                    wx.CallAfter(self.UpdateTitle, titleTxt)
                    if path.split('.')[-1] == 'c':
                        self.FileFlag = 0
                        self.log.Clear()
                        self.rtc.SetBackgroundColour((236,248,224))
                        self.log.SetBackgroundColour((236,248,224))
                    else:
                        self.FileFlag = 1
                        self.log.Clear()
                        self.rtc.SetBackgroundColour((224,236,248))
                        self.log.SetBackgroundColour((224,236,248))
                    self.SyntaxHighlight()
                    self.TabToSpace()
        dlg.Destroy()
        
    def OnFileSave(self, evt):
        path = self.rtc.GetFilename()
        if path:
            #self.rtc.SaveFile(path, 1)
            self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
            f = file(path, 'w')
            f.write(self.FileTxt)
            f.close()
        else:
            self.OnFileSaveAs(evt)
            return
        
    def OnFileSaveAs(self, evt):
        ## wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)
        wildcard = "Files (*.c;*.cpp)|*.c;*.cpp"
        dlg = wx.FileDialog(self, "Choose a filename", wildcard=wildcard, style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:

                ## fileType = types[dlg.GetFilterIndex()]
                ## ext = rt.RichTextBuffer.FindHandlerByType(fileType).GetExtension()
                ## if not path.endswith(ext):
                ##     path += '.' + ext

                # auto add file extention
                if wx.Platform == "__WXMSW__":
                    if path.split('.')[-1] == 'c' and self.FileFlag == 1:
                        path = path.split('.')[0] + ".cpp"
                    if path.split('.')[-1] == 'cpp' and self.FileFlag == 0:
                        path = path.split('.')[0] + ".c"
                    if path.split('.')[-1] != 'c' and path.split('.')[-1] != 'cpp':
                        if self.FileFlag == 0:
                            path += ".c"
                        else:
                            path += ".cpp"

                else:
                    if path.split('.')[-1] == 'c' and self.FileFlag == 1:
                        path = path.split('.')[0] + ".cpp"
                    if path.split('.')[-1] == 'cpp' and self.FileFlag == 0:
                        path = path.split('.')[0] + ".c"
                    if path.split('.')[-1] != 'c' and path.split('.')[-1] != 'cpp':
                        if self.FileFlag == 0:
                            path += ".c"
                        else:
                            path += ".cpp"

                #self.rtc.SaveFile(path, fileType)
                self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
                f = file(path, 'w')
                f.write(str(self.FileTxt))
                f.close()
                self.rtc.SetFilename(path)
                titleTxt = "[" + path + "] - " + Version
                wx.CallAfter(self.UpdateTitle, titleTxt)
        dlg.Destroy()
                
    def OnExit(self, evt):
        if self.WarningDlg(evt):
            self.Destroy()

    def OnKeyUp(self, evt):
        if evt.GetKeyCode() == wx.WXK_SPACE:
            self.SyntaxHighlight()
        if evt.GetKeyCode() == wx.WXK_RETURN:
            self.AutoIndent()
            self.SyntaxHighlight()
        if evt.GetKeyCode() == wx.WXK_TAB:
            self.TabToSpace()
        if evt.GetKeyCode() == wx.WXK_BACK:
            self.DelPrevTab()
        # if evt.GetKeyCode() == wx.WXK_DELETE:
        #     self.DelNextTab()

    def OnForceExit(self, evt):
        sys.exit(0)

    def OnRun(self, evt):
        # compile the exist file in its same directory
        OrigFilePath = ""
        if self.rtc.GetFilename():
            OrigFilePath = self.rtc.GetFilename() #.encode("utf-8")

        # get tmp source file path
        if self.FileFlag == 0:
            CC = "gcc"
            FilePath = TmpBin + ".c"
        elif self.FileFlag == 1:
            CC = "g++"
            FilePath = TmpBin + ".cpp"

        # delete old tmp files
        if wx.Platform == "__WXMSW__":
            os.system("del C:\\foo*")
        else:
            os.system("rm -rf /tmp/foo* > /dev/null 2>&1")

        # save file: tmp var FileTxt shoule be used here, but not self.FileTxt, for the change is not write into orig file
        # self.rtc.SaveFile(FilePath, 1)
        FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
        f = file(FilePath, 'w')
        f.write(FileTxt)
        f.close()

        os.system(CC + " -Wall " + FilePath + " -o " + TmpBin + " > " + TmpLog + " 2>&1")

        # recover to the orig file path if compile an exist file
        if OrigFilePath:
            self.rtc.SetFilename(OrigFilePath)

        if wx.Platform == "__WXMSW__":
            if os.path.isfile(TmpBin + ".exe"):
                os.system("cmd /C " + TmpBin)
                self.log.SetDefaultStyle(wx.TextAttr("black",wx.NullColor))
            else:
                self.log.SetDefaultStyle(wx.TextAttr("red",wx.NullColor))
            info = os.popen("type " + TmpLog).read()
            date = os.popen("time /t").read()
            self.log.SetValue("************ Build Time: " + date.split("\n")[0] + " ************\n")
            self.log.AppendText(info + "\n") 
        else:
            if os.path.isfile(TmpBin):
                gwin.RunComm(TmpBin)
                self.log.SetDefaultStyle(wx.TextAttr("black",wx.NullColor))
            else:
                self.log.SetDefaultStyle(wx.TextAttr("red",wx.NullColor))
            info = os.popen("cat " + TmpLog).read()
            date = os.popen("date").read()
            self.log.SetValue("************ Build Time: " + date.split(" ")[4] + " ************\n")
            self.log.AppendText(info + "\n")

    def OnLock(self, evt):
        if self.lock:
            self.rtc.SetEditable(True)
            self.CtrlMenuBars(ID_MB_LIST, True)
            self.CtrlToolBars(ID_TB_LIST, True)
            wx.CallAfter(self.UpdateStatus, "Unlock edit", 0)
            self.lock = False
        else:
            self.rtc.SetEditable(False)
            self.CtrlMenuBars(ID_MB_LIST, False)
            self.CtrlToolBars(ID_TB_LIST, False)
            wx.CallAfter(self.UpdateStatus, "Lock edit", 0)
            self.lock = True

    def OnUpdateLock(self, evt):
        evt.Check(self.lock)

    def OnFullScreen(self, evt):
        if self.FullScreen:
            self.ShowFullScreen(False)
            self.FullScreen = False
        else:
            self.ShowFullScreen(True, wx.FULLSCREEN_NOBORDER | wx.FULLSCREEN_NOCAPTION)
            self.FullScreen = True

    def OnUpdateFullScreen(self, evt):
        evt.Check(self.FullScreen)

    def OnShowFind(self, evt):
        data = wx.FindReplaceData()

        # set down to end to find as defautl
        data.SetFlags(wx.FR_DOWN) 

        dlg = wx.FindReplaceDialog(self, data, "Find", wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD)
        dlg.data = data  # save a reference to it...
        dlg.Show(True)

    def OnShowReplace(self, evt):
        data = wx.FindReplaceData()

        # set down to end to find as defautl
        data.SetFlags(wx.FR_DOWN) 

        dlg = wx.FindReplaceDialog(self, data, "Replace", wx.FR_REPLACEDIALOG | wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD)
        dlg.data = data  # save a reference to it...
        dlg.Show(True)

    def OnFind(self, evt):
        start = self.rtc.GetInsertionPoint()
        end = self.rtc.GetLastPosition()

        # case unsensitive
        textStr = self.rtc.GetRange(0, end).lower()
        findTxt = evt.GetFindString().lower()

        # down to end to find
        if evt.GetFlags() == 1:
            loc = textStr.find(findTxt, start)

        # up to beginning to find
        else:
            loc = textStr.rfind(findTxt, 0, start)

        # not found and start at beginning
        if loc == -1 and start != 0:
            if evt.GetFlags() == 1:
                loc = textStr.find(findTxt, 0)
            else:
                loc = textStr.rfind(findTxt, 0, end)

        if loc == -1:
            statusTxt = 'Not Found "' + findTxt + '"'
            wx.CallAfter(self.UpdateStatus, statusTxt, 0)
        else:
            self.rtc.ShowPosition(loc)
            self.rtc.SetSelection(loc, loc + len(findTxt))


    def OnReplace(self, evt):
        start = self.rtc.GetInsertionPoint()
        end = self.rtc.GetLastPosition()

        # case sensitive
        replaceTxt = evt.GetReplaceString()
        findTxt = evt.GetFindString()
        textStr = self.rtc.GetRange(0, end)

        # down to end to find
        if evt.GetFlags() == 1:
            loc = textStr.find(findTxt, start)
        # up to beginning to find
        else:
            loc = textStr.rfind(findTxt, 0, start)

        # not found and start at beginning
        if loc == -1 and start != 0:
            if evt.GetFlags() == 1:
                loc = textStr.find(findTxt, 0)
            else:
                loc = textStr.rfind(findTxt, 0, end)

        if loc == -1:
            statusTxt = 'Not Found "' + findTxt + '"'
            wx.CallAfter(self.UpdateStatus, statusTxt, 0)
        else:
            self.rtc.ShowPosition(loc)
            self.rtc.SetSelection(loc, loc + len(findTxt))

            # replace and select again
            self.rtc.Replace(loc, loc + len(findTxt), replaceTxt)
            self.rtc.SetSelection(loc, loc + len(replaceTxt))

    def OnReplaceAll(self, evt):
        count = 0
        start = 0
        flag = True

        end = self.rtc.GetLastPosition()

        # case sensitive
        replaceTxt = evt.GetReplaceString()
        findTxt = evt.GetFindString()

        while flag:
            # case sensitive, and textStr will change after replace 
            textStr = self.rtc.GetRange(0, end)
            loc = textStr.find(findTxt, start, end)
            if loc == -1 or start >= end:
                break
            self.rtc.ShowPosition(loc)
            self.rtc.SetSelection(loc, loc + len(findTxt))
            self.rtc.Replace(loc, loc + len(findTxt), replaceTxt)
            count += 1
            start = loc + len(replaceTxt)

            # after textStr changed, end need to be updated too
            end = self.rtc.GetLastPosition()

        if count > 0:
             if count == 1:
                 statusTxt = 'Total replaced ' + str(count) + ' time'
             else:
                 statusTxt = 'Total replaced ' + str(count) + ' times'
             wx.CallAfter(self.UpdateStatus, statusTxt, 0)
        else:
            statusTxt = 'Not Found "' + findTxt + '"'
            wx.CallAfter(self.UpdateStatus, statusTxt, 0)
 
        # after finished replace, close itself
        #evt.GetDialog().Destroy()

    def OnFindClose(self, evt):
        evt.GetDialog().Destroy()

    def OnAbout(self, evt):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = Version.split(" ")[0]
        info.Version = Version.split(" ")[1]
        info.Copyright = "(C) 2011 Zechao Wang"
        info.Description = wordwrap("The \"wxgcc\" is a GUI toolkit for GCC based wxPython which can be used under Windows and Linux, with that tool user can create and compile a C/C++ program very fast.", 350, wx.ClientDC(self))
        info.WebSite = ("http://code.google.com/p/wxgcc/", "wxgcc home page")
        info.Developers = [ "Zechao Wang <zwang@ucrobotics.com>" ]

        info.License = wordwrap(LicenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def OnCheckUpdate(self, evt):
        url = "http://code.google.com/p/wxgcc/downloads/list"
        webbrowser.open(url)

    def ForwardEvent(self, evt):
        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.rtc.ProcessEvent(evt)

        # get line info
        RangeTxt = self.rtc.GetRange(0, self.rtc.GetInsertionPoint())
        PositionInfo =  "Row: " + str(len(RangeTxt.split('\n'))) + "    |    " + "Col: " + str(len(RangeTxt.split('\n')[-1])) + "    |    " + "Total Line Numbers: " + str(self.rtc.GetNumberOfLines())

        # update status bar
        wx.CallAfter(self.UpdateStatus, PositionInfo, 1)

    def SyntaxHighlight(self):
        end = self.rtc.GetLastPosition()
        textStr = self.rtc.GetRange(0, end).lower()

        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)

        # First: set system default colour
        start = 0
        SysColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUTEXT)
        attr.SetTextColour(SysColor)
        self.rtc.SetStyle((start,end), attr)

        # Second: set macro definition colour
        attr.SetTextColour(DefColor)
        start = 0
        while True:
            loc = textStr.find('#', start, end)
            if loc == -1 or start >= end:
                break
            locend = loc + 1
            while locend < end and textStr[locend] != '\n':
                locend += 1
            self.rtc.SetStyle((loc,locend), attr)
            start = locend + 1

        # Third: set keyword colour
        attr.SetTextColour(KeyColor)
        for key in KeyWords.split(' '):
            start = 0
            while True:
                loc = textStr.find(key, start, end)
                if loc == -1 or start >= end:
                    break
                locend = loc + len(key) 
                if loc == 0 and textStr[locend] == ' ':
                    self.rtc.SetStyle((loc,locend), attr)
                if loc > 0 and locend < end and textStr[loc-1] not in ArrList and textStr[locend] not in ArrList:
                    self.rtc.SetStyle((loc,locend), attr)
                start = locend 

        # Four: set string colour
        attr.SetTextColour(StrColor)
        arr1 = []
        start = 0
        while start <= end:
            loc = textStr.find('"', start, end)
            if loc == -1 or start >= end:
                break
            arr1.append(loc)
            start = loc + 1
        if len(arr1) > 0 and len(arr1) % 2 != 0:
            arr1.append(end)
        i = len(arr1)
        j = 0
        while i > 0 and j < i:
            self.rtc.SetStyle((arr1[j], arr1[j+1]+1), attr)
            j += 2

        arr2 = []
        start = 0
        while start <= end:
            loc = textStr.find("'", start, end)
            if loc == -1 or start >= end:
                break
            arr2.append(loc)
            start = loc + 1
        if len(arr2) > 0 and len(arr2) % 2 != 0:
            arr2.append(end)
        i = len(arr2)
        j = 0
        while i > 0 and j < i:
            self.rtc.SetStyle((arr2[j], arr2[j+1]+1), attr)
            j += 2
            
        # Five: set comment colour
        attr.SetTextColour(ComColor)
        start = 0
        while True:
            loc = textStr.find('//', start, end)
            if loc == -1 or start >= end:
                break
            locend = loc + 1
            while locend < end and textStr[locend] != '\n':
                locend += 1
            self.rtc.SetStyle((loc,locend), attr)
            start = locend + 1

        arr3 = []
        start = 0
        while start <= end:
            loc = textStr.find('/*', start, end)
            if loc == -1 or start >= end:
                break
            if textStr[loc-1] != '/': #for case: //*point = a
                arr3.append(loc)
            start = loc + 1

        arr4 = []
        start = 0
        while start <= end:
            loc = textStr.find('*/', start, end)
            if loc == -1 or start >= end:
                break
            arr4.append(loc)
            start = loc + 1

        if len(arr3) == len(arr4) and len(arr3) > 0:
            i = len(arr3)
            j = 0
            while j < i:
                self.rtc.SetStyle((arr3[j], arr4[j]+2), attr)
                j += 1
        if len(arr3) > len(arr4):
            arr4.append(end)
            i = len(arr4)
            j = 0
            while j < i:
                self.rtc.SetStyle((arr3[j], arr4[j]+2), attr)
                j += 1
        if len(arr3) < len(arr4) and len(arr3) > 0:
            i = len(arr3)
            j = 0
            while j < i:
                self.rtc.SetStyle((arr3[j], arr4[j]+2), attr)
                j += 1

    def TabToSpace(self):
        start = 0
        end = self.rtc.GetLastPosition()
        while True:
            # textStr will change after replace for end position is changed
            textStr = self.rtc.GetRange(0, end)
            loc = textStr.find('\t', start, end)
            if loc == -1 or start >= end:
                break
            self.rtc.ShowPosition(loc)
            self.rtc.SetSelection(loc, loc + 1)
            self.rtc.Replace(loc, loc + 1, " " * TabLen)
            start = loc + TabLen
            # after textStr changed, end need to be updated too
            end = self.rtc.GetLastPosition()

    def AutoIndent(self):
        RangeTxt = self.rtc.GetRange(0, self.rtc.GetInsertionPoint())
        # get the space number in the beginning of previous line
        SpaceNum = 0
        if len(RangeTxt.split('\n')) > 1:
            for c in RangeTxt.split('\n')[-2]:
                if c == " ":
                    SpaceNum += 1
                else:
                   break
        # auto indent
        if SpaceNum > 0:
            self.rtc.WriteText(" " * SpaceNum)

    def DelPrevTab(self):
        RangeTxt = self.rtc.GetRange(0, self.rtc.GetInsertionPoint())
        # get the space number in the previous of current point
        SpaceNum = 0
        loc = self.rtc.GetInsertionPoint()
        i = loc
        while i > 0 and RangeTxt[i - 1] == " ":
            i -= 1
            SpaceNum += 1
        if SpaceNum % 8 == 7: # OnkeyUp need 7 space, OnKeyDown need 8 space
            if loc == 7:
                self.rtc.ShowPosition(0)
                self.rtc.SetSelection(0, 7)
                self.rtc.Replace(0, 7, " ")
            else:
                self.rtc.ShowPosition(loc - 8)
                self.rtc.SetSelection(loc - 8, loc)
                self.rtc.Replace(loc - 8, loc, RangeTxt[loc - 8])

    """
    def DelNextTab(self):
        loc = self.rtc.GetInsertionPoint()
        end = self.rtc.GetLastPosition()
        i = loc
        RangeTxt = self.rtc.GetRange(0, end)
        # get the space number in the next of current point
        SpaceNum = 0
        while i < end and RangeTxt[i] == " ":
            i += 1
            SpaceNum += 1
        print SpaceNum
        if SpaceNum >= 7 and SpaceNum % 8 != 0: # OnkeyUp need 7 space, OnKeyDown need 8 space
            if loc == end - 7:
                self.rtc.ShowPosition(loc)
                self.rtc.SetSelection(loc, end)
                self.rtc.Replace(loc, end, " ")
            else:
                self.rtc.ShowPosition(loc)
                self.rtc.SetSelection(loc, loc + 8)
                self.rtc.Replace(loc, loc + 8, RangeTxt[loc + 8])
    """

    def MakeMenuBar(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_MENU, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
            
        fileMenu = wx.Menu()
        doBind( fileMenu.Append(ID_MB_NEW_C, "&New C\tCtrl+N", "Create a C file"), self.OnNewC )
        doBind( fileMenu.Append(ID_MB_NEW_CPP, "&New C++\tCtrl+P", "Create a C++ file"), self.OnNewCpp )
        doBind( fileMenu.Append(ID_MB_OPEN, "&Open\tCtrl+O", "Open a file"), self.OnFileOpen )
	fileMenu.AppendSeparator()
        doBind( fileMenu.Append(-1, "&Save\tCtrl+S", "Save a file"), self.OnFileSave )
        doBind( fileMenu.Append(-1, "&Save As...\tF12", "Save to a new file"), self.OnFileSaveAs )
        fileMenu.AppendSeparator()
        doBind( fileMenu.Append(-1, "E&xit\tCtrl+Q", "Exit this program"), self.OnExit )
        doBind( fileMenu.Append(-1, "&Force Exit\tShift+Ctrl+Q", "Force to exit"), self.OnForceExit )
        
        editMenu = wx.Menu()
        doBind( editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl+Z"), self.ForwardEvent, self.ForwardEvent)
        doBind( editMenu.Append(wx.ID_REDO, "&Redo\tCtrl+Y"), self.ForwardEvent, self.ForwardEvent )
        editMenu.AppendSeparator()
        doBind( editMenu.Append(wx.ID_CUT, "Cu&t\tCtrl+X"), self.ForwardEvent, self.ForwardEvent )
        doBind( editMenu.Append(wx.ID_COPY, "&Copy\tCtrl+C"), self.ForwardEvent, self.ForwardEvent)
        doBind( editMenu.Append(wx.ID_PASTE, "&Paste\tCtrl+V"), self.ForwardEvent, self.ForwardEvent)
        #doBind( editMenu.Append(wx.ID_CLEAR, "&Delete\tDel"), self.ForwardEvent, self.ForwardEvent)
        editMenu.AppendSeparator()
        doBind( editMenu.Append(wx.ID_SELECTALL, "Select A&ll\tCtrl+A"), self.ForwardEvent, self.ForwardEvent )

        toolMenu = wx.Menu()
        doBind( toolMenu.Append(-1, "&Find...\tCtrl+F"), self.OnShowFind )
        doBind( toolMenu.Append(ID_MB_REPLACE, "&Replace...\tCtrl+R"), self.OnShowReplace )
        toolMenu.AppendSeparator()
        doBind( toolMenu.AppendCheckItem(-1, "&Lock Edit\tCtrl+L", "Lock edit"), self.OnLock, self.OnUpdateLock)
        doBind( toolMenu.AppendCheckItem(-1, "&Full Screen\tF11", "Set frame full screen"), self.OnFullScreen, self.OnUpdateFullScreen)
        toolMenu.AppendSeparator()
        doBind( toolMenu.Append(ID_MB_RUN, "&Run C/C++\tF5", "Compile and run C/C++ files"), self.OnRun)

        helpMenu = wx.Menu()
        doBind( helpMenu.Append(-1, "&About"), self.OnAbout)
        doBind( helpMenu.Append(-1, "&Check Update"), self.OnCheckUpdate)
        
        self.mb = wx.MenuBar()
        self.mb.Append(fileMenu, "&File")
        self.mb.Append(editMenu, "&Edit")
        self.mb.Append(toolMenu, "&Tool")
        self.mb.Append(helpMenu, "&Help")
        self.SetMenuBar(self.mb)

    def MakeToolBar(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        
        self.tbar = self.CreateToolBar()
        doBind( self.tbar.AddTool(ID_TB_NEW_C, wx.Bitmap("./icon/c.png"), shortHelpString="New C"), self.OnNewC)
        doBind( self.tbar.AddTool(ID_TB_NEW_CPP, wx.Bitmap("./icon/cpp.png"), shortHelpString="New C++"), self.OnNewCpp)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_OPEN, wx.Bitmap("./icon/open.png"), shortHelpString="Open"), self.OnFileOpen)
        doBind( self.tbar.AddTool(-1, wx.Bitmap("./icon/save.png"), shortHelpString="Save"), self.OnFileSave)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(wx.ID_UNDO, wx.Bitmap("./icon/undo.png"), shortHelpString="Undo"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.tbar.AddTool(wx.ID_REDO, wx.Bitmap("./icon/redo.png"), shortHelpString="Redo"), self.ForwardEvent, self.ForwardEvent)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(-1, wx.Bitmap("./icon/find.png"), shortHelpString="Find"), self.OnShowFind)
        doBind( self.tbar.AddTool(ID_TB_REPLACE, wx.Bitmap("./icon/replace.png"), shortHelpString="Replace"), self.OnShowReplace)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_RUN, wx.Bitmap("./icon/run.png"), shortHelpString="Run C/C++"), self.OnRun)
        doBind( self.tbar.AddTool(-1, wx.Bitmap("./icon/lock.png"), isToggle=True, shortHelpString="Lock/Unlock Edit"), self.OnLock, self.OnUpdateLock)

        self.tbar.Realize()

    def UpdateStatus(self, msg, num):
        self.StatusBar.SetStatusText(msg, num)

    def UpdateTitle(self, msg):
        self.SetTitle(msg)

    def CtrlMenuBars(self, idlist, flag):
        for iditem in idlist:
            self.mb.Enable(iditem, flag)

    def CtrlToolBars(self, idlist, flag):
        for iditem in idlist:
            self.tbar.EnableTool(iditem, flag)

"""
class MyThread(threading.Thread):
    def __init__(self, rtc):
        self.active = False
        self.rtc = rtc
        threading.Thread.__init__(self)

    def run(self):
        # do something ...
        pass
"""

#----------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.PySimpleApp()
    mwin = WxgccFrame(None)
    mwin.Show(True)
    gwin = GtkWin()
    app.MainLoop()

