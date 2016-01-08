# -*- coding: utf-8 -*-
# cardioreesp56.py Conversion to Python 3.4
# Modified to work at 11Hz (no down-sampling)
# Release version derived from Cardio_generate_h5_04.py
"""
Created on Sun Nov 04 11:30:19 2014
@author: David Trowbridge
"""
import numpy as np
import scipy as sp

from pandas import DataFrame
import pandas as pd

session = input('TXT filename (without extension): ')

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
    filepath = 'C:/MuseRec/'
    fullfilename = filepath+dataName+'.txt'

    data = np.loadtxt(fullfilename, skiprows=7, usecols=(0,1,2))
    
    global t, v, p, tt, pp, ts, v_data, p_data, v_df, p_df
    
    t = [row[0] for row in data] # first column contains time-stamps of sample 
    v = [row[1] for row in data] # second column contains EKG voltage (mv)
    p = [row[2] for row in data] # third column contains breath pressure (kPa)
                                 # a fourth columns contains voltages from
                                 # button-press probe and can be ignored
    
    t_arr = np.array(t) # convert lists to np arrays
    v_arr = np.array(v)

    # For the pressure array, let's use 20 samples/s rather than 200
    # (or 10 samples/s rather than 100 for files created at 100 Hz)
    # In tt array, keep only every 10th value (every 1/20th second)
    #tt = t[:-1:10] # Down-sample sample times
    
#    tt_arr = np.array(tt) # convert list to np array
    tt_arr = np.array(t) # convert list to np array
    # similarly for pressure values
    #p2 = p[:-1:10] # Ensure that the p2 array corresponds to the tt array
            
    # Filter breath signal using FFT    
    #fft = sp.fft(p2)
    fft = sp.fft(p)
    bpp2 = fft[:]
    # Filter all frequencies > 1000 (determined empirically)
    for i in range(len(bpp2)):
#        if i >= 1000:bpp2[i] = 0 # appropriate for 220 Hz
        if i >= 100:bpp2[i] = 0 # appropriate for 11Hz
    # Do inverse FFT to recover filtered respiration signal
#        pp = sp.ifft(bpp2)
    pp = sp.ifft(bpp2).real
    
    pp_arr = np.array(pp) # convert list to np array
    # Return filtered signal, etc.
    
    
    return dataName, t_arr, v_arr, tt_arr, pp_arr

def save_data(cr_data):
    v_data = {'time': cr_data[1], 'mv': cr_data[2]}
    v_df = DataFrame(v_data, index = cr_data[1], columns = ['mv'])
    v_df.index.name = 'time'
    v_df.columns.name = 'v'
    
    p_data = {'time': cr_data[3], 'kPa': cr_data[4]}
    p_df = DataFrame(p_data, index = cr_data[3], columns = ['kPa'])
    p_df.index.name = 'time'
    p_df.columns.name = 'p'
    
    """
    v_data = {'time': t_arr, 'mv': v_arr}
    v_df = DataFrame(v_data, index = t_arr, columns = ['mv'])
    v_df.index.name = 'time'
    v_df.columns.name = 'v'
    
    p_data = {'time': tt_arr, 'kPa': pp_arr}
    p_df = DataFrame(p_data, index = tt_arr, columns = ['kPa'])
    p_df.index.name = 'time'
    p_df.columns.name = 'p'
    """
    global session
    session = session[3:6] # Retain only the digits after 'lab' in 'lab##'
    session = 'rec' + session # New string is 'rec##'
    print(session)
    global v_store, p_store
    v_store = pd.HDFStore(session+'_cardio.h5')
    v_store['cardio_data'] = v_df
    v_store.close() # This is important!
    
    p_store = pd.HDFStore(session+'_breath.h5')
    p_store['resp_data'] = p_df
    p_store.close() # This is important!

cr_data = load_data(session)
save_data(cr_data)