#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sys
#WX
import wx
import wx.aui

import wx.lib.agw.aui as aui

import wx.lib.buttons
import ui.widgets
import ui.PyCollapsiblePane as pycp

import apimanager
import crud

import  wx.lib.scrolledpanel as scrolled

import  wx.py  as  py #for pyshell


from settings import PATH_ICONS, MODELS_OPTIONS, VC_RATIO

from tools.misc import Counter

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as NavigationToolbar

#pubsub
from wx.lib.pubsub import Publisher as pub

#plots
import plots


from wx.lib.embeddedimage import PyEmbeddedImage




class PlotPanel(wx.Panel):
    """ Creates the main panel with all the controls on it:
             * mpl canvas 
             * mpl navigation toolbar
             * Control panel for interaction"""
        
    def __init__ (self, parent, id, diagram_type='PT', arrays=None):
        
        wx.Panel.__init__(self, parent, id, style = wx.FULL_REPAINT_ON_RESIZE)
        
 
        
        self.plot = getattr(plots, diagram_type)(self) #any type of diagram

        self.plot.canvas.mpl_connect('button_release_event',        #binding matplotlib event
                                self.onMouseButtonClick)

        self.plot.canvas.mpl_connect('motion_notify_event', 
                                        self.onMouseMotion)


        self.toolbar = NavigationToolbar(self.plot.canvas)      #the canvas from plot
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.plot.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

        if arrays:
            self.plot.setup_curves(arrays)

        #binding via pubsub
        #pub.subscribe(self.OnPlotPT, 'plot.PT')

    def onMouseMotion(self, event):
        if event.inaxes:
            pub.sendMessage('status', 'X=%g Y=%g' % (event.xdata, event.ydata) )
        

        
    def onMouseButtonClick(self, event):
        if event.button == 3: 

            if not hasattr(self, 'menu'):               
                self.menu = wx.Menu()

                for curve in self.plot.curves:
                    self.menu.Append(curve['wx_id'], curve['name'], kind=wx.ITEM_CHECK)
                    self.Bind(wx.EVT_MENU, self.plot.OnToggleCurve, id=curve['wx_id'])
                    self.menu.Check(curve['wx_id'], True)
    
                self.menu.AppendSeparator()
                
                for prop, wx_id in self.plot.properties.iteritems():
                    self.menu.Append(wx_id, prop, kind=wx.ITEM_CHECK)
                    self.Bind(wx.EVT_MENU, self.plot.OnToggleProperty, id=wx_id)


            
                # make a submenu
                #sm = wx.Menu()
                #sm.Append(self.popupID8, "sub item 1")
                #sm.Append(self.popupID9, "sub item 1")
                #self.menu.AppendMenu(self.popupID7, "Test Submenu", sm)


            # Popup the menu.  If an item is selected then its handler
            # will be called before PopupMenu returns.
            wx.CallAfter(self.PopupMenu, self.menu)

    


    def Plot(self, event=None):
        
        self.plot.plot()


          
   

class SuitePlotsPanel(wx.Panel):
    """a general tabbed panel to show plots"""

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.nb = wx.aui.AuiNotebook(self)

       

        #pub.subscribe(self.OnAddPlot, 'plot.PT')

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        

        
                
        pub.subscribe(self.OnMakeSuite, 'make.suite')

    def OnMakeSuite(self, message):
        case_id, case_name, arrays = message.data

        for type in ['PT', 'Tx', 'Px', 'Trho', 'Prho']:
            pp = PlotPanel(self,  -1, type, arrays)
            self.nb.AddPage(pp, "%s (%s)" % (pp.plot.short_title, case_name))
            pp.Plot()
        
        #by default it include a log_messages panel
        



class VarsAndParamPanel(wx.Panel):
    """a panel with 2 columns of inputs. First colums input EOS variables. 
        The second one are the inputs to model parameters (change depending
        the model selected). 
        This parameter are related and is possible to calcule a group of values
        defining the other one. 
        """

    def __init__(self, parent, id, model_id=1, setup_data=None):
        """setup_data: (id, name, tc, pc, vc, om)"""

        wx.Panel.__init__(self, parent, id, style = wx.TAB_TRAVERSAL
                     | wx.CLIP_CHILDREN
                     | wx.FULL_REPAINT_ON_RESIZE
                     )

        gbs = self.gbs = ui.widgets.GridBagSizerEnh(6, 5)
        
        self.api_manager = parent.api_manager

        vars_label = (('Tc [K]', 'Critical temperature'), 
                ('Pc [bar]', 'Critical Pressure'), 
                ('Vol [l/mol]', 'Critical Volume'), 
                (u'\u03c9', 'Acentric Factor') )

        #add title
        self.title = wx.StaticText(self, -1, '', (5, 120), style = wx.ALIGN_LEFT)
        self.title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))
        gbs.Add(self.title, (0,0), (1,4),  flag=wx.ALIGN_CENTER)


        #add first col
        self.vars = []
        for row, var in enumerate(vars_label):
            gbs.Add( wx.StaticText(self, -1, var[0]), (row+2, 0), flag=wx.ALIGN_RIGHT)
            box = ui.widgets.FloatCtrl(self, -1)
            box.SetToolTipString(var[1])
            self.vars.append(box)
            gbs.Add ( box, (row+2, 1))


        self.params = []


    
        #add radio buttons
        self.radio1 = wx.RadioButton( self, -1, "", style = wx.RB_GROUP)
        self.radio2 = wx.RadioButton( self, -1, "")
        self.gbs.Add(self.radio1, (1,1))
        self.gbs.Add(self.radio2, (1,4))


        self.params_labels = {1: ((u'ac [bar·m⁶Kmol²]', u'descrip ac'), 
                             ('b [l/mol]', 'descrip b'), (u'm', u'descrip m')  ),
                         2: ((u'ac [bar·m⁶Kmol²]', u'descrip ac'), 
                             (u'b [l/mol]', u'descrip b'), (u'm', u'descrip m')  ),
                         3: ((u'ac [bar·m⁶Kmol²]', u'descrip ac'), 
                             (u'b [l/mol]', u'descrip b'), (u'ω', 'descrip '),
                              ('k', 'descrip k') ),
                         4: ((u'ε/k', u'descript ε/k'), (u'ρ', u'descript ρ'),
                             (u'm', u'descript u') ),
                         6: ((u'T* [k]', u'descript T*'), (u'V* [l/mol]', 'descript V*'),
                             (u'c', u'descript c'))
                        }


        #add button in the center
        self.arrow = (wx.Bitmap(os.path.join(PATH_ICONS,"go-next.png")), 
                        wx.Bitmap(os.path.join(PATH_ICONS,"go-previous.png")))
        self.button = wx.BitmapButton(self, -1, self.arrow[0], style = wx.CENTRE | wx.BU_AUTODRAW)
        #self.button2left = wx.BitmapButton(self, -1, wx.Bitmap("/home/tin/facu/pi/src/images/go-previous.png", wx.BITMAP_TYPE_ANY))
        gbs.Add(self.button, (3,2), flag=wx.FIXED_MINSIZE | wx.ALIGN_CENTER)


   
        

        # Add a spacer at the end to ensure some extra space at the bottom
        #gbs.Add((10,10), (14,7))
    
        self.box = wx.BoxSizer()
        self.box.Add(gbs, 0, wx.ALL, 10)


        #set default on form
        self.direction = 0
        self.model_id = model_id
      

        if setup_data is not None:
            self.enabled = True
            self.SetData(setup_data)
            self.SetDirectionOnForm()
        else:
            
            self.EnableAll(False)

        
        self.SetParamsForm(self.model_id)
        


        #binding
        self.Bind(wx.EVT_BUTTON, self.OnButton,  self.button)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnDirectionSelect, self.radio1 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnDirectionSelect, self.radio2 )

    def SetData(self, data):
        self.compound_id = data[0]
        self.compound_name = data[1]    #in case the title != compound_name
        self.title.SetLabel(data[1]) 
        self.SetVarsValues(data[2:])

        #TODO reset param columns. 
        self.EnableAll()

    def GetData(self):
        """Return a compound list [id, name, vars...]   useful to redefine the system"""
        if self.enabled:
            return [self.compound_id, self.compound_name] + self.GetVarsValues()

    def GetTotalData(self):
        """Return a compound list tuple (name, (vars...), (param...))"""
        self.OnButton(None) #Ensure last numbers
        tmp_var = self.GetVarsValues()
        tmp_var = tmp_var[:-2] + [tmp_var[-1], tmp_var[-2]]  #gpecout has order changed: vc <-> omega

        return (self.compound_name, tmp_var, self.GetParamsValues())


    def EnableAll(self, flag=True):
        self.enabled = flag
        for box in self.vars :
            box.Enable(flag)
        
        if self.model_id != 3:
            self.vars[2].Enable(False)

        self.button.Enable(flag)
        self.radio1.Enable(flag)
        self.radio2.Enable(flag)
        

    def GetVarsValues(self):
        """Return vars values of defined compound"""
        if self.enabled:
            return [box.GetValue() for box in self.vars]

    def SetVarsValues(self, data):
        try:
            for box, data in zip(self.vars, data):
                box.SetValue(str(data))
        except:
            pub.sendMessage('log', ('error',  "not enough data or boxes for EOS vars"))
            
            

    
    def GetParamsValues(self):
        """Return params values of defined compound"""
        if self.enabled:
            return [box.GetValue() for box in self.params]


    def SetParamsValues(self, data):
        if len(data) == len(self.params):
            for box, data in zip(self.params, data):
                box.SetValue(str(data))
        else:
            pub.sendMessage('log', ('error',  "not enough data or boxes for EOS vars"))
            
            
                


    
    def OnDirectionSelect(self, event):
        radio_selected = event.GetEventObject()
        if radio_selected == self.radio1:
            self.direction = 0
        else:
            self.direction = 1
        self.SetDirectionOnForm()

    def SetDirectionOnForm(self):
        """Update the form. Direction and enable of"""

        if self.direction == 0:
            for box in self.vars:
                box.Enable(True)
        
            if self.model_id != 3:
                self.vars[2].Enable(False)


            for box in self.params:
                box.Enable(False)
            
            self.button.SetBitmapLabel(self.arrow[0])
        else:
            for box in self.vars:
                box.Enable(False)
            for box in self.params:
                box.Enable(True)
            self.button.SetBitmapLabel(self.arrow[1])







    def OnButton(self, event):
    
        if self.direction == 0:
            data = [box.GetValue() for box in self.vars]
        else:
            data = [box.GetValue() for box in self.params]

        self.api_manager.write_conparin(self.direction, self.model_id, data)

        data = self.api_manager.read_conparout(self.model_id) 
        
        if data is not None:

            #~ if self.direction == 0:
                #~ self.SetParamsValues(data[1])
            #~ else:
                #~ self.SetVarsValues(data[0])
            
            self.SetVarsValues(data[0])
            self.SetParamsValues(data[1])

        else:
            wx.Bell()
            print "error handling ModelsParam output"
            



    def SetParamsForm(self, model_id):
        """set a column of widgets for params depending on selected model"""
        #clean up
        self.model_id = model_id
        for row in range(len(self.params)):
            self.gbs.remove_gbitem(row + 2, 3)
            self.gbs.remove_gbitem(row + 2, 4)

 
        self.params = []

        for row, var in enumerate(self.params_labels[model_id]):
            #add row an box to the form and the list
            self.gbs.Add(wx.StaticText(self, -1, var[0]), (row+2, 3), flag=wx.ALIGN_RIGHT)
            box = ui.widgets.FloatCtrl(self, -1)
            box.SetToolTipString(var[1])
            self.params.append(box)
            self.gbs.Add ( box, (row+2, 4))
    

        if self.direction == 0:
            self.SetDirectionOnForm()

        self.EnableAll(self.enabled)

        #FIT all
        self.gbs.Layout()
        self.SetSizerAndFit(self.box)
        self.SetClientSize(self.GetSize())



class TestFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, "Model Params")
        self.SetBackgroundColour(wx.NullColour) #hack for win32


        self.CenterOnScreen()

        self.CreateStatusBar()
        self.SetStatusText("This is the statusbar")


        menu = [
            ('&File', [
                ('&Open', self.FileOpen),
                (),
                ('&Exit', self.onCloseWindow, "Quit this program"),

            ]),
            ('&Edit', [
                ('&Copy', self.EditCopy),
                ('&Paste', self.EditPaste),
            ]),
            ('&View', [
                ('&One item', curry(self.DataBox, 1)),
                ('&Second item', curry(self.DataBox, 2)),
                ('Sub&menu', [
                    ('&Three', curry(self.DataBox, 3)),
                    ('&Four', curry(self.DataBox, 4)),
                ]),
            ]),
        ]
        self.SetMenuBar(self.BuildMenu(menu))



        hsizer =  wx.BoxSizer(wx.HORIZONTAL)

        self.vsplitter  = wx.SplitterWindow(self, -1, style= wx.SP_LIVE_UPDATE | wx.SP_3D )
        #self.hsplitter = wx.SplitterWindow(self, -1, style= wx.SP_LIVE_UPDATE | wx.SP_3D )

   
        self.case_panel = CasePanel(self.vsplitter, -1)
        
        vsizer =  wx.BoxSizer(wx.VERTICAL)    

        panel_right = wx.Panel(self, -1)

        self.plot_panel = PlotPanel(panel_right, -1)
        self.log_panel = LogPanel(panel_right, -1)

        vsizer.Add(self.plot_panel, 2)
        vsizer.Add(self.log_panel, 1)

        panel_right.SetSizerAndFit(vsizer)
        

        #self.hsplitter.SplitHorizontally( self.plot_panel, self.log_panel, self.plot_panel.GetSize().GetHeight())

        self.vsplitter.SetMinimumPaneSize(4)
       

        self.vsplitter.SplitVertically(self.case_panel, panel_right,
                                        self.case_panel.GetSize().GetWidth() )

        hsizer.Add(self.vsplitter, 0, wx.EXPAND )
        #hsizer.Add(case_panel, 0, wx.EXPAND )
        #hsizer.Add(plot_panel, 0, wx.EXPAND )

        self.SetSizerAndFit(hsizer)
        self.SetClientSize(self.GetSize())




    def onCloseWindow(self, event):
        # dialog to verify exit (including menuExit)
        dlg = wx.MessageDialog(self, "Want to exit?", "Exit", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()  # frame
        dlg.Destroy()


    def FileOpen(self, event):
        self.Info(self, 'You chose File->Open')
    def EditCopy(self, event):
        self.Info(self, 'You chose Edit->Copy')
    def EditPaste(self, event):
        self.Info(self, 'You chose Edit->Paste')
    def DataBox(self, num, event):
        self.Info(self, 'You chose item %d' % (num,))
    def Info(self, parent, message, caption = 'Better Menus'):
        dlg = wx.MessageDialog(parent, message, caption, \
            wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()



    def BuildMenu(self, menu):
        mainMenu = wx.MenuBar()
        for title, subMenu in menu:
            mainMenu.Append(self.BuildSubmenu(subMenu), title)
        return mainMenu

    def BuildSubmenu(self, subMenu):
        subMenuObject = wx.Menu()
        for item in subMenu:
            if not item:                #allow now to add separators
                subMenuObject.AppendSeparator()
                continue
            statustext = '';    uihandler = None
            if len(item) == 2:
                title, action = item
            elif len(item) == 3:
                if type(item[2]) is str:
                    title, action, statustext = item
                else:
                    title, action, statustext = item
            elif len(item) == 4:
                title, action, statustext, uihandler = item
            else:
                raise AssertionError, \
                    'Item %s should have either 2 to 4 parts' % (item,)
            if type(action) is list:
                _id = wx.NewId()
                subMenuObject.AppendMenu(_id, title, self.BuildSubmenu(action))
            else:
                _id = wx.NewId()
                subMenuObject.Append(_id, title, statustext)
                wx.EVT_MENU(self, _id, action)
            if uihandler:
                wx.EVT_UPDATE_UI(self, _id, uihandler)
        return subMenuObject


    
    


class TabbedCases(wx.Panel):

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.nb = wx.aui.AuiNotebook(self, style = wx.aui.AUI_NB_TOP )
        
        ico = os.path.join(PATH_ICONS, 'add.png')

        self.addNewCase(0) #a first one case

        self.nb.AddPage(wx.Panel(self,-1), "", bitmap=wx.Bitmap(ico, wx.BITMAP_TYPE_PNG)) #dummy Panel
        
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.onPageChange, self.nb)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.onPageClose, self.nb) #TODO

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        size = self.nb.GetPage(0).GetSize()
        self.SetSize(size)
    

    def onPageClose(self, evt):
        evt.Veto()
        if evt.GetSelection() + 2 == self.nb.GetPageCount(): #last tab selected
            wx.CallAfter(self.nb.SetSelection,  0)
            
            
            
            


    def onPageChange(self, evt):
        if evt.GetSelection() + 1 == self.nb.GetPageCount(): #last tab selected
            self.addNewCase(evt.GetSelection())

    def addNewCase(self, location):
        case = CasePanel(self, -1)

        self.nb.InsertPage(location, case, "Case %i" % case.case_id)
        wx.CallAfter(self.nb.SetSelection, location)

        
 
    
            

class CasePanel(scrolled.ScrolledPanel):
    def __init__(self, parent, id):
        #wx.Panel.__init__(self, parent, id, style = wx.TAB_TRAVERSAL
        #                                        | wx.CLIP_CHILDREN
        #                                        | wx.FULL_REPAINT_ON_RESIZE)
        scrolled.ScrolledPanel.__init__(self, parent, id, style = wx.TAB_TRAVERSAL
                                                | wx.CLIP_CHILDREN
                                                | wx.FULL_REPAINT_ON_RESIZE)
        
        self.case_id = Counter().get_id()
        self.name = 'Case %i' % self.case_id

        self.api_manager = apimanager.ApiManager(self.case_id)
        


        self.box = wx.BoxSizer(wx.VERTICAL)

        

        self.model_options =  MODELS_OPTIONS

        self.ch = wx.Choice(self, -1, choices = self.model_options.keys())
        
        #model ID by default
        self.model_id = 1
        self.ch.SetSelection(0)

        first_row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.load_button = wx.lib.buttons.GenBitmapTextButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS,"compose.png")), "Define system")
        
        first_row_sizer.Add(self.load_button, 0, flag=wx.ALL | wx.ALIGN_LEFT | wx.EXPAND , border=5)
        first_row_sizer.Add((10, 20), 0, wx.EXPAND)

        first_row_sizer.Add(wx.StaticText(self, -1, "Model:"), 0, flag= wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        first_row_sizer.Add(self.ch, 0, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL , border=5)
        self.box.Add( first_row_sizer, 0, flag= wx.TOP | wx.LEFT | wx.FIXED_MINSIZE | wx.ALIGN_LEFT, border = 5)

        
        self.panels = (VarsAndParamPanel(self,-1), VarsAndParamPanel(self,-1))

        self.box.Add(self.panels[0], 0, wx.EXPAND )
        self.box.Add(self.panels[1], 0, wx.EXPAND )


        #collapsible for extra variables

        self.cp = cp = pycp.PyCollapsiblePane(self, label='Other case variables',
                                          style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE|pycp.CP_GTK_EXPANDER)
        self.MakeCollipsable(cp.GetPane())
        self.box.Add(self.cp, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)

            
        self.plot_button = wx.lib.buttons.GenBitmapTextButton(self, -1, wx.Bitmap(os.path.join(PATH_ICONS,"plot.png")), "Plot!")


        but_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        
        but_sizer.Add(self.plot_button, 0, flag=wx.ALL , border=5)

        self.box.Add(but_sizer, 0, flag= wx.ALL | wx.FIXED_MINSIZE | wx.ALIGN_RIGHT, border = 5)

        
        #self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)


        self.SetSizerAndFit(self.box)
        self.SetClientSize(self.GetSize())

        self.SetupScrolling(scroll_x = False)

        #Binding
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
        self.Bind(wx.EVT_CHOICE, self.OnSetModel, self.ch)
        self.Bind(wx.EVT_BUTTON, self.OnLoadSystem, self.load_button)
        self.Bind(wx.EVT_BUTTON, self.OnMakePlots, self.plot_button)
        
        #self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)



    def MakeCollipsable(self, pane):
        addrSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
    
   
        self.cr_options = {0: 'van Der Waals', 1:'Lorentz-Berthelot'}       # candidate to a sorted dictionary

        self.combining_rules = wx.Choice(pane, -1, choices = [self.cr_options[key] 
                                         for key in sorted(self.cr_options.keys())] )

        self.combining_rules.SetSelection(0)

        combining_rulesLbl = wx.StaticText(pane, -1, "Combining Rule")

        
 
        self.max_p = ui.widgets.FloatCtrl(pane, -1, "2000.0");
        max_pLbl = wx.StaticText(pane, -1, "Maximum Pressure for\n LL critical line  [bar]")

        self.k12 = ui.widgets.FloatCtrl(pane, -1);
        k12Lbl = wx.StaticText(pane, -1, "K12")

        self.l12 = ui.widgets.FloatCtrl(pane, -1);
        l12Lbl = wx.StaticText(pane, -1, "L12")

        addrSizer.Add(combining_rulesLbl, 0, 
                wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)
        addrSizer.Add(self.combining_rules, 0, wx.ALIGN_BOTTOM)

        addrSizer.Add(max_pLbl, 0, 
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.max_p, 0)
        addrSizer.Add(l12Lbl, 0, 
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.l12, 0)
        addrSizer.Add(k12Lbl, 0, 
                wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.k12, 0)

        border = wx.BoxSizer()
        border.Add(addrSizer, 1, wx.EXPAND|wx.ALL, 5)
        pane.SetSizer(border)
    
    def OnPaneChanged(self, evt=None):
        # redo the layout
        self.Layout()
        self.SetClientSize(self.GetSize())
        self.Fit()

        p = self.GetParent()
        
        if isinstance(p, wx.SplitterWindow):
            
            p.UpdateSize()
        else:
            p.SetClientSize(self.GetSize())
        

    

    def OnLoadSystem(self, event):        

        #GET DATA IF vars-paramPanels are enabled
        compounds_data =  [panel.GetData() for panel in self.panels if  panel.enabled ]  
        
        


        dlg = crud.DefineSystemDialog(None, -1, compounds_data)        
    
        if dlg.ShowModal()  == wx.ID_OK:
        
            for panel, data in zip (self.panels, compounds_data):
                panel.SetData(data)

        dlg.Destroy()


    def OnSetModel(self, event):

        self.model_id = self.model_options[event.GetString()]


        if self.model_id in (4,6):
            #constraint  ``PC-SAFT`` y ``SPHCT`` exigen que la regla sea ``Lorentz-Berthelot``.
            self.combining_rules.SetSelection(0)   
            self.combining_rules.Disable()
        else:
            self.combining_rules.Enable()
        

        for panel in self.panels:
            panel.model_id = self.model_id
            panel.SetParamsForm(self.model_id)

        self.SetSizerAndFit(self.box)
        self.SetClientSize(self.GetSize())

    def OnMakePlots(self, event):

        if self.panels[0].enabled and self.panels[1].enabled:

            comp1 = self.panels[0].GetTotalData()
            comp2 = self.panels[1].GetTotalData()
            ncomb = self.combining_rules.GetSelection() 
            k12 = self.k12.GetValue()
            l12 = self.l12.GetValue()
            max_p = self.max_p.GetValue()

            self.api_manager.write_gpecin(self.model_id, comp1, comp2, ncomb, 0, k12, l12, max_p)

            curves = self.api_manager.read_gpecout()            
            pub.sendMessage('make.suite', (self.case_id, self.name, curves))
        else:
            pub.sendMessage('log', ('error', "Nothing to calculate. Define the system first."))


class ShellPanel(wx.Panel):
    """A python shell """

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.shell = py.shell.Shell(self, -1, introText='Welcome To GPEC' )
   
        sizer = wx.BoxSizer()
        sizer.Add(self.shell, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)


class InfoPanel(wx.Panel):
    """a general tabbed panel including a log list and other useful information"""

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.nb = wx.aui.AuiNotebook(self, style=aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT )



        #by default it include a log_messages panel
        self.log_panel = LogMessagesPanel(self, -1)

        self.io_panel = IOPanel(self, -1)

        self.shell_panel = ShellPanel(self, -1)

        self.nb.AddPage(self.log_panel, "Log")
        self.nb.AddPage(self.io_panel, "Input/Output ")
        
        self.nb.AddPage(self.shell_panel, "Shell")



        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        
        #self.Bind(wx.aui.EVT_AUINOTEBOOK_BUTTON, self.onPageChange)

        
        



  
        



class IOPanel(wx.Panel):
    """an info panel to show input an output text files"""

    #TODO!   #pub.subscribe(self.OnAddTextPage, 'add_txt')

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        #TREE
        self.tree = wx.TreeCtrl(self, -1, wx.DefaultPosition, wx.DefaultSize,
                               wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)

        
        self.root = self.tree.AddRoot("")
        
        
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged, self.tree)
       

        #TEXT
        self.text_ctrl = wx.TextCtrl(self, -1,  style=wx.TE_MULTILINE|wx.TE_READONLY)

        #TODO make this through a sash

        #sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(self.tree, 1, wx.EXPAND)        
        sizer.Add(self.text_ctrl, 4, wx.EXPAND)
        self.SetSizerAndFit(sizer)

        

        self.cases = {} #id:item_ID
        pub.subscribe(self.OnAddItem, 'add_txt')



    def OnTreeSelChanged(self, event):
        item = event.GetItem()
        try:
            content = self.tree.GetItemPyData(item)
            self.text_ctrl.Clear()
            self.text_ctrl.AppendText(content)
        except:
            pass 


    def OnAddItem(self, msg):

        filepath, case_id = msg.data

        head,filename = os.path.split(filepath)

        if case_id not in self.cases.keys():
            #if case is unknown, create it
            node = self.tree.AppendItem(self.root, "Case %d" % case_id)
            self.cases[case_id] = node
            
        
        else:
            node = self.cases[case_id]


        with open( filepath, 'r') as fh:
            content = fh.read()

            item = self.tree.AppendItem(node, filename)
            self.tree.SetPyData(item, content)
                    

        #self.tree.Expand(node)
        self.tree.SelectItem(item)  #TODO refresh text_ctrl?
        


class LogMessagesPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        self.list = wx.ListCtrl(self, -1,  style=  wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.setupList()

    
        sizer = wx.BoxSizer()
        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)
    
        pub.subscribe(self.OnAppendLog, 'log')
        
        
    

    def setupList(self):
        """sets columns and append a imagelist """
        
         #setup first column (which accept icons)
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Message"
        self.list.InsertColumnInfo(0, info)
        self.list.SetColumnWidth(0, 550)

        #insert second column
        self.list.InsertColumn(1, 'Time')   
        self.list.SetColumnWidth(1, 70)

        #setup imagelist and an associated dict to map status->image_index
        imgList = wx.ImageList(16, 16)
        ico_dir = os.path.join(PATH_ICONS, 'log')
        ico_filenames = [ico for ico in os.listdir(ico_dir) if ico[-3:] != 'svn' ]
        ico_list = [os.path.join(ico_dir, ico) for ico in ico_filenames]

        self.icon_map = {}
        for ico, filename in zip(ico_list, ico_filenames):
            indx = imgList.Add( wx.Bitmap(ico, wx.BITMAP_TYPE_PNG))
            self.icon_map[filename[:-4]] = indx
        self.list.AssignImageList(imgList, wx.IMAGE_LIST_SMALL)
        
    def OnAppendLog(self, msg):
        ico = self.icon_map[msg.data[0]]

        message = msg.data[1]
        index = self.list.InsertImageStringItem(sys.maxint, message, ico)
        self.list.SetStringItem(index, 1, time.strftime('%H:%M:%S'))
        self.list.EnsureVisible(index) #keep scroll at bottom

        if msg.data[0] == 'error':
            wx.Bell()

