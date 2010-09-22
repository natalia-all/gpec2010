#!/usr/bin/env python
# -*- coding: utf-8 -*-

#MATPLOTLIB
import matplotlib
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
from mpl_toolkits.mplot3d.axes3d import Axes3D

import wx

class BasePlot(object):
    """a base plot class for GPEC"""

    def __init__(self, parent, arrays=None, title=None, xlabel="", ylabel="", system=(), projection="2d", zlabel="", **karg):

        self.title = title
        if len(system)==2:
            self.title += '-  System %s-%s' % system 

        self.system = system
        self.arrays = arrays

        
        self.fig = Figure()     #dpi=self.dpi
        self.canvas = FigCanvas(parent, -1, self.fig)
        

        if projection == '3d':
            self.axes = Axes3D(self.fig)
            self.axes.set_zlabel(zlabel)
        else: 
            self.axes = self.fig.add_subplot(111)

        self.axes.set_title(title)
        self.axes.set_ylabel(ylabel)
        self.axes.set_xlabel(xlabel)

        self.axes.set_autoscale_on(True)
                

        self.properties = {'Grid':wx.NewId(), 'Legends':wx.NewId(), 'Log X': wx.NewId(), 'Log Y': wx.NewId(), }
   

        self.curves = []    #curves to plot

        if arrays:
            self.setup_curves()

     

    def setup_curves (self):
        """each one sutype declare curves as a group of line2d

            - redefined by each sub class"""

        pass


    def plot(self):
        """plot all visible curves"""
        for curve in self.curves:
            if curve['visible']:
                marker = '' if 'marker' not in curve.keys() else curve['marker']
                curve['line2d'] = self.axes.plot(*curve['lines'], color=curve['color'], marker=marker, label=curve['name'])
        

        
        self.canvas.draw()


    def OnToggleCurve(self, event):
        wx_id = event.GetId()
        curve = [curve for curve in self.curves  if curve['wx_id'] == wx_id][0]     #TODO better way?        

        curve['visible'] = not curve['visible']
        for line in curve['line2d']:
            line.set_visible(curve['visible']) 

        self.canvas.draw()

    def OnToggleProperty(self, event):
        wx_id = event.GetId()
        prop = dict([[v,k] for k,v in self.properties.items()])[wx_id] #inverted dict

        if prop == 'Grid':
            self.axes.grid()

        elif prop == 'Legends':
            if self.axes.get_legend():
                self.axes.legend_ = None        #a tricky way to remove lengeds
            else:
                self.axes.legend(loc='best')  

        elif prop == 'Log X':
            if self.axes.get_xscale() == 'linear':
                self.axes.set_xscale('log')
            else:
                self.axes.set_xscale('linear')

        elif prop == 'Log Y':
            if self.axes.get_yscale() == 'linear':
                self.axes.set_yscale('log')
            else:
                self.axes.set_yscale('linear')



        self.canvas.draw()


class PTrho(BasePlot):
    def __init__(self, parent, arrays=None, system=()):

        self.short_title = u"P-T-\u03c1"
        self.title = u'Pressure-Temperature-Density projection of a global phase equilibrium diagram'
        self.xlabel = u'Temperature [K]'
        self.ylabel = u'Density [mol/l]'
        self.zlabel = u'Pressure [bar]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, system, projection='3d', zlabel=self.zlabel)        

    def setup_curves(self, arrays):

        if 'VAP' in arrays.keys():
            for num, vap_curve in enumerate(arrays['VAP']):
                
                counter = u'' if len(arrays['VAP']) == 1 else u' %i' % (num + 1)

                self.curves.append( {'name': u'Pure compound vapor pressure lines (L)' + counter , 
                                     'visible':True, 
                                     'lines':( vap_curve[:,0], vap_curve[:,2], vap_curve[:,1]),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'VAP',
                                        } )             

                self.curves.append( {'name': u'Pure compound vapor pressure lines (V)' + counter , 
                                     'visible':True, 
                                     'lines':( vap_curve[:,0], vap_curve[:,3], vap_curve[:,1]),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'VAP',
                                        } )


        if 'CRI' in arrays.keys():
            for num, cri_curve in enumerate(arrays['CRI']):

                counter = u'' if len(arrays['CRI']) == 1 else u' %i' % (num + 1)
                self.curves.append( {'name': u'Critical line' + counter , 
                                     'visible':True, 
                                     'lines':(cri_curve[:,0],cri_curve[:,2], cri_curve[:,1]),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'CRI'
                                    } )


        if 'LLV' in arrays.keys():
            for num, llv_curve in enumerate(arrays['LLV']):
                self.curves.append( { 'name': 'LLV', 
                                      'visible':True,
                                      'lines': (llv_curve[:,0], llv_curve[:,1], llv_curve[:,7]),           #TODO
                                      'color': 'red', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )




class PTx(BasePlot):
    """PTx 3D projection"""

    def __init__(self, parent, arrays=None, system=()):

        self.short_title = u"P-T-x"
        self.title = u'Pressure-Temperature-Composition projection of a global phase equilibrium diagram'
        self.xlabel = u'Temperature [K]'
        self.ylabel = u'Composition'
        self.zlabel = u'Pressure [bar]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, system, projection='3d', zlabel=self.zlabel)        

    def setup_curves(self, arrays):


        if 'CRI' in arrays.keys():
            for num, cri_curve in enumerate(arrays['CRI']):

                counter = u'' if len(arrays['CRI']) == 1 else u' %i' % (num + 1)
                self.curves.append( {'name': u'Critical line' + counter , 
                                     'visible':True, 
                                     'lines':(cri_curve[:,0],cri_curve[:,3], cri_curve[:,1]),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'CRI'
                                    } )


        if 'LLV' in arrays.keys():
            for num, llv_curve in enumerate(arrays['LLV']):
                self.curves.append( { 'name': 'LLV', 
                                      'visible':True,
                                      'lines': (llv_curve[:,0], llv_curve[:,2], llv_curve[:,1]),           #TODO
                                      'color': 'red', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )

class IsoPT(BasePlot):
    """Isopleth PT diagram"""
    
    def __init__(self, parent, arrays=None, **kwarg):

        self.short_title = u"Isopleth P-T"
        self.title = u'Isopleth Graph for a Composition (Z = %s)' % kwarg['z']
        self.xlabel = u'Temperature [K]'
        self.ylabel = u'Pressure [bar]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

        if 'ISO' in arrays.keys():
            for num, vap_curve in enumerate(arrays['ISO']):
                
                counter = u'' if len(arrays['ISO']) == 1 else u' %i' % (num + 1)

                self.curves.append( {'name': u'Isopleth line' + counter , 
                                     'visible':True, 
                                     'lines':( vap_curve[:,0], vap_curve[:,1]),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )             

        if 'LLV' in arrays.keys():
            for num, llv_curve in enumerate(arrays['LLV']):
        
                if llv_curve.shape == (2,):  
                    #POINT 

                    self.curves.append( { 'name': 'LLV Critical Point', 
                                          'visible':True,
                                          'lines': (llv_curve[0], llv_curve[1]),           #TODO
                                          'color': 'blue', 
                                          'marker': '^',
                                          'wx_id' : wx.NewId(),
                                           'type': 'LLV',
                                           
                                        } )

                else:
                    color = 'blue' if num % 2 == 0 else 'red'

                    self.curves.append( { 'name': 'LLV', 
                                          'visible':True,
                                          'lines': (llv_curve[:,0], llv_curve[:,1]),           #TODO
                                          'color': color, 
                                          'wx_id' : wx.NewId(),
                                           'type': 'LLV',
                                        } )
                    


class IsoTx(BasePlot):
    """Isopleth Tx diagram"""
    
    def __init__(self, parent, arrays=None, **kwarg):

        self.short_title = u"Isopleth T-x"
        self.title = u'T-x projection of the Isopleth Graph for a Composition (Z=%s)' % kwarg['z']
        self.xlabel = u'Temperature [K]'
        self.ylabel = u'Composition'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

        if 'ISO' in arrays.keys():
            for num, vap_curve in enumerate(arrays['ISO']):
                

                self.curves.append( {'name': u'Incipient Face.',
                                     'visible': True, 
                                     'lines':( 1 - vap_curve[:,3], vap_curve[:,0]),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )             

                #a same lenght vector constant at maximum ("z" composition given)
                saturated =  np.repeat( np.max(vap_curve[:,2]), len(vap_curve[:,2]))    
            

                self.curves.append( {'name': u'Major (Saturated) Face.',
                                     'visible':True, 
                                     'lines':( saturated, vap_curve[:,0]),
                                      'color' : 'red',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )             


        
class IsoPx(BasePlot):
    """Isopleth Px diagram"""
    
    def __init__(self, parent, arrays=None, **kwarg):

        self.short_title = u"Isopleth P-x"
        self.title = u'P-x projection of the Isopleth Graph for a Composition (Z=%s)' % kwarg['z']
        self.xlabel = u'Composition'
        self.ylabel = u'Pressure [bar]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

        if 'ISO' in arrays.keys():
            for num, vap_curve in enumerate(arrays['ISO']):
                
                counter = u'' if len(arrays['ISO']) == 1 else u' %i' % (num + 1)

                self.curves.append( {'name': u'Incipient Face.' + counter , 
                                     'visible':True, 
                                     'lines':( 1 - vap_curve[:,3], vap_curve[:,1]),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )

                #a same lenght vector constant at maximum ("z" composition given)
                saturated =  np.repeat( np.max(vap_curve[:,2]), len(vap_curve[:,2]))    
            

                self.curves.append( {'name': u'Major (Saturated) Face.',
                                     'visible':True, 
                                     'lines':( saturated, vap_curve[:,1]),
                                      'color' : 'red',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )     
                


class IsoTrho(BasePlot):
    """Isopleth Trho diagram"""
    
    def __init__(self, parent, arrays=None, **kwarg):

        self.short_title = u"Isopleth T-\u03c1" 
        self.title = u'T-\u03c1 projection of the Isopleth Graph for a Composition (Z=%s)' % kwarg['z']
        self.xlabel = u'Density [mol/l]'
        self.ylabel = u'Temperature [K]'
        

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

        if 'ISO' in arrays.keys():
            for num, vap_curve in enumerate(arrays['ISO']):

                self.curves.append( {'name': u'Incipient Face.', 
                                     'visible':True, 
                                     'lines':( vap_curve[:,4], vap_curve[:,0]),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )


                self.curves.append( {'name': u'Major (Saturated) Face.',
                                     'visible':True, 
                                     'lines': (vap_curve[:,5], vap_curve[:,0]),
                                      'color' : 'red',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )     
                
           
        
                

        
class IsoPrho(BasePlot):
    """Isopleth Prho diagram"""
    
    def __init__(self, parent, arrays=None, **kwarg):

        self.short_title = u"Isopleth P-\u03c1" 
        self.title = u'P-\u03c1 projection of the Isopleth Graph for a Composition (Z=%s)' % kwarg['z']
        self.xlabel = u'Density [mol/l]'
        self.ylabel = u'Temperature [K]'
        

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

        if 'ISO' in arrays.keys():
            for num, vap_curve in enumerate(arrays['ISO']):

                self.curves.append( {'name': u'Incipient Face.', 
                                     'visible':True, 
                                     'lines':( vap_curve[:,4], vap_curve[:,1]),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )


                self.curves.append( {'name': u'Major (Saturated) Face.',
                                     'visible':True, 
                                     'lines': (vap_curve[:,5], vap_curve[:,1]),
                                      'color' : 'red',
                                      'wx_id' : wx.NewId(),
                                      'type': 'ISO',
                                        } )     
                

class PT(BasePlot):
    """pressure-temperature diagram"""
    
    def __init__(self, parent, arrays=None, system=()):

        self.short_title = u"P-T"
        self.title = u'Pressure-Temperature projection of a global phase equilibrium diagram'
        self.xlabel = u'Temperature [K]'
        self.ylabel = u'Pressure [bar]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, system)        

    def setup_curves(self, arrays):

        if 'VAP' in arrays.keys():
            lines = []
            for num, vap_curve in enumerate(arrays['VAP']):
                lines += [ vap_curve[:,0], vap_curve[:,1] ]

                #counter = u'' if len(arrays['VAP']) == 1 else u' %i' % (num + 1)

            self.curves.append( {'name': u'Pure compound vapor pressure lines', # + counter , 
                                     'visible':True, 
                                     #'lines':( vap_curve[:,0], vap_curve[:,1]),
                                      'lines': tuple(lines),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'VAP',
                                        } )             

        if 'CRI' in arrays.keys():
            lines = []
            for num, cri_curve in enumerate(arrays['CRI']):
                lines += [cri_curve[:,0],cri_curve[:,1]]

                #counter = u'' if len(arrays['CRI']) == 1 else u' %i' % (num + 1)
            self.curves.append( {'name': u'Critical lines', 
                                 'visible':True, 
                                 #'lines':(cri_curve[:,0],cri_curve[:,1]),
                                 'lines': tuple(lines),
                                 'color' : 'black',
                                 'wx_id' : wx.NewId(),
                                 'type': 'CRI'
                                } )


        if 'LLV' in arrays.keys():
            
            for num, llv_curve in enumerate(arrays['LLV']):

                self.curves.append( { 'name': 'LLV', 
                                      'visible':True,
                                      'lines': (llv_curve[:,0], llv_curve[:,1]),           #TODO
                                      'color': 'red', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )

        
        if 'AZE' in arrays.keys():
            for num, aze_curve in enumerate(arrays['AZE']):
                self.curves.append( { 'name': u'Azeotropic lines', 
                                      'visible':True,
                                      'lines': (aze_curve[:,0], aze_curve[:,1]),           #TODO
                                      'color': 'magenta', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )



class Tx(BasePlot):
    """T-x plot"""
    
    def __init__(self, parent, arrays=None, system=()):
        self.short_title = u"T-x"
        self.title = u'Temperature-Composition projection of a global phase equilibrium diagram'
        self.xlabel = u'Composition'    #TODO DEFINE system inside the plot
        self.ylabel = u'Temperature [K]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, system)        

    def setup_curves(self, arrays):

               
        
        if 'CRI' in arrays.keys():
            lines = []
            for num, cri_curve in enumerate(arrays['CRI']):
                lines += [ cri_curve[:,3],cri_curve[:,0] ] 

                #counter = u'' if len(arrays['CRI']) == 1 else u' %i' % (num + 1)

            #this block could be inside the for to split the critical lines in separated segments

            self.curves.append( {'name': u'Critical lines', # + counter, 
                                 'visible':True, 
                                 #'lines':(cri_curve[:,3],cri_curve[:,0]),
                                 'lines': tuple(lines),
                                 'color' : 'black',
                                 'wx_id' : wx.NewId(),
                                 'type': 'CRI'
                                } )

        if 'LLV' in arrays.keys():
            for num, llv_curve in enumerate(arrays['LLV']):
            
                counter = u'' if len(arrays['LLV']) == 1 else u' %i' % (num + 1)

                self.curves.append( { 'name': 'LLV' + counter, 
                                      'visible':True,
                                      'lines': (llv_curve[:,2], llv_curve[:,0], llv_curve[:,3], llv_curve[:,0] ),   
                                      'color': 'blue', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )

                self.curves.append( { 'name': 'LLV' + counter, 
                                      'visible':True,
                                      'lines': (llv_curve[:,4], llv_curve[:,0]),   
                                      'color': 'red', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )


        if 'AZE' in arrays.keys():

            for num, aze_curve in enumerate(arrays['AZE']):
                self.curves.append( { 'name': u'Azeotropic line', 
                                      'visible':True,
                                      'lines': (aze_curve[:,2], aze_curve[:,0]),           #TODO
                                      'color': 'magenta', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )



class Pxy(BasePlot):
    """Pxy Px (isothermal)"""
    
    def __init__(self, parent, arrays=None, **kwarg):
        self.short_title = u"Pxy (isothermal)"
        self.title = u'Isothermal fluid phase equilibrium for T=%s [k]' % kwarg['t']

        self.ylabel = u'Pressure [bar]'
        self.xlabel = u'Composition '    #TODO DEFINE system inside the plot
        

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

               
        
        if 'Pxy' in arrays.keys():
            for num, isot_curve in enumerate(arrays['Pxy']):

                counter = u'' if len(arrays['Pxy']) == 1 else u' %i' % (num + 1)

                self.curves.append( {'name': u'Isothermal lines ' + counter, 
                                     'visible':True, 
                                     'lines':(isot_curve[:,1],isot_curve[:,0], isot_curve[:,2],isot_curve[:,0]),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'Pxy'
                                    } )



class PxyPrho(BasePlot):
    """Pxy P-Rho projection (isothermal)"""
    
    def __init__(self, parent, arrays=None, **kwarg):
        self.short_title = u"P-\u03c1 (isothermal)"
        self.title = u'Pressure-Density of the Isothermal fluid phase equilibrium for T=%s [k]' % kwarg['t']

        self.ylabel = u'Pressure [bar]'
        self.xlabel = u'Density [mol/l]'    #TODO DEFINE system inside the plot
        
        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

               
        
        if 'Pxy' in arrays.keys():
            for num, isot_curve in enumerate(arrays['Pxy']):

                counter = u'' if len(arrays['Pxy']) == 1 else u' %i' % (num + 1)

                self.curves.append( {'name': u'Isothermal lines ' + counter, 
                                     'visible':True, 
                                     'lines':(isot_curve[:,5],isot_curve[:,0], isot_curve[:,6], isot_curve[:,0]),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'Pxy'
                                    } )



class Txy(BasePlot):
    """Txy Tx (isobaric)"""
    
    def __init__(self, parent, arrays=None, **kwarg):
        self.short_title = u"Txy (isobaric)"
        self.title = u'Isobaric fluid phase equilibrium for P=%s [bar]' % kwarg['p']

        self.ylabel = u'Temperature [k]'
        self.xlabel = u'Composition'    #TODO DEFINE system inside the plot
        

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    def setup_curves(self, arrays):

               
        
        if 'Txy' in arrays.keys():
            for num, isob_curve in enumerate(arrays['Txy']):

                counter = u'' if len(arrays['Txy']) == 1 else u' %i' % (num + 1)

                self.curves.append( {'name': u'Isobaric lines' + counter, 
                                     'visible':True, 
                                     'lines':(isob_curve[:,1],isob_curve[:,0], isob_curve[:,2],isob_curve[:,0]),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'Txy'
                                    } )

class TxyTrho(BasePlot):
    """Txy T-Rho projection (isobaric)"""
    
    def __init__(self, parent, arrays=None, **kwarg):
        self.short_title = u"T-\u03c1 (isobaric)"
        self.title = u'Temperature-Density of the Isobaric fluid phase equilibrium for P=%s [bar]' % kwarg['p']

        self.ylabel = u'Temperature [bar]'
        self.xlabel = u'Density [mol/l]'    #TODO DEFINE system inside the plot
        
        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, **kwarg)        

    
    def setup_curves(self, arrays):

               
        
        if 'Txy' in arrays.keys():
            for num, isob_curve in enumerate(arrays['Txy']):

                counter = u'' if len(arrays['Txy']) == 1 else u' %i' % (num + 1)

                self.curves.append( {'name': u'Isobaric lines' + counter, 
                                     'visible':True, 
                                     'lines':(isob_curve[:,5],isob_curve[:,0], isob_curve[:,6],isob_curve[:,0]),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'Pxy'
                                    } )

                
class Px(BasePlot):
    """P-x diagram"""
    
    def __init__(self, parent, arrays=None, system=()):
        self.short_title = u"P-x"
        self.title = u'Pressure-Composition projection of a global phase equilibrium diagram'

        self.ylabel = u'Pressure [bar]'
        self.xlabel = u'Composition'    #TODO DEFINE system inside the plot
        

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, system)        

    def setup_curves(self, arrays):

               
        
        if 'CRI' in arrays.keys():
            lines = []
            for num, cri_curve in enumerate(arrays['CRI']):
                lines += [ cri_curve[:,3],cri_curve[:,1] ]
        

                #counter = u'' if len(arrays['CRI']) == 1 else u' %i' % (num + 1)

            self.curves.append( {'name': u'Critical lines', # + counter, 
                                     'visible':True, 
                                     #'lines':(cri_curve[:,3],cri_curve[:,1]),
                                     'lines': tuple(lines),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'CRI'
                                    } )

        if 'LLV' in arrays.keys():
            lines = []
            for num, llv_curve in enumerate(arrays['LLV']):
                lines += [llv_curve[:,2], llv_curve[:,1]]
            

                #counter = u'' if len(arrays['LLV']) == 1 else u' %i' % (num + 1)

            self.curves.append( { 'name': 'LLV', #+ counter, 
                                      'visible':True,
                                      #'lines': (llv_curve[:,2], llv_curve[:,1]),   
                                      'lines': tuple(lines),
                                      'color': 'red', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )

        if 'AZE' in arrays.keys():

            for num, aze_curve in enumerate(arrays['AZE']):
                self.curves.append( { 'name': u'Azeotropic line', 
                                      'visible':True,
                                      'lines': (aze_curve[:,2], aze_curve[:,1]),           #TODO
                                      'color': 'magenta', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )




class Trho(BasePlot):
    """temperature-density diagram"""
    
    def __init__(self, parent, arrays=None, system=()):

        self.short_title = u'T-\u03c1'
        self.title = u'Temperature-Density projection of a global phase equilibrium diagram'
        self.xlabel = u'Density [mol/l]'
        self.ylabel = u'Temperature [K]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, system)        

    def setup_curves(self, arrays):

        if 'VAP' in arrays.keys():
            lines = []
            for num, vap_curve in enumerate(arrays['VAP']):
                lines += [ vap_curve[:,2], vap_curve[:,0], vap_curve[:,3], vap_curve[:,0] ] 

                #counter = u'' if len(arrays['VAP']) == 1 else u' %i' % (num + 1)

            self.curves.append( {'name': u'Pure compound vapor pressure lines', 
                                     'visible':True, 
                                      #'lines':(vap_curve[:,2], vap_curve[:,0], vap_curve[:,3], vap_curve[:,0]),
                                      'lines': tuple(lines),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'VAP',
                                        } )      
                
       

        if 'CRI' in arrays.keys():
            lines = []
            for num, cri_curve in enumerate(arrays['CRI']):
                lines += [cri_curve[:,2],cri_curve[:,0]]
            

                #counter = u'' if len(arrays['CRI']) == 1 else u' %i' % (num + 1)
            self.curves.append( {'name': u'Critical lines', # + counter , 
                                     'visible':True, 
                                     #'lines':(cri_curve[:,2],cri_curve[:,0]),
                                     'lines': tuple(lines),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'CRI'
                                    } )


        if 'LLV' in arrays.keys():
            for num, llv_curve in enumerate(arrays['LLV']):
                self.curves.append( { 'name': 'LLV', 
                                      'visible':True,
                                      'lines': (llv_curve[:,7], llv_curve[:,0], llv_curve[:,8], llv_curve[:,0]),           #TODO
                                      'color': 'blue', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )


        if 'AZE' in arrays.keys():

            for num, aze_curve in enumerate(arrays['AZE']):
                self.curves.append( { 'name': u'Azeotropic line', 
                                      'visible':True,
                                      'lines': (aze_curve[:,4], aze_curve[:,0], aze_curve[:,5], aze_curve[:,0]),           #TODO
                                      'color': 'magenta', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )


class Prho(BasePlot):
    """pressure-density diagram"""
    
    def __init__(self, parent, arrays=None, system=()):

        self.short_title = u'P-\u03c1'
        self.title = u'Pressure-Density projection of a global phase equilibrium diagram'
        self.xlabel = u'Density [mol/l]'
        self.ylabel = u'Pressure [bar]'

        BasePlot.__init__(self, parent, arrays, self.title, self.xlabel, self.ylabel, system)        

    def setup_curves(self, arrays):

        if 'VAP' in arrays.keys():
            lines = []
            for num, vap_curve in enumerate(arrays['VAP']):
                lines += [vap_curve[:,2], vap_curve[:,1], vap_curve[:,3], vap_curve[:,1] ]
        
                
                #counter = u'' if len(arrays['VAP']) == 1 else u' %i' % (num + 1)

            self.curves.append( {'name': u'Pure compound vapor pressure lines', 
                                     'visible':True, 
                                      #'lines':( vap_curve[:,2], vap_curve[:,1], vap_curve[:,3], vap_curve[:,1]),
                                      'lines': tuple(lines),
                                      'color' : 'green',
                                      'wx_id' : wx.NewId(),
                                      'type': 'VAP',
                                        } )      
        
       

        if 'CRI' in arrays.keys():
            lines = []
            for num, cri_curve in enumerate(arrays['CRI']):
                lines += [cri_curve[:,2],cri_curve[:,1]]

                #counter = u'' if len(arrays['CRI']) == 1 else u' %i' % (num + 1)
            self.curves.append( {'name': u'Critical lines', # + counter , 
                                     'visible':True, 
                                     #lines':(cri_curve[:,2],cri_curve[:,1]),
                                     'lines': tuple(lines),
                                     'color' : 'black',
                                     'wx_id' : wx.NewId(),
                                     'type': 'CRI'
                                    } )


        if 'LLV' in arrays.keys():
            for num, llv_curve in enumerate(arrays['LLV']):

                self.curves.append( { 'name': 'LLV', 
                                      'visible':True,
                                      'lines': (llv_curve[:,7], llv_curve[:,1]),           #TODO
                                      'color': 'red', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )

        if 'AZE' in arrays.keys():
            for num, aze_curve in enumerate(arrays['AZE']):
                self.curves.append( { 'name': u'Azeotropic line', 
                                      'visible':True,
                                      'lines': (aze_curve[:,4], aze_curve[:,1], aze_curve[:,5], aze_curve[:,1]),           #TODO
                                      'color': 'magenta', 
                                      'wx_id' : wx.NewId(),
                                       'type': 'LLV',
                                    } )
