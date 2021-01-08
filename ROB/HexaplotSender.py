import time
import zmq
import msgpack
import random


class HexaplotSender:

    def __init__(self, ip="127.0.0.1", port=5555):
        context = zmq.Context()

        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://"+ip+":"+str(port))

    def send_points(self, points=[(0.0, 0.0, 0.0)]):
        self.socket.send(msgpack.packb(points))

    def walk(self, fac=0.05, sleep=0.5):
        dummyPoints = [
                (-0.05, 0.1, 0.0),
                (-0.1, 0.0, 0.0),
                (-0.05, -0.1, 0.0),
                (0.05, -0.1, 0.0),
                (0.1, 0.0, 0.0),
                (0.05, 0.1, 0.0)
        ]

        while True:
            newPoints = []
            for i,points in enumerate(dummyPoints):
                x = points[0]+random.random()*fac
                y = points[1]+random.random()*fac
                z = points[2]+random.random()*fac
                newPoints.append((x, y, z))
            self.send_points(newPoints)
            time.sleep(sleep)

    def leg(self, sleep=0.5):
        dummyPoints = [
                [
                    (0.0, 0.0, 0.0),
                    (0.1, 0.0, 0.0),
                    (0.2, 0.0, 0.0)
                ],
                [
                    (0.0, 0.0, 0.0),
                    (0.1, 0.0, 0.0),
                    (0.18, 0.0, -0.05)
                ],
                [
                    (0.0, 0.0, 0.0),
                    (0.1, 0.0, 0.0),
                    (0.16, 0.0, -0.09)
                ],
                [
                    (0.0, 0.0, 0.0),
                    (0.1, 0.0, 0.01),
                    (0.13, 0.0, -0.1)
                ],
                [
                    (0.0, 0.0, 0.0),
                    (0.1, 0.0, 0.015),
                    (0.1, 0.0, -0.1)
                ],
        ]

        while True:
            for points in dummyPoints:
                self.send_points(points)
                time.sleep(sleep)

    def random_dot(self, step_size=0.1, sleep=0.1):
        while True:
            x = random.uniform(-1, 1)*step_size
            y = random.uniform(-1, 1)*step_size
            z = random.uniform(-1, 1)*step_size
            self.send_points([(x, y, z)])
            time.sleep(sleep)


if __name__ == "__main__":
    hps = HexaplotSender()

    # hps.random_dot(sleep=1)
    hps.leg()
    # hps.walk()
