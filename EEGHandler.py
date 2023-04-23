from pythonosc import dispatcher
from pythonosc import osc_server
from threading import Thread
import time

class EEGHandler:
    def __init__(self, ip="0.0.0.0", port=5000, covariates=None):
        self.ip = ip
        self.port = port
        self.server_dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None
        self.start_time = None
        self.latest_data = dict()
        self.buffer = []
        self.register_handler("/muse/eeg", self.raw_data_handler)
        if covariates:
            self.latest_data = {address: covariates[address] for address in covariates.keys()}
            for address in covariates.keys():
                self.register_handler(address, self._update_handler_data)

    def start_server(self):
        self.server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), self.server_dispatcher)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.start_time = time.time()
        self.server_thread.start()
        print(f"Listening on UDP port {self.port}")

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server_thread.join()
            self.server = None
            self.server_thread = None
            print("OSC server stopped")

    def register_handler(self, address_pattern, handler_function):
        self.server_dispatcher.map(address_pattern, handler_function)

    def unregister_handler(self, address_pattern):
        if address_pattern in self.server_dispatcher.handlers:
            del self.server_dispatcher.handlers[address_pattern]

    def is_running(self):
        return self.server is not None

    def raw_data_handler(self, address, *args):
        elapsed_time = (time.time() - self.start_time) * 1000
        eeg_data = list(args)
        self.buffer.append([elapsed_time] + eeg_data + self.covariables())

    def _update_handler_data(self, address, *args):
        if address in self.latest_data:
            self.latest_data[address] = args

    def covariables(self):
        flattened_data = []
        for values in self.latest_data.values():
            if isinstance(values, (list, tuple)):
                flattened_data.extend(values)
            else:
                flattened_data.append(values)
        return flattened_data

    def get_data(self):
        data = self.buffer
        self.buffer = []
        return data

if __name__ == "__main__":
    import time

    listening = {"/muse/gyro":[0]*3, "/muse/acc":[0]*3, "/muse/elements/blink":0}

    eeg_handler = EEGHandler(covariates=listening)

    eeg_handler.start_server()
    try:
        while True:
            time.sleep(1)
            now = time.time()
            print(f"{int(now / 60)}:{now % 60:02.2f}")
            print(*eeg_handler.get_data(), sep="\n")
    except KeyboardInterrupt:
        eeg_handler.stop_server()