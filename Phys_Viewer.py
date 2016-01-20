# -*- coding: utf-8 -*-
# Tabbed Notebook GUI derived from https://gist.github.com/mikofski/5851633
# Notebook documentation at http://docs.python.org/py3k/library/tkinter.ttk.html?highlight=ttk#notebook
"""
Created on Tue Feb 10 06:27:33 2015
Physiology Viewer release version derived from Phys_74.py Oct 12, 2015

Documentation for using the program can be found at 
http://still-breathing.net/technical-details/ and
http://still-breathing.net/software/

@author: David Trowbridge
"""

import tkinter as tk
from tkinter import BOTH, TOP, Y, N, S, E, W, END
from tkinter import ttk, Canvas, Frame, Text, IntVar, StringVar, DoubleVar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
#from matplotlib.figure import Figure

LARGE_FONT = ("Verdana", 12)
NORM_FONT =  ("Verdana", 10)
SMALL_FONT = ("Verdana", 18)

graphs = {'d': 'delta', 
          't': 'theta', 
          'a': 'alpha', 
          'b': 'beta', 
          'g': 'gamma',
          'k': 'blink', 
          'j': 'jaw clench', 
          'c': 'concentration', 
          'm': 'mellow', 
          'v': 'heart', 
          'p': 'breath'}
        
plotlabel = {'d_m':'delta', 'dlb':'delta lb', 'dlf':'delta lf', 'drf':'delta rf', 'drb':'delta rb',
        't_m':'theta', 'tlb':'theta lb', 'tlf':'theta lf', 'trf':'theta rf', 'trb':'theta rb',
        'a_m':'alpha', 'alb':'alpha lb', 'alf':'alpha lf', 'arf':'alpha rf', 'arb':'alpha rb',
        'b_m':'beta', 'blb':'beta lb', 'blf':'beta lf', 'brf':'beta rf', 'brb':'beta rb',
        'g_m':'gamma', 'glb':'gamma lb', 'glf':'gamma lf', 'grf':'gamma rf', 'grb':'gamma rb',
        'x':'sway', 'k':'blink', 'j':'jaw clench', 'c':'concentration', 'm':'mellow', 'v':'heart', 'p':'breath',
        'lb':'raw lb', 'lf':'raw lf', 'rf':'raw rf', 'rb':'raw rb',
        }
        
plotcolor = {'d_m':'blue', 'dlb':'dodgerblue', 'dlf':'royalblue', 'drf':'cornflowerblue', 'drb':'deepskyblue',
        't_m':'cyan', 'tlb':'turquoise', 'tlf':'aquamarine', 'trf':'paleturquoise', 'trb':'powderblue',
        'a_m':'green', 'alb':'limegreen', 'alf':'mediumseagreen', 'arf':'springgreen', 'arb':'lightgreen',
        'b_m':'darkred', 'blb':'brown', 'blf':'sienna', 'brf':'darkgoldenrod', 'brb':'darkorange',
        'g_m':'magenta', 'glb':'mediumpurple', 'glf':'orchid', 'grf':'mediumorchid', 'grb':'plum',
        'x':'lime', 'k':'purple', 'j':'maroon', 'c':'goldenrod', 'm':'cadetblue', 'v':'red', 'p':'skyblue',
        'lb':'deeppink', 'lf':'deeppink', 'rf':'deeppink', 'rb':'deeppink',
        }
        
freqbands = ['delta', 'theta', 'alpha', 'beta', 'gamma']
locations = [['d_m', 'dlb', 'dlf','drf','drb'],
             ['t_m', 'tlb', 'tlf','trf','trb'],
             ['a_m', 'alb', 'alf','arf','arb'],
             ['b_m', 'blb', 'blf','brf','brb'],
             ['g_m', 'glb', 'glf','grf','grb']]


d_bands = {'d_m', 'dlb', 'dlf','drf','drb'}
t_bands = {'t_m', 'tlb', 'tlf','trf','trb'}
a_bands = {'a_m', 'alb', 'alf','arf','arb'}
b_bands = {'b_m', 'blb', 'blf','brf','brb'}
g_bands = {'g_m', 'glb', 'glf','grf','grb'}

cardioresp = {'v':'mv', 'p':'kPa'}

# The following is used for psd semi-log graphs only
XMIN = 0 # minimum frequency
XMAX = 55 # maximum frequency
YMIN = 0.1 # minimum PSD value
YMAX = 100 # maximum PSD value
lblY = YMAX - 30

band_patches = [
    patches.Rectangle((XMIN, YMIN), 4, YMAX, facecolor="blue", alpha=0.2),
    patches.Rectangle((4, YMIN), 4, YMAX, facecolor="cyan", alpha=0.2),
    patches.Rectangle((8, YMIN), 4, YMAX, facecolor="green", alpha=0.2),
    patches.Rectangle((12, YMIN), 18, YMAX, facecolor="orange", alpha=0.2),
    patches.Rectangle((30, YMIN), XMAX-30, YMAX, facecolor="magenta", alpha=0.2),
]

"""
    d~delta, t~theta, a~alpha, b~beta, g~gamma
    Individual spectrograms:
    s1 ~ left ear (TP9)
    s2 ~ left forehead (FP1)
    s3 ~ right forehead (FP2)
    s4 ~ right ear (TP10)
    
    x ~ swaying left/right x (/acc(2) in column 3)
      ~ rocking forward/back y (/acc(0))
      ~ bouncing up/down z (/acc(1))
    b ~ blink (in column 1)
    j ~ jaw clench (in column 1)
    c ~ concentration (in column 1)
    m ~ mellow (in column 1)
    
    dlb ~ delta, left, back (column 1)
    dlf ~ delta, left, front (column 2)
    drf ~ delta, right, front (column 3)
    dlf ~ delta, right, back (column 4)
    ...
    grb ~ gamma, right, back
    
    v ~ heart signal (EKG) in mv
    p ~ breath in kPa
    
    means ~ numerical mean values and standard deviations for each of four sensors
    medians ~ numerical median values and standard deviations for each of four sensors
       
"""


#current_index = 60 #Index for rec33
#current_index = 51 #Index for rec24
current_index = 29 #Index for rec1

def radar_factory(num_vars, frame='circle'):
    # Derived from http://matplotlib.org/examples/api/radar_chart.html
    """
    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.
    """
    # calculate evenly-spaced axis angles
    theta = 2*np.pi * np.linspace(0, 1-1./num_vars, num_vars)
    # rotate theta such that the first axis is at the top
    # theta += np.pi/2
    # rotate theta such that left front sensor, lf is at upper left 
    theta -= np.pi/4

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):
        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(theta * 180/np.pi, labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta

def unit_poly_verts(theta):
    """
    Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts

class PV(ttk.Frame):
     
    Labels = ['Interval', 'ti', 'tf']
    LabelObject = []
    EntryObject = []

    def __init__(self, name='phys_viewer'):
        ttk.Frame.__init__(self, name=name)
        self.index_var = IntVar()
        self.recording_var = StringVar()
        self.title_var = StringVar()
        self.person_var = StringVar()
        self.subject_var = StringVar()
        self.date_time_var = StringVar()
        self.graph_type_var = StringVar() # used by redio buttons for Time series, Radar, Table, etc.

        self.data_source_var = StringVar() #used by redio buttons for lb, lf, rf, rb, left, right, etc.
        self.data_type_var = {'d': IntVar(), 't': IntVar(), 'a': IntVar(), 'b': IntVar(), 'g': IntVar(), \
            'p': IntVar(), 'v': IntVar(), 'c': IntVar(), 'm': IntVar(), 'j': IntVar(), 'k': IntVar()}
        self.abs_offset_var = DoubleVar()
        self.abs_scale_var = DoubleVar()
        self.c_scale_var = DoubleVar()
        self.m_scale_var = DoubleVar()
        self.p_offset_var = DoubleVar()
        self.p_scale_var = DoubleVar()
        self.v_offset_var = DoubleVar()
        self.v_scale_var = DoubleVar()
       
        self.duration_var = StringVar()
        self.notes_var = StringVar()
        self.eeg_check_value = IntVar()
        self.heart_check_value = IntVar()
        self.breath_check_value = IntVar()
        self.eeg_label = StringVar()
        self.eeg_label.set(' EEG (220 Hz)')
        self.heart_label = StringVar()
        self.heart_label.set(' Heart (220 Hz)')
        self.breath_label = StringVar()
        self.breath_label.set(' Breath (22 Hz)')
        self.sample_rate_var = IntVar()
        self.rel_abs_var = StringVar()
        self.med_mean_var = StringVar()
        self.type_average_var = StringVar() # type of average (mean, median, std, meanstd) in tables
    
        self.interval = IntVar() # integer variable for keeping track 
        # of radiobutton selected

        # Nine rows of StringVar for each selectable radiobutton
        # Row zero is the default interval for the entire session
        # Rows 1-8 are for user-defined intervals
        # Columns are for interval name, initial time and final time        
        self.sva = [[StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()], \
        [StringVar(), StringVar(), StringVar()]]
        self.RadioObject = []
#        self.interval_int = IntVar()
#        self.interval_int.set(0)
        self.int_value = self.interval.set(0)
        self.graph_type_var.set('timeseries') # initialize graph_type radio button
        self.data_type_var['a'].set(1) #initialize data_type_var so that 'a' is selected
        self.data_source_var.set('lb') # initialize data_source as 'lb'
        self.type_average_var.set('mean') # initialize for type of table
        
        self.abs_offset_var.set(1.667)
        self.abs_scale_var.set(30.0)
        self.c_scale_var.set(1.333)
        self.m_scale_var.set(1.333)
        self.p_offset_var.set(0.0)
        self.p_scale_var.set(1.0)
        self.v_offset_var.set(0.0)
        self.v_scale_var.set(1.0)
        
        self.rel_abs_var.set('relative')
        self.med_mean_var.set('median')
        self.pack(expand=Y, fill=BOTH)
        self.master.title('Physiology Viewer')
        self.load_session_data()
        self._create_viewer_panel()
                         
    def load_session_data(self):
        """
        IMPORTANT: Currently data are stored in a hard-wired directory, C:\MedRec
        Session data is an Excel file in that directory, EEG_CardioRespSessions.xls
        """
        self.path = 'C:/MedRec/'
        self.sessions_file = 'EEG_CardioRespSessions.xls'
        self.sessions_data = pd.ExcelFile(self.path+self.sessions_file)
        self.sessions_df = self.sessions_data.parse('Sheet1', index_col='index', na_values=['None'])
#        self.sessions_file.close()
            
    def _create_viewer_panel(self):
        viewerPanel = Frame(self, name='pv')
        viewerPanel.pack(side=TOP, fill=BOTH, expand=Y)
                 
        # create the notebook
        nb = ttk.Notebook(viewerPanel, name='notebook')
 
        # extend bindings to top level window allowing
        #   CTRL+TAB - cycles thru tabs
        #   SHIFT+CTRL+TAB - previous tab
        #   ALT+K - select tab using mnemonic (K = underlined letter)
        nb.enable_traversal()
         
        nb.pack(fill=BOTH, expand=Y, padx=2, pady=3)
#        self._create_session_tab(nb)
#        self._create_request_tab(nb)
        self._create_UI_tab(nb)  #NEW
        self._create_Settings_tab(nb)  #NEW
                                

    def _create_UI_tab(self, nb):
        """
        Creates the Main user interface (UI) tab in the Physiology Viewer.
        """
        self.widEEG = {}
        
        def update_session_data(event):
            """ 
            This routine updates the contents of the dataframe sessions_df
            whenever a new session is selected in the drop-down combobox cbx1
            on the _create_UI_tab.
            """
            global current_index
            current_index =  self.cbx1.current()
            #print('current_index = '+str(current_index))
            self.index_var.set(current_index)
            self.recording_var.set(self.sessions_df.ix[current_index]['recording'])
            self.person_var.set(self.sessions_df.ix[current_index]['person'])
            self.subject_var.set(self.sessions_df.ix[current_index]['subject'])
            self.date_time_var.set(self.sessions_df.ix[current_index]['date_time'])
            self.duration_var.set(self.sessions_df.ix[current_index]['duration'])
            notes = self.sessions_df['notes'][self.index_var.get()]
            self.txt1.delete(1.0, END) # Delete from line 1, character 0 to end of text
            self.txt1.insert(END, notes)
            self.eeg_check_value.set(self.sessions_df.ix[current_index]['eeg'])
            self.heart_check_value.set(self.sessions_df.ix[current_index]['hrt'])
            self.breath_check_value.set(self.sessions_df.ix[current_index]['bth'])
            self.sample_rate_var.set(self.sessions_df.ix[current_index]['Hz'])
            #print('current_index=', current_index)
            #print('eeg_check_value=', self.eeg_check_value.get())
            #print('heart_check_value=', self.heart_check_value.get())
            #print('breath_check_value=', self.breath_check_value.get())
            update_widgets()
            update_labels()
    #        interval1 = str(self.interval1_var.get())
    #        print('interval1 = '+str(interval1))
            self.sva[0][0].set('entire session') # Initial line is 
            # initialized with ti=0, tf=duration
            self.sva[0][1].set('0')
            duration = self.duration_var.get()
            self.sva[0][2].set(duration)
            for i in range(1,9): # fill in user-defined intervals in rows 1-8
                #print('i = '+str(i))
                #print('current_index = '+str(current_index))
                self.sva[i][0].set(self.sessions_df.ix[current_index]['interval'+str(i)])
                self.sva[i][1].set(self.sessions_df.ix[current_index]['ti'+str(i)])
                self.sva[i][2].set(self.sessions_df.ix[current_index]['tf'+str(i)])
    
            
            print(self.notes_var.get())
            update_graph_data(current_index)
            
        def update_graph_data(index):
            """
            Using the values of the checkboxes 'eeg', 'hrt' and 'bth',
            reads data for session index from the corresponding .h5 file and 
            populates the dataframes absolute_df, relative_df, user_df and raw_df, and
            cardio_df and resp_df.
            """
            global recording, sessions_df
    #        global relative_df, user_df, raw_df, cardio_df, resp_df
            if 0 < index < 29:
                recording = 'lqt'+str(index)
            elif 29 <= index:
                recording = 'rec'+str(index-27)
            else:
                print('index out of range')
            #print('recording='+recording)
            
            # Reset dataframes to None to clear out residual data from previous selections
            self.absolute_df = None
            self.relative_df = None
            self.user_df = None
            self.raw_df = None
            self.cardio_df = None
            self.resp_df = None
            
            # Read data from files indicated as existent by checkboxes
            if str(self.sessions_df['eeg'][index]) == '1':
                #print('reading EEG data')
                self.absolute_df = pd.read_hdf(self.path+recording+'_eeg_abs.h5', 'abs_data')
                self.relative_df = pd.read_hdf(self.path+recording+'_eeg_rel.h5', 'rel_data')
                self.user_df = pd.read_hdf(self.path+recording+'_eeg_user.h5', 'user_data')
                self.raw_df = pd.read_hdf(self.path+recording+'_eeg_raw.h5', 'raw_data')
                nsamples = len(self.raw_df)
                self.fs = 220.0
                timeseries = np.arange(nsamples)/self.fs
                self.raw_df.insert(0, 't', pd.Series(timeseries, index=self.raw_df.index))
            if str(self.sessions_df['hrt'][index]) == '1':
                #print('reading cardio data')
                # Try to normalize heart values to minimize overlap with breath and eeg
                self.cardio_df = (pd.read_hdf(self.path+recording+'_cardio.h5', 'cardio_data') + 1.0)/8.0 + 0.5
            if str(self.sessions_df['bth'][index]) == '1':
                #print('reading respiration data')
                # Try to normalize breath values to minimize overlap with heart and eeg
                self.resp_df = (pd.read_hdf(self.path+recording+'_breath.h5', 'resp_data') - 103)
    
        def update_notes(notes):
            self.sessions_df.set(current_index, 'notes', notes)
            print(notes)
            
        def update_widgets():
            print('in update_widgets')
            graph = self.graph_type_var.get()
            if self.eeg_check_value.get(): # EEG data exists
                if graph == 'timeseries':
                    self.enable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean|self.widSrc)
                elif graph == 'spectrogram':
                    self.disable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean)
                    self.enable_widget(self.widSrc)
                elif graph == 'psd':
                    self.disable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean)
                    self.enable_widget(self.widSrc)
                elif graph == 'raweeg':
                    self.disable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean)
                    self.enable_widget(self.widSrc)
                elif graph == 'radar':
                    self.disable_widget(self.widBands|self.widUser|self.widMedMean|self.widSrc)
                    self.enable_widget(self.widRelAbs)
                elif graph == 'table':
                    self.disable_widget(self.widBands|self.widUser|self.widMedMean|self.widSrc)
                    self.enable_widget(self.widRelAbs)
            else: # EEG data does not exist
                self.disable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean|self.widSrc)                
                self.uncheck_data_source_widgets(['d', 't', 'a', 'b', 'g', 'c', 'm', 'j', 'k']) # EEG bands do not apply
            if self.heart_check_value.get(): # heart data exists
                if graph == 'timeseries':
                    self.widHeart.configure(state='normal')
                else:
                    self.widHeart.configure(state='disabled')
            else: # heart data does not exist
                self.widHeart.configure(state='disabled')
                self.uncheck_data_source_widgets(['v']) # EEG bands do not apply
            if self.breath_check_value.get(): # breath data exists
                if graph == 'timeseries':
                    self.widBreath.configure(state='normal')
                else:
                    self.widBreath.configure(state='disabled')
            else: # breath data does not exist
                self.widBreath.configure(state='disabled')
                self.uncheck_data_source_widgets(['p']) # EEG bands do not apply
                    
                
        def update_labels():
            #print('entering update_labels')
            #print('heart_check_value=', self.heart_check_value.get())
            if self.eeg_check_value.get():
                self.eeg_label.set(' EEG (220 Hz)')
            else:
                self.eeg_label.set('')
            if self.heart_check_value.get():
                self.heart_label.set(' Heart (220 Hz)')
            else:
                self.heart_label.set('')
            if self.breath_check_value.get():
                self.breath_label.set(' Breath (22 Hz)')
            else:
                self.breath_label.set('')
            #print('heart_label=',self.heart_label.get())
            
        # frame to hold contentx
        self.frame = ttk.Frame(nb, height='10i', width='8i', name='main')
        # widgets to be displayed on 'Session' tab
        lbl0 = ttk.Label(self.frame, text='Session title goes here', width=40)    
        lbl0.grid(row=0, column=0, columnspan=3, sticky=N)

        self.cbx1 = ttk.Combobox(self.frame, width=50, textvariable=self.title_var, state='readonly')
#        self.cbx1 = ttk.Combobox(self.frame, width=50, textvariable=self.person_title_var, state='readonly')
        sessions_list = self.sessions_df['recording'] + ' - ' + self.sessions_df['person'] + ' - ' + self.sessions_df['title']
        self.cbx1['values'] = [row for row in sessions_list]
        self.cbx1.current(29) # Sets current value to first session involving brain waves
        self.cbx1.bind("<<ComboboxSelected>>", update_session_data)
        self.cbx1.grid(row=1, column=0, columnspan=3, sticky=W)
        
        self.txt1 = Text(self.frame, height=10, wrap=tk.WORD)
        notes = self.sessions_df['notes'][self.index_var.get()]
        self.txt1.insert(END, notes)
        self.txt1.grid(row=2, column=0, rowspan=3, columnspan=4, sticky=(N,S,E,W))
        self.notes_var.trace("w", lambda name, index, mode, notes_var=self.notes_var: self.update_notes(notes))
#        print(txt1.get(1))

        lbl1 = ttk.Label(self.frame, textvariable=self.eeg_label, width=15)
        lbl1.grid(row=2, column=4, sticky=(N,W))
        lbl2 = ttk.Label(self.frame, textvariable=self.heart_label, width=15)
        lbl2.grid(row=3, column=4, sticky=(N,W))
        lbl3 = ttk.Label(self.frame, textvariable=self.breath_label, width=15)
        lbl3.grid(row=4, column=4, sticky=(N,W))

        rdo1 = ttk.Radiobutton(self.frame, text='Time Series', variable=self.graph_type_var, value='timeseries', command=lambda: update_widgets())
        rdo2 = ttk.Radiobutton(self.frame, text='Spectrogram', variable=self.graph_type_var, value='spectrogram', command=lambda: update_widgets())
        rdo3 = ttk.Radiobutton(self.frame, text='PSD vs Frequency', variable=self.graph_type_var, value='psd', command=lambda: update_widgets())
        rdo4 = ttk.Radiobutton(self.frame, text='Raw EEG', variable=self.graph_type_var, value='raweeg', command=lambda: update_widgets())
        rdo5 = ttk.Radiobutton(self.frame, text='Radar Chart', variable=self.graph_type_var, value='radar', command=lambda: update_widgets())
        rdo6 = ttk.Radiobutton(self.frame, text='Table', variable=self.graph_type_var, value='table', command=lambda: update_widgets())

        rdo1.grid(row=5, column=0, sticky=W)
        rdo2.grid(row=7, column=0, sticky=W)
        rdo3.grid(row=8, column=0, sticky=W)
        rdo4.grid(row=9, column=0, sticky=W)
        rdo5.grid(row=10, column=0, sticky=W)
        rdo6.grid(row=11, column=0, sticky=W)

        frm1 = ttk.Frame(self.frame, borderwidth=2, width=20) # frame for containing checkboxes d,t,a,b,g,...
        frm1.grid(row=5, column=1, sticky=W)
        chk1 = ttk.Checkbutton(frm1, text='d ', variable=self.data_type_var['d'])
        chk2 = ttk.Checkbutton(frm1, text='t ', variable=self.data_type_var['t'])
        chk3 = ttk.Checkbutton(frm1, text='a ', variable=self.data_type_var['a'])
        chk4 = ttk.Checkbutton(frm1, text='b ', variable=self.data_type_var['b'])
        chk5 = ttk.Checkbutton(frm1, text='g ', variable=self.data_type_var['g'])
        chk6 = ttk.Checkbutton(frm1, text='p ', variable=self.data_type_var['p'])
        chk7 = ttk.Checkbutton(frm1, text='v ', variable=self.data_type_var['v'])
        chk8 = ttk.Checkbutton(frm1, text='c ', variable=self.data_type_var['c'])
        chk9 = ttk.Checkbutton(frm1, text='m ', variable=self.data_type_var['m'])
        chk10 = ttk.Checkbutton(frm1, text='j ', variable=self.data_type_var['j'])
        chk11 = ttk.Checkbutton(frm1, text='k', variable=self.data_type_var['k'])
        
        chk1.grid(row=0, column=0)
        chk2.grid(row=0, column=1)
        chk3.grid(row=0, column=2)
        chk4.grid(row=0, column=3)
        chk5.grid(row=0, column=4)
        chk6.grid(row=1, column=0)
        chk7.grid(row=1, column=1)
        chk8.grid(row=1, column=2)
        chk9.grid(row=1, column=3)
        chk10.grid(row=1, column=4)
        chk11.grid(row=1, column=5)

        frm3 = ttk.Frame(self.frame, borderwidth=2, width=20) # frame for radio buttons relative,absolute,median,mean,...
        frm3.grid(row=5, column=2, sticky=W)

        rdo20 = ttk.Radiobutton(frm3, text='relative', variable=self.rel_abs_var, value='relative')
        rdo21 = ttk.Radiobutton(frm3, text='absolute', variable=self.rel_abs_var, value='absolute')

        rdo22 = ttk.Radiobutton(frm3, text='median', variable=self.med_mean_var, value='median')
        rdo23 = ttk.Radiobutton(frm3, text='mean', variable=self.med_mean_var, value='mean')

        rdo20.grid(row=0, column=0, sticky=E)
        rdo21.grid(row=0, column=1, sticky=E)
        rdo22.grid(row=1, column=0, sticky=E)
        rdo23.grid(row=1, column=1, sticky=E)

        cbx2 = ttk.Combobox(self.frame, width=18, textvariable=self.type_average_var, state='readonly')
        cbx2.grid(row=11, column=1, sticky=W)
        cbx2['values'] = ('mean', 'median', 'std', 'meanstd')
#        cbx2.bind('<<ComboboxSelected>>', self.set_table_type())

        frm4 = ttk.Frame(self.frame, borderwidth=2, width=20) # frame for radio buttons lf,rf,...
        frm4.grid(row=5, column=3, sticky=W)

        rdo11 = ttk.Radiobutton(frm4, text='lb', variable=self.data_source_var, value='lb')
        rdo12 = ttk.Radiobutton(frm4, text='lf', variable=self.data_source_var, value='lf')
        rdo13 = ttk.Radiobutton(frm4, text='rf', variable=self.data_source_var, value='rf')
        rdo14 = ttk.Radiobutton(frm4, text='rb', variable=self.data_source_var, value='rb')
        """ # Disable controls for left/right, front/back and mean averages until implementation later
        rdo15 = ttk.Radiobutton(frm4, text='left', variable=self.data_source_var, value='left')
        rdo16 = ttk.Radiobutton(frm4, text='right', variable=self.data_source_var, value='right')
        rdo17 = ttk.Radiobutton(frm4, text='front', variable=self.data_source_var, value='front')
        rdo18 = ttk.Radiobutton(frm4, text='back', variable=self.data_source_var, value='back')
        rdo19 = ttk.Radiobutton(frm4, text='mean', variable=self.data_source_var, value='mean')
        """
        rdo11.grid(row=2, column=0, sticky=E)
        rdo12.grid(row=0, column=0, sticky=E)
        rdo13.grid(row=0, column=2, sticky=W)
        rdo14.grid(row=2, column=2, sticky=W)
        """ # Disable until future implementation
        rdo15.grid(row=3, column=0, sticky=E)
        rdo16.grid(row=3, column=2, sticky=W)
        rdo17.grid(row=0, column=3, sticky=E)
        rdo18.grid(row=2, column=3, sticky=E)
        rdo19.grid(row=3, column=3, sticky=E)
        """

        frm411 = ttk.Frame(frm4, borderwidth=2, width=20) # frame for head graphic,...
        frm411.grid(row=1, column=1, sticky=(N,S,E,W))
        
        can = Canvas(frm411, width=55, height=55)
        can.grid()
        can.create_oval(5, 7, 50, 52, fill="blanched almond") # scalp
        can.create_oval(2, 20, 6, 35, fill="blanched almond") # left ear
        can.create_oval(49, 20, 53, 35, fill="blanched almond") # right ear
        can.create_polygon(23, 7, 27.5, 2, 32, 7, fill="blanched almond", outline="black") # nose

        frm2 = ttk.Frame(self.frame, borderwidth=2, width=20) # frame for Intervals, t_initial, t_final
        frm2.grid(row=12, column=0, columnspan=3, sticky=W)

        lbl4 = ttk.Label(frm2, text='Intervals', width=12)
        lbl5 = ttk.Label(frm2, text='t_initial', width=10)
        lbl6 = ttk.Label(frm2, text='t_final', width=10)

        lbl4.grid(row=0, column=1, sticky=W)
        lbl5.grid(row=0, column=2, sticky=E)
        lbl6.grid(row=0, column=3, sticky=E)

        btn0 = ttk.Button(self.frame, text='Display', command=self.select_graph)
        btn0.grid(row=11, column=3)

        for i in range(9):
            self.sva[i][0].trace("w", lambda name, index, mode, var=self.sva[i][0], i=i:
                              self.update_value(var, i, 0))
            self.sva[i][1].trace("w", lambda name, index, mode, var=self.sva[i][1], i=i:
                              self.update_value(var, i, 1))
            self.sva[i][2].trace("w", lambda name, index, mode, var=self.sva[i][2], i=i:
                              self.update_value(var, i, 2))
            self.RadioObject.append(ttk.Radiobutton(frm2, textvariable=self.sva[i][0], variable=self.interval, value=i).grid(row=i+1, column=0, sticky=W))     # radiobutton
            self.interval.set(0)
            self.EntryObject.append(ttk.Entry(frm2, width=20, textvariable=self.sva[i][0]).grid(row=i+1, column=1,sticky=W)) # interval entry
            self.EntryObject.append(ttk.Entry(frm2, width=8, textvariable=self.sva[i][1]).grid(row=i+1, column=2, sticky=W)) #ti entry
            self.EntryObject.append(ttk.Entry(frm2, width=8, textvariable=self.sva[i][2]).grid(row=i+1, column=3, sticky=W)) # tf entry

        btn1 = ttk.Button(frm2, text='Save', command=self.save_session_data)
        btn1.grid(row=10, column=2, columnspan=2)
        
#        self.frame.rowconfigure(1, weight=1)
#        self.frame.columnconfigure((0,1), weight=1, uniform=1)
         
        # add to notebook (underline = index for short-cut character)
        nb.add(self.frame, text='Main', underline=0, padding=2)
        
        self.widBands = {chk1, chk2, chk3, chk4, chk5}
        self.widUser = {chk8, chk9, chk10, chk11}
        self.widRelAbs = {rdo20, rdo21}
        self.widMedMean = {rdo22, rdo23}
        self.widSrc = {rdo11, rdo12, rdo13, rdo14}
#        self.widSrc = {rdo11, rdo12, rdo13, rdo14, rdo15, rdo16, rdo17, rdo18, rdo19}
        self.widBreath = chk6
        self.widHeart = chk7

        update_session_data(self) # Causes update even when do combobox selection has been made
        
    def uncheck_data_source_widgets(self, srclist):
        """
        When EEG, heart or breath data do not exist, uncheck corresponding data source checkboxes
        (to prevent draw_graph routine from trying to plot missing data)
        """
        for x in srclist:
            self.data_type_var[x].set(0)

                
    def disable_widget(self, widset):
        for wid in widset:
            wid.configure(state='disabled')

    def enable_widget(self, widset):
        for wid in widset:
            wid.configure(state='normal')

    def _create_Settings_tab(self, nb):
        """
        Creates the Settings tab in the Physiology Viewer.
        """
        # frame to hold contentx
        self.frame = ttk.Frame(nb, name='settings')
        # add to notebook (underline = index for short-cut character)
        nb.add(self.frame, text='Settings', underline=0, padding=2)
        
        
    def draw_spectrogram(self):
        popup = tk.Tk()
        popup.geometry('700x460') # Set dimensions of popup window to 800x500 pixels
        popup.wm_title("Physiology graph")
        p = plt.figure()
        self.ax = plt.subplot(111)
        # In preparation for plotting, get the current radiobutton selection and the 
        # corresponding initial and final times of the interval        
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        #print('int_value = '+str(int_value))
        
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())
        r = self.data_source_var.get()
        graph_title = 'Spectrogram for '+str(r)
        plt.xlabel('time (s)')
        plt.ylabel('frequency (Hz)')
# A future feature may be to display a spectrogram superimposed with a plot of
# absolute EEG time series (2nd ordinate on the right), in which case this will
# be a loop.
#        item_list = list(self.data_type_var.items())
#        for pair in item_list:
#            if pair[1].get(): # if the corresponding checkbox is checked        
        #                    Pxx, freqs, bins, im = self.ax.specgram(self.raw_df[spect[d]],NFFT=256,Fs=220) # E.g., request 's1' --> key 'lb'
        i = int(ti*self.fs)
        f = int(tf*self.fs)
        i_range = np.logical_and(i < self.raw_df.index, self.raw_df.index < f)
        signal = self.raw_df[r][i_range]
        Pxx, freqs, bins, im = self.ax.specgram(signal, NFFT=1024, noverlap=512, Fs=220, xextent=(ti,tf))
        plt.ylim(0,55) # cutoff frequency less than 60 Hz which is due to AC power contamination
        plt.xlim(ti, tf)

#        cb = p.colorbar(im, shrink=0.9, pad=0.02)
        cb = p.colorbar(im, shrink=0.9, pad=0.02)
        cb.set_label('Intensity (dB)')
        
        recording = self.sessions_df.ix[current_index]['recording']
        title = self.sessions_df.ix[current_index]['title']
        subject = self.sessions_df.ix[current_index]['subject']
#        duration = self.sessions_df.ix[current_index]['duration']
#        date_time = self.sessions_df.ix[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')

        box = self.ax.get_position()
#        self.ax.set_position([box.x0, box.y0, box.width, box.height*0.9])
#        self.ax.set_position([box.x0, box.y0-0.04, box.width, box.height*0.95])
        self.ax.set_position([box.x0, box.y0, box.width, box.height*0.95])

        plt.show()

#        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
#        text=recording+' recorded '+str(date_time)+' at ('+str('%.0f' % duration)+' s'+')')
#        lbl0.pack(side=tk.BOTTOM, fill=X)
        
        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)
        
        toolbar = NavigationToolbar2TkAgg(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)
        
        popup.mainloop()
        return None

    def draw_psd(self):
        popup = tk.Tk()
        popup.geometry('720x480') # Set dimensions of popup window to 800x500 pixels
        popup.wm_title("Power Spectral Density")
        p = plt.figure()
        self.ax = plt.subplot(111)
        # In preparation for plotting, get the current radiobutton selection and the 
        # corresponding initial and final times of the interval        
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        #print('int_value = '+str(int_value))
        
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())

        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width, box.height*0.95])

        recording = self.sessions_df.ix[current_index]['recording']
        title = self.sessions_df.ix[current_index]['title']
        subject = self.sessions_df.ix[current_index]['subject']
#        duration = self.sessions_df.ix[current_index]['duration']
#        date_time = self.sessions_df.ix[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        d = self.data_source_var.get()
        graph_title = 'Power Spectral Density at '+str(d)
        i = int(ti*self.fs)
        f = int(tf*self.fs)
        i_range = np.logical_and(i < self.raw_df.index, self.raw_df.index < f)
        signal = self.raw_df[d][i_range]
        Pxx, freqs = plt.psd(signal, NFFT=1024, noverlap=512, Fs=220, color="black")
        self.ax.set_yscale('log')
        self.ax.set_xscale('linear')
        """
        axpos = self.ax.get_position()
        axx0 = axpos.x0 # left of ax
        axy0 = axpos.y0 # bottom of ax
        axwidth = axpos.width # width of ax
        axheight = axpos.height # height of ax
        print('x0=',axx0)
        print('y0=',axy0) # bottom
        print('width=',axwidth)
        print('height=',axheight)
        """
        plt.xlabel('Frequency (Hz)')
        plt.xlim(XMIN, XMAX)
        plt.ylim(YMIN, YMAX)
        for ptch in band_patches:
            self.ax.add_patch(ptch)
        self.ax.annotate('delta', xy=(2,lblY), fontsize=10, color=None, horizontalalignment='center')
        self.ax.annotate('theta', xy=(6,lblY), fontsize=10, color=None, horizontalalignment='center')
        self.ax.annotate('alpha', xy=(10,lblY), fontsize=10, color=None, horizontalalignment='center')
        self.ax.annotate('beta', xy=(21,lblY), fontsize=10, color=None, horizontalalignment='center')
        self.ax.annotate('gamma', xy=(42,lblY), fontsize=10, color=None, horizontalalignment='center')

        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')
        plt.show()

#        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
#        text=recording+' recorded '+str(date_time)+' at ('+str('%.0f' % duration)+' s'+')')
#        lbl0.pack(side=tk.BOTTOM, fill=X)
        
        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)
        
        toolbar = NavigationToolbar2TkAgg(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)
        
        popup.mainloop()
        return None
    
    def draw_raw_eeg(self):
        popup = tk.Tk()
        popup.geometry('700x460') # Set dimensions of popup window to 800x500 pixels
        popup.wm_title("Raw EEG")
        p = plt.figure()
        self.ax = plt.subplot(111)
        # In preparation for plotting, get the current radiobutton selection and the 
        # corresponding initial and final times of the interval        
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        #print('int_value = '+str(int_value))
        
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())

        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width, box.height*0.9])

        recording = self.sessions_df.ix[current_index]['recording']
        title = self.sessions_df.ix[current_index]['title']
        subject = self.sessions_df.ix[current_index]['subject']
#        duration = self.sessions_df.ix[current_index]['duration']
#        date_time = self.sessions_df.ix[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        graph_title = 'Raw EEG Signal'
        plt.xlabel('samples (220 per second)')
        plt.ylabel('voltage (microvolts)')
        d = self.data_source_var.get()
        i = int(ti*self.fs)
        f = int(tf*self.fs)
        i_range = np.logical_and(i < self.raw_df.index, self.raw_df.index < f)
        self.ax.plot(self.raw_df[d][i_range].index, self.raw_df[d][i_range], color=plotcolor[d], label=plotlabel[d])

        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')
        plt.show()

#        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
#        text=recording+' recorded '+str(date_time)+' at ('+str('%.0f' % duration)+' s'+')')
#        lbl0.pack(side=tk.BOTTOM, fill=X)
        
        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)
        
        toolbar = NavigationToolbar2TkAgg(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)
        
        popup.mainloop()
        return None

    def draw_radar_chart(self):
        """
        In a new pop-up window, draws a radar chart with positions lb, lf, rf, rb
        arranged around a circle. Each of the five are plotted with a unique color:
        delta: blue, theta: cyan, alpha: green, beta: orange, gamma: red.
        Power values are indicated by the radial lengths of the vertices of a polygon.
        
        Median values are plotted for relative power, mean values for absolute power.
        Range of median relative power is [0:1]; range of mean absolute power is [0:100].
        """
        theta = radar_factory(4, frame='circle')

        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        if int_value > 0:
            #interval_string = self.sessions_df.ix[current_index]['interval'+str(int_value)]
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'
#        print('interval_string='+interval_string)
        popup = tk.Tk()
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())
#        print('ti='+str('%.3f' % ti))
#        print('tf='+str('%.3f' % tf))
        if self.rel_abs_var.get()=='absolute': # Absolute values
            popup.wm_title("Radar Chart of Mean Absolute EEG values")
#            graph_title = 'EEG Inverse Log of Mean Absolute Band Power'
            graph_title = 'EEG of Mean Absolute Band Power'
            t_range = np.logical_and(ti < self.absolute_df.index, self.absolute_df.index < tf) # t_range is the same for all relative bands
#            print('t_range for absolute')
#            print(t_range)
            values_list = []
            values_array = []
            for i in range(len(freqbands)):
                for j in range(len(locations[i])-1, 0, -1): # omit average value; step down for proper radar display
                    values_list.append(30*(self.absolute_df[freqbands[i]][t_range][locations[i][j]]+1.667).mean())
#                    values_list.append(50*(self.absolute_df[freqbands[i]][t_range][locations[i][j]]+1).mean())
#                    print('absolute values_list')
#                    print(values_list)
                values_array.append(values_list)
                values_list = []
        elif self.rel_abs_var.get()=='relative': # Relative values
            popup.wm_title("Radar Chart of Median Relative EEG values")
            graph_title = 'EEG Median Relative Band Power'
            t_range = np.logical_and(ti < self.relative_df.index, self.relative_df.index < tf) # t_range is the same for all relative bands
#            print('t_range for relative')
#            print(t_range)
            values_list = []
            values_array = []
            for i in range(len(freqbands)):
                for j in range(len(locations[i])-1, 0, -1): # omit average value; step down for proper radar display
                    values_list.append(self.relative_df[freqbands[i]][t_range][locations[i][j]].median())
                    print('relative values_list')
                    print(values_list)
                values_array.append(values_list)
                values_list = []
        data = values_array
#        print('data=')
#        print(data)
        spoke_labels = ['rb', 'rf', 'lf', 'lb']
        
    
        p = plt.figure(figsize=(6, 6))
        p.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    
        colors = ['blue', 'cyan', 'green', 'orange', 'magenta']
        
        self.ax = plt.subplot(111, projection='radar')

        # Adjust the height of the window so that title and legend are fully visible        
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width*0.95, box.height*0.95])

        if self.rel_abs_var.get()=='absolute': # Absolute values
            plt.rgrids([20, 40, 60, 80])
            plt.ylim(0, 100)
        elif self.rel_abs_var.get()=='relative': # Relative values
            plt.rgrids([0.2, 0.4, 0.6, 0.8])
            plt.ylim(0, 0.8)
#        plt.rgrids([0.2, 0.4, 0.6, 0.8])
        self.ax.set_title(interval_string, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        i = 0
        for d, color in zip(data, colors):
            self.ax.plot(theta, d, color=color)
            """
            if i < 4:
#               print('theta['+str(i)+']='+str('%.2f' % theta[i])+' d='+str('%.3f' % d[i])+' color='+str(color))
                print('theta['+str(i)+']='+str('%.2f' % theta[i]))
                print(d)
            i += 1
            """
            self.ax.fill(theta, d, facecolor=color, alpha=0.25)
        
        self.ax.set_varlabels(spoke_labels)
        
        
        # add legend relative to top-left plot
        plt.subplot(1, 1, 1)
        labels = ('Delta', 'Theta', 'Alpha', 'Beta', 'Gamma')
        legend = plt.legend(labels, loc=(0.9, .95), labelspacing=0.2)
        plt.figtext(0.04, 0.82, 'lf ~ left front (FP1)\n\
rf ~ right front (FP2)\n\
lb ~ left back (TP9)\n\
rb ~ right back (TP10)', ha='left', color='black', size='medium')
        plt.setp(legend.get_texts(), fontsize='medium')
        plt.setp(legend.get_lines(), linewidth='3')
#        plt.figtext(0.5, 0.965, 'Median Relative Power of Five Frequency Bands',
#                    ha='center', color='black', weight='bold', size='large')
        title = self.sessions_df.ix[current_index]['title']
        recording = self.sessions_df.ix[current_index]['recording']
        subject = self.sessions_df.ix[current_index]['subject']
        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')
        plt.show()
        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)
        
        toolbar = NavigationToolbar2TkAgg(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)
        popup.mainloop()
            
    def draw_table(self):
        """
        In a new pop-up window, draws a text box and fills it with lines of data
        corresponding to selected interval of a session. Options include mean,
        median and standard deviation for either relative or absolute power.
        EEG values for each of four sensors are in four rows.
        
        There are five columns of data: delta, theta, alpha, beta, gamma
        and four rows: lb, lf, rf, rb. This format makes for ease in
        copy/paste from the table into Excel when graphing power vs. time charts.
       
        The grph commands 'mean', 'median' and 'std' display corresponding tables
        of values.
                
        The grph command 'meanstd' is different. In the case of relative power,
        it displays a table with both mean and standard deviation values.
        In the case of absolute power, it displays inverse logarithms of
        mean absolute values and corresponding standard deviations.
        """
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        if int_value > 0:
            #interval_string = self.sessions_df.ix[current_index]['interval'+str(int_value)]
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'
        title = self.sessions_df.ix[current_index]['title']
        recording = self.sessions_df.ix[current_index]['recording']
        subject = self.sessions_df.ix[current_index]['subject']
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())
#        band_vals = []
        values_list = []
        values_array = []
        popup = tk.Tk()
        grph = self.type_average_var.get()
        if self.rel_abs_var.get()=='absolute': # Display absolute values normalized to range [0:100] in table
            popup.wm_title("Average Absolute EEG values")
            t_range = np.logical_and(ti < self.absolute_df.index, self.absolute_df.index < tf) # t_range is the same for all relative bands
            if grph == 'meanstd': # columns are delta, d-std, theta, t-std, alpha, a-std, beta, b-std, gamma, gstd 
                                   # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(np.power(10,self.absolute_df[freqbands[i]][t_range][locations[i][j]].mean()))
                        values_list.append(self.absolute_df[freqbands[i]][t_range][locations[i][j]].std())
    #                print('values_list')
    #                print(values_list)
                    values_array.append(values_list)
                    values_list = []
    #            print('values_array')
    #            print(values_array)
                
                dataline = recording+' inverse log of mean absolute values for ' +subject+' | '+ title + ' | ' + interval_string + ' | ' + '\n'
                header = 'rows: lb, lf, rf, rb\ndelta d-std theta t-std alpha a-std beta  b-std gamma g-std\n'
                values = '' # string of values for averages and standard deviations
                for i in range(len(locations)-1): #loop over 4 locations
                    for x in values_array[i]:
                        values = values + str('%.3f' % x) + ' '
                    values = values + '\n'
    #            print('values')
    #            print(values)
            else: # grph is NOT meanstd
                if grph == 'mean': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                    for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                        for i in range(len(freqbands)):
                            values_list.append(30*(self.absolute_df[freqbands[i]][t_range][locations[i][j]].mean()+1.667))
#                            values_list.append(50*(self.absolute_df[freqbands[i]][t_range][locations[i][j]].mean()+1))
                        values_array.append(values_list)
                        values_list = []
                elif grph == 'median': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                    for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                        for i in range(len(freqbands)):
                            values_list.append(30*(self.absolute_df[freqbands[i]][t_range][locations[i][j]].median()+1.667))
#                            values_list.append(50*(self.absolute_df[freqbands[i]][t_range][locations[i][j]].median()+1))
                        values_array.append(values_list)
                        values_list = []
                elif grph == 'std': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                    for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                        for i in range(len(freqbands)):
                            values_list.append(self.absolute_df[freqbands[i]][t_range][locations[i][j]].std()+1) # CORRECT THIS!
                        values_array.append(values_list)
                        values_list = []
                dataline = recording+' '+grph + ' normalized absolute values for ' +subject+' | '+ title + ' | ' + interval_string + ' | ' + '\n'
                header = 'rows: lb, lf, rf, rb\ndelta theta alpha beta  gamma\n'
                values = '' # string of values for averages and standard deviations
#                print('values_array')
#                print(values_array)
                for i in range(len(locations)-1):
                    for x in values_array[i]:
                        values = values + str('%.1f' % x) + ' '
                    values = values + '\n'
        elif self.rel_abs_var.get()=='relative': # Display relative values in table
            popup.wm_title("Average Relative EEG values")
            t_range = np.logical_and(ti < self.relative_df.index, self.relative_df.index < tf) # t_range is the same for all relative bands
            if grph == 'meanstd': # columns are delta, d-std, theta, t-std, alpha, a-std, beta, b-std, gamma, gstd 
                                   # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(self.relative_df[freqbands[i]][t_range][locations[i][j]].mean())
                        values_list.append(self.relative_df[freqbands[i]][t_range][locations[i][j]].std())
    #                print('values_list')
    #                print(values_list)
                    values_array.append(values_list)
                    values_list = []
    #            print('values_array')
    #            print(values_array)
                
                dataline = recording+' mean relative values for ' +subject+' | '+ title + ' | ' + interval_string + ' | ' + '\n'
                header = 'rows: lb, lf, rf, rb\ndelta d-std theta t-std alpha a-std beta  b-std gamma g-std\n'
                values = '' # string of values for averages and standard deviations
                for i in range(len(locations)-1): #loop over 4 locations
                    for x in values_array[i]:
                        values = values + str('%.3f' % x) + ' '
                    values = values + '\n'
    #            print('values')
    #            print(values)
            else: # grph is NOT meanstd
                if grph == 'mean': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                    for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                        for i in range(len(freqbands)):
                            values_list.append(self.relative_df[freqbands[i]][t_range][locations[i][j]].mean())
                        values_array.append(values_list)
                        values_list = []
                elif grph == 'median': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                    for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                        for i in range(len(freqbands)):
                            values_list.append(self.relative_df[freqbands[i]][t_range][locations[i][j]].median())
                        values_array.append(values_list)
                        values_list = []
                elif grph == 'std': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                    for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                        for i in range(len(freqbands)):
                            values_list.append(self.relative_df[freqbands[i]][t_range][locations[i][j]].std())
                        values_array.append(values_list)
                        values_list = []
                dataline = recording+' '+grph + ' relative values for ' +subject+' | '+ title + ' | ' + interval_string + ' | ' + '\n'
                header = 'rows: lb, lf, rf, rb\ndelta theta alpha beta  gamma\n'
                values = '' # string of values for averages and standard deviations
#                print('values_array')
#                print(values_array)
                for i in range(len(locations)-1):
                    for x in values_array[i]:
                        values = values + str('%.3f' % x) + ' '
                    values = values + '\n'
        txt1 = Text(popup, width=70, height=9, wrap=tk.WORD)
        txt1.insert(END, dataline+header+values)
        txt1.grid(row=1, column=1, sticky=W)
        
    def band(self, key):
        print('key=',key)
        if key in d_bands:
            return 'delta'
        elif key in t_bands:
            return 'theta'
        elif key in a_bands:
            return 'alpha'
        elif key in b_bands:
            return 'beta'
        elif key in g_bands:
            return 'gamma'
        else:
            return None

    def med_mean_legend(self, avg_list, d):
        """
        Add requested median or mean legend to time-series graph.
        avg_list is list of either median or mean values. 
        """
        i = len(avg_list)
        self.ax.annotate(avg_list, xy=(1.01, 0.15),  xycoords='axes fraction',
                    xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                    color=plotcolor[d], backgroundcolor='white',
                    horizontalalignment='left', verticalalignment='top')

    def draw_graph(self):
        """
        In a new pop-up window, draw a set of axes with labels and title,
        and plot data for variables requested in grph command.
        
        Median values are plotted for relative values; mean values for absolute.
        
        Use single letter commands to plot graphs of median values
        (d=delta, t=theta, a=alpha, b=beta, g=gamma).
        
        Variables include j=jaw clench, k=blink, c=concentration, m=mellow.
        
        When respiration and breathing data are available, plots cmay
        include, p=breath, v=heart
        
        """
        
        global current_index
        #print('current_index = '+str(current_index))
    
        popup = tk.Tk()
        popup.geometry('700x460') # Set dimensions of popup window to 800x500 pixels
        popup.wm_title("Physiology graph")
        p = plt.figure()
        self.ax = plt.subplot(111)
        # In preparation for plotting, get the current radiobutton selection and the 
        # corresponding initial and final times of the interval        
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        #print('int_value = '+str(int_value))
        
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())
        
        fourthirds = 4/3.0  #To undo the 0.75 factor of c and m values (set8)
                            #introduced in EEG-open-21.py when converting CSV to h5
            
        graph_title = ''
        i=0

        item_list = list(self.data_type_var.items())
        for pair in item_list:
            if pair[1].get(): # if the corresponding checkbox is checked
                q = pair[0] # assign q to d, t, a, b, g, p, v, c, m, j, k
                if q in {'d', 't', 'a', 'b', 'g'}:
                    r = self.data_source_var.get() # assign r to value of selected radio button ('lb','lf','rf','rb')
                    d = str(q+r) # concatenate two strings q and r
                    band = self.band(d)
                    #print('d=',d)
                    #print('band=',band)
                
                    if self.rel_abs_var.get()=='absolute': # Absolute values
                        t_range = np.logical_and(ti < self.absolute_df.index, self.absolute_df.index < tf) # t_range is the same for all relative bands
                        graph_title = 'EEG of Absolute Power'
                        plt.xlabel('time (s)')
                        plt.ylabel('absolute power')
                        plt.ylim(0,100)
                        # The factor 30 and shift 1.667 are chosen empirically so that range of absolute power values are withing range 0 - 100
                        self.ax.plot(self.absolute_df[band].index[t_range], 30*(self.absolute_df[band][t_range][d]+1.667), color=plotcolor[d], label=plotlabel[d])
                        if self.med_mean_var.get()=='median':
                            median_val = 30*(self.absolute_df[band][t_range][d]+1.667).median()
                            std_val = 30*(self.absolute_df[band][t_range][d]+1.667).std()
                            plt.axhline(median_val, 0, 1, linewidth=2, color=plotcolor[d])
                            the_median = 'median '+str('%.2f' % median_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                            self.ax.annotate(the_median, xy=(1.01, 0.15),  xycoords='axes fraction',
                                        xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                        color=plotcolor[d], backgroundcolor='white',
                                        horizontalalignment='left', verticalalignment='top')
                        elif self.med_mean_var.get()=='mean':
                            mean_val = 30*(self.absolute_df[band][t_range][d]+1.667).mean()
                            std_val = 30*(self.absolute_df[band][t_range][d]+1.667).std()
                            plt.axhline(mean_val, 0, 1, linewidth=2, color=plotcolor[d])
                            the_mean = 'mean '+str('%.2f' % mean_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                            #print(the_median)
                            #median_list.append(the_median)
                            self.ax.annotate(the_mean, xy=(1.01, 0.15),  xycoords='axes fraction',
                                        xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                        color=plotcolor[d], backgroundcolor='white',
                                        horizontalalignment='left', verticalalignment='top')
                        i+=1
                    elif self.rel_abs_var.get()=='relative': # Relative values
                        t_range = np.logical_and(ti < self.relative_df.index, self.relative_df.index < tf) # t_range is the same for all relative bands
                        graph_title = 'EEG Relative Power'
                        plt.xlabel('time (s)')
                        plt.ylabel('relative power')
                        plt.ylim(0,1.0) # relative power in any one band never seems to exceed 80%
                        print('d='+str(d))
                        self.ax.plot(self.relative_df[band].index[t_range], self.relative_df[band][t_range][d], color=plotcolor[d], label=plotlabel[d])
                        if self.med_mean_var.get()=='median':
                            median_val = self.relative_df[band][t_range][d].median()
                            std_val = self.relative_df[band][t_range][d].std()
                            plt.axhline(median_val, 0, 1, linewidth=2, color=plotcolor[d])
                            the_median = 'median '+str('%.2f' % median_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                            self.ax.annotate(the_median, xy=(1.01, 0.15),  xycoords='axes fraction',
                                        xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                        color=plotcolor[d], backgroundcolor='white',
                                        horizontalalignment='left', verticalalignment='top')
                        elif self.med_mean_var.get()=='mean':
                            mean_val = self.relative_df[band][t_range][d].mean()
                            std_val = self.relative_df[band][t_range][d].std()
                            plt.axhline(mean_val, 0, 1, linewidth=2, color=plotcolor[d])
                            the_mean = 'mean '+str('%.2f' % mean_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                            #print(the_median)
                            #median_list.append(the_median)
                            self.ax.annotate(the_mean, xy=(1.01, 0.15),  xycoords='axes fraction',
                                        xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                        color=plotcolor[d], backgroundcolor='white',
                                        horizontalalignment='left', verticalalignment='top')
                        i+=1
                        #print('median_list'+str(median_list))
#                        if self.med_mean_var.get()=='mean':
#                            self.med_mean_legend(mean_list, d)
#                        if self.med_mean_var.get()=='median':
#                            self.med_mean_legend(median_list, d)
                elif q in {'j', 'k'}:
                    d = str(q)
                    #print('d=',d)
                    t_range = np.logical_and(ti < self.user_df.index, self.user_df.index < tf) 
                    self.ax.plot(self.user_df[d].index[t_range], self.user_df[d][t_range], color=plotcolor[d], label=plotlabel[d])
                elif q in {'c', 'm'}:
                    d = str(q)
                    #print('d=',d)
                    graph_title = "Muse Values for 'concentration' and 'mellow'"
                    plt.xlabel('time (s)')
                    plt.ylabel('fraction')
    #                    plt.ylim(0,1) # range of concentration and mellow are 0 - 1
                    t_range = np.logical_and(ti < self.user_df.index, self.user_df.index < tf) 
                    self.ax.plot(self.user_df[d].index[t_range], self.user_df[d][t_range]*fourthirds, color=plotcolor[d], label=plotlabel[d])
                    mean_val = self.user_df[d][t_range][d].mean()*fourthirds
                    plt.axhline(mean_val, 0, 1, linewidth=2, color=plotcolor[d])
                    the_mean = 'mean '+str('%.1f' % mean_val)
                    mean_list.append(the_mean)
                    #print(the_mean)
                    self.ax.annotate(mean_list[i], xy=(1.01, 0.15),  xycoords='axes fraction',
                                xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                color=plotcolor[d], backgroundcolor='white',
                                horizontalalignment='left', verticalalignment='top')
                    i+=1
                elif q in {'v'}:
                    d = str(q)
                    #print('d=',d)
                    t_range = np.logical_and(ti < self.cardio_df.index, self.cardio_df.index < tf) 
                    self.ax.plot(self.cardio_df[cardioresp[d]].index[t_range], self.cardio_df[cardioresp[d]][t_range], color=plotcolor[d], label=plotlabel[d])
                    graph_title = 'Electrocardiogram'
                    plt.xlabel('time (s)')
                    plt.ylabel('voltage (arbitrary units)')
                elif q in {'p'}:
                    d = str(q)
                    #print('d=',d)
                    t_range = np.logical_and(ti < self.resp_df.index, self.resp_df.index < tf)
                    self.ax.plot(self.resp_df[cardioresp[d]].index[t_range], self.resp_df[cardioresp[d]][t_range], color=plotcolor[d], label=plotlabel[d])
                    graph_title = 'Respiration'
                    plt.xlabel('time (s)')
                    plt.ylabel('pressure (arbitrary units)')
                
        # Adjust the width of the window so that legend is visible        
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width*0.75, box.height*0.9])
        self.ax.legend(loc='upper left', bbox_to_anchor=(1,0.25)) # Place to the right of the graph, near bottom
        # Get strings from the sessions_df dataframe to use in the graph title        
        recording = self.sessions_df.ix[current_index]['recording']
        title = self.sessions_df.ix[current_index]['title']
        subject = self.sessions_df.ix[current_index]['subject']
#        duration = self.sessions_df.ix[current_index]['duration']
#        date_time = self.sessions_df.ix[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')
        plt.show()

#        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
#        text=recording+' recorded '+str(date_time)+' at ('+str('%.0f' % duration)+' s'+')')
#        lbl0.pack(side=tk.BOTTOM, fill=X)
        
        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)
        
        toolbar = NavigationToolbar2TkAgg(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)
        
        popup.mainloop()
        return None
    
    def save_session_data(self):
        """
        Updates the Excel file EEG_CardioRespSessions.xls in C:/MedRec/
        including session name, t_initial and t_final.
        
        Presently, CANNOT UPDATE description text on Session tab.
        """
        self.sessions_df.to_excel(self.path+self.sessions_file, \
        sheet_name='Sheet1', engine='xlsxwriter', merge_cells=False)
            
    def update_value(self, sv, i, j):
        """
        Updates sessions_df dataframe values whenever entries in Entry boxes are changed.
        Values of i range from 0 - 4, where i=0 corresponds to default values interval0, ti0, tf0, and
        values of i from 1 - 4 correspond to user-defined rows interval1, ti1, tf1, etc.
        Values of j range from 0 - 2, where j=0 ~ interval, j=1 ~ ti, j=2 ~ tf
        """
        if j==0:
            self.sessions_df.set_value(current_index, 'interval'+str(i), self.sva[i][0].get())
            #print('new name = '+str(self.sessions_df.get_value(current_index, 'interval'+str(i))))
        elif j==1:
            self.sessions_df.set_value(current_index, 'ti'+str(i), self.sva[i][1].get())
            #print('new ti = '+str(self.sessions_df.get_value(current_index, 'ti'+str(i))))
        elif j==2:
            self.sessions_df.set_value(current_index, 'tf'+str(i), self.sva[i][2].get())
            #print('new tf = '+str(self.sessions_df.get_value(current_index, 'tf'+str(i))))
        self.interval.set(0)
        
            
    def select_graph(self):
        """
        Selects plotting routine based on graph type radiobutton selection
        """
        graph_type = self.graph_type_var.get()
        if graph_type == 'timeseries':
            self.draw_graph()
        elif graph_type == 'spectrogram':
            self.draw_spectrogram()
        elif graph_type == 'psd':
            self.draw_psd()
        elif graph_type == 'raweeg':
            self.draw_raw_eeg()
        elif graph_type == 'radar':
            self.draw_radar_chart()
        elif graph_type == 'table':
            self.draw_table()
            
         
if __name__ == '__main__':
    PV().mainloop()