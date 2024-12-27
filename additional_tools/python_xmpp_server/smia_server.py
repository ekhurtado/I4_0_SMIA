import argparse
import asyncio
import sys

from pyjabber.server import Server


def main():
    parser = argparse.ArgumentParser(description='Parser for XMPP Server CLI arguments')
    parser.add_argument("-hs", "--host", default="0.0.0.0")
    parser.add_argument("-c_p", "--client_port", type=int, default=5222)
    parser.add_argument("-s_p", "--server_port", type=int, default=5269)
    args = parser.parse_args(sys.argv[1:])

    my_server = Server(
        host=args.host,
        client_port=args.client_port,
        server_port=args.server_port,
        connection_timeout=500,
    )

    asyncio.run(my_server.start())


if __name__ == "__main__":
    main()


