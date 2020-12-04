# !/usr/bin/env python3
# C:\Python39\

# How to execute:
# This program should be run client side.
# Do not forget to run comServer.py before you attempt to connect.

# Feel free to add yourself, either by real- or nickname.
# All authors:
#       Morton-Rennalls, Tristan
#       surname, name
#       surname, name
#       surname, name

# PLEASE COMMENT LAST MODIFICATIONS BELOW:
# Author:       Morton-Rennalls, Tristan
# Date:         2020-12-04
# Changes:      initial code

# TODO List:
# Code is from M.Engel ("sender.py") and needs to be adjusted, to receive variable data from the game controller


import zmq
import msgpack

__PORT = "5556"

context = zmq.Context()

socket = context.socket(zmq.PAIR)
socket.connect("tcp://127.0.0.1:"+__PORT)

while True:
    msg_send = input("Winkel angeben: ")
    socket.send(msgpack.packb([1,2,3, [],[], {"test":123}]))