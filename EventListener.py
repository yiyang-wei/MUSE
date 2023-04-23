# import tkinter as tk
# from tkinter import ttk
# import threading
# import time
# from pythonosc import dispatcher, osc_server
# from pynput import keyboard
# import csv
#
# osc_data = [None] * 6
# keyboard_timestamps = []
# state_colors = {'A': 'red', 'B': 'blue', 'C': 'green', 'D': 'yellow'}
# current_state = 'None'
#
# def osc_handler(address, *args):
#     global osc_data
#     osc_data.append((time.time(), args))
#
# dispatcher = dispatcher.Dispatcher()
# dispatcher.map("/ME", osc_handler)
#
# def osc_server_thread():
#     server = osc_server.ThreadingOSCUDPServer(("localhost", 9000), dispatcher)  # Adjust IP and port as needed
#     server.serve_forever()
#
# def keyboard_listener():
#     def on_press(key):
#         try:
#             k = key.char
#             if k in state_colors:
#                 keyboard_timestamps.append((time.time(), k))
#         except AttributeError:
#             pass
#
#     with keyboard.Listener(on_press=on_press) as listener:
#         listener.join()
#
# class App(tk.Tk):
#     def __init__(self):
#         super().__init__()
#
#         self.title("OSC Classifier")
#         self.geometry("300x200")
#
#         style = ttk.Style()
#         style.configure("Green.TButton", background="green")
#         style.configure("Red.TButton", background="red")
#
#         self.start_button = ttk.Button(self, text="START", command=self.start, style="Green.TButton")
#         self.start_button.pack(pady=10)
#
#         self.stop_button = ttk.Button(self, text="STOP", command=self.stop, style="Red.TButton", state="disabled")
#         self.stop_button.pack(pady=10)
#
#         self.duration_label = ttk.Label(self, text="00:00")
#         self.duration_label.pack(pady=10)
#
#         self.state_labels = {}
#         for state in state_colors:
#             frame = tk.Frame(self, background=state_colors[state], relief="sunken", width=30, height=30)
#             label = ttk.Label(frame, text=state)
#             label.pack(padx=5, pady=5)
#             frame.pack(side="left", padx=5, pady=5)
#             self.state_labels[state] = frame
#
#         self.recording = False
#         self.start_time = 0
#         self.update_duration()
#
#     def start(self):
#         self.recording = True
#         self.start_time = time.time()
#         self.start_button.configure(state="disabled")
#         self.stop_button.configure(state="normal")
#
#     def stop(self):
#         self.recording = False
#         self.start_button.configure(state="normal")
#         self.stop_button.configure(state="disabled")
#         self.save_data()
#
#     def update_duration(self):
#         if self.recording:
#             elapsed = int(time.time() - self.start_time)
#             minutes, seconds = divmod(elapsed, 60)
#             self.duration_label.configure(text="{:02d}:{:02d}".format(minutes, seconds))
#         self.after(1000, self.update_duration)
#
#     def save_data(self):
#         with open("output.csv", "w", newline='') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow(["timestamp", "state", "osc_data"])
#
#             osc_index = 0
#             for timestamp, state in keyboard_timestamps:
#                 while osc_index < len(osc_data) and osc_data[osc_index][0] < timestamp - 1:
#                     osc_index += 1
#
#                 if osc_index < len(osc_data):
#                     writer.writerow([timestamp, state, osc_data[osc_index][1]])
#
#                 while osc_index < len(osc_data) and osc_data[osc_index][0] < timestamp + 1:
#                     osc_index += 1
#
#             keyboard_timestamps.clear()
#             osc_data.clear()
#
# if __name__ == "__main__":
#     app = App()
#
#     osc_thread = threading.Thread(target=osc_server_thread, daemon=True)
#     osc_thread.start()
#
#     keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
#     keyboard_thread.start()
#
#     app.mainloop()

import tkinter as tk
import threading
import time
from pythonosc import dispatcher, osc_server
from pynput import keyboard
import csv

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("OSC and Keyboard Listener")
        self.geometry("500x500")

        self.start_stop_button = tk.Button(self, text="START", fg="white", bg="green", command=self.start_stop)
        self.start_stop_button.pack(pady=10)

        self.recording = False
        self.data = []
        self.start_time = 0

    def start_stop(self):
        if self.recording:
            self.recording = False
            self.start_stop_button.configure(text="START", bg="green")
            self.save_data()
        else:
            self.recording = True
            self.data = []
            self.start_stop_button.configure(text="STOP 00:00", bg="red")
            self.start_time = time.time()
            self.update_duration()

    def update_duration(self):
        if self.recording:
            elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.start_stop_button.configure(text=f"STOP {minutes:02d}:{seconds:02d}", bg="red")
            self.after(100, self.update_duration)

    def save_data(self):
        print(self.data)


if __name__ == "__main__":
    app = App()
    app.mainloop()