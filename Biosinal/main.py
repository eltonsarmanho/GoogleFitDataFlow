# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections
import numpy as np
import matplotlib.pyplot as plt
import datetime

# import data from included examples
from pyphysio import EvenlySignal
# import all pyphysio classes and methods
import pyphysio as ph
import pyphysio.filters.Filters as flt
import heartpy as hp
import os
import glob
import matplotlib
import neurokit2 as nk
import rapidhrv as rhv
from rapidhrv import preprocess
from rapidhrv.preprocess import preprocess

matplotlib.use('TkAgg')
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Preprocess the data (filter, find peaks, etc.)


    # Compute relevant features


    data = hp.get_data('../data/hr.csv',delim = ',', column_name='heartRate')
    print(data)
    datetime_data = hp.get_data('../data/hr.csv',delim = ',', column_name = 'time')
    fs = hp.get_samplerate_datetime(datetime_data,timeformat='%Y-%m-%d %H:%M:%S')
    print(fs)

    #processed_data, info = nk.bio_process(ppg=data, sampling_rate=fs)

    #my_data = np.load("my_data.npy")  # Load data

    # The high-pass filter is implemented with a cutoff of 0.5Hz by default, which can be changed with highpass_cutoff.
    preprocessed = preprocess(inputdata=data,samplingrate=fs,)

    #hp.plotter(working_data, measures)

    #working_data, measures = hp.process(data,fs)
    # plot with different title
    #hp.plotter(working_data, measures, title='Heart Beat Detection on Noisy Signal')
    #plt.show()

