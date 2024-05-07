import asyncio
import getpass

import spade
from aioxmpp import PresenceShow
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from behaviours.myBehaviour import *


class DummyAgent(Agent):

    async def setup(self):
        print("Agent starting . . .")
        b = MyBehaviour()
        self.add_behaviour(b)




async def main():
    # jid = input("JID> ")
    # passwd = getpass.getpass()
    jid = "gcis@localhost"
    passwd = "gcis"

    dummy = DummyAgent(jid, passwd)
    await dummy.start(auto_register=True)
    dummy.presence.set_available()
    await dummy.web.start(hostname="127.0.0.1", port="10000") # si se quiere lanzarlo con interfaz web
    print("DummyAgent started. Check its console to see the output.")
    print("Wait until user interrupts with ctrl+C")

    await wait_until_finished(dummy)


if __name__ == "__main__":
    spade.run(main())