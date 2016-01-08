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
from tkinter import BOTH, TOP, X, Y, N, W, LEFT, END
from tkinter import ttk, Frame, Text, IntVar, StringVar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
#from matplotlib.figure import Figure

LARGE_FONT = ("Verdana", 12)
NORM_FONT =  ("Verdana", 10)
SMALL_FONT = ("Verdana", 18)

graphs = ['d_m', 'dlb', 'dlf', 'drf', 'drb',
        't_m', 'tlb', 'tlf', 'trf', 'trb',
        'a_m', 'alb', 'alf', 'arf', 'arb',
        'b_m', 'blb', 'blf', 'brf', 'brb',
        'g_m', 'glb', 'glf', 'grf', 'grb',
        'x', 'k', 'j', 'c', 'm', 'v', 'p',
        'lb', 'lf', 'rf', 'rb',
        's1', 's2', 's3', 's4',
        'mean', 'median', 'std', 'meanstd', 'radar'
        ]
        
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

set1 = {'d', 't', 'a', 'b', 'g'}
set2 = {'s1', 's2', 's3', 's4'}
set3 = {'x', 'k', 'j'}
set4 = {'dlb', 'dlf','drf','drb',
        'tlb', 'tlf','trf','trb',
        'alb', 'alf','arf','arb',
        'blb', 'blf','brf','brb',
        'glb', 'glf','grf','grb'}
set5 = {'v','p'}
set6 = {'lb', 'lf', 'rf', 'rb'} # commands for raw eeg (time domain)
set7 = {'mean', 'median', 'std', 'meanstd'}
set8 = {'c', 'm'} # commands for concentration and mellow
set9 = {'radar'}
set10 = {'psd1', 'psd2', 'psd3', 'psd4'} # commands for power spectral density (frequency domain)

spect = {'s1':'lb', 's2':'lf', 's3':'rf', 's4':'rb'} # spectrograms
psd = {'psd1':'lb', 'psd2':'lf', 'psd3':'rf', 'psd4':'rb'} # power spectral density graphs
cardioresp = {'v':'mv', 'p':'kPa'}

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
    
    lb ~ raw EEG for left back sensor
    lf ~ raw EEG for left front sensor
    rf ~ raw EEG for right front sensor
    rb ~ raw EEG for right back sensor
    
    lbt ~ Fourier transformed lb signal
    lft ~ Fourier transformed lf signal
    rft ~ Fourier transformed rf signal
    rbt ~ Fourier transformed rb signal
    
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
        self.duration_var = StringVar()
        self.notes_var = StringVar()
        self.eeg_check_value = IntVar()
        self.heart_check_value = IntVar()
        self.breath_check_value = IntVar()
        self.sample_rate_var = IntVar()
        self.absolute_check_value = IntVar()
    
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
        self.absolute_check_value.set(0)
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
        self._create_session_tab(nb)
        self._create_request_tab(nb)
                                
    def update_session_data(self, event):
        """ 
        This routine updates the contents of the dataframe sessions_df
        whenever a new session is selected in the drop-down combobox cbx1
        on the _create_session_tab.
        """
        global current_index
        current_index =  self.cbx1.current()
        print('current_index = '+str(current_index))
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
        self.update_graph_data(current_index)
        
    def update_notes(self, notes):
        self.sessions_df.set(current_index, 'notes', notes)
        print(notes)
        
    def update_check(self, whichcheck):
        if whichcheck == 'eeg':
            self.sessions_df.set_value(current_index, 'eeg', self.eeg_check_value.get())
        elif whichcheck == 'heart':
            self.sessions_df.set_value(current_index, 'hrt', self.heart_check_value.get())
        elif whichcheck == 'breath':
            self.sessions_df.set_value(current_index, 'bth', self.breath_check_value.get())
        
    def _create_session_tab(self, nb):
        """
        Creates the Session tab in the Physiology Viewer.
        """
        # frame to hold contentx
        self.frame = ttk.Frame(nb, height='4i', width='6i', name='session')
        # widgets to be displayed on 'Session' tab
            
        self.cbx1 = ttk.Combobox(self.frame, width=50, textvariable=self.title_var, state='readonly')
#        self.cbx1 = ttk.Combobox(self.frame, width=50, textvariable=self.person_title_var, state='readonly')
        sessions_list = self.sessions_df['recording'] + ' - ' + self.sessions_df['person'] + ' - ' + self.sessions_df['title']
        self.cbx1['values'] = [row for row in sessions_list]
        self.cbx1.current(29) # Sets current value to first session involving brain waves
        self.cbx1.bind("<<ComboboxSelected>>", self.update_session_data)
        
        lbl1 = ttk.Label(self.frame, width=6, textvariable=self.index_var)
        lbl2 = ttk.Label(self.frame, width=6, textvariable=self.recording_var)
        etr1 = ttk.Entry(self.frame, width=8, textvariable=self.subject_var)
        etr2 = ttk.Entry(self.frame, width=24, textvariable=self.date_time_var)
        etr3 = ttk.Entry(self.frame, width=8, textvariable=self.duration_var)
        self.txt1 = Text(self.frame, width=50, height=10, wrap=tk.WORD)
        notes = self.sessions_df['notes'][self.index_var.get()]
        self.txt1.insert(END, notes)
        self.notes_var.trace("w", lambda name, index, mode, notes_var=self.notes_var: self.update_notes(notes))
#        print(txt1.get(1))
        chk1 = ttk.Checkbutton(self.frame, text='EEG', variable=self.eeg_check_value, command=lambda: self.update_check('eeg')) 
        chk2 = ttk.Checkbutton(self.frame, text='Heart', variable=self.heart_check_value, command=lambda: self.update_check('heart')) 
        chk3 = ttk.Checkbutton(self.frame, text='Breath', variable=self.breath_check_value, command=lambda: self.update_check('breath'))
        lbl3 = ttk.Label(self.frame, width=6, textvariable=self.sample_rate_var)
        btn1 = ttk.Button(self.frame, text='Save', command=self.save_session_data)
        
        self.cbx1.grid(row=1, column=2, columnspan=3, sticky=W)
#        etr1.grid(row=1, column=2, columnspan=2)
        lbl1.grid(row=1, column=1, sticky=W)
        lbl2.grid(row=2, column=1, sticky=W)
        etr1.grid(row=2, column=2, sticky=W)
        etr2.grid(row=2, column=3, sticky=W)
        etr3.grid(row=2, column=4, sticky=W)
        self.txt1.grid(row=3, column=1, rowspan=4, columnspan=4, sticky=W)
        chk1.grid(row=3, column=5, sticky=W)
        chk2.grid(row=4, column=5, sticky=W)
        chk3.grid(row=5, column=5, sticky=W)
        lbl3.grid(row=6, column=5, sticky=W)
        btn1.grid(row=7, column=5, sticky=W)
        
        # position and set resize behaviour
#        lbl.grid(row=0, column=0, columnspan=2, sticky='new', pady=5)
#        btn.grid(row=1, column=0, pady=(2,4))
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure((0,1), weight=1, uniform=1)
         
        # add to notebook (underline = index for short-cut character)
        nb.add(self.frame, text='Session', underline=0, padding=2)
        
    def update_graph_data(self, index):
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

    def band(self, key):
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
        print('interval_string='+interval_string)
        popup = tk.Tk()
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())
        print('ti='+str('%.3f' % ti))
        print('tf='+str('%.3f' % tf))
        if self.absolute_check_value.get(): # Absolute values
            popup.wm_title("Radar Chart of Mean Absolute EEG values")
#            graph_title = 'EEG Inverse Log of Mean Absolute Band Power'
            graph_title = 'EEG of Mean Absolute Band Power'
            t_range = np.logical_and(ti < self.absolute_df.index, self.absolute_df.index < tf) # t_range is the same for all relative bands
            print('t_range for absolute')
            print(t_range)
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
        else: # Relative values
            popup.wm_title("Radar Chart of Median Relative EEG values")
            graph_title = 'EEG Median Relative Band Power'
            t_range = np.logical_and(ti < self.relative_df.index, self.relative_df.index < tf) # t_range is the same for all relative bands
            print('t_range for relative')
            print(t_range)
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
        print('data=')
        print(data)
        spoke_labels = ['rb', 'rf', 'lf', 'lb']
        
    
        p = plt.figure(figsize=(6, 6))
        p.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    
        colors = ['blue', 'cyan', 'green', 'orange', 'magenta']
        
        self.ax = plt.subplot(111, projection='radar')

        # Adjust the height of the window so that title and legend are fully visible        
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width*0.95, box.height*0.95])

        if self.absolute_check_value.get(): # Absolute values
            plt.rgrids([20, 40, 60, 80])
            plt.ylim(0, 100)
        else: # Relative values
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
            
    def draw_table(self, grph):
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
        if self.absolute_check_value.get():  # Display absolute values normalized to range [0:100] in table
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
        else:  # Display relative values in table
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
        
    def draw_graph(self, grph, data):
        """
        In a new pop-up window, draws a set of axes with labels and title,
        and plots data for variables requested in grph command.
        
        Median values are plotted for relative values; mean values for absolute.
        
        Single letters (d=delta, t=theta, a=alpha, b=beta, g=gamma) plot
        average median values of four sensors (lb, lf, rf, fb).
        
        Variables include j=jaw clench, k=blink, c=concentration, m=mellow.
        
        When respiration and breathing data are available, plots can
        include, p=breath, v=heart
        
        3-letter codes plot values for individual sensors, e.g., 
        alf=(alpha, left, front), drb=(delta, right, back).
        
        Multiple variable can be displayed on the same set of axes using '&',
        for example, 'a&b', 'dlb&j', 'p&v'
        
        Minimum and maximum ordinate values are chosen automatically by
        plot command in matplotlib.
        
        Raw EEG signal for four sensors are plotted using lb, lf, rf, rb.
        
        Fourier transfomations of raw EEG signals are displayed in magnitude vs.
        frequency plots.
        
        Spectrograms for sensors lb, lf, rf, rb are plotted using commands
        s1, s2, s3, s4 respectively.
        
        """
        global current_index
        #print('current_index = '+str(current_index))
    
        popup = tk.Tk()
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
            
        median_list = []
        mean_list = []
        graph_title = ''
        i = 0

        for d in data:
            #print('d='+str(d))
            if self.eeg_check_value.get() > 0: # If data exists for eeg
                if d in set1: # Mean value among 4 sensors
                    d = d+'_m' # 'd' is used to request graph of delta band, but 'd_m' is the key for the dictionaries
                if d in d_bands|t_bands|a_bands|b_bands|g_bands:
                    band = self.band(d) # calls function band() which returns 'delta', 'theta', etc.
                    if self.absolute_check_value.get(): # Absolute values
                        t_range = np.logical_and(ti < self.absolute_df.index, self.absolute_df.index < tf) # t_range is the same for all relative bands
                        graph_title = 'EEG of Absolute Power'
                        plt.xlabel('time (s)')
                        plt.ylabel('absolute power')
                        plt.ylim(0,100)
                        # The factor 30 and shift 1.667 are chosen empirically so that range of absolute power values are withing range 0 - 100
                        self.ax.plot(self.absolute_df[band].index[t_range], 30*(self.absolute_df[band][t_range][d]+1.667), color=plotcolor[d], label=plotlabel[d])
                        mean_val = 30*(self.absolute_df[band][t_range][d]+1.667).mean()
                        std_val = 30*(self.absolute_df[band][t_range][d]+1.667).std() # CHECK THIS!
#                        self.ax.plot(self.absolute_df[band].index[t_range], 50*(self.absolute_df[band][t_range][d]+1), color=plotcolor[d], label=plotlabel[d])
#                        mean_val = 50*(self.absolute_df[band][t_range][d]+1).mean()
#                        std_val = 50*(self.absolute_df[band][t_range][d]+1).std()
                        plt.axhline(mean_val, 0, 1, linewidth=2, color=plotcolor[d])
                        the_mean = 'mean '+str('%.1f' % mean_val)+u"\u00B1"+str('%.1f' % std_val) # median with +/- symbol for standard deviation
                        #print(the_median)
                        mean_list.append(the_mean)
                        #print('mean_list'+str(mean_list))
                        self.ax.annotate(mean_list[i], xy=(1.01, 0.15),  xycoords='axes fraction',
                                    xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                    color=plotcolor[d], backgroundcolor='white',
                                    horizontalalignment='left', verticalalignment='top')
                        i+=1
                    else: # Relative values
                        t_range = np.logical_and(ti < self.relative_df.index, self.relative_df.index < tf) # t_range is the same for all relative bands
                        graph_title = 'EEG Relative Power'
                        plt.xlabel('time (s)')
                        plt.ylabel('relative power')
                        plt.ylim(0,1.0) # relative power in any one band never seems to exceed 80%
                        print('d='+str(d))
                        self.ax.plot(self.relative_df[band].index[t_range], self.relative_df[band][t_range][d], color=plotcolor[d], label=plotlabel[d])
                        # plt.hold(True)
                        median_val = self.relative_df[band][t_range][d].median()
                        std_val = self.relative_df[band][t_range][d].std()
                        plt.axhline(median_val, 0, 1, linewidth=2, color=plotcolor[d])
                        the_median = 'median '+str('%.2f' % median_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                        #print(the_median)
                        median_list.append(the_median)
                        #print('median_list'+str(median_list))
                        self.ax.annotate(median_list[i], xy=(1.01, 0.15),  xycoords='axes fraction',
                                    xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                    color=plotcolor[d], backgroundcolor='white',
                                    horizontalalignment='left', verticalalignment='top')
                        i+=1
                elif d in set2: # spectrogram plots of frequency vs. time
                    graph_title = 'Spectrogram of Frequency vs. Time for '+str(spect[d])
                    plt.xlabel('time (s)')
                    plt.ylabel('frequency (Hz)')
#                    Pxx, freqs, bins, im = self.ax.specgram(self.raw_df[spect[d]],NFFT=256,Fs=220) # E.g., request 's1' --> key 'lb'
                    i = int(ti*self.fs)
                    f = int(tf*self.fs)
                    i_range = np.logical_and(i < self.raw_df.index, self.raw_df.index < f)
                    signal = self.raw_df[spect[d]][i_range]
                    Pxx, freqs, bins, im = self.ax.specgram(signal, NFFT=256,Fs=220, xextent=(ti,tf))
                    plt.ylim(0,55) # cutoff frequency less than 60 Hz which is due to AC power contamination
                    plt.xlim(ti, tf)
                elif d in set3: # x ~ sway; k ~ blink; j ~ jaw clench
                    t_range = np.logical_and(ti < self.user_df.index, self.user_df.index < tf) 
                    self.ax.plot(self.user_df[d].index[t_range], self.user_df[d][t_range], color=plotcolor[d], label=plotlabel[d])
                elif d in set6: # raw EEG for lb, lf, rf, rb
                    graph_title = 'Raw EEG Signal'
                    plt.xlabel('samples (220 per second)')
                    plt.ylabel('voltage (microvolts)')
                    t_range = np.logical_and(ti < self.raw_df.index, self.raw_df.index < tf) 
                    self.ax.plot(self.raw_df[d].index, self.raw_df[d], color=plotcolor[d], label=plotlabel[d])
                elif d in set8: # c ~ concentration; m~ mellow
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
                elif d in set10: # power spectral density for lb, lf, rf, rb
                    graph_title = 'Power Spectral Density at '+str(psd[d])
                    plt.xlabel('frequency (Hz)')
                    i = int(ti*self.fs)
                    f = int(tf*self.fs)
                    i_range = np.logical_and(i < self.raw_df.index, self.raw_df.index < f)
                    signal = self.raw_df[psd[d]][i_range]
                    Pxx, freqs = plt.psd(signal, NFFT=2048, noverlap=1024, Fs=220)
                    self.ax.set_yscale('log')
                    self.ax.set_xscale('linear')
                    plt.xlim(1,25)
                    plt.ylim(1,60)
            if self.heart_check_value.get() > 0: # If data exists for heart
                if d == 'v':
                    t_range = np.logical_and(ti < self.cardio_df.index, self.cardio_df.index < tf) 
                    self.ax.plot(self.cardio_df[cardioresp[d]].index[t_range], self.cardio_df[cardioresp[d]][t_range], color=plotcolor[d], label=plotlabel[d])
                    graph_title = 'Electrocardiogram'
                    plt.xlabel('time (s)')
                    plt.ylabel('voltage (arbitrary units)')
            if self.breath_check_value.get() > 0: # If data exists for breath
                if d == 'p':
                    t_range = np.logical_and(ti < self.resp_df.index, self.resp_df.index < tf)
                    self.ax.plot(self.resp_df[cardioresp[d]].index[t_range], self.resp_df[cardioresp[d]][t_range], color=plotcolor[d], label=plotlabel[d])
                    graph_title = 'Respiration'
                    plt.xlabel('time (s)')
                    plt.ylabel('pressure (arbitrary units)')
            if not ((self.eeg_check_value.get() > 0) or (self.heart_check_value.get() > 0) or (self.breath_check_value.get() > 0)):
                print('No data found for '+str(d))

        # Adjust the height of the window so that legend is visible        
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width*0.75, box.height*0.9])
        self.ax.legend(loc='upper left', bbox_to_anchor=(1,0.25)) # Place to the right of the graph, near bottom
        # Get strings from the sessions_df dataframe to use in the graph title        
        recording = self.sessions_df.ix[current_index]['recording']
        title = self.sessions_df.ix[current_index]['title']
        subject = self.sessions_df.ix[current_index]['subject']
        duration = self.sessions_df.ix[current_index]['duration']
        date_time = self.sessions_df.ix[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')
        plt.show()

        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
        text=recording+' recorded '+str(date_time)+' at ('+str('%.0f' % duration)+' s'+')')
        lbl0.pack(side=tk.BOTTOM, fill=X)
        
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
        
            
    def _create_request_tab(self, nb):
        """
        Creates the Graphs Request tab in the Physiology Viewer.
        """
        self.frame = ttk.Frame(nb, name='request')
         
        # widgets to be displayed on 'Request' tab
        msg = ["Mean values: d=delta, t=theta, a=alpha, b=beta, g=gamma,\n\
j=jaw_clench, k=blink, c=concentration, m=mellow\n\
Specify graphs for individual sensors: alf=(alpha, left, front)\n\
Specify multi-line graphs with '&': brf&drb&j\n\
Tables of values: median, mean; Polar chart: radar\n\
Raw EEG for four sensors: lb, lf, rf, rb; Spectrograms: s1, s2, s3, s4"]
         
        lbl = ttk.Label(self.frame, wraplength='6i', justify=LEFT, anchor=N,
                        text=''.join(msg))
        lbl11 = ttk.Label(self.frame, text='t_initial', width=10)
        lbl12 = ttk.Label(self.frame, text='t_final', width=10)
        # position and set resize behaviour
        lbl.grid(row=0, column=0, columnspan=4, sticky='W', pady=5)
        lbl11.grid(row=1, column=2, sticky='SW')
        lbl12.grid(row=1, column=3, sticky='SW')

        self.tv = StringVar()  # Should this be self.tv = StringVar() ?
#        self.tv.set('median')  
#        self.tv.set('radar')  
        self.tv.set('a&b')  
#        self.tv.set('alb&brf')  
#        self.tv.set('meanstd')  
#        interval = IntVar()
        self.interval.set(0)
        self.int_value = 0

        # Add radiobuttons for intervals and text entry boxes for initial and final times        
        etr = ttk.Entry(self.frame, width = 20, textvariable=self.tv)
        etr.grid(row=1, column=0, columnspan=3, sticky=W)
        etr.bind("<Return>", lambda x : self.get_graphs(self.tv.get()))
        
        cbx = ttk.Checkbutton(self.frame, text="absolute", variable=self.absolute_check_value, \
                            onvalue=1, offvalue=0)
        cbx.grid(row=1, column=1, sticky=W)
        
        #print('button selected = '+str(self.interval.get()))
        
        for i in range(9):
            self.sva[i][0].trace("w", lambda name, index, mode, var=self.sva[i][0], i=i:
                              self.update_value(var, i, 0))
            self.sva[i][1].trace("w", lambda name, index, mode, var=self.sva[i][1], i=i:
                              self.update_value(var, i, 1))
            self.sva[i][2].trace("w", lambda name, index, mode, var=self.sva[i][2], i=i:
                              self.update_value(var, i, 2))
            self.RadioObject.append(ttk.Radiobutton(self.frame, textvariable=self.sva[i][0], variable=self.interval, value=i).grid(row=i+2, column=0, sticky=W))     # radiobutton
            self.interval.set(0)
            self.EntryObject.append(ttk.Entry(self.frame, width=20, textvariable=self.sva[i][0]).grid(row=i+2, column=1, sticky=W)) # interval entry
            self.EntryObject.append(ttk.Entry(self.frame, width=8, textvariable=self.sva[i][1]).grid(row=i+2, column=2, sticky=W)) #ti entry
            self.EntryObject.append(ttk.Entry(self.frame, width=8, textvariable=self.sva[i][2]).grid(row=i+2, column=3, sticky=W)) # tf entry

        btn2 = ttk.Button(self.frame, text='Save', command=self.save_session_data)
        btn2.grid(row=11, column=2, columnspan=2)
        self.interval.set(0)
        #print('in _create_request_tab; interval.get() = '+str(self.interval.get()))
        self.int_value = 0

        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure((0,1), weight=1, uniform=1)
        nb.add(self.frame, text='Graphs Request', underline=0, padding=2)
        #self.RadioObject[0].invoke()     
         
    def remove_dups(self, alist):
        aset = set(alist)
        return list(aset)
        
    def clean_command(self, command):
        # David, you really need to understand this
        command = "".join(command.split()) # Remove all white space
        return command  

        
    def parse(self, grph):
        """
        If grph contains '&' then prepare list of multi-data before
        returning list of pairs [band, col];
        otherwise simply return simple single-line data
        """
    #    print('In parse(grph) with grph= '+str(grph))
        
        data_list = []
        if '&' in grph:
            multi_data_list = []
            tokens = grph.split('&')
            #print('tokens='+str(tokens))
            for tok in tokens:
                #print('multi_data_list = '+str(multi_data_list))
                new_item = self.prepare_data_items(tok)
                #print('new_item = '+str(new_item))
                assert len(new_item) == 1
                multi_data_list.append(new_item[0]) # Assume len(new_item) == 1
            #print('multi_data_list: ',str(multi_data_list))
            return multi_data_list
        else:
            data_list = self.prepare_data_items(grph)
            #print('data_list: '+str(data_list))
            return data_list
    
    def prepare_data_items(self, tok):
        data_items = []
        if tok in set1:
            data_items.append(tok) # Mean values are in column 5
        elif tok in set2:
            data_items.append(tok) 
            #print(tok+': spectrogram')            
        elif tok in set3:
            data_items.append(tok)
            #print(tok+": found in set3 {'k', 'j', 'c', 'm'}")
        elif tok in set4:
            data_items.append(tok)
            #print(tok+' found in set4')
        elif tok in set5:
            data_items.append(tok) 
            #print(tok+': cardioresp')            
        elif tok in set6:
            data_items.append(tok)
            #print(tok+' found in set6')
        elif tok in set7:
            data_items.append(tok)
            #print(tok+' found in set7')
        elif tok in set8:
            data_items.append(tok)
            #print(tok+' found in set8')
        elif tok in set9:
            data_items.append(tok)
            #print(tok+' found in set9')
        elif tok in set10:
            data_items.append(tok)
            #print(tok+' found in set10')
        else:
            print('unknown token')
        #print('data_items: '+str(data_items))
        return data_items

    def prepare_graphs(self, graph_list):
        """
        Examines items in graph_list:
        Prepare list of data items to be plotted.
        """
        #print('graph_list: '+str(graph_list))
        for grph in graph_list:
            #print('grph='+grph)
            data_list = self.parse(grph)
            if grph in set7:
                self.draw_table(grph)
            elif grph in set9:
                self.draw_radar_chart()
            else:
                self.draw_graph(grph, data_list)
        return None
    
    def get_graphs(self, command):
        graph_list = []
#        print('command:'+str(command))
        #print('type(command) = '+str(type(command)))
        graph_tokens = command.split(sep=',')
        while '' in graph_tokens:
            graph_tokens.remove('')
            #print('graph_tokens:'+str(graph_tokens))
        for tok in graph_tokens:
            #print(tok)
            graph_list.append(tok)
        graph_list = self.remove_dups(graph_list)
        #print('graph_list: '+str(graph_list), flush=True)
        self.prepare_graphs(graph_list)
        return graph_list
    
         
if __name__ == '__main__':
    PV().mainloop()