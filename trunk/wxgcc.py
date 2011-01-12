#!/bin/env python
# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------
# Name:         wxgcc.py
# Purpose:      A rich text editor with C/C++ programs compiling support.
#
# Author:       Zechao Wang <zwang@ucrobotics.com>
#
# Created:      26-Dec-2010
# RCS-ID:       
# Copyright:    (c) 2010 by Zechao Wang
# Licence:      GPLV2
#----------------------------------------------------------------------------

import os
import sys
import wx
import wx.aui
import wx.richtext as rt
from wx.lib.wordwrap import wordwrap

TmpBin = "/tmp/foo"
TmpLog = "/tmp/foo.log"
TmpRes = "/tmp/foo.res"

ID_MB_NEW             = 11
ID_MB_NEW_C           = 12
ID_MB_NEW_CPP         = 13
ID_MB_OPEN            = 14
#ID_MB_SAVE           = 15
#ID_MB_SAVE_AS        = 16

#ID_MB_UNDO           = 21  # wx.ID_UNDO
#ID_MB_REDO           = 22  # wx.ID_REDO
#ID_MB_CUT            = 23  # wx.ID_CUT
#ID_MB_PASTE          = 24  # wx.ID_PASTE
#ID_MB_DEL            = 25  # wx.ID_CLEAR

ID_MB_BOLD            = 31
ID_MB_ITALIC          = 32
ID_MB_UNDERLINE       = 33
ID_MB_LEFT            = 34
ID_MB_CENTER          = 35
ID_MB_RIGHT           = 36
ID_MB_INDENT_MORE     = 37
ID_MB_INDENT_LESS     = 38
ID_MB_INCREASE_SPACE  = 39
ID_MB_DECREASE_SPACE  = 40
ID_MB_NORMAL_LINE     = 41
ID_MB_MORE_LINE       = 42
ID_MB_DOUBLE_LINE     = 43
ID_MB_FONT            = 44

ID_MB_REPLACE         = 51
ID_MB_IMG             = 52
ID_MB_RUN             = 53

ID_TB_NEW             = 61
ID_TB_NEW_C           = 62
ID_TB_NEW_CPP         = 63
ID_TB_OPEN            = 64
#ID_TB_SAVE           = 65
#ID_TB_UNDO           = 66
#ID_TB_REDO           = 67
ID_TB_BOLD            = 68
ID_TB_ITALIC          = 69
ID_TB_UNDERLINE       = 70
ID_TB_LEFT            = 71
ID_TB_CENTER          = 72
ID_TB_RIGHT           = 73
ID_TB_INDENT_LESS     = 74
ID_TB_INDENT_MORE     = 75
ID_TB_FONT            = 76
ID_TB_COLOR           = 77
ID_TB_IMG             = 78
ID_TB_RUN             = 79
ID_TB_REPLACE         = 80

ID_MB_LIST = [ID_MB_NEW, ID_MB_NEW_C, ID_MB_NEW_CPP, ID_MB_OPEN, wx.ID_UNDO, wx.ID_REDO, wx.ID_CUT, wx.ID_PASTE, ID_MB_BOLD, ID_MB_ITALIC, ID_MB_UNDERLINE, ID_MB_LEFT, ID_MB_CENTER, ID_MB_RIGHT, ID_MB_INDENT_MORE, ID_MB_INDENT_LESS, ID_MB_INCREASE_SPACE, ID_MB_DECREASE_SPACE, ID_MB_NORMAL_LINE, ID_MB_MORE_LINE, ID_MB_DOUBLE_LINE, ID_MB_FONT, ID_MB_REPLACE, ID_MB_IMG, ID_MB_RUN]

ID_TB_LIST = [ID_TB_NEW, ID_TB_NEW_C, ID_TB_NEW_CPP, ID_TB_OPEN, wx.ID_UNDO, wx.ID_REDO, ID_TB_BOLD, ID_TB_ITALIC, ID_TB_UNDERLINE, ID_TB_LEFT, ID_TB_CENTER, ID_TB_RIGHT, ID_TB_INDENT_LESS, ID_TB_INDENT_MORE, ID_TB_FONT, ID_TB_COLOR, ID_TB_IMG, ID_TB_RUN, ID_TB_REPLACE]

licenseText = """
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

#----------------------------------------------------------------------

class WxgccFrame(wx.Frame):
    def __init__(self, parent, id=-1):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title='wxPython GCC ToolKit 1.5', size=(800, 600), style = wx.DEFAULT_FRAME_STYLE)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        # set the frame icon
        self.SetIcon(wx.Icon('./icon/wxgcc.ico', wx.BITMAP_TYPE_ICO))

        # set the window center
        self.Center()

        self.FileFlag = 0
        self.FileTxt = ""
        self.lock = False
        self.FullScreen = False
        self.panel = wx.Panel(self, wx.ID_ANY)

        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(self.panel)

        self.MakeMenuBar()
        self.MakeToolBar()
        self.StatusBar = self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(2)
        #self.StatusBar.SetStatusWidths([-3,-2])

        # create log box
        self.log = wx.TextCtrl(self.panel, -1, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL, size=(-1,200))

        # create richText box and init: http://docs.wxwidgets.org/stable/wx_wxrichtextctrl.html
        self.rtc = rt.RichTextCtrl(self.panel, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER, size=(-1,300));
        wx.CallAfter(self.rtc.SetFocus)
        #self.InitC()
        self.rtc.SetFilename("")

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

        self.rtc.SetBackgroundColour((207,247,207))
        self.log.SetBackgroundColour((207,247,207))

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

        self.rtc.WriteText("    printf(\"Hello C !\\n\");")
        self.rtc.Newline()

        self.rtc.WriteText("    return 0;")
        self.rtc.Newline()

        self.rtc.WriteText("}")

        self.rtc.Thaw()

    def InitCpp(self):
        self.rtc.Freeze()

        self.rtc.SetBackgroundColour((207,207,247))
        self.log.SetBackgroundColour((207,207,247))

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

        self.rtc.WriteText("    std::cout << \"Hello C++ !\\n\";")
        self.rtc.Newline()

        self.rtc.WriteText("    return 0;")
        self.rtc.Newline()

        self.rtc.WriteText("}")

        self.rtc.Thaw()

    def OnURL(self, evt):
        wx.MessageBox(evt.GetString(), "URL Clicked")

    def OnNew(self, evt):
        if self.WarningDlg(evt):
            self.rtc.Clear()
            self.log.Clear()
            self.rtc.SetBackgroundColour((255,255,255))
            self.log.SetBackgroundColour((255,255,255))
            self.FileTxt = ""
            self.FileFlag = 0
            self.rtc.SetFilename("")
            self.rtc.SetInsertionPoint(0)
            titleTxt = "[Untitled Txt File] - WxGcc"
            wx.CallAfter(self.UpdateTitle, titleTxt)
            self.CtrlRunBars(False)
            self.CtrlImgBars(True)
        
    def OnNewC(self, evt):
        if self.WarningDlg(evt):
            self.rtc.Clear()
            self.log.Clear()
            self.InitC()
            self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
            self.FileFlag = 1
            self.rtc.SetFilename("")
            self.rtc.SetInsertionPoint(0)
            titleTxt = "[Untitled C File] - WxGcc"
            wx.CallAfter(self.UpdateTitle, titleTxt)
            #wx.CallAfter(self.UpdateStatus, "")
            self.CtrlRunBars(True)
            self.CtrlImgBars(False)

    def OnNewCpp(self, evt):
        if self.WarningDlg(evt):
            self.rtc.Clear()
            self.log.Clear()
            self.InitCpp()
            self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
            self.FileFlag = 2
            self.rtc.SetFilename("")
            self.rtc.SetInsertionPoint(0)
            titleTxt = "[Untitled C++ File] - WxGcc"
            wx.CallAfter(self.UpdateTitle, titleTxt)
            #wx.CallAfter(self.UpdateStatus, "New C++ file")
            self.CtrlRunBars(True)
            self.CtrlImgBars(False)

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
        ##wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
        wildcard = "Files (*.c;*.cpp;*.txt)|*.c;*.cpp;*.txt"
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
                    titleTxt = "[" + path + "] - WxGcc"
                    wx.CallAfter(self.UpdateTitle, titleTxt)

                    if path.split('.')[-1] == 'c':
                        self.FileFlag = 1
                        self.log.Clear()
                        self.rtc.SetBackgroundColour((207,247,207))
                        self.log.SetBackgroundColour((207,247,207))
                        self.CtrlRunBars(True)
                        self.CtrlImgBars(False)
                    elif path.split('.')[-1] == 'cpp':
                        self.FileFlag = 2
                        self.log.Clear()
                        self.rtc.SetBackgroundColour((207,207,247))
                        self.log.SetBackgroundColour((207,207,247))
                        self.CtrlRunBars(True)
                        self.CtrlImgBars(False)
                    else:
                        self.FileFlag = 0
                        self.log.Clear()
                        self.rtc.SetBackgroundColour((255,255,255))
                        self.log.SetBackgroundColour((255,255,255))
                        self.CtrlRunBars(False)
                        self.CtrlImgBars(True)

        dlg.Destroy()
        
    def OnFileSave(self, evt):
        path = self.rtc.GetFilename()
        if path:
            #self.rtc.SaveFile(path, 1)
            self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
            f = file(path, 'w')
            f.write(self.FileTxt)
            f.close()
            titleTxt = "[" + path + "] - WxGcc"
            wx.CallAfter(self.UpdateTitle, titleTxt)
        else:
            self.OnFileSaveAs(evt)
            return
        
    def OnFileSaveAs(self, evt):
        ##wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)
        wildcard = "Files (*.c;*.cpp;*.txt)|*.c;*.cpp;*.txt"
        dlg = wx.FileDialog(self, "Choose a filename", wildcard=wildcard, style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:

                ##fileType = types[dlg.GetFilterIndex()]
                ##ext = rt.RichTextBuffer.FindHandlerByType(fileType).GetExtension()
                ##if not path.endswith(ext):
                ##    path += '.' + ext

                #self.rtc.SaveFile(path, fileType)
                self.FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
                f = file(path, 'w')
                f.write(str(self.FileTxt))
                f.close()
                titleTxt = "[" + path + "] - WxGcc"
                wx.CallAfter(self.UpdateTitle, titleTxt)

        dlg.Destroy()
                
    def OnExit(self, evt):
        if self.WarningDlg(evt):
            self.Destroy()

    def OnForceExit(self, evt):
        sys.exit(0)

    def OnBold(self, evt):
        self.rtc.ApplyBoldToSelection()
        
    def OnItalic(self, evt): 
        self.rtc.ApplyItalicToSelection()
        
    def OnUnderline(self, evt):
        self.rtc.ApplyUnderlineToSelection()
        
    def OnAlignLeft(self, evt):
        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_LEFT)
        
    def OnAlignRight(self, evt):
        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_RIGHT)
        
    def OnAlignCenter(self, evt):
        self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_CENTRE)
        
    def OnIndentMore(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetLeftIndent(attr.GetLeftIndent() + 100)
            attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)
        
    def OnIndentLess(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

        if attr.GetLeftIndent() >= 100:
            attr.SetLeftIndent(attr.GetLeftIndent() - 100)
            attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)
        
    def OnParagraphSpacingMore(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
            attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
            self.rtc.SetStyle(r, attr)
        
    def OnParagraphSpacingLess(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            if attr.GetParagraphSpacingAfter() >= 20:
                attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
                attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
                self.rtc.SetStyle(r, attr)
        
    def OnLineSpacingSingle(self, evt): 
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(10)
            self.rtc.SetStyle(r, attr)
                
    def OnLineSpacingHalf(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(15)
            self.rtc.SetStyle(r, attr)
        
    def OnLineSpacingDouble(self, evt):
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(20)
            self.rtc.SetStyle(r, attr)

    def OnFont(self, evt):
        if not self.rtc.HasSelection():
            return

        r = self.rtc.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_FONT)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(rt.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.rtc.SetStyle(r, attr)
        dlg.Destroy()

    def OnColour(self, evt):
        colourData = wx.ColourData()
        attr = rt.TextAttrEx()
        attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            colourData.SetColour(attr.GetTextColour())

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colourData = dlg.GetColourData()
            colour = colourData.GetColour()
            if colour:
                if not self.rtc.HasSelection():
                    self.rtc.BeginTextColour(colour)
                else:
                    r = self.rtc.GetSelectionRange()
                    attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
                    attr.SetTextColour(colour)
                    self.rtc.SetStyle(r, attr)
        dlg.Destroy()

    def OnImg(self, evt):
        wildcard = "Images (*.jpg;*.png;*.gif;*.bmp)|*.jpg;*.png;*.gif;*.bmp"
        dlg = wx.FileDialog(self, "Choose a image", wildcard=wildcard, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                self.rtc.WriteImage(wx.Image(path, wx.BITMAP_TYPE_ANY))
        dlg.Destroy()

    def OnRun(self, evt):
        # compile the exist file in its same directory
        OrigFilePath = ""
        if self.rtc.GetFilename():
            OrigFilePath = self.rtc.GetFilename() #.encode("utf-8")

        # get tmp source file path
        if self.FileFlag == 1:
            CC = "gcc"
            FilePath = TmpBin + ".c"
        elif self.FileFlag == 2:
            CC = "g++"
            FilePath = TmpBin + ".cpp"

        # delete old tmp files
        os.system("rm -rf /tmp/foo* > /dev/null 2>&1")

        # save file: tmp var FileTxt shoule be used here, but not self.FileTxt, for the change is not write into orig file
        #self.rtc.SaveFile(FilePath, 1)
        FileTxt = self.rtc.GetRange(0, self.rtc.GetLastPosition()).encode("utf-8")
        f = file(FilePath, 'w')
        f.write(FileTxt)
        f.close()

        os.system(CC + " " + FilePath + " -o " + TmpBin + " > " + TmpLog + " 2>&1")

        # recover to the orig file path if compile an exist file
        if OrigFilePath:
            self.rtc.SetFilename(OrigFilePath)

        # get run log if compile success
        if os.path.isfile(TmpBin):
            os.system(TmpBin + " > " + TmpRes + " 2>&1")
            info = os.popen("cat " + TmpRes).read()
            self.log.SetDefaultStyle(wx.TextAttr("black",wx.NullColor))

        #get build log if compile failed
        else:
            info = os.popen("cat " + TmpLog).read()
            self.log.SetDefaultStyle(wx.TextAttr("red",wx.NullColor))

        # write log to log panel with timestamp
        date = os.popen("date").read()
        self.log.SetValue("************ Time: " + date.split(" ")[4] + " ************\n")
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
        info.Name = "wxgcc"
        info.Version = "1.5"
        info.Copyright = "(C) 2010 Zechao Wang"
        info.Description = wordwrap(
            "The \"wxgcc (wxPython GCC Compiler)\" is a simple C language compiler toolkit which used under Linux."
            "With that tool user can create and compile a C program very fast."
            
            "\n\nBesides a C compiler, it's also a rich text editor and support styled text and images editing.", 
            350, wx.ClientDC(self))
        info.WebSite = ("http://www.ucrobotics.com", "wxgcc home page")
        info.Developers = [ "Zechao Wang <zwang@ucrobotics.com>" ]

        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def OnUpdateBold(self, evt):
        evt.Check(self.rtc.IsSelectionBold())
    
    def OnUpdateItalic(self, evt): 
        evt.Check(self.rtc.IsSelectionItalics())
    
    def OnUpdateUnderline(self, evt): 
        evt.Check(self.rtc.IsSelectionUnderlined())
    
    def OnUpdateAlignLeft(self, evt):
        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_LEFT))
        
    def OnUpdateAlignCenter(self, evt):
        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_CENTRE))
        
    def OnUpdateAlignRight(self, evt):
        evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_RIGHT))
    
    def ForwardEvent(self, evt):
        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.rtc.ProcessEvent(evt)

        RangeTxt = self.rtc.GetRange(0, self.rtc.GetInsertionPoint())
        PositionInfo =  "Row: " + str(len(RangeTxt.split('\n'))) + "    |    " + "Col: " + str(len(RangeTxt.split('\n')[-1])) + "    |    " + "Total Line Numbers: " + str(self.rtc.GetNumberOfLines())
        wx.CallAfter(self.UpdateStatus, PositionInfo, 1)

    def MakeMenuBar(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_MENU, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
            
        fileMenu = wx.Menu()
        doBind( fileMenu.Append(ID_MB_NEW, "&New \tCtrl+T", "Create a Txt file"), self.OnNew )
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

        formatMenu = wx.Menu()
        doBind( formatMenu.AppendCheckItem(ID_MB_BOLD, "&Bold\tCtrl+B"), self.OnBold, self.OnUpdateBold)
        doBind( formatMenu.AppendCheckItem(ID_MB_ITALIC, "&Italic\tCtrl+I"), self.OnItalic, self.OnUpdateItalic)
        doBind( formatMenu.AppendCheckItem(ID_MB_UNDERLINE, "&Underline\tCtrl+U"), self.OnUnderline, self.OnUpdateUnderline)
        formatMenu.AppendSeparator()
        doBind( formatMenu.AppendCheckItem(ID_MB_LEFT, "L&eft Align"), self.OnAlignLeft, self.OnUpdateAlignLeft)
        doBind( formatMenu.AppendCheckItem(ID_MB_CENTER, "&Centre"), self.OnAlignCenter, self.OnUpdateAlignCenter)
        doBind( formatMenu.AppendCheckItem(ID_MB_RIGHT, "&Right Align"), self.OnAlignRight, self.OnUpdateAlignRight)
        formatMenu.AppendSeparator()
        doBind( formatMenu.Append(ID_MB_INDENT_MORE, "Indent &More"), self.OnIndentMore)
        doBind( formatMenu.Append(ID_MB_INDENT_LESS, "Indent &Less"), self.OnIndentLess)
        formatMenu.AppendSeparator()
        doBind( formatMenu.Append(ID_MB_INCREASE_SPACE, "Increase Paragraph &Spacing"), self.OnParagraphSpacingMore)
        doBind( formatMenu.Append(ID_MB_DECREASE_SPACE, "Decrease &Paragraph Spacing"), self.OnParagraphSpacingLess)
        formatMenu.AppendSeparator()
        doBind( formatMenu.Append(ID_MB_NORMAL_LINE, "Normal Line Spacing"), self.OnLineSpacingSingle)
        doBind( formatMenu.Append(ID_MB_MORE_LINE, "1.5 Line Spacing"), self.OnLineSpacingHalf)
        doBind( formatMenu.Append(ID_MB_DOUBLE_LINE, "Double Line Spacing"), self.OnLineSpacingDouble)
        formatMenu.AppendSeparator()
        doBind( formatMenu.Append(ID_MB_FONT, "&Font..."), self.OnFont)

        toolMenu = wx.Menu()
        doBind( toolMenu.Append(-1, "&Find...\tCtrl+F"), self.OnShowFind )
        doBind( toolMenu.Append(ID_MB_REPLACE, "&Replace...\tCtrl+R"), self.OnShowReplace )
        toolMenu.AppendSeparator()
        doBind( toolMenu.Append(ID_MB_IMG, "&Insert Images\tCtrl+M", "Insert images"), self.OnImg)
        doBind( toolMenu.Append(ID_MB_RUN, "&Run C/C++\tF5", "Compile and run C/C++ files"), self.OnRun)
        toolMenu.AppendSeparator()
        doBind( toolMenu.AppendCheckItem(-1, "&Lock Edit\tCtrl+L", "Lock edit"), self.OnLock, self.OnUpdateLock)
        doBind( toolMenu.AppendCheckItem(-1, "&Full Screen\tF11", "Set frame full screen"), self.OnFullScreen, self.OnUpdateFullScreen)

        helpMenu = wx.Menu()
        doBind( helpMenu.Append(-1, "&About"), self.OnAbout)
        
        self.mb = wx.MenuBar()
        self.mb.Append(fileMenu, "&File")
        self.mb.Append(editMenu, "&Edit")
        self.mb.Append(formatMenu, "F&ormat")
        self.mb.Append(toolMenu, "&Tool")
        self.mb.Append(helpMenu, "&Help")
        self.SetMenuBar(self.mb)

        self.mb.Enable(ID_MB_RUN, False)

    def MakeToolBar(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        
        self.tbar = self.CreateToolBar()
        doBind( self.tbar.AddTool(ID_TB_NEW, wx.Bitmap("./icon/new.png"), shortHelpString="New Txt"), self.OnNew)
        doBind( self.tbar.AddTool(ID_TB_NEW_C, wx.Bitmap("./icon/c.png"), shortHelpString="New C"), self.OnNewC)
        doBind( self.tbar.AddTool(ID_TB_NEW_CPP, wx.Bitmap("./icon/cpp.png"), shortHelpString="New C++"), self.OnNewCpp)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_OPEN, wx.Bitmap("./icon/open.png"), shortHelpString="Open"), self.OnFileOpen)
        doBind( self.tbar.AddTool(-1, wx.Bitmap("./icon/save.png"), shortHelpString="Save"), self.OnFileSave)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(wx.ID_UNDO, wx.Bitmap("./icon/undo.png"), shortHelpString="Undo"), self.ForwardEvent, self.ForwardEvent)
        doBind( self.tbar.AddTool(wx.ID_REDO, wx.Bitmap("./icon/redo.png"), shortHelpString="Redo"), self.ForwardEvent, self.ForwardEvent)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_BOLD, wx.Bitmap("./icon/bold.png"), isToggle=True, shortHelpString="Bold"), self.OnBold, self.OnUpdateBold)
        doBind( self.tbar.AddTool(ID_TB_ITALIC, wx.Bitmap("./icon/italic.png"), isToggle=True, shortHelpString="Italic"), self.OnItalic, self.OnUpdateItalic)
        doBind( self.tbar.AddTool(ID_TB_UNDERLINE, wx.Bitmap("./icon/underline.png"), isToggle=True, shortHelpString="Underline"), self.OnUnderline, self.OnUpdateUnderline)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_LEFT, wx.Bitmap("./icon/left.png"), isToggle=True, shortHelpString="Align Left"), self.OnAlignLeft, self.OnUpdateAlignLeft)
        doBind( self.tbar.AddTool(ID_TB_CENTER, wx.Bitmap("./icon/center.png"), isToggle=True, shortHelpString="Center"), self.OnAlignCenter, self.OnUpdateAlignCenter)
        doBind( self.tbar.AddTool(ID_TB_RIGHT, wx.Bitmap("./icon/right.png"), isToggle=True, shortHelpString="Align Right"), self.OnAlignRight, self.OnUpdateAlignRight)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_INDENT_LESS, wx.Bitmap("./icon/indent-less.png"), shortHelpString="Indent Less"), self.OnIndentLess)
        doBind( self.tbar.AddTool(ID_TB_INDENT_MORE, wx.Bitmap("./icon/indent-more.png"), shortHelpString="Indent More"), self.OnIndentMore)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_FONT, wx.Bitmap("./icon/font.png"),  shortHelpString="Font"), self.OnFont)
        doBind( self.tbar.AddTool(ID_TB_COLOR, wx.Bitmap("./icon/colour.png"), shortHelpString="Font Colour"), self.OnColour)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(ID_TB_IMG, wx.Bitmap("./icon/img.png"), shortHelpString="Insert Images"), self.OnImg)
        doBind( self.tbar.AddTool(ID_TB_RUN, wx.Bitmap("./icon/run.png"), shortHelpString="Run C/C++"), self.OnRun)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(-1, wx.Bitmap("./icon/find.png"), shortHelpString="Find"), self.OnShowFind)
        doBind( self.tbar.AddTool(ID_TB_REPLACE, wx.Bitmap("./icon/replace.png"), shortHelpString="Replace"), self.OnShowReplace)
        self.tbar.AddSeparator()
        doBind( self.tbar.AddTool(-1, wx.Bitmap("./icon/lock.png"), isToggle=True, shortHelpString="lock/unlock edit"), self.OnLock, self.OnUpdateLock)

        self.tbar.Realize()

        self.tbar.EnableTool(ID_TB_RUN, False)

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

    def CtrlRunBars(self, flag):
        self.mb.Enable(ID_MB_RUN, flag)
        self.tbar.EnableTool(ID_TB_RUN, flag)

    def CtrlImgBars(self, flag):
        self.mb.Enable(ID_MB_IMG, flag)
        self.tbar.EnableTool(ID_TB_IMG, flag)


#----------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.PySimpleApp()
    mwin = WxgccFrame(None)
    mwin.Show(True)
    app.MainLoop()

