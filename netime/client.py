import socket
import time
from typing import List, Optional, Tuple

from matplotlib import pyplot as plt

from netime import logger
from netime.utils import Addr


class UDPClient:
    def __init__(self, timeout=None):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._destination: Optional[Tuple[str, int]] = None

        if timeout:
            self._socket.settimeout(timeout)

    def _get_destination(self, destination) -> Optional[Addr]:
        if not any([self._destination, destination]):
            raise ValueError("Destination is not specified")
        return destination or self._destination

    def send(self, message: str, destination: Optional[Tuple[str, int]] = None):
        destination = self._get_destination(destination)
        logger.debug("Sending packet to %s", destination[0])
        self._socket.sendto(message.encode(), self._get_destination(destination))

    def receive(self) -> Optional[Tuple[Optional[bytes], Optional[Tuple]]]:
        try:
            data, addr = self._socket.recvfrom(1000)
            logger.debug("Received data from %s on port %s", addr[0], addr[1])
            return data, addr[:2]
        except socket.timeout:
            logger.warning("Timeout on receive")
            return None, None

    def connect(self, ip: str, port: int):
        self._destination = (ip, port)


class ClientRTTService:
    def __init__(self, client: UDPClient, g_factor=0.9):
        self._client = client
        self._g_factor = g_factor
        self.rtt_values = {}

    def prepare_message(self) -> str:
        return str(time.time())

    def parse_message(self, message: bytes) -> Optional[float]:
        try:
            return float(message.decode())
        except ValueError:
            logger.warning("Unable to parse message: %s", message)
            return None

    def check_once(self):
        message = self.prepare_message()
        self._client.send(message)
        data, addr = self._client.receive()
        if data and addr:
            self.update_rtt_values(data, addr)

    def update_rtt_values(self, data: bytes, addr: Addr):
        """
        A = (1-g)A + gM
        """
        now: float = time.time()
        timestamp = self.parse_message(data)
        if timestamp:
            rtt = now - timestamp
            self.rtt_values.setdefault(addr[0], {})
            self.rtt_values[addr[0]].setdefault("rtt_list", [rtt])
            rtt_estimations_list = self.rtt_values[addr[0]].setdefault("rtt_estimations_list", [rtt])
            rtt_estimations_list.append(rtt_estimations_list[-1]*(1-self._g_factor)+self._g_factor * rtt)
            self.rtt_values[addr[0]]["rtt_list"].append(rtt)
        else:
            logger.error("Not implemented")

    def plot_rtt_for_server(self, ip: str):
        if ip not in self.rtt_values:
            logger.warning("IP %s has no measured rtt")
            return
        fig, ax = plt.subplots(2)
        rtt_list: List[float] = self.rtt_values[ip]["rtt_list"]
        rtt_estimations_list: List[float] = self.rtt_values[ip]["rtt_estimations_list"]
        ax[0].set_title("RTT")
        ax[0].plot(range(len(rtt_list)), rtt_list)
        ax[1].set_title("RTT estimation")
        ax[1].plot(range(len(rtt_estimations_list)), rtt_estimations_list)
        plt.show()
