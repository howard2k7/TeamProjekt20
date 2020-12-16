import zmq
from threading import Thread

def listen(socket):
    while True:
        try:
            print(socket.recv_string())
        except KeyboardInterrupt:
            break

def send(socket):
    while True:
        try:
            msg = input()
            socket.send_string(msg)
        except KeyboardInterrupt:
            break

def main():
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://127.0.0.1:5555")

    listen_thread = Thread(target=listen, args=(socket, ))
    listen_thread.start()

    print("Client is ready!")
    send(socket)


if __name__ == '__main__':
    main()
