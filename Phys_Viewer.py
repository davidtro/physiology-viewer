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
from tkinter import BOTH, TOP, LEFT, CENTER, X, Y, N, S, E, W, END
from tkinter import ttk, Canvas, Frame, Toplevel, Text, IntVar, StringVar, DoubleVar
from tkinter.filedialog import askopenfilename, askdirectory
#import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.mlab as m
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#from matplotlib.figure import Figure

from configparser import ConfigParser
import os

LARGE_FONT = ("Verdana", 12)
NORM_FONT =  ("Verdana", 10)
SMALL_FONT = ("Verdana", 18)

graphs = {'d': 'delta',
          't': 'theta',
          'a': 'alpha',
          'b': 'beta',
          'g': 'gamma',
          'c': 'concentration',
          'p': 'breath',
          'v': 'heart',
          's': 'button press',
          'j': 'jaw clench',
          'k': 'blink',
          'm': 'mellow',
          }

plotlabel = {'d_m':'delta', 'dlb':'delta lb', 'dlf':'delta lf', 'drf':'delta rf', 'drb':'delta rb',
        't_m':'theta', 'tlb':'theta lb', 'tlf':'theta lf', 'trf':'theta rf', 'trb':'theta rb',
        'a_m':'alpha', 'alb':'alpha lb', 'alf':'alpha lf', 'arf':'alpha rf', 'arb':'alpha rb',
        'b_m':'beta', 'blb':'beta lb', 'blf':'beta lf', 'brf':'beta rf', 'brb':'beta rb',
        'g_m':'gamma', 'glb':'gamma lb', 'glf':'gamma lf', 'grf':'gamma rf', 'grb':'gamma rb',
        's':'button press', 'k':'blink', 'j':'jaw clench', 'c':'concentration', 'm':'mellow', 'v':'heart', 'p':'breath',
        'lb':'raw lb', 'lf':'raw lf', 'rf':'raw rf', 'rb':'raw rb',
        }

plotcolor = {'d_m':'blue', 'dlb':'dodgerblue', 'dlf':'royalblue', 'drf':'cornflowerblue', 'drb':'deepskyblue',
        't_m':'cyan', 'tlb':'turquoise', 'tlf':'aquamarine', 'trf':'paleturquoise', 'trb':'powderblue',
        'a_m':'green', 'alb':'limegreen', 'alf':'mediumseagreen', 'arf':'springgreen', 'arb':'lightgreen',
        'b_m':'darkred', 'blb':'brown', 'blf':'sienna', 'brf':'darkgoldenrod', 'brb':'darkorange',
        'g_m':'magenta', 'glb':'mediumpurple', 'glf':'orchid', 'grf':'mediumorchid', 'grb':'plum',
        's':'black', 'k':'purple', 'j':'crimson', 'c':'goldenrod', 'm':'cadetblue', 'v':'red', 'p':'skyblue',
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

cardioresp = {'v':'mv', 'p':'kPa', 's':'ma'}

title_str = ''

fs = 220.0

class WinPsd(Toplevel):
    def __init__(self, master, cnf={}, **kw):
        Toplevel.__init__(self, master, **kw)
        self._create_plot()

    def _create_plot(self):
        # The following is used for psd semi-log graphs only
        XMIN = 3 # minimum frequency (used in log-log plot only)
        XMAX = 55 # maximum frequency
        if self.master.fixed_var[3].get() == 1:
            YMIN = self.master.spin_var[3][0].get() # minimum PSD y-value
            YMAX = self.master.spin_var[3][1].get() # maximum PSD y-value
        else:
            YMIN = 0.1 # minimum PSD y-value
            YMAX = 100 # maximum PSD y-value
        lblY = 0.7*YMAX
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        ax = self.ax
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height*0.95])

        ax.set_yscale('log')
        ax.set_xscale('linear')

        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Power Spectral Density (dB/Hz)')
        if self.master.loglog_check_value.get():
            ax.set_xscale('log')
            ax.set_xlim(XMIN, XMAX)
        else:
            ax.set_xlim(0, XMAX)
        ax.set_ylim(YMIN, YMAX)


        band_patches = [
            patches.Rectangle((0, YMIN), 4, YMAX, facecolor="blue", alpha=0.2),
            patches.Rectangle((4, YMIN), 4, YMAX, facecolor="cyan", alpha=0.2),
            patches.Rectangle((8, YMIN), 4, YMAX, facecolor="green", alpha=0.2),
            patches.Rectangle((12, YMIN), 18, YMAX, facecolor="orange", alpha=0.2),
            patches.Rectangle((30, YMIN), XMAX-30, YMAX, facecolor="magenta", alpha=0.2)]
        # delta: 0 - 4 Hz
        # theta: 4 - 8 Hz
        # alpha: 8 -12 Hz
        # beta: 12 - 30 Hz
        # gamma: 30 - XMAX Hz

        for ptch in band_patches:
            ax.add_patch(ptch)
        ax.annotate('delta', xy=(2,lblY), fontsize=10, color=None, horizontalalignment='center')
        ax.annotate('theta', xy=(6,lblY), fontsize=10, color=None, horizontalalignment='center')
        ax.annotate('alpha', xy=(10,lblY), fontsize=10, color=None, horizontalalignment='center')
        ax.annotate('beta', xy=(21,lblY), fontsize=10, color=None, horizontalalignment='center')
        ax.annotate('gamma', xy=(42,lblY), fontsize=10, color=None, horizontalalignment='center')

        xdata,ydata = [],[]
        self.line, = ax.plot(xdata, ydata)

        canvas = FigureCanvasTkAgg(self.fig, master=self)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(fill='both', expand=1)
        canvas.draw()

    def draw(self, xdata, ydata, title_str):
        self.ax.set_title(title_str)
        self.line.set_xdata(xdata)
        self.line.set_ydata(ydata)
        self.fig.canvas.draw()



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
    s ~ button press in ma

    means ~ numerical mean values and standard deviations for each of four sensors
    medians ~ numerical median values and standard deviations for each of four sensors

"""


current_index = 29 #Index for rec1

def update_graph_data():
    """
    Using the values of the checkboxes 'eeg', 'hrt', 'bth' and 'btn',
    reads data for session index from the corresponding .h5 file and
    populates the dataframes absolute_df, relative_df, user_df and raw_df,
    cardio_df, resp_df and button_df.
    """
    #global relative_df, user_df, raw_df, cardio_df, resp_df
    global recording
    global absolute_df, relative_df, user_df, raw_df, cardio_df, resp_df, button_df
    if 0 < current_index < 29:
        recording = 'lqt'+str(current_index)
    elif 29 <= current_index:
        recording = 'rec'+str(current_index-27)
    else:
        print('index out of range')
    # Reset dataframes to None to clear out residual data from previous selections
    absolute_df = None
    relative_df = None
    user_df = None
    raw_df = None
    cardio_df = None
    resp_df = None
    button_df = None
    # Read data from h5 files
    if str(sessions_df['eeg'][current_index]) == '1':
        absolute_df = pd.read_hdf(data_path+recording+'_eeg_abs.h5', 'abs_data')
        relative_df = pd.read_hdf(data_path+recording+'_eeg_rel.h5', 'rel_data')
        user_df = pd.read_hdf(data_path+recording+'_eeg_user.h5', 'user_data')
        raw_df = pd.read_hdf(data_path+recording+'_eeg_raw.h5', 'raw_data')
    if str(sessions_df['hrt'][current_index]) == '1':
        cardio_df = pd.read_hdf(data_path+recording+'_cardio.h5', 'cardio_data')
    if str(sessions_df['bth'][current_index]) == '1':
        resp_df = pd.read_hdf(data_path+recording+'_breath.h5', 'resp_data')
    if str(sessions_df['btn'][current_index]) == '1':
        button_df = pd.read_hdf(data_path+recording+'_button.h5', 'btn_data')

class PV(tk.Tk):

    Labels = ['Interval', 'ti', 'tf']
    LabelObject = []
    EntryObject = []

    def __init__(self, name='Physiology Viewer', **kw):
        tk.Tk.__init__(self, **kw)
        self.title(name)
#        self.customFont = tk.Font(family="Helvetica", size=14)
        self.index_var = IntVar()
        self.recording_var = StringVar()
        self.title_var = StringVar() # Used in cbx1 combo box
        self.session_title_var = StringVar() # Used in label lbl0
        self.person_var = StringVar()
        self.subject_var = StringVar()
        self.date_time_var = StringVar()
        self.graph_type_var = StringVar() # used by redio buttons for Time series, Radar, Table, etc.
        self.data_dir_var = StringVar() # directory in which .h5 files are stored (generally C:\MedRec)
        self.sessions_data_path_var = StringVar() # path to EEG_CardioRespSessions.xls

        self.data_source_var = StringVar() #used by redio buttons for lb, lf, rf, rb, left, right, etc.
        self.data_type_var = {'d': IntVar(), 't': IntVar(), 'a': IntVar(), 'b': IntVar(), 'g': IntVar(), \
            'p': IntVar(), 'v': IntVar(), 'c': IntVar(), 'm': IntVar(), 'j': IntVar(), 'k': IntVar(), 's': IntVar()}
        self.abs_offset_var = DoubleVar()
        self.abs_scale_var = DoubleVar()
        self.c_scale_var = DoubleVar()
        self.m_scale_var = DoubleVar()
        self.v_offset_var = DoubleVar()
        self.v_scale_var = DoubleVar()
        self.p_offset_var = DoubleVar()
        self.p_scale_var = DoubleVar()
        self.s_offset_var = DoubleVar()
        self.s_scale_var = DoubleVar()
        self.k_offset_var = DoubleVar()
        self.k_scale_var = DoubleVar()
        self.j_offset_var = DoubleVar()
        self.j_scale_var = DoubleVar()

        self.duration_var = StringVar()
        self.notes_var = StringVar()
        self.eeg_check_value = IntVar()
        self.heart_check_value = IntVar()
        self.breath_check_value = IntVar()
        self.button_check_value = IntVar()
        self.eeg_label = StringVar()
        self.heart_label = StringVar()
        self.breath_label = StringVar()
        self.button_label = StringVar()
        self.labquest_sample_rate_var = IntVar()
        self.muse_sample_rate_var = IntVar()
        self.rel_abs_var = StringVar()
        self.med_mean_var = StringVar()
        self.type_average_var = StringVar() # type of average (mean, median, standard deviation, inverse log) in tables
        self.overlay_check_value = IntVar()
        self.loglog_check_value = IntVar()

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

        self.inipath = '.\\pv.ini'
        self.config = ConfigParser()
        self.config.read(self.inipath)
        if not os.path.exists(self.inipath):
            self.config.add_section('data_directory')
            self.config.add_section('ts_relative')
            self.config.add_section('ts_absolute')
            self.config.add_section('spectrogram')
            self.config.add_section('psd')
            self.config.add_section('raw_eeg')
            self.config.add_section('rc_relative')
            self.config.add_section('rc_absolute')
            self.config.add_section('heart')
            self.config.add_section('breath')
            self.config.add_section('button_press')
            self.config.add_section('eye_blink')
            self.config.add_section('jaw_clench')


        self.abs_offset_var.set(1.667)
        self.abs_scale_var.set(30.0)
        self.c_scale_var.set(1.333)
        self.m_scale_var.set(1.333)
        """
        self.v_offset_var.set(0.0)
        self.v_scale_var.set(0.5)
        self.p_offset_var.set(103.0) # 103 is close to the minimum pressure
        self.p_scale_var.set(0.15)   # range of pressure values is about 6.0
        self.s_offset_var.set(0.5)
        self.s_scale_var.set(0.3)
        self.k_offset_var.set(0.5)
        self.k_scale_var.set(0.3)
        self.j_offset_var.set(0.4)
        self.j_scale_var.set(0.3)
        """
        self.overlay_check_value.set(0)
        self.loglog_check_value.set(0)

        self.rel_abs_var.set('relative')
        self.med_mean_var.set('median')
#        self.pack(expand=Y, fill=BOTH) # NECESSARY??
#        self.master.title('Physiology Viewer') # NECESSARY??

#        self.data_dir_var.set("C:\\MedRec\\")
#        self.sessions_data_path_var.set("C:\\MedRec\\EEG_CardioRespSessions.xls")
        self.fixed_var = [IntVar(), IntVar(), IntVar(), \
                IntVar(), IntVar(), IntVar(), IntVar()]
        #for i in range(6): # Set all Fixed checkboxes to unchecked initially
        #    self.fixed_var[i].set(0)
        self.spin_var = [[DoubleVar(), DoubleVar()], \
                         [DoubleVar(), DoubleVar()], \
                         [DoubleVar(), DoubleVar()], \
                         [DoubleVar(), DoubleVar()], \
                         [DoubleVar(), DoubleVar()], \
                         [DoubleVar(), DoubleVar()], \
                         [DoubleVar(), DoubleVar()]]

        self.read_settings() # read settings from pv.ini file

        try:
            self.load_session_data()
        except:
            print('Failed to load data')
        self._create_viewer_panel()

    def get_data_path(self):
        self.data_dir_var.set(askdirectory(\
            initialdir="C:\\MedRec\\", \
            title = "Choose directory where .h5 data files are located."))
        self.load_session_data()
        # Reload session data from indicated directory

    def get_sessions_path(self):
        self.sessions_data_path_var.set(askopenfilename(\
            initialdir="C:\\MedRec\\", \
            filetypes =(("Excel File", "*.xls"),("All Files","*.*")), \
            title = "Choose spreadsheet file containing sessions data."))

    #def load_session_data(self, dpath='C:\\MedRec\\', dfile='C:\\MedRec\\EEG_CardioRespSessions.xls'):
    def load_session_data(self):
        """
        The default directory for .h5 recording data files is C:\MedRec
        The default file name for session data is C:\MedRec\EEG_CardioRespSessions.xls
        """
        global sessions_df, data_path
        #self.path = self.data_dir_var.get()
        #self.sessions_file = self.sessions_data_path_var.get()
        #self.path = 'C:/MedRec/'
        #self.sessions_file = 'EEG_CardioRespSessions.xls'
        #self.path = dpath
        #self.sessions_file = dfile
        data_path = self.data_dir_var.get()
        self.sessions_file = self.sessions_data_path_var.get()
        #print('path='+self.path)
        #print('sessions_file='+self.sessions_file)
#        self.sessions_data = pd.ExcelFile(self.path+self.sessions_file)
        self.sessions_data = pd.ExcelFile(self.sessions_file)
        sessions_df = self.sessions_data.parse('Sheet1', index_col='index', na_values=['None'])
#        self.sessions_file.close()

    class Spinbox(ttk.Widget):
        def __init__(self, master, **kw):
            ttk.Widget.__init__(self, master, 'ttk::spinbox', kw)

    def toggle_spin_widget(self, row, widlist=[]):
        if self.fixed_var[row].get():
            for wid in widlist:
                wid.configure(state='normal')
        else:
            for wid in widlist:
                wid.configure(state='disabled')

    def read_settings(self):
        self.inipath = '.\\pv.ini'
        self.config = ConfigParser()
        self.config.read(self.inipath)
        #print(self.config.get('ts_relative', 'fixed'))

        self.data_dir_var.set(self.config.get('directory', 'data_dir'))
        self.sessions_data_path_var.set(self.config.get('directory', 'sessions_file'))

        self.fixed_var[0].set(self.config.get('ts_relative', 'fixed')) #chk2_11
        self.spin_var[0][0].set(0.0) #lbl12
        self.spin_var[0][1].set(self.config.get('ts_relative', 'y_max')) #spb2_13

        self.fixed_var[1].set(self.config.get('ts_absolute', 'fixed')) #chk2_21
        self.spin_var[1][0].set(self.config.get('ts_absolute', 'y_min')) #spb2_22
        self.spin_var[1][1].set(self.config.get('ts_absolute', 'y_max')) #spb2_23

        self.fixed_var[2].set(self.config.get('spectrogram', 'fixed')) #chk2_31
        self.spin_var[2][0].set(0.0) #spb2_32
        self.spin_var[2][1].set(self.config.get('spectrogram', 'y_max')) #spb2_33

        self.fixed_var[3].set(self.config.get('psd', 'fixed')) #chk2_41
        self.spin_var[3][0].set(self.config.get('psd', 'y_min')) #spb2_42
        self.spin_var[3][1].set(self.config.get('psd', 'y_max')) #spb2_43

        self.fixed_var[4].set(self.config.get('raw_eeg', 'fixed')) #chk2_51
        self.spin_var[4][0].set(self.config.get('raw_eeg', 'y_min')) #spb2_52
        self.spin_var[4][1].set(self.config.get('raw_eeg', 'y_max')) #spb2_53

        self.fixed_var[5].set(self.config.get('rc_relative', 'fixed')) #chk2_71
        self.spin_var[5][0].set(0.0) #lbl72
        self.spin_var[5][1].set(self.config.get('rc_relative', 'y_max')) #spb2_73

        self.fixed_var[6].set(self.config.get('rc_absolute', 'fixed')) #chk2_81
        self.spin_var[6][0].set(0.0) #lbl82
        self.spin_var[6][1].set(self.config.get('rc_absolute', 'y_max')) #spb2_83

        self.v_offset_var.set(self.config.get('heart', 'offset'))
        self.v_scale_var.set(self.config.get('heart', 'scale'))

        self.p_offset_var.set(self.config.get('breath', 'offset'))
        self.p_scale_var.set(self.config.get('breath', 'scale'))

        self.s_offset_var.set(self.config.get('button_press', 'offset'))
        self.s_scale_var.set(self.config.get('button_press', 'scale'))

        self.k_offset_var.set(self.config.get('eye_blink', 'offset'))
        self.k_scale_var.set(self.config.get('eye_blink', 'scale'))

        self.j_offset_var.set(self.config.get('jaw_clench', 'offset'))
        self.j_scale_var.set(self.config.get('jaw_clench', 'scale'))


    def save_settings(self):
        #print(str(self.spin_var[1][1].value.get()))
        self.config.set('directory', 'data_dir', str(self.data_dir_var.get()))
        self.config.set('directory', 'sessions_file', str(self.sessions_data_path_var.get()))

        self.config.set('ts_relative', 'fixed', str(self.fixed_var[0].get()))
        self.config.set('ts_relative', 'y_min', '0')
        self.config.set('ts_relative', 'y_max', str(self.spb2_13.get()))

        self.config.set('ts_absolute', 'fixed', str(self.fixed_var[1].get()))
        self.config.set('ts_absolute', 'y_min', str(self.spb2_22.get()))
        self.config.set('ts_absolute', 'y_max', str(self.spb2_23.get()))

        self.config.set('spectrogram', 'fixed', str(self.fixed_var[2].get()))
        self.config.set('spectrogram', 'y_min', '0')
        self.config.set('spectrogram', 'y_max', str(self.spb2_33.get()))

        self.config.set('psd', 'fixed', str(self.fixed_var[3].get()))
        self.config.set('psd', 'y_min', str(self.spb2_42.get()))
        self.config.set('psd', 'y_max', str(self.spb2_43.get()))

        self.config.set('raw_eeg', 'fixed', str(self.fixed_var[4].get()))
        self.config.set('raw_eeg', 'y_min', str(self.spb2_52.get()))
        self.config.set('raw_eeg', 'y_max', str(self.spb2_53.get()))

        self.config.set('rc_relative', 'fixed', str(self.fixed_var[5].get()))
        self.config.set('rc_relative', 'y_min', '0')
        self.config.set('rc_relative', 'y_max', str(self.spb2_73.get()))

        self.config.set('rc_absolute', 'fixed', str(self.fixed_var[6].get()))
        self.config.set('rc_absolute', 'y_min', '0')
        self.config.set('rc_absolute', 'y_max', str(self.spb2_83.get()))

        self.config.set('heart', 'offset', str(self.v_offset_var.get()))
        self.config.set('heart', 'scale', str(self.v_scale_var.get()))

        self.config.set('breath', 'offset', str(self.p_offset_var.get()))
        self.config.set('breath', 'scale', str(self.p_scale_var.get()))

        self.config.set('button_press', 'offset', str(self.s_offset_var.get()))
        self.config.set('button_press', 'scale', str(self.s_scale_var.get()))

        self.config.set('eye_blink', 'offset', str(self.k_offset_var.get()))
        self.config.set('eye_blink', 'scale', str(self.k_scale_var.get()))

        self.config.set('jaw_clench', 'offset', str(self.j_offset_var.get()))
        self.config.set('jaw_clench', 'scale', str(self.j_scale_var.get()))

        with open(self.inipath, 'w') as f:
           self.config.write(f)

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

        self.update_widgets_select()
        self.update_labels()

    def update_session_data(self, event):
        """
        This routine updates the contents of the dataframe sessions_df
        whenever a new session is selected in the drop-down combobox cbx1
        on the _create_UI_tab.
        """
        global current_index, sessions_df
        current_index =  self.cbx1.current()
        #print('current_index = '+str(current_index))
        self.index_var.set(current_index)
        self.recording_var.set(sessions_df.iloc[current_index]['recording'])
        self.session_title_var.set(sessions_df.iloc[current_index]['title'])
        self.person_var.set(sessions_df.iloc[current_index]['person'])
        self.subject_var.set(sessions_df.iloc[current_index]['subject'])
        self.date_time_var.set(sessions_df.iloc[current_index]['date_time'])
        self.duration_var.set(sessions_df.iloc[current_index]['duration'])
        notes = sessions_df['notes'][self.index_var.get()]
        self.txt1.delete(1.0, END) # Delete from line 1, character 0 to end of text
        self.txt1.insert(END, notes)
        self.eeg_check_value.set(sessions_df.iloc[current_index]['eeg'])
        self.heart_check_value.set(sessions_df.iloc[current_index]['hrt'])
        self.breath_check_value.set(sessions_df.iloc[current_index]['bth'])
        self.button_check_value.set(sessions_df.iloc[current_index]['btn'])
        self.labquest_sample_rate_var.set(sessions_df.iloc[current_index]['Hz'])
        self.muse_sample_rate_var.set(220)
        #print('\ncurrent_index=', current_index)
        #print('eeg_check_value=', self.eeg_check_value.get())
        #print('heart_check_value=', self.heart_check_value.get())
        #print('breath_check_value=', self.breath_check_value.get())
        #print('button_check_value=', self.button_check_value.get())
        #interval1 = str(self.interval1_var.get())
        #print('interval1 = '+str(interval1))
        self.sva[0][0].set('entire session') # Initial line is
        # initialized with ti=0, tf=duration
        self.sva[0][1].set('0')
        self.sva[0][2].set(self.duration_var.get())
        for i in range(1,9): # fill in user-defined intervals in rows 1-8
            #print('i = '+str(i))
            #print('current_index = '+str(current_index))
            self.sva[i][0].set(sessions_df.iloc[current_index]['interval'+str(i)])
            self.sva[i][1].set(sessions_df.iloc[current_index]['ti'+str(i)])
            self.sva[i][2].set(sessions_df.iloc[current_index]['tf'+str(i)])


        #print(self.notes_var.get())
        #print('self in update_session_data=', self)
        update_graph_data() #routine is OUTSIDE of PV class, so does not require self.
        self.update_labels() #Make sure that labels for EEG, Heart, Breath and Button are up to date
        self.update_widgets_select() # Make sure that widgets (e.g. widSrc, widBands) are up to date


    def update_notes(self, notes):
        sessions_df.set(current_index, 'notes', notes)
        #print(notes)

    def update_widgets_select(self):
        """
        Enables or disables widgets according to values in spreadsheet columns eeg, hrt, bth, btn
        when selection is made in drop-down list of sessions
        """
        #print('\nin update_widgets_select')
        #print('self.eeg_check_value=', self.eeg_check_value.get())
        self.graph_type_var.set('timeseries') # default radio button selection is for rdo1 (Time Series)
        for x in self.data_type_var:
            self.data_type_var[x].set(0) #initialize data_type_var to unchecked
        self.data_type_var['a'].set(1) #initialize data_type_var so that 'a' is selected

        self.disable_widget(self.widProprietary) # Postpone implementation of proprietary data 'c' and 'm'
        if self.eeg_check_value.get(): # EEG data exists
            self.enable_widget(self.widEEG)
            self.enable_widget(self.widEEGonly)
            self.enable_widget(self.widDisplay)
        else: # EEG data does not exist
            self.disable_widget(self.widEEG)
            self.disable_widget(self.widEEGonly)
        if self.heart_check_value.get(): # heart data exists
            self.enable_widget(self.widHeart)
            self.enable_widget(self.widDisplay)
        else: # heart data does not exist
            self.disable_widget(self.widHeart)
        if self.breath_check_value.get(): # breath data exists
            self.enable_widget(self.widBreath)
            self.enable_widget(self.widDisplay)
        else: # breath data does not exist
            self.disable_widget(self.widBreath)
            self.disable_widget(self.widOverlay)
            self.overlay_check_value.set(0) # be sure the Overlay checkbox in unchecked if there is no breath data
        if self.button_check_value.get(): # button data exists
            self.enable_widget(self.widButton)
            self.enable_widget(self.widDisplay)
        else: # button data does not exist
            self.disable_widget(self.widButton)

    def update_widgets_click(self):
        """
        Enables or disables widgets based on which chart type is clicked:
        timeseries, spectrogram, psd, raw, radar or table
        """
        graph = self.graph_type_var.get()
        #print('\nin update_widgets_click')
        #print('graph=', graph)
        if graph == 'timeseries':
            self.enable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean|self.widSrc|self.widDisplay)
            self.disable_widget(self.widOverlay|self.widLogLog|self.widTabletype)
            if self.breath_check_value.get(): # breath data exists
                self.enable_widget(self.widBreath)
            else: # breath data does not exist
                self.disable_widget(self.widBreath)
            if self.heart_check_value.get(): # heart data exists
                self.enable_widget(self.widHeart)
                self.enable_widget(self.widDisplay)
            else: # heart data does not exist
                self.disable_widget(self.widHeart)
            if self.button_check_value.get(): # button data exists
                self.enable_widget(self.widButton)
                self.enable_widget(self.widDisplay)
            else: # button data does not exist
                self.disable_widget(self.widButton)
        elif graph == 'spectrogram':
            if self.breath_check_value.get(): # breath data exists
                self.enable_widget(self.widOverlay|self.widSrc|self.widDisplay)
                self.disable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean|self.widpvs|self.widLogLog|self.widTabletype)
            else: # Prevent use of Overlay checkbox when no breath data exists
                self.disable_widget(self.widOverlay)
        elif graph == 'psd':
            self.enable_widget(self.widLogLog|self.widSrc|self.widDisplay)
            self.disable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean|self.widpvs|self.widOverlay|self.widTabletype)
        elif graph == 'raweeg':
            self.enable_widget(self.widRelAbs|self.widMedMean|self.widSrc|self.widDisplay)
            self.disable_widget(self.widBands|self.widUser|self.widRelAbs|self.widMedMean|self.widLogLog|self.widOverlay|self.widTabletype)
        elif graph == 'radar':
            self.enable_widget(self.widRelAbs|self.widDisplay)
            # We don't bother with median values for radar chart
            self.disable_widget(self.widBands|self.widUser|self.widMedMean|self.widSrc|self.widpvs|self.widTabletype)
        elif graph == 'table':
            self.enable_widget(self.widRelAbs|self.widTabletype|self.widDisplay)
            self.disable_widget(self.widRelAbs|self.widBands|self.widSrc|self.widUser|self.widMedMean|self.widpvs|self.widLogLog|self.widOverlay)


    def update_labels(self):
        """
        Uses values in columns eeg, hrt, bth and btn of the EEG_CardioRespSessions.xls
        spreadsheet to set the labels to the right of the session description:
        EEG (220 Hz), Heart (220 Hz), Breath (220 Hz) and Button (220 Hz)
        """
        #print('\nentering update_labels')
        #print('eeg_check_value=', self.eeg_check_value.get())
        #print('heart_check_value=', self.heart_check_value.get())
        #print('breath_check_value=', self.breath_check_value.get())
        #print('button_check_value=', self.button_check_value.get())
        if self.eeg_check_value.get():
            self.eeg_label.set(' EEG ('+str(self.muse_sample_rate_var.get())+' Hz)')
        else:
            self.eeg_label.set('')
        if self.heart_check_value.get():
            self.heart_label.set(' Heart ('+str(self.labquest_sample_rate_var.get())+' Hz)')
        else:
            self.heart_label.set('')
        if self.breath_check_value.get():
            self.breath_label.set(' Breath ('+str(self.labquest_sample_rate_var.get())+' Hz)')
        else:
            self.breath_label.set('')
        if self.button_check_value.get():
            self.button_label.set(' Button ('+str(self.labquest_sample_rate_var.get())+' Hz)')
        else:
            self.button_label.set('')
        #print('eeg_label=', self.eeg_label.get())
        #print('heart_label=', self.heart_label.get())
        #print('breath_label=', self.breath_label.get())
        #print('button_label=', self.button_label.get())

    def _create_UI_tab(self, nb):
        """
        Creates the Main user interface (UI) tab in the Physiology Viewer.
        """
        self.widEEG = {}

        # frame to hold contentx
        self.frame = ttk.Frame(nb, height='10i', width='8i', name='main')
        # widgets to be displayed on 'Session' tab
        lbl0 = ttk.Label(self.frame, textvariable=self.session_title_var, width=40, font=("Helvetica", 16))
        lbl0.grid(row=0, column=0, columnspan=3, sticky=N)

        self.cbx1 = ttk.Combobox(self.frame, width=80, textvariable=self.title_var, state='readonly')
#        self.cbx1 = ttk.Combobox(self.frame, width=50, textvariable=self.person_title_var, state='readonly')
#        date_time = sessions_df.iloc[current_index]['date_time']
#        sessions_list = sessions_df['recording'] + ' - ' + str('{0:%Y-%m-%d}'.format(date_time)) + ' - ' + sessions_df['person'] + ' - ' + sessions_df['title']
#        sessions_list = sessions_df['recording'] + ' - ' + '{0:%Y-%m-%d}'.format(sessions_df['date_time']) + ' - ' + sessions_df['person'] + ' - ' + sessions_df['title']
#        date_time = sessions_df.iloc[current_index]['date_time']
#        sessions_list = sessions_df['recording'] + ' - ' + sessions_df['person'] + ' - ' + sessions_df['title']
#        print(sessions_list[100])
#        print('\n---\n')
#        print(sessions_df['date_time'])
#        print('{0:%Y-%m-%d}'.format(sessions_df.iloc[100]['date_time']))
#        print('# of lines = ', len(sessions_df))
        sessions_list = [str(sessions_df['recording'][i]) + ' - ' + \
                         str(sessions_df['date_time'][i]) + ' - ' + \
                         str(sessions_df['person'][i]) + ' - ' + \
                         str(sessions_df['title'][i])
                         for i in range(len(sessions_df))]
        self.cbx1['values'] = [row for row in sessions_list]
        self.cbx1.current(29) # Sets current value to first session involving brain waves
        self.cbx1.bind("<<ComboboxSelected>>", self.update_session_data)
        self.cbx1.grid(row=1, column=0, columnspan=3, sticky=W)

        self.txt1 = Text(self.frame, height=10, wrap=tk.WORD)
        notes = sessions_df['notes'][self.index_var.get()]
        self.txt1.insert(END, notes)
        self.txt1.grid(row=2, column=0, rowspan=4, columnspan=4, sticky=(N,S,E,W))
        self.notes_var.trace("w", lambda name, index, mode, notes_var=self.notes_var: self.update_notes(notes))
#        print(txt1.get(1))
        lbl1 = ttk.Label(self.frame, textvariable=self.eeg_label, width=15)
        lbl1.grid(row=2, column=4, sticky=(N,W))
        lbl2 = ttk.Label(self.frame, textvariable=self.heart_label, width=15)
        lbl2.grid(row=3, column=4, sticky=(N,W))
        lbl3 = ttk.Label(self.frame, textvariable=self.breath_label, width=15)
        lbl3.grid(row=4, column=4, sticky=(N,W))
        lbl7 = ttk.Label(self.frame, textvariable=self.button_label, width=15)
        lbl7.grid(row=5, column=4, sticky=(N,W))

        rdo1 = ttk.Radiobutton(self.frame, text='Time Series', variable=self.graph_type_var, value='timeseries', command=lambda: self.update_widgets_click())
        rdo2 = ttk.Radiobutton(self.frame, text='Spectrogram', variable=self.graph_type_var, value='spectrogram', command=lambda: self.update_widgets_click())
        rdo3 = ttk.Radiobutton(self.frame, text='PSD vs Frequency', variable=self.graph_type_var, value='psd', command=lambda: self.update_widgets_click())
        rdo4 = ttk.Radiobutton(self.frame, text='Raw EEG', variable=self.graph_type_var, value='raweeg', command=lambda: self.update_widgets_click())
        rdo5 = ttk.Radiobutton(self.frame, text='Radar Chart', variable=self.graph_type_var, value='radar', command=lambda: self.update_widgets_click())
        rdo6 = ttk.Radiobutton(self.frame, text='Table', variable=self.graph_type_var, value='table', command=lambda: self.update_widgets_click())

        chk13 = ttk.Checkbutton(self.frame, text='Overlay breath', variable=self.overlay_check_value)
        chk14 = ttk.Checkbutton(self.frame, text='Log-log plot', variable=self.loglog_check_value)

        rdo1.grid(row=6, column=0, sticky=W)
        rdo2.grid(row=8, column=0, sticky=W)
        rdo3.grid(row=9, column=0, sticky=W)
        rdo4.grid(row=10, column=0, sticky=W)
        rdo5.grid(row=11, column=0, sticky=W)
        rdo6.grid(row=12, column=0, sticky=W)

        frm1 = ttk.Frame(self.frame, borderwidth=2, width=20) # frame for containing checkboxes d,t,a,b,g,...
        frm1.grid(row=6, column=1, sticky=W)
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
        chk12 = ttk.Checkbutton(frm1, text='s', variable=self.data_type_var['s'])

        chk1.grid(row=0, column=0)
        chk2.grid(row=0, column=1)
        chk3.grid(row=0, column=2)
        chk4.grid(row=0, column=3)
        chk5.grid(row=0, column=4)
        chk8.grid(row=0, column=5)
        chk6.grid(row=1, column=0)
        chk7.grid(row=1, column=1)
        chk12.grid(row=1, column=2)
        chk10.grid(row=1, column=3)
        chk11.grid(row=1, column=4)
        chk9.grid(row=1, column=5)

        chk13.grid(row=8, column=1, sticky=W)
        chk14.grid(row=9, column=1, sticky=W)

        frm3 = ttk.Frame(self.frame, borderwidth=2, width=20) # frame for radio buttons relative,absolute,median,mean,...
        frm3.grid(row=6, column=2, sticky=W)

        rdo20 = ttk.Radiobutton(frm3, text='relative', variable=self.rel_abs_var, value='relative')
        rdo21 = ttk.Radiobutton(frm3, text='absolute', variable=self.rel_abs_var, value='absolute')

        rdo22 = ttk.Radiobutton(frm3, text='median', variable=self.med_mean_var, value='median')
        rdo23 = ttk.Radiobutton(frm3, text='mean', variable=self.med_mean_var, value='mean')

        rdo20.grid(row=0, column=0, sticky=E)
        rdo21.grid(row=0, column=1, sticky=E)
        rdo22.grid(row=1, column=0, sticky=E)
        rdo23.grid(row=1, column=1, sticky=E)

        cbx2 = ttk.Combobox(self.frame, width=18, textvariable=self.type_average_var, state='readonly')
        cbx2.grid(row=12, column=1, sticky=W)
        cbx2['values'] = ('mean', 'median', 'standard deviation', 'inverse log')
#        cbx2.bind('<<ComboboxSelected>>', self.set_table_type())

        frm4 = ttk.Frame(self.frame, borderwidth=2, width=20) # frame for radio buttons lf,rf,...
        frm4.grid(row=6, column=3, sticky=W)

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
        frm2.grid(row=13, column=0, columnspan=3, sticky=W)

        lbl4 = ttk.Label(frm2, text='Intervals', width=12)
        lbl5 = ttk.Label(frm2, text='t_initial', width=10)
        lbl6 = ttk.Label(frm2, text='t_final', width=10)

        lbl4.grid(row=0, column=1, sticky=W)
        lbl5.grid(row=0, column=2, sticky=E)
        lbl6.grid(row=0, column=3, sticky=E)

        btn0 = ttk.Button(self.frame, text='Display', command=self.select_graph)
        btn0.grid(row=9, column=3)

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

        txt1 = Text(self.frame, width=30, height=17, background='#F0F0F0', padx=5, pady=3)
        txt1.insert('1.0', "Muse frequency bands:\n")
        contents = "\
  d ~ delta (f <=4 Hz)\n\
  t ~ theta (4 < f <= 8 Hz)\n\
  a ~ alpha (8 < f <=12 Hz)\n\
  b ~ beta (12 < f <= 30 Hz)\n\
  g ~ gamma (30 < f Hz)\n\
LabQuest data:\n\
  p ~ breath\n\
  v ~ heart\n\
  s ~ button press\n\
Muse auxiliary:\n\
  j ~ jaw clench\n\
  k ~ eye blink\n\
Muse proprietary:\n\
  c ~ concentration\n\
  m ~ mellow\n\
"

        txt1.insert(END, contents)
        txt1['state'] = 'disabled'
        txt1['relief'] = 'flat'
        txt1.grid(row=11, column=2, rowspan=5, columnspan=2, sticky=N)

        btn1 = ttk.Button(frm2, text='Save', command=self.save_session_data)
        btn1.grid(row=14, column=2, columnspan=2)

#        self.frame.rowconfigure(1, weight=1)
#        self.frame.columnconfigure((0,1), weight=1, uniform=1)

        # add to notebook (underline = index for short-cut character)
        nb.add(self.frame, text='Main', underline=0, padding=2)

        self.widDisplay = {btn0}
        self.widEEGonly = {rdo2, rdo3, rdo4, rdo5, rdo6}
        self.widBands = {chk1, chk2, chk3, chk4, chk5}
        self.widUser = {chk10, chk11}
        self.widProprietary = {chk8, chk9}
        self.widBreath = {chk6}
        self.widHeart = {chk7}
        self.widButton = {chk12}
        self.widpvs = {chk6, chk7, chk12}
        self.widRelAbs = {rdo20, rdo21}
        self.widMedMean = {rdo22, rdo23}
        self.widOverlay = {chk13}
        self.widLogLog = {chk14}
        self.widTabletype = {cbx2}
        self.widAccessory = {chk13, chk14, cbx2}
        self.widSrc = {rdo11, rdo12, rdo13, rdo14}
        self.widEEG = self.widBands|self.widUser|self.widRelAbs|self.widMedMean|self.widSrc|self.widAccessory

        self.update_session_data(self) # Causes update even when no combobox selection has been made

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

        heading1 = ttk.Label(self.frame, text='Data Directory', font=("Helvetica", 14), padding=15)
        frm1 = ttk.Frame(self.frame, borderwidth=2)
        heading2 = ttk.Label(self.frame, text='Graph Limits', font=("Helvetica", 14), padding=15)
        frm2 = ttk.Frame(self.frame, borderwidth=2)
        heading3 = ttk.Label(self.frame, text='Incidental Scale and Offset', font=("Helvetica", 14), padding=15)
        frm3 = ttk.Frame(self.frame, borderwidth=2)

        heading1.grid(row=1, column=0)
        frm1.grid(row=2, column=0, sticky=W)
        heading2.grid(row=3, column=0)
        frm2.grid(row=4, column=0, sticky=W)
        heading3.grid(row=5, column=0)
        frm3.grid(row=6, column=0, sticky=W)

        lbl1_00 = ttk.Label(frm1, width=20, text='Data file directory')
        etr1_10 = ttk.Entry(frm1, width=90, textvariable=self.data_dir_var)
        btn1_11 = ttk.Button(frm1, text='Open', command=self.get_data_path)
        lbl1_02 = ttk.Label(frm1, width=20, text='Sessions data file')
        etr1_30 = ttk.Entry(frm1, width=90, textvariable=self.sessions_data_path_var)
        btn1_31 = ttk.Button(frm1, text='Open', command=self.get_sessions_path)

        lbl1_00.grid(row=0, column=0, sticky=W)
        etr1_10.grid(row=1, column=0, sticky=W)
        btn1_11.grid(row=1, column=1, sticky=W)
        lbl1_02.grid(row=2, column=0, sticky=W)
        etr1_30.grid(row=3, column=0, sticky=W)
        btn1_31.grid(row=3, column=1, sticky=W)

        self.lbl2_00 = ttk.Label(frm2, width=20, text='Time Series')
        self.lbl2_01 = ttk.Label(frm2, width=8, text='Fixed')
        self.lbl2_02 = ttk.Label(frm2, width=7, text='Min y', justify=LEFT)
        self.lbl2_03 = ttk.Label(frm2, width=10, text='Max y')
        self.lbl2_10 = ttk.Label(frm2, width=10, text='relative')
        self.lbl2_12 = ttk.Label(frm2, width=5, text='0', justify=CENTER)
        opts13 = { 'from': 0.1, 'to': 1.0, 'increment': 0.1, 'state': 'disabled'}
        self.spb2_13 = tk.Spinbox(frm2, textvariable=self.spin_var[0][1], **opts13)
        #print(self.spb2_13.get())
        self.chk2_11 = ttk.Checkbutton(frm2, variable=self.fixed_var[0], \
            onvalue=1, offvalue=0, \
            command=lambda: self.toggle_spin_widget(0, [self.spb2_13]))
        self.toggle_spin_widget(0, [self.spb2_13])

        self.lbl2_20 = ttk.Label(frm2, width=10, text='absolute')
        opts22 = { 'from': -2.0, 'to': 0.0, 'increment': 0.1, 'state': 'disabled'}
        self.spb2_22 = tk.Spinbox(frm2, textvariable=self.spin_var[1][0], **opts22)
        opts23 = { 'from': 0.0, 'to': 2.0, 'increment': 0.1, 'state': 'disabled'}
        self.spb2_23 = tk.Spinbox(frm2, textvariable=self.spin_var[1][1], **opts23)
        self.chk2_21 = ttk.Checkbutton(frm2, variable=self.fixed_var[1], \
            onvalue=1, offvalue=0, \
            command=lambda: self.toggle_spin_widget(1, [self.spb2_22, self.spb2_23]))
        self.toggle_spin_widget(1, [self.spb2_22, self.spb2_23])

        self.lbl2_30 = ttk.Label(frm2, width=20, text='Spectrogram')
        self.lbl2_32 = ttk.Label(frm2, width=5, text='0', justify=CENTER)
        opts33 = { 'from': 10, 'to': 100, 'increment': 5, 'state': 'disabled'}
        self.spb2_33 = tk.Spinbox(frm2, textvariable=self.spin_var[2][1], **opts33)
        self.chk2_31 = ttk.Checkbutton(frm2, variable=self.fixed_var[2], \
            onvalue=1, offvalue=0, \
            command=lambda: self.toggle_spin_widget(2, [self.spb2_33]))
        self.toggle_spin_widget(2, [self.spb2_33])

        self.lbl2_40 = ttk.Label(frm2, width=20, text='PSD vs. Frequency')
        opts42 = { 'from': 0, 'to': 0, 'increment': 0.1, 'state': 'disabled'}
        self.spb2_42 = tk.Spinbox(frm2, textvariable=self.spin_var[3][0], **opts42)
        opts43 = { 'from': 10, 'to': 100, 'increment': 5, 'state': 'disabled'}
        self.spb2_43 = tk.Spinbox(frm2, textvariable=self.spin_var[3][1], **opts43)
        self.chk2_41 = ttk.Checkbutton(frm2, variable=self.fixed_var[3], \
            onvalue=1, offvalue=0, \
            command=lambda: self.toggle_spin_widget(3, [self.spb2_42, self.spb2_43]))
        self.toggle_spin_widget(3, [self.spb2_42, self.spb2_43])

        self.lbl2_50 = ttk.Label(frm2, width=10, text='Raw EEG')
        opts52 = { 'from': 0, 'to': 800, 'increment': 100, 'state': 'disabled'}
        self.spb2_52 = tk.Spinbox(frm2, textvariable=self.spin_var[4][0], **opts52)
        opts53 = { 'from': 800, 'to': 1500, 'increment': 100, 'state': 'disabled'}
        self.spb2_53 = tk.Spinbox(frm2, textvariable=self.spin_var[4][1], **opts53)
        self.chk2_51 = ttk.Checkbutton(frm2, variable=self.fixed_var[4], \
            onvalue=1, offvalue=0, \
            command=lambda: self.toggle_spin_widget(4, [self.spb2_52, self.spb2_53]))
        self.toggle_spin_widget(4, [self.spb2_52, self.spb2_53])

        self.lbl2_60 = ttk.Label(frm2, width=20, text='Radar Chart')

        self.lbl2_70 = ttk.Label(frm2, width=10, text='relative')
        self.lbl2_72 = ttk.Label(frm2, width=5, text='0', justify=CENTER)
        opts73 = { 'from': 0, 'to': 1.0, 'increment': 0.1, 'state': 'disabled'}
        self.spb2_73 = tk.Spinbox(frm2, textvariable=self.spin_var[5][1], **opts73)
        self.chk2_71 = ttk.Checkbutton(frm2, variable=self.fixed_var[5], \
            onvalue=1, offvalue=0, \
            command=lambda: self.toggle_spin_widget(5, [self.spb2_73]))
        self.toggle_spin_widget(5, [self.spb2_73])

        self.lbl2_80 = ttk.Label(frm2, width=10, text='absolute')
        self.lbl2_82 = ttk.Label(frm2, width=5, text='0', justify=CENTER)
        opts83 = { 'from': 0, 'to': 100, 'increment': 10, 'state': 'disabled'}
        self.spb2_83 = tk.Spinbox(frm2, textvariable=self.spin_var[6][1], **opts83)
        self.chk2_81 = ttk.Checkbutton(frm2, variable=self.fixed_var[6], \
            onvalue=1, offvalue=0, \
            command=lambda: self.toggle_spin_widget(6, [self.spb2_83]))
        self.toggle_spin_widget(6, [self.spb2_83])

        self.btn83 = ttk.Button(self.frame, text='Save Settings', command=self.save_settings)

        self.lbl2_00.grid(row=0, column=0)
        self.lbl2_01.grid(row=0, column=1)
        self.lbl2_02.grid(row=0, column=2)
        self.lbl2_03.grid(row=0, column=3)

        self.lbl2_10.grid(row=1, column=0)
        self.chk2_11.grid(row=1, column=1)
        self.lbl2_12.grid(row=1, column=2)
        self.spb2_13.grid(row=1, column=3)

        self.lbl2_20.grid(row=2, column=0)
        self.chk2_21.grid(row=2, column=1)
        self.spb2_22.grid(row=2, column=2)
        self.spb2_23.grid(row=2, column=3)

        self.lbl2_30.grid(row=3, column=0, sticky=W)
        self.chk2_31.grid(row=3, column=1)
        self.lbl2_32.grid(row=3, column=2)
        self.spb2_33.grid(row=3, column=3)

        self.lbl2_40.grid(row=4, column=0, sticky=W)
        self.chk2_41.grid(row=4, column=1)
        self.spb2_42.grid(row=4, column=2)
        self.spb2_43.grid(row=4, column=3)

        self.lbl2_50.grid(row=5, column=0, sticky=W)
        self.chk2_51.grid(row=5, column=1)
        self.spb2_52.grid(row=5, column=2)
        self.spb2_53.grid(row=5, column=3)

        self.lbl2_60.grid(row=6, column=0, sticky=W)

        self.lbl2_70.grid(row=7, column=0)
        self.chk2_71.grid(row=7, column=1)
        self.lbl2_72.grid(row=7, column=2)
        self.spb2_73.grid(row=7, column=3)

        self.lbl2_80.grid(row=8, column=0)
        self.chk2_81.grid(row=8, column=1)
        self.lbl2_82.grid(row=8, column=2)
        self.spb2_83.grid(row=8, column=3)

        self.btn83.grid(row=9, column=0, sticky=E)

        lbl3_01 = ttk.Label(frm3, width=20, text='Heart')
        lbl3_03 = ttk.Label(frm3, width=20, text='Breath')
        lbl3_05 = ttk.Label(frm3, width=20, text='Button Press')
        lbl3_10 = ttk.Label(frm3, width=10, anchor=tk.E, text='v offset')
        etr3_11 = ttk.Entry(frm3, width=20, textvariable=self.v_offset_var)
        lbl3_12 = ttk.Label(frm3, width=10, anchor=tk.E, text='p offset')
        etr3_13 = ttk.Entry(frm3, width=20, textvariable=self.p_offset_var)
        lbl3_14 = ttk.Label(frm3, width=10, anchor=tk.E, text='s offset')
        etr3_15 = ttk.Entry(frm3, width=20, textvariable=self.s_offset_var)
        lbl3_20 = ttk.Label(frm3, width=10, anchor=tk.E, text='v scale')
        etr3_21 = ttk.Entry(frm3, width=20, textvariable=self.v_scale_var)
        lbl3_22 = ttk.Label(frm3, width=10, anchor=tk.E, text='p scale')
        etr3_23 = ttk.Entry(frm3, width=20, textvariable=self.p_scale_var)
        lbl3_24 = ttk.Label(frm3, width=10, anchor=tk.E, text='s scale')
        etr3_25 = ttk.Entry(frm3, width=20, textvariable=self.s_scale_var)

        lbl3_31 = ttk.Label(frm3, width=20, text='Eye Blink')
        lbl3_33 = ttk.Label(frm3, width=20, text='Jaw Clench')
        lbl3_40 = ttk.Label(frm3, width=10, anchor=tk.E, text='k offset')
        etr3_41 = ttk.Entry(frm3, width=20, textvariable=self.k_offset_var)
        lbl3_42 = ttk.Label(frm3, width=10, anchor=tk.E, text='j offset')
        etr3_43 = ttk.Entry(frm3, width=20, textvariable=self.j_offset_var)
        lbl3_50 = ttk.Label(frm3, width=10, anchor=tk.E, text='k scale')
        etr3_51 = ttk.Entry(frm3, width=20, textvariable=self.k_scale_var)
        lbl3_52 = ttk.Label(frm3, width=10, anchor=tk.E, text='j scale')
        etr3_53 = ttk.Entry(frm3, width=20, textvariable=self.j_scale_var)

        lbl3_01.grid(row=0, column=1)
        lbl3_03.grid(row=0, column=3)
        lbl3_05.grid(row=0, column=5)
        lbl3_10.grid(row=1, column=0, sticky=W)
        etr3_11.grid(row=1, column=1, sticky=W)
        lbl3_12.grid(row=1, column=2)
        etr3_13.grid(row=1, column=3)
        lbl3_14.grid(row=1, column=4, sticky=E)
        etr3_15.grid(row=1, column=5, sticky=E)
        lbl3_20.grid(row=2, column=0, sticky=W)
        etr3_21.grid(row=2, column=1, sticky=W)
        lbl3_22.grid(row=2, column=2)
        etr3_23.grid(row=2, column=3)
        lbl3_24.grid(row=2, column=4, sticky=E)
        etr3_25.grid(row=2, column=5, sticky=E)

        lbl3_31.grid(row=3, column=1)
        lbl3_33.grid(row=3, column=3)
        lbl3_40.grid(row=4, column=0, sticky=W)
        etr3_41.grid(row=4, column=1, sticky=W)
        lbl3_42.grid(row=4, column=2)
        etr3_43.grid(row=4, column=3)
        lbl3_50.grid(row=5, column=0, sticky=W)
        etr3_51.grid(row=5, column=1, sticky=W)
        lbl3_52.grid(row=5, column=2)
        etr3_53.grid(row=5, column=3)

    def __str__(self):
        return '[current_index, recording: %s, %s]' % (current_index, recording)
#        return '[current_index: %s]' % (current_index)
        #return '[sessions_file: %s]' % (self.sessions_file)
        #int_value = self.interval.get() # int_value represents the currently selected radiobutton
        #return '[ti, tf: %s %s]' % (float(pv.self.sva[int_value][1].get()), float(pv.self.sva[int_value][2].get()))
        #current_index = self.cbx1.current()
        #return '[sessions_df: %s]' % (sessions_df.iloc[current_index])

    def draw_spectrogram(self):
        popup = tk.Tk()
        popup.geometry('700x460') # Set dimensions of popup window to 800x500 pixels
        popup.wm_title("Spectrogram")
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
        #                    Pxx, freqs, bins, im = self.ax.specgram(raw_df[spect[d]],NFFT=256,Fs=220) # E.g., request 's1' --> key 'lb'
        i = int(ti*fs)
        f = int(tf*fs)
        i_range = np.logical_and(i < raw_df.index, raw_df.index < f)
        signal = raw_df[r][i_range]
        Pxx, freqs, bins, im = self.ax.specgram(signal, NFFT=1024, noverlap=512, Fs=220, xextent=(ti,tf))
        #plt.ylim(0,55) # cutoff frequency less than 60 Hz which is due to AC power contamination
        if self.fixed_var[2].get() == 1:
            self.ax.set_ylim([self.spin_var[2][0].get(), self.spin_var[2][1].get()])
        else:
            self.ax.set_ylim(0, 110)
        plt.xlim(ti, tf)

        if self.overlay_check_value.get()==0: # Only display colorbar when not overlaying breath
            cb = p.colorbar(im, shrink=0.9, pad=0.02)
            cb.set_label('Intensity (dB)')

        recording = sessions_df.iloc[current_index]['recording']
        title = sessions_df.iloc[current_index]['title']
        subject = sessions_df.iloc[current_index]['subject']
        duration = sessions_df.iloc[current_index]['duration']
        date_time = sessions_df.iloc[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')

        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width, box.height*0.95])

        if self.overlay_check_value.get():
            ax2 = self.ax.twinx()
            ax2.set_ylim(0,1)
            ax2.set_ylabel('breath', color='blue')
            ax2.yaxis.set_major_locator(plt.NullLocator()) #Turns off tick marks and numbers
            ax2.set_xlim(ti, tf)
            t_range = np.logical_and(ti <resp_df.index, resp_df.index < tf)
            ax2.plot(resp_df['kPa'].index[t_range], \
                self.p_scale_var.get()*(resp_df['kPa'][t_range]-self.p_offset_var.get()), \
                color='blue')
            box2 = ax2.get_position()
            ax2.set_position([box2.x0, box2.y0, box2.width, box2.height*0.95])

        plt.show()

        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
        text=recording+' recorded '+str(date_time)+' ('+str('%.0f' % duration)+' seconds'+')')
        lbl0.pack(side=tk.BOTTOM, fill=X)

        canvas = FigureCanvasTkAgg(p, master=popup)
#       canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)

        toolbar = NavigationToolbar2Tk(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)

        popup.mainloop()
        return None

    def draw_psd(self):
        # In preparation for plotting, get the current radiobutton selection and the
        # corresponding initial and final times of the interval
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        #print('int_value = '+str(int_value))

        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())

        recording = sessions_df.iloc[current_index]['recording']
        title = sessions_df.iloc[current_index]['title']
        subject = sessions_df.iloc[current_index]['subject']
        duration = sessions_df.iloc[current_index]['duration']
        date_time = sessions_df.iloc[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        d = self.data_source_var.get()
        graph_title = 'Power Spectral Density at '+str(d)+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string
        #print('ti=', ti, ', tf=', tf)
        i = int(ti*fs)
        f = int(tf*fs)
        #print('i=', i, ', f=', f)

        i_range = np.logical_and(i < raw_df.index, raw_df.index < f)
        signal = raw_df[d][i_range]

#        xdata,ydata = [range(50)],[range(50)] #get some data from somewhere
#        Pxx, freqs = m.psd(signal, NFFT=1024, noverlap=512, Fs=220, color="black")
#        Pxx, freqs = m.psd(signal, NFFT=1024, noverlap=512, Fs=220)
        ydata, xdata = m.psd(signal, NFFT=1024, noverlap=512, Fs=220)
#        ydata, xdata = m.psd(signal, NFFT=2048, noverlap=512, Fs=220)

#        self.ax.set_ylim([self.spin_var[3][0].get(), self.spin_var[3][1].get()])
        popup = WinPsd(pv)
        popup.geometry('720x480') # Set dimensions of popup window to 800x500 pixels
        popup.wm_title("Power Spectral Density")

        popup.draw(xdata, ydata, graph_title)

        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
        text=recording+' recorded '+str(date_time)+' ('+str('%.0f' % duration)+' seconds'+')')
        lbl0.pack(side=tk.BOTTOM, fill=X)

        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)


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

        recording = sessions_df.iloc[current_index]['recording']
        title = sessions_df.iloc[current_index]['title']
        subject = sessions_df.iloc[current_index]['subject']
        duration = sessions_df.iloc[current_index]['duration']
        date_time = sessions_df.iloc[current_index]['date_time']
        if int_value > 0:
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'

        graph_title = 'Raw EEG Signal'
        plt.xlabel('samples (220 per second)')
        plt.ylabel('voltage (microvolts)')
        d = self.data_source_var.get()
        i = int(ti*fs)
        f = int(tf*fs)
        i_range = np.logical_and(i < raw_df.index, raw_df.index < f)
        self.ax.plot(raw_df[d][i_range].index, raw_df[d][i_range], color=plotcolor[d], label=plotlabel[d])

        if self.fixed_var[4].get() == 1:
            self.ax.set_ylim([self.spin_var[4][0].get(), self.spin_var[4][1].get()])
        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')
        plt.show()

        lbl0 = ttk.Label(popup, justify=LEFT, anchor=W, \
        text=recording+' recorded '+str(date_time)+' ('+str('%.0f' % duration)+' seconds'+')')
        lbl0.pack(side=tk.BOTTOM, fill=X)

        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)

        toolbar = NavigationToolbar2Tk(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)

        popup.mainloop()
        return None

    def draw_radar_chart(self):
        """
        In a new pop-up window, draws a radar chart with positions lb, lf, rf, rb
        arranged around a circle. Each of five frequency bands are plotted:
        delta: blue, theta: cyan, alpha: green, beta: orange, gamma: red.
        Power values are indicated by the radial lengths of the vertices of a polygon.

        Median values are plotted for relative power, mean values for absolute power.
        Range of median relative power is [0:1]; range of mean absolute power is [0:100].
        """

        #theta = radar_factory(4, frame='circle')

        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        if int_value > 0:
            #interval_string = sessions_df.iloc[current_index]['interval'+str(int_value)]
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
            popup.wm_title("Radar Chart")
#            graph_title = 'EEG Inverse Log of Mean Absolute Band Power'
            graph_title = 'EEG Mean Absolute Band Power'
            t_range = np.logical_and(ti < absolute_df.index, absolute_df.index < tf) # t_range is the same for all relative bands
#            print('t_range for absolute')
#            print(t_range)
            values_list = []
            values_array_list = []
            for i in range(len(freqbands)):
                for j in range(len(locations[i])-1, 0, -1): # omit average value; step down for proper radar display
                    values_list.append(30*(absolute_df[freqbands[i]][t_range][locations[i][j]]+1.667).mean())
                values_list.append(values_list[0])
                print('absolute values_list', values_list)
                values_array_list.append(values_list)
                values_list = [] # Clear list before continuing for loop
        elif self.rel_abs_var.get()=='relative': # Relative values
            popup.wm_title("Radar Charts")
            graph_title = 'EEG Mean Relative Band Power'
            t_range = np.logical_and(ti < relative_df.index, relative_df.index < tf) # t_range is the same for all relative bands
#            print('t_range for relative')
#            print(t_range)
            values_list = []
            values_array_list = []
            for i in range(len(freqbands)):
                for j in range(len(locations[i])-1, 0, -1): # omit average value; step down for proper radar display
                    values_list.append(relative_df[freqbands[i]][t_range][locations[i][j]].mean())
                values_list.append(values_list[0])
                #print('relative values_list', values_list)
                values_array_list.append(values_list)
                values_list = [] # Clear list before continuing for loop
        else:
            print('unknown value in rel_abs_var')
        #print('values_array_list = ', values_array_list)

        data = np.array(values_array_list)
        #print('data = ', data)
        #print('data.shape = ', data.shape)
        spoke_labels = ['rb', 'rf', 'lf', 'lb']
        angles = np.pi/4 + np.linspace(0, 2*np.pi, 4, endpoint=False)
        theta_list = list(angles)
        theta_list.append(theta_list[0])
        #theta_list = np.concatenate((theta_list, [theta_list[0]]))
        #print('theta_list = ', theta_list)
        theta = np.array(theta_list)
        #print('theta = ', theta)
        #print('theta.shape = ', theta.shape)

        #p = plt.figure(figsize=(6, 6))
        #p.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

        p = plt.figure(figsize=(7, 6))
        p.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

        colors = ['blue', 'cyan', 'green', 'orange', 'magenta']

        self.ax = plt.subplot(111, polar=True)

        # Adjust the height of the window so that title and legend are fully visible
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width*0.95, box.height*0.95])

        if self.rel_abs_var.get()=='absolute': # Absolute values
            plt.rgrids([20, 40, 60, 80])
            if self.fixed_var[6].get() == 1: #Get limits from Settings tab
                self.ax.set_ylim([self.spin_var[6][0].get(), self.spin_var[6][1].get()])
        elif self.rel_abs_var.get()=='relative': # Relative values
            plt.rgrids([0.2, 0.4, 0.6, 0.8])
            if self.fixed_var[5].get() == 1: # Get limits from Settings tab
                self.ax.set_ylim([self.spin_var[5][0].get(), self.spin_var[5][1].get()])
#        plt.rgrids([0.2, 0.4, 0.6, 0.8])
        self.ax.set_title(interval_string, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        i = 0
        #print('data.shape = ', data.shape)
        #print('theta.shape = ', theta.shape)

        for d, color in zip(data, colors):
            self.ax.plot(theta, d, color=color)
            self.ax.fill(theta, d, facecolor=color, alpha=0.25)

        #print('angles=', angles)

        self.ax.set_thetagrids(theta * 180/np.pi, spoke_labels)

        #self.ax.set_varlabels(spoke_labels)


        # add legend relative to top-left plot
        plt.subplot(1, 1, 1)
        labels = ('Delta', 'Theta', 'Alpha', 'Beta', 'Gamma')
        legend = plt.legend(labels, loc=(0.9, .95), labelspacing=0.2)
        ###plt.figtext(0.04, 0.82, ha='left', color='black', size='medium')
        plt.setp(legend.get_texts(), fontsize='medium')
        plt.setp(legend.get_lines(), linewidth='3')
#        plt.figtext(0.5, 0.965, 'Median Relative Power of Five Frequency Bands',
#                    ha='center', color='black', weight='bold', size='large')
        title = sessions_df.iloc[current_index]['title']
        recording = sessions_df.iloc[current_index]['recording']
        subject = sessions_df.iloc[current_index]['subject']
        plt.title(graph_title+'\n'\
            +recording+' ('+subject+') '+title+'\n'\
            +interval_string, fontsize = 'large')
        self.ax.grid(True) ### <---
        plt.show()
        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)

        toolbar = NavigationToolbar2Tk(canvas, popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, expand=1)
        popup.mainloop()

    def draw_table(self):
        """
        In a new pop-up window, draws a text box and fills it with lines of data
        corresponding to the selected interval of a session and the selection of
        relative or absolute power. Dropdown menu options include mean, median,
        standard deviation, and inverse log (for absolute power only).

        EEG values for each of four sensors are in four rows: lb, lf, rf, rb.

        There are five columns of data: delta, theta, alpha, beta, gamma.
        Values are separated by tabs to facilitate pasting in Excel spreadsheets.

        The values of table_type are 'mean', 'median', 'standard deviation', and 'inverse log' .
        """
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        if int_value > 0:
            #interval_string = sessions_df.iloc[current_index]['interval'+str(int_value)]
            # Ensure that graph title includes interval name as entered
            interval_string = self.sva[self.interval.get()][0].get()
        else:
            interval_string = 'full session'
        recording = sessions_df.iloc[current_index]['recording']
        subject = sessions_df.iloc[current_index]['subject']
        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())
#        band_vals = []
        values_list = []
        values_array = []
        popup = tk.Tk()
        table_type = self.type_average_var.get()
        abs_rel = self.rel_abs_var.get()
        if abs_rel=='absolute': # Display absolute values normalized to range [0:100] in table
            popup.wm_title("Table of Absolute EEG values")
            t_range = np.logical_and(ti < absolute_df.index, absolute_df.index < tf) # t_range is the same for all relative bands
            if table_type == 'mean': # columns are delta, theta, alpha, beta, gamma
                               # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(absolute_df[freqbands[i]][t_range][locations[i][j]].mean())
                    values_array.append(values_list)
                    values_list = []
            elif table_type == 'median': # columns are delta, theta, alpha, beta, gamma
                               # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(absolute_df[freqbands[i]][t_range][locations[i][j]].median())
                    values_array.append(values_list)
                    values_list = []
            elif table_type == 'standard deviation': # columns are delta, theta, alpha, beta, gamma
                               # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(absolute_df[freqbands[i]][t_range][locations[i][j]].std())
                    values_array.append(values_list)
                    values_list = []
            elif table_type == 'inverse log': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(np.power(10,absolute_df[freqbands[i]][t_range][locations[i][j]].mean()))
                    values_array.append(values_list)
                    values_list = []
        elif abs_rel=='relative': # Display relative values in table
            popup.wm_title("Table of Relative EEG values")
            t_range = np.logical_and(ti < relative_df.index, relative_df.index < tf) # t_range is the same for all relative bands
            if table_type == 'mean': # columns are delta, theta, alpha, beta, gamma
                               # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(relative_df[freqbands[i]][t_range][locations[i][j]].mean())
                    values_array.append(values_list)
                    values_list = []
            elif table_type == 'median': # columns are delta, theta, alpha, beta, gamma
                               # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(relative_df[freqbands[i]][t_range][locations[i][j]].median())
                    values_array.append(values_list)
                    values_list = []
            elif table_type == 'standard deviation': # columns are delta, theta, alpha, beta, gamma
                               # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(relative_df[freqbands[i]][t_range][locations[i][j]].std())
                    values_array.append(values_list)
                    values_list = []
            elif table_type == 'inverse log': # columns are delta, theta, alpha, beta, gamma
                                   # rows are lb, lf, rf, rb
                for j in range(1, len(locations)): # loop over 4 locations, ignoring avg
                    for i in range(len(freqbands)):
                        values_list.append(np.power(10,relative_df[freqbands[i]][t_range][locations[i][j]].mean()))
                    values_array.append(values_list)
                    values_list = []
        dataline = abs_rel+' '+ table_type+' values for '+recording+' ('+ subject+', '+ interval_string+')\n'
        header = 'rows: lb, lf, rf, rb\ndelta\ttheta\talpha\tbeta\tgamma\n'
        values = '' # string of values for averages
        for i in range(len(locations)-1): #loop over 4 locations
            for x in values_array[i]:
                values = values + str('%.3f' % x) + '\t'
            values = values + '\n'
#            values = values + abs_rel + '\t' + table_type +  '\n'
#            print('values')
#            print(values)
        txt1 = Text(popup, width=70, height=9, wrap=tk.WORD)
        txt1.insert(END, dataline+header+values)
        txt1.grid(row=1, column=1, sticky=W)

    def band(self, key):
        #print('canvas.draw()',key)
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
        and plot data for variables requested.

        Median values are plotted for relative values; mean values for absolute.

        Use single letter commands to plot graphs of median values
        (d=delta, t=theta, a=alpha, b=beta, g=gamma).

        Variables include j=jaw clench, k=blink, c=concentration, m=mellow.

        When respiration and breathing data are available, plots cmay
        include, p=breath, v=heart

        """

        #print('current_index = '+str(current_index))

        popup = tk.Tk()
        popup.geometry('700x460') # Set dimensions of popup window to 800x500 pixels
        popup.wm_title("Time Series graph")
        p = plt.figure()
        self.ax = plt.subplot(111)
        # In preparation for plotting, get the current radiobutton selection and the
        # corresponding initial and final times of the interval
        int_value = self.interval.get() # int_value represents the currently selected radiobutton
        #print('int_value = '+str(int_value))

        ti = float(self.sva[int_value][1].get())
        tf = float(self.sva[int_value][2].get())

        graph_title = ''
        i=0

        item_list = list(self.data_type_var.items())
        mean_list = []
        for pair in item_list:
            if pair[1].get(): # if the corresponding checkbox is checked
                q = pair[0] # assign q to d, t, a, b, g, p, v, c, m, j, k
                if q in {'d', 't', 'a', 'b', 'g'}:
                    r = self.data_source_var.get() # assign r to value of selected radio button ('lb','lf','rf','rb')
                    d = str(q+r) # concatenate two strings q and r
                    band = self.band(d)
                    #print('d=',d)
                    #print('band=',band)

                    if self.eeg_check_value.get(): # EEG data exists
                        if self.rel_abs_var.get()=='absolute': # Absolute values
                            t_range = np.logical_and(ti < absolute_df.index, absolute_df.index < tf) # t_range is the same for all relative bands
                            graph_title = 'EEG Absolute Power'
                            plt.xlabel('time (s)')
                            plt.ylabel('absolute power (Bels)')
                            if self.fixed_var[1].get() == 1:
                                self.ax.set_ylim([self.spin_var[1][0].get(), self.spin_var[1][1].get()])
                            self.ax.plot(absolute_df[band].index[t_range], absolute_df[band][t_range][d], color=plotcolor[d], label=plotlabel[d])
                            if self.med_mean_var.get()=='median':
                                median_val = absolute_df[band][t_range][d].median()
                                std_val = absolute_df[band][t_range][d].std()
                                plt.axhline(median_val, 0, 1, linewidth=1, color=plotcolor[d])
                                the_median = 'median '+str('%.2f' % median_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                                self.ax.annotate(the_median, xy=(1.01, 0.15),  xycoords='axes fraction',
                                            xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                            color=plotcolor[d], backgroundcolor='white',
                                            horizontalalignment='left', verticalalignment='top')
                            elif self.med_mean_var.get()=='mean':
                                mean_val = absolute_df[band][t_range][d].mean()
                                std_val = absolute_df[band][t_range][d].std()
                                plt.axhline(mean_val, 0, 1, linewidth=1, color=plotcolor[d])
                                the_mean = 'mean '+str('%.2f' % mean_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                                #print(the_median)
                                #median_list.append(the_median)
                                self.ax.annotate(the_mean, xy=(1.01, 0.15),  xycoords='axes fraction',
                                            xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                            color=plotcolor[d], backgroundcolor='white',
                                            horizontalalignment='left', verticalalignment='top')
                            i+=1
                        elif self.rel_abs_var.get()=='relative': # Relative values
                            t_range = np.logical_and(ti < relative_df.index, relative_df.index < tf) # t_range is the same for all relative bands
                            graph_title = 'EEG Relative Power'
                            plt.xlabel('time (s)')
                            plt.ylabel('relative power (fraction)')
                            if self.fixed_var[0].get() == 1:
                                self.ax.set_ylim([self.spin_var[0][0].get(), self.spin_var[0][1].get()])
                            #print('d='+str(d))
                            self.ax.plot(relative_df[band].index[t_range], relative_df[band][t_range][d], color=plotcolor[d], label=plotlabel[d])
                            if self.med_mean_var.get()=='median':
                                median_val = relative_df[band][t_range][d].median()
                                std_val = relative_df[band][t_range][d].std()
                                plt.axhline(median_val, 0, 1, linewidth=1, color=plotcolor[d])
                                the_median = 'median '+str('%.2f' % median_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                                self.ax.annotate(the_median, xy=(1.01, 0.15),  xycoords='axes fraction',
                                            xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                            color=plotcolor[d], backgroundcolor='white',
                                            horizontalalignment='left', verticalalignment='top')
                            elif self.med_mean_var.get()=='mean':
                                mean_val = relative_df[band][t_range][d].mean()
                                std_val = relative_df[band][t_range][d].std()
                                plt.axhline(mean_val, 0, 1, linewidth=1, color=plotcolor[d])
                                the_mean = 'mean '+str('%.2f' % mean_val)+u"\u00B1"+str('%.2f' % std_val) # median with +/- symbol for standard deviation
                                #print(the_median)
                                #median_list.append(the_median)
                                self.ax.annotate(the_mean, xy=(1.01, 0.15),  xycoords='axes fraction',
                                            xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                            color=plotcolor[d], backgroundcolor='white',
                                            horizontalalignment='left', verticalalignment='top')
                            i+=1
                    elif q in {'k'}:
                        d = str(q)
                        print('d=',d)
                        t_range = np.logical_and(ti < user_df.index, user_df.index < tf)
                        self.ax.plot(user_df[d].index[t_range], \
                            self.k_scale_var.get()*(user_df[d][t_range] - self.k_offset_var.get()), \
                            color=plotcolor[d], label=plotlabel[d])
                    elif q in {'j'}:
                        d = str(q)
                        print('d=',d)
                        t_range = np.logical_and(ti < user_df.index, user_df.index < tf)
                        self.ax.plot(user_df[d].index[t_range], \
                            self.j_scale_var.get()*(user_df[d][t_range] - self.j_offset_var.get()), \
                            color=plotcolor[d], label=plotlabel[d])
                    """ # Dealing with 'c' and 'm' is problematic; postpone implementation for now
                    elif q in {'c', 'm'}:
                        d = str(q)
                        #print('d=',d)
                        graph_title = "Muse Values for 'concentration' and 'mellow'"
                        plt.xlabel('time (s)')
                        plt.ylabel('fraction')
                        t_range = np.logical_and(ti < user_df.index, user_df.index < tf)
                        self.ax.plot(user_df[d].index[t_range], user_df[d][t_range], color=plotcolor[d], label=plotlabel[d])
                        mean_val = user_df[d][t_range][d].mean()
                        plt.axhline(mean_val, 0, 1, linewidth=1, color=plotcolor[d])
                        the_mean = 'mean '+str('%.1f' % mean_val)
                        mean_list.append(the_mean)
                        #print(the_mean)
                        self.ax.annotate(mean_list[i], xy=(1.01, 0.15),  xycoords='axes fraction',
                                    xytext=(1.05, 0.95-i*0.1), textcoords='axes fraction',
                                    color=plotcolor[d], backgroundcolor='white',
                                    horizontalalignment='left', verticalalignment='top')
                        i+=1
                    """
                elif q in {'v'}:
                    d = str(q)
                    #print('d=',d)
                    t_range = np.logical_and(ti < cardio_df.index, cardio_df.index < tf)
                    self.ax.plot(cardio_df[cardioresp[d]].index[t_range], \
                        self.v_scale_var.get()*(cardio_df[cardioresp[d]][t_range]-self.v_offset_var.get()), \
                        color=plotcolor[d], label=plotlabel[d])
                    graph_title = 'Electrocardiogram'
                    plt.xlabel('time (s)')
                    plt.ylabel('voltage (arbitrary units)')
                elif q in {'p'}:
                    d = str(q)
                    #print('d=',d)
                    t_range = np.logical_and(ti < resp_df.index, resp_df.index < tf)
                    self.ax.plot(resp_df[cardioresp[d]].index[t_range], \
                        self.p_scale_var.get()*(resp_df[cardioresp[d]][t_range]-self.p_offset_var.get()), \
                        color=plotcolor[d], label=plotlabel[d])
                    graph_title = 'Respiration'
                    plt.xlabel('time (s)')
                    plt.ylabel('pressure (arbitrary units)')
                elif q in {'s'}:
                    d = str(q)
                    #print('d=',d)
                    t_range = np.logical_and(ti < button_df.index, button_df.index < tf)
                    self.ax.plot(button_df[cardioresp[d]].index[t_range], \
                        self.s_scale_var.get()*(button_df[cardioresp[d]][t_range]-self.s_offset_var.get()), \
                        color=plotcolor[d], label=plotlabel[d])
                    graph_title = 'Button Press'
                    plt.xlabel('time (s)')
                    plt.ylabel('current (arbitrary units)')

        # Adjust the width of the window so that legend is visible
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width*0.75, box.height*0.9])
        self.ax.legend(loc='upper left', bbox_to_anchor=(1,0.25)) # Place to the right of the graph, near bottom
        # Get strings from the sessions_df dataframe to use in the graph title
        recording = sessions_df.iloc[current_index]['recording']
        title = sessions_df.iloc[current_index]['title']
        subject = sessions_df.iloc[current_index]['subject']
        duration = sessions_df.iloc[current_index]['duration']
        date_time = sessions_df.iloc[current_index]['date_time']
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
        text=recording+' recorded '+str(date_time)+' ('+str('%.0f' % duration)+' seconds'+')')
        lbl0.pack(side=tk.BOTTOM, fill=X)

        canvas = FigureCanvasTkAgg(p, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        btn = ttk.Button(popup, text="Close", command=popup.destroy)
        btn.pack(side=tk.RIGHT)

        toolbar = NavigationToolbar2Tk(canvas, popup)
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
        #sessions_df.to_excel(self.path+self.sessions_file, \
        #sheet_name='Sheet1', engine='xlsxwriter', merge_cells=False)
        sessions_df.to_excel(self.sessions_file, \
        sheet_name='Sheet1', engine='xlsxwriter', merge_cells=False)

    def update_value(self, sv, i, j):
        """
        Updates sessions_df dataframe values whenever entries in Entry boxes are changed.
        Values of i range from 0 - 4, where i=0 corresponds to default values interval0, ti0, tf0, and
        values of i from 1 - 4 correspond to user-defined rows interval1, ti1, tf1, etc.
        Values of j range from 0 - 2, where j=0 ~ interval, j=1 ~ ti, j=2 ~ tf
        """
        if j==0:
            sessions_df.at[current_index, 'interval'+str(i)] = str(self.sva[i][0].get())
            #print('new name = '+str(sessions_df.at[current_index, 'interval'+str(i)]))
        elif j==1:
            #print('ti = '+str(sessions_df.at[current_index, 'ti'+str(i)]))
            try: # This prevents crashing when user tries to edit an NaN value for t_initial or t_final
                sessions_df.at[current_index, 'ti'+str(i)] = str(self.sva[i][1].get())
            except:
                pass
                #print('not updating ti')
            #print('new ti = '+str(sessions_df.at[current_index, 'ti'+str(i)]))
        elif j==2:
            #print('new tf = '+str(sessions_df.at[current_index, 'tf'+str(i)]))
            try:
                sessions_df.at[current_index, 'tf'+str(i)] = str(self.sva[i][2].get())
            except:
                pass
                #print('not updating tf')
            #print('new tf = '+str(sessions_df.get_value(current_index, 'tf'+str(i))))
        self.interval.set(0)


    def select_graph(self):
        """
        Selects plotting routine based on graph type radiobutton selection
        """
        graph_type = self.graph_type_var.get()
        #print('graph_type=', graph_type)
        #"""
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
        #"""

if __name__ == '__main__':
    pv = PV()
    pv.mainloop()
