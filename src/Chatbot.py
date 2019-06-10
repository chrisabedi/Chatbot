import socket
import re
from queue import Queue
from time import sleep
from enum import Enum
import random

"""
    Simple Internet Relay Char (IRC) chat bot. Twitch doesn't have implementations for all the IRC protocols, and even 
    some listed on there wiki ( missing standards such as WHO , and NAMES, ROOMSTATE) In anycase, This is the 
    implementation I use when I want to stream.
    
    potential implementation of NAMES and ROOMSTATE if they extend their  interface:
    if re.search("names", current):
        bot.sock.send("NAMES #chrisabedi\n".encode())
    if re.search("state", command):
        bot.sock.send(":tmi.twitch.tv ROOMSTATE #chrisabedi\n".encode())
"""


HOST = "irc.chat.twitch.tv"
PORT = 6667


class Colors(Enum):
    Blue = 1
    BlueViolet = 2
    CadetBlue = 3
    Chocolate = 4
    Coral = 5
    DodgerBlue = 6
    Firebrick = 7
    GoldenRod = 8
    Green = 9
    HotPink = 10
    OrangeRed = 11
    Red = 12
    SeaGreen = 13
    SpringGreen = 14
    YellowGreen = 15


class Chatbot:

    def __init__(self, host, port):
        self.channel= "#chrisabedi"
        self.password = ""
        self.nick = "chrisabedi"
        self.sock = socket.socket()
        self._join_room(host, port)

    def _join_room(self, host, port):
        self.sock.connect((host, port))
        self.sock.send(f"PASS {self.password}\n".encode())
        self.sock.send((f"NICK {self.nick}\n".encode()))
        self.sock.send((f"JOIN {self.channel}\n".encode()))
        self.sock.send("CAP REQ :twitch.tv/membership\n".encode())
        self.sock.send("CAP REQ :twitch.tv/tags\n".encode())
        self.sock.send("CAP REQ :twitch.tv/commands\n".encode())

    def send_message(self, message):
        self.sock.send(f"PRIVMSG #chrisabedi :{message}\n".encode())

    def irc_command(self, command) -> str:
        self.sock.send(command.encode())
        sleep(1)
        return self.message_split(self.sock.recv(1024).decode())

    def message_split(self, message) -> str:
        return message.split(":", 2)[2]

    def get_user(self, msg) -> str:
        temp = msg.split(":", 2)[1]
        return temp.split("!")[0]


def parse_n_execute(bot: Chatbot, command: str):
    if re.search("PING", command):
        bot.sock.send("PONG\n".encode())
    if re.search("game", command):
        bot.send_message("we're playing\n")
    if re.search("rand", command):
        color = Colors(random.randint(1, 15)).name
        bot.send_message(f"/color {color}\n")
    if re.search("JOIN", command):
        bot.send_message(f"Welcome {bot.get_user(command)}\n")
    # TODO ROOMSTATE and NAMES implementations

def main():
    bot = Chatbot(HOST, PORT)
    read_buffer = Queue(maxsize=5)

    while True:
        resp = bot.sock.recv(1024).decode().split("\n")[0]
        read_buffer.put(resp)
        current = read_buffer.get()
        print("Current: " + current)
        print("Response: " + resp)
        parse_n_execute(bot, current)


if __name__ == '__main__':
    main()