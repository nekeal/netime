import random
import socket
import struct
import time

from netime import logger, settings
from netime.client import UDPClient


class UDPServer(UDPClient):

    def __init__(self, delay_std=0, delay_mean=0, loss_chance=0, *args, **kwargs):
        self._delay_std = delay_std
        self._delay_mean = delay_mean
        self._loss_chance = loss_chance
        self._addr = None
        super().__init__(*args, **kwargs)

    def bind(self, addr, port):
        self._addr = (addr, port)
        self._socket.bind((addr, port))
        if addr == "0.0.0.0":
            mreq = struct.pack("4sl", socket.inet_aton(settings.MULTICAST_GROUP), socket.INADDR_ANY)
            self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def wait(self):
        value = random.gauss(self._delay_mean, self._delay_std)
        logger.debug("Delaying packet for %s", value)
        time.sleep(value)
        return value

    def skip_packet(self):
        if random.random() <= self._loss_chance:
            logger.debug("Packet skipped")
            return True
        return False

    def run(self):
        logger.info(f"Server started on {self._addr}")
        while True:
            data, cli_addr = self.receive()
            logger.debug("Received packet of size %s", len(data))
            if self.skip_packet():
                continue
            self.wait()
            self.send(data.decode(), cli_addr)
