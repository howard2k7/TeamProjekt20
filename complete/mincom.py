import zmq
from threading import Thread
import time
import msgpack

class MinCom():

    __PORT = "5556"

    def __init__(self):
        self.data = 0

        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.bind("tcp://*:"+self.__PORT)

        listen_thread = Thread(target=self.listen, args=(self.socket, ))
        listen_thread.start()

    def listen(self, socket):
        while True:
            try:
                #self.data = int(socket.recv_string())
                self.data = msgpack.unpackb(socket.recv())
            except:
                pass

    def getData(self):
        return self.data


if __name__ == "__main__":
    mc = MinCom()
    while True:
        print("Data: ", mc.getData())
        time.sleep(1)