import time
import zmq
import msgpack
from threading import Thread

class HexaplotReceiver:

    def __init__(self, ip="127.0.0.1", port=5555):
        self.data = [(0, 0, 0)]

        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.bind("tcp://"+ip+":"+str(port))

        listen_thread = Thread(target=self.listen, args=(self.socket,))
        listen_thread.start()

    def listen(self, socket):
        while True:
            try:
                self.data = msgpack.unpackb(socket.recv())
            except:
                pass

    def getPoints(self):
        return self.data

if __name__ == "__main__":
    hpr = HexaplotReceiver()
    while True:
        print("Data: ", hpr.getData())
        time.sleep(1)