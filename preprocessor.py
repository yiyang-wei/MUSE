import os
import numpy as np
import pandas as pd


filenames = []
for file in os.listdir("records"):
    filenames.append(file)


def drop_nan(data):
    before = data.shape[0]
    data = data.dropna(axis=0)
    after = data.shape[0]

    return before, after


for filename in filenames:
    # read the csv file
    data = pd.read_csv("records/" + filename, header=None)

    before, after = drop_nan(data)
    if before != after:
        print(f"File {filename} has {before - after} rows with nan.")

# # time should be increasing, sort by time
# data = data.sort_values(by=[0])

# # time is the 1st column
# time = np.array(data.iloc[:, 0])
#
# # eeg is the 2 - 7 columns
# eeg = np.array(data.iloc[:, 1:7])
#
# # confirmed is the 8th column
# confirmed = np.array(data.iloc[:, 7])
#
# # consecutive is the 9th column
# consecutive = np.array(data.iloc[:, 8])
#
# # grid is the 10 - 18 columns
# grid = np.array(data.iloc[:, 9:17])
