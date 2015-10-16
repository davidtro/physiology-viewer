# physiology-viewer
This is a suite of python programs and some example data files for displaying graphs and charts of EEG, ECG and respiration data recorded by the Muse headband and Vernier probe devices.

Visit http://still-breathing.net/software for more details.

Program Files: 
Phys_Viewer.py   This is the Physiology Viewer program. It needs to open the file EEG_CardioRespSessions.xls, which must be in the directory C:\MedRec. Data files *.h5 data files must also be in that same directory.

EEG_CardioRespSessions.xls   This is an Excel file containing details about recording sessions (name of session, subject name, duration, names and start/end times of named intervals in the session, etc.) This particular file has only one row of example data, (index 60, rec33) to illustrate how session data is saved and displayed. The file MUST BE in the directory C:\MedRec.

EEG_generate_h5.py   This is a file conversion program that starts with .CSV datafiles created by the Muse Player from data produced by the Muse headband. It writes into the current four .h5 files containing EEG data. The .CSV datafile MUST be in the directory C:\MuseRec.

Cardio_generate_h5.py   This is a file conversion program that starts with .TXT files created by Logger Pro software from Vernier. It writes into the current directory two .h5 files containing respiration and electorcardiogram data. The .TXT datafile MUST be in the directory C:\MuseRec.

Cardiorespiratory and EEG data files generated for session #33:

rec33_breath.h5   time series of pressure values from the Vernier Respiration monitor

rec33_cardio.h5   time series of voltage values from the Vernier Electrocardiogram sensor

rec33_eeg.abs.h5  time series of EEG absolute power values from the Muse Headband

rec33_eeg.raw.h5  time series of raw EEG voltages from the Muse Headband

rec33_eeg.rel.h5  time series of EEG relative power values from the Muse Headband

rec33_eeg.user.h5 time series of EEG user data (jaw clench, blink, concentration, mellow) from the Muse Headband

README.md   This file.
