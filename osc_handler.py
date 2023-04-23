from pythonosc import dispatcher
from pythonosc import osc_server
from threading import Thread

class OSCHandler:
    def __init__(self, ip="0.0.0.0", port=5000):
        self.ip = ip
        self.port = port
        self.server_dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None

    def start_server(self):
        self.server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), self.server_dispatcher)
        self.server_thread = Thread(target=self.server.serve_forever)
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

if __name__ == "__main__":
    osc_handler = OSCHandler()

    def example_eeg_handler(address: str, *args):
        print(f"Address: {address}, Data: {args}")

    osc_handler.register_handler("/muse/eeg", example_eeg_handler)
    osc_handler.start_server()
