import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import spectrogram


def plot_spectrograms(data, window_size=220, overlap_factor=0.90, fs=220, nperseg=None, noverlap=None):
    sensor_data = data.iloc[:, 1:7].values

    if nperseg is None:
        nperseg = window_size
    if noverlap is None:
        noverlap = int(nperseg * overlap_factor)

    for sensor_index in range(sensor_data.shape[1]):
        single_sensor_data = sensor_data[:, sensor_index]

        frequencies, times, Sxx = spectrogram(single_sensor_data, fs=fs, nperseg=nperseg, noverlap=noverlap)

        plt.figure()
        plt.pcolormesh(times, frequencies, Sxx, shading='gouraud')
        plt.title(f'Spectrogram of Sensor {sensor_index + 1}')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [s]')
    plt.show()


# Read the data from a CSV file
filename = "records/2023-04-14_16-48-37.csv"
data = pd.read_csv(filename)

# Plot the spectrograms for all sensors
plot_spectrograms(data)

