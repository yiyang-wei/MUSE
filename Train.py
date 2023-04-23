import numpy as np
import pandas as pd
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Flatten
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from tcn import TCN
import matplotlib.pyplot as plt
import time

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

FOLDER = "blinks/"

# Preprocess a file
def preprocess_file(filename):
    data = pd.read_csv(FOLDER + filename, header=None)
    X = np.array(data.iloc[:, 1:7])
    y = np.array(data.iloc[:, 7])

    return X, y

# Create overlapping window samples
def create_overlapping_window_samples(X, y, window_size, step_size, out_window):
    X_samples, y_samples = [], []

    for i in range(0, len(X) - window_size, step_size):
        X_samples.append(X[i:i + window_size, :])
        y_mean = np.mean(y[i + window_size - out_window:i + window_size], axis=0)
        y_samples.append(y_mean)


    return np.array(X_samples), np.array(y_samples)

window_size = 600
step_size = 60
out_window = 20
X_all, y_all = [], []

filenames = []
for file in os.listdir(FOLDER):
    filenames.append(file)

for filename in filenames:
    X, y = preprocess_file(filename)
    X_samples, y_samples = create_overlapping_window_samples(X, y, window_size, step_size, out_window)

    # Append the samples to the overall dataset
    X_all.append(X_samples)
    y_all.append(y_samples)

# Concatenate all samples
X_all = np.concatenate(X_all, axis=0)
y_all = np.concatenate(y_all, axis=0)
print(np.mean(y_all))

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_all, y_all, test_size=0.2, random_state=42)


def train_LSTM():
    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(32, input_shape=(window_size, 6), return_sequences=True))
    model.add(Dropout(0.5))
    # model.add(LSTM(32, return_sequences=True))
    # model.add(Dropout(0.2))
    model.add(LSTM(16))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    # model.add(Dense(1, activation='linear'))


    # Compile the model
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    # model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

    # Train the model
    history = model.fit(X_train, y_train, epochs=20, batch_size=8, validation_data=(X_val, y_val))

    return model, history


def train_TCN():
    model = Sequential()
    model.add(TCN(input_shape=(window_size, 6), nb_filters=32, kernel_size=3, nb_stacks=1, dilations=[4, 8, 16, 32, 64],
                  activation='relu', padding='causal', use_skip_connections=True, return_sequences=False))
    model.add(Flatten())
    # model.add(Dense(1, activation='sigmoid'))
    model.add(Dense(1, activation='linear'))

    # model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

    history = model.fit(X_train, y_train, epochs=20, batch_size=8, validation_data=(X_val, y_val))

    return model, history

model, history = train_LSTM()
# model, history = train_TCN()

# Make predictions on the test data
before = time.time()
y_pred = model.predict(X_val)
after = time.time()
print(f"Time taken to predict {len(X_val)} samples: {after - before} seconds")

# Print the predicted and true outcomes for each test data
for i in range(len(X_val)):
    print(f"Test Data {i + 1}:")
    print(f"Predicted outcome: {y_pred[i]}")
    print(f"True outcome: {y_val[i]}\n")

# Plot the accuracy
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('LSTM Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# # Plot the Mean Absolute Error (MAE)
# plt.plot(history.history['mae'], label='Training MAE')
# plt.plot(history.history['val_mae'], label='Validation MAE')
# plt.title('LSTM Model Mean Absolute Error')
# plt.xlabel('Epoch')
# plt.ylabel('MAE')
# plt.legend()
# plt.show()
