#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 on Thu Jul  1 16:18:38 2010

import wx
import wx.lib.sized_controls as sc

#pubsub
from wx.lib.pubsub import Publisher as pub

import sqlite3

import ui.widgets
        
# begin wxGlade: extracode
# end wxGlade
import os
from settings import PATH_ICONS, WEIGHT_POWER


class DefineSystemDialog(wx.Dialog):
    def __init__(self, parent, id, compounds_data):
        
        # begin wxGlade: MyFrame.__init__
        #kwds["style"] = wx.DEFAULT_FRAME_STYLE ^ ( wx.RESIZE_BORDER | 
        #                                    wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX )   

        wx.Dialog.__init__(self, parent, id)
        self.SetBackgroundColour(wx.NullColour) #hack for win32

        #database handler
        conn = sqlite3.connect('gpec.sqlite')
        self.c = conn.cursor()
        
        #cache database
        self.c.execute("select id, name, tc, pc, vc, acentric_factor, vc_rat from compounds")
        self.list_base_data = {}
        for row in self.c:
            id = row[0]
            data = list(row[1:6])
            data[-2] = data[-2] * row[6]   #VCeos = VCMODEL*VCrat  - TODO: MAKE this configurable
            self.list_base_data[id] = tuple(data)
            

        self.notebook_1 = wx.Notebook(self, -1, style=0)
        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, -1)

        self.search = wx.SearchCtrl(self, size=(200,-1))

        self.list_base = wx.ListCtrl(self.notebook_1_pane_1, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        

        self.button_new = wx.BitmapButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS, "document-new.png")))
        self.button_edit = wx.BitmapButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS,"document-properties.png")))
        self.button_duplicate = wx.BitmapButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS,"edit-copy.png")))
        self.button_remove = wx.BitmapButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS,"list-remove.png")))
        
        self.button_add2system = wx.BitmapButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS,"go-next.png")))
        self.button_remove4system = wx.BitmapButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS,"go-previous.png")))


        self.compounds_data = compounds_data
        self.list_system = wx.ListCtrl(self, -1, validator= SystemValidator(self.compounds_data), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        


        
        

        self.button_cancel = wx.Button(self, wx.ID_CANCEL)
        self.button_accept = wx.Button(self, wx.ID_OK)
        self.button_accept.SetDefault()

        self.__set_properties()
        self.__do_layout()
        # end wxGlade


    
        

        #---- BINDING EVENTS ----------
        #search
        self.Bind(wx.EVT_TEXT, self.OnDoSearch, self.search)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelSearch, self.search)

        #toolbar CRUD
        self.Bind(wx.EVT_BUTTON, self.OnNew, self.button_new)
        self.Bind(wx.EVT_BUTTON, self.OnEdit, self.button_edit)
        self.Bind(wx.EVT_BUTTON, self.OnDuplicate, self.button_duplicate)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.button_remove)

        #system
        self.Bind(wx.EVT_BUTTON, self.OnAddToSystem, self.button_add2system)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveFromSystem, self.button_remove4system)

        #accept / cancel
        #self.Bind(wx.EVT_BUTTON, self.OnAccept, self.button_accept)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.button_cancel)

        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Define a binary system")
        self.button_new.SetSize(self.button_new.GetBestSize())
        self.button_edit.SetSize(self.button_edit.GetBestSize())
        self.button_duplicate.SetSize(self.button_duplicate.GetBestSize())
        self.button_remove.SetSize(self.button_remove.GetBestSize())
        self.button_add2system.SetSize(self.button_add2system.GetBestSize())
        self.button_remove4system.SetSize(self.button_remove4system.GetBestSize())
        # end wxGlade

        self.button_new.SetToolTipString('Create a new compound')
        self.button_edit.SetToolTipString('Edit selected compound')
        self.button_duplicate.SetToolTipString('Duplicate selected compound')
        self.button_remove.SetToolTipString('Remove selected compound from database')
        self.button_add2system.SetToolTipString('Add selected compound to the system')
        self.button_remove4system.SetToolTipString('Remove selected compound from system')


        self.search.ShowSearchButton(True)
        self.search.ShowCancelButton(True)

        self.list_base.InsertColumn(0, "Compounds", width=185)
        self.list_system.InsertColumn(0, "System", width=185)

        self.PopulateLists()

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_20 = wx.BoxSizer(wx.VERTICAL)
        sizer_19 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.VERTICAL)
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15.Add(self.search, 0, wx.ALL, 3)
        sizer_9.Add(sizer_15, 1, wx.EXPAND, 0)
        sizer_14.Add(self.list_base, 1, wx.EXPAND, 0)
        self.notebook_1_pane_1.SetSizer(sizer_14)
        self.notebook_1.AddPage(self.notebook_1_pane_1, "Compound base")
        sizer_7.Add(self.notebook_1, 1, wx.EXPAND, 0)
        sizer_9.Add(sizer_7, 7, wx.EXPAND, 0)
        sizer_21.Add(self.button_new, 0, wx.ALL, 3)
        sizer_21.Add(self.button_edit, 0, wx.ALL, 3)
        sizer_21.Add(self.button_duplicate, 0, wx.ALL, 3)
        sizer_21.Add(self.button_remove, 0, wx.ALL, 3)
        sizer_16.Add(sizer_21, 1, wx.EXPAND, 0)
        sizer_9.Add(sizer_16, 1, wx.EXPAND, 0)
        sizer_8.Add(sizer_9, 4, wx.EXPAND, 0)
        sizer_10.Add(sizer_11, 2, wx.EXPAND, 0)
        sizer_17.Add(self.button_add2system, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        sizer_17.Add(self.button_remove4system, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        sizer_10.Add(sizer_17, 1, wx.EXPAND, 0)
        sizer_10.Add(sizer_12, 2, wx.EXPAND, 0)
        sizer_8.Add(sizer_10, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_5, 1, wx.EXPAND, 0)
        sizer_2.Add(self.list_system, 1, wx.EXPAND, 0)
        sizer_3.Add(sizer_18, 1, wx.EXPAND, 0)
        sizer_4.Add(self.button_cancel, 0, wx.ALL|wx.ALIGN_BOTTOM, 3)
        sizer_4.Add(self.button_accept, 0, wx.ALL|wx.ALIGN_BOTTOM, 3)
        sizer_3.Add(sizer_4, 0, wx.EXPAND|wx.ALIGN_BOTTOM, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_19.Add(sizer_2, 1, wx.EXPAND, 0)
        sizer_8.Add(sizer_19, 4, wx.EXPAND, 0)
        sizer_8.Add(sizer_20, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_8, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()


        self.Fit()
        self.SetMinSize(self.GetSize())

        # end wxGlade

# end of class MyFrame


    def PopulateLists(self, filter=''):
        """populate compound base from cached database"""
    
        def filterer(s1, s2=filter):
            if s2 == '' or s1.lower().find(s2.lower())!=-1:
                #we have a winner
                return True
            else:
                return False

        self.list_base.DeleteAllItems()
        for id, data in self.list_base_data.iteritems():

            if filterer(data[0]):
                #print filter, data[1]
                self.list_base.Append([data[0]]) #name
                key = self.list_base.GetItemCount() - 1
                self.list_base.SetItemData(key, id)
                        



    #EVENTS HANDLERS

    def OnNew(self, evt):
        dlg = DataFormDialog(self, -1)
        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()
    
        if val == wx.ID_OK:
            pass
        else:
            pass

        dlg.Destroy()



    def OnEdit(self, evt):
        key = self.list_base.GetFirstSelected()
        id = self.list_base.GetItemData(key)
        data = self.list_base_data[id]

        dlg = DataFormDialog(self, -1, title="Edit compound", data=data)
        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()
    
        if val == wx.ID_OK:
            pass
        else:
            pass

        dlg.Destroy()



    def OnDuplicate(self, evt):
        pass

    def OnRemove(self, evt):
        pass

    def OnAddToSystem(self, evt):
        """Add the at the most two compounds selected to the system"""

        comp_left = 2 - self.list_system.GetItemCount()
        comp_selected = self.list_base.GetSelectedItemCount()

        if  comp_selected <= comp_left:

            current = -1
            for iter in range(comp_selected):
                key = self.list_base.GetNextSelected(current) 
                id = self.list_base.GetItemData(key)    #compound's id
                self.list_system.Append([self.list_base_data[id][0]]) 
                self.compounds_data.append( [id] + list(self.list_base_data[id]))
                current = key
        
        else:
            wx.Bell()

    


    def OnRemoveFromSystem(self, evt):
        key = self.list_system.GetFirstSelected()
        if key != -1:
            self.list_system.DeleteItem(key)
            self.compounds_data.pop(key)
        else:
            wx.Bell()


    def OnDoSearch(self, evt):
        filter = self.search.GetValue()
        self.PopulateLists(filter)

    def OnCancelSearch(self, evt):
        self.search.SetValue('')
        self.PopulateLists()

    def OnCancel(self, evt):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close and discard the system?",
            "Confirm discard", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()


    

        
class SystemValidator(wx.PyValidator):
    def __init__(self, compounds_data):
        wx.PyValidator.__init__(self)
        self.compounds_data = compounds_data


    def Clone(self):
        return SystemValidator(self.compounds_data)
    
    def Validate(self, parent):
        win = self.GetWindow()
        if win.GetItemCount() != 2:
            wx.MessageBox(self, "Do you know what binary means?", "Your system needs 2 compounds", wx.OK|wx.ICON_ERROR|wx.CENTRE)
            return False
        else:
            return True
        
    def TransferToWindow(self):
        listCtrl = self.GetWindow()
        

        for compound in self.compounds_data:
            listCtrl.Append([compound[1]]) #add name
            
        return True          
        
    
    def TransferFromWindow(self):
        """the compound 2 must be more heavy than 1""" 
        

        def get_weight(tc, pc):
            return float(tc)**WEIGHT_POWER / float(pc)

        tc1 = self.compounds_data[0][2]
        tc2 = self.compounds_data[1][2]
        pc1 = self.compounds_data[0][3]
        pc2 = self.compounds_data[1][3]

        if get_weight(tc1, pc1) >  get_weight(tc2, pc2):
            
        
            tmp = self.compounds_data[0]
            self.compounds_data[0] = self.compounds_data[1]
            self.compounds_data[1] = tmp
            
            pub.sendMessage('log', ('info', '%s is heavier than %s. The system was inverted' % 
                                    (self.compounds_data[1][1], self.compounds_data[0][1])
                                   )
                            )
   
        pub.sendMessage('log', ('ok', 'The system %s-%s was defined succesfully' %  
                                (self.compounds_data[0][1], self.compounds_data[1][1]) 
                                )
                        )
        return True    


class DataFormDialog(sc.SizedDialog):
    def __init__(self, parent, id, title="New Compound", data=None ):

        sc.SizedDialog.__init__(self, None, -1, title, 
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        
        
        self.controls = []

        wx.StaticText(pane, -1, u'Name')
        self.controls.append(wx.TextCtrl(pane, -1))
        self.controls[-1].SetSizerProps(expand=True)
        
        # row 2
        wx.StaticText(pane, -1, u'Formula')
        self.controls.append(wx.TextCtrl(pane, -1))
        self.controls[-1].SetSizerProps(expand=True)
        
        # row 3
        wx.StaticText(pane, -1, u'Extended Formula')
        self.controls.append(wx.TextCtrl(pane, -1))
        self.controls[-1].SetSizerProps(expand=True)

        # row 4
        wx.StaticText(pane, -1, u'Critical Temperature [K]')
        self.controls.append(ui.widgets.FloatCtrl(pane, -1))
        
        #row 5
        wx.StaticText(pane, -1, u'Critical Pressure [bar]')
        self.controls.append(ui.widgets.FloatCtrl(pane, -1))
        
        wx.StaticText(pane, -1, u'Critical Volume [m³/Kmol]')
        self.controls.append( ui.widgets.FloatCtrl(pane, -1))
        
        wx.StaticText(pane, -1, "Acentric Factor")
        self.controls.append(  ui.widgets.FloatCtrl(pane, -1))
        
        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        
        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

        if data is not None:
            self.SetData(data)

    def SetData(self, data):
        print data
        #assert len(data) == len(self.controls) + 1, 'Not enough data to fill the form'
        
        self.table = data[0]

        for control, value in zip(self.controls, data[1:]):
            control.SetValue(str(value))



if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()

    
    dlg = DefineSystemDialog(None, -1)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
