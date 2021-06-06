import time

import click

from netime import settings
from netime.client import ClientRTTService, UDPClient
from netime.server import UDPServer


@click.group()
def cli():
    pass


@cli.command()
@click.option("-s", "--server-address", default="127.0.0.1", help="Server address")
@click.option("-p", "--port", default=settings.SERVICE_PORT, type=int, help="Server port")
@click.option("-t", "--timeout", default=1, type=float, help="Timeout for socket")
@click.option("-n", default=100, type=int, help="Number of packets to send")
def run_client(server_address: str, port: int, timeout: int, n: int):
    client = UDPClient(timeout)
    client.connect(server_address, port)
    service = ClientRTTService(client)
    for _ in range(n):
        service.check_once()
        time.sleep(0.2)
    service.plot_rtt_for_server(server_address)


@cli.command()
@click.option("-s", "--server-address", default="127.0.0.1", help="Server address")
@click.option("-p", "--port", default=settings.SERVICE_PORT, type=int, help="Server port")
@click.option("-m", "--mean-delay", default=0, type=float, help="Server mean delay")
@click.option("-d", "--std-delay", default=0, type=float, help="Server standard deviation delay")
@click.option("-l", "--loss-chance", default=0, type=float, help="Server chance do loss packet")
def run_server(server_address: str, port: int, mean_delay, std_delay, loss_chance):
    server = UDPServer(mean_delay, std_delay, loss_chance)
    server.bind(server_address, port)
    server.run()


if __name__ == "__main__":
    cli()
