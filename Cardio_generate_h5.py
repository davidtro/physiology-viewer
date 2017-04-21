# -*- coding: utf-8 -*-
# cardioreesp56.py Conversion to Python 3.4
# Modified to work at 11Hz (no down-sampling)
# Release version derived from Cardio_generate_h5_04.py
"""
Created on Sun Nov 04 11:30:19 2014
@author: David Trowbridge
"""
import numpy as np

from pandas import DataFrame
import pandas as pd

def load_data(dataName):
    """
    Attempts to open tab-delimited text file for session data.
    First 7 lines contain header information from Logger Pro 3 software
    when exporting LabQuest data in .txt format.
    
    Preferred LabQuest sample rate is 220 Hz, for consistency
    with Muse headband EEG recording sample rate.
    Use np.loadtxt() for obtaining data.
    
    Create global arrays 
    v_arr for heart voltage (original sampling rate),
    t_arr for timestamps corresponding to heart voltages,
    pp_arr for filtered breath pressures (one-tenth original sampling rate),
    tt_arr for timestamps corresponding to breath pressures
    
    """

    global data, ncols
    data = np.loadtxt(dataName, skiprows=7)
    nsamps, ncols = data.shape
    print('ncols=',ncols)
    #print('example p data: ', data[2])
    
    global t, v, p, s, tt, pp, ts, v_data, p_data, s_data, v_df, p_df, s_df
    
    t = [row[0] for row in data] # first column contains time-stamps of sample 
    v = [row[1] for row in data] # second column contains EKG voltage (mv)
    p = [row[2] for row in data] # third column contains breath pressure (kPa)
    
    t_arr = np.array(t) # convert lists to np arrays
    v_arr = np.array(v)
    p_arr = np.array(p)

    if ncols>3:
        s = [row[3] for row in data] # a fourth column button-press currents
        s_arr = np.array(s)
        return dataName, t_arr, v_arr, p_arr, s_arr
    else:
        return dataName, t_arr, v_arr, p_arr

#    return dataName, t_arr, v_arr, t_arr, p_arr, t_arr, s_arr
    
def save_data(cr_data):
    v_data = {'time': cr_data[1], 'mv': cr_data[2]}
    v_df = DataFrame(v_data, index = cr_data[1], columns = ['mv'])
    v_df.index.name = 'time'
    v_df.columns.name = 'v'
    
    p_data = {'time': cr_data[1], 'kPa': cr_data[3]}
    p_df = DataFrame(p_data, index = cr_data[1], columns = ['kPa'])
    p_df.index.name = 'time'
    p_df.columns.name = 'p'
    
    if ncols>3:
        s_data = {'time': cr_data[1], 'ma': cr_data[4]}
        s_df = DataFrame(s_data, index = cr_data[1], columns = ['ma'])
        s_df.index.name = 'time'
        s_df.columns.name = 's'
    
    global session
    session = session[3:6] # Retain only the digits after 'lab' in 'lab##'
    session = 'rec' + session # New string is 'rec##'
    print(session)
    global v_store, p_store, s_store
    v_store = pd.HDFStore(session+'_cardio.h5')
    v_store['cardio_data'] = v_df
    v_store.close() # This is important!
    
    p_store = pd.HDFStore(session+'_breath.h5')
    p_store['resp_data'] = p_df
    p_store.close() # This is important!

    if ncols>3:
        s_store = pd.HDFStore(session+'_button.h5')
        s_store['btn_data'] = s_df
        s_store.close() # This is important!

filepath = 'C:/MuseRec/'
session = input('TXT filename (without extension): ')
fullfilename = filepath+session+'.txt'

save_data(load_data(fullfilename))