import tkinter as tk
import csv
from datetime import datetime
from EEGHandler import EEGHandler


class SimpleEEGRecorder(tk.Frame):
    def __init__(self, eeg_handler, folder="records", master=None):
        super().__init__(master)
        self.eeg_handler = eeg_handler
        self.folder = folder
        self.master = master
        self.pack()
        self.recording = False
        self.filename = ""
        self.buffer_time = 2
        self.record_button = tk.Button(self, text="Start", command=self.toggle_recording)
        self.record_button.pack(side="top")

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.config(text="Stop")
        self.filename = self.folder + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
        self.eeg_handler.start_server()
        print("Recording started. (Press space to stop.)")
        self.master.bind("<space>", self.toggle_recording)

    def stop_recording(self):
        self.recording = False
        eeg_handler.stop_server()
        self.record_button.config(text="Start")
        self.save_data()
        print("Recording stopped. Data saved to " + self.filename)
        self.master.unbind("<space>")

    def save_data(self):
        data = self.eeg_handler.get_data()
        with open(self.filename, mode='a') as file:
            writer = csv.writer(file)
            for eeg_data in data:
                writer.writerow(eeg_data)

    def periodic_task(self):
        if self.recording:
            self.save_data()
        self.master.after(self.buffer_time * 1000, self.periodic_task)

if __name__ == "__main__":
    # listening_addresses = {"/muse/gyro": [0] * 3, "/muse/acc": [0] * 3, "/muse/elements/blink": 0}
    listening_addresses = {"/muse/elements/blink": 0}
    eeg_handler = EEGHandler(covariates=listening_addresses)

    root = tk.Tk()
    app = SimpleEEGRecorder(eeg_handler=eeg_handler, folder="blinks/", master=root)
    app.eeg_handler = eeg_handler
    app.periodic_task()
    app.mainloop()
