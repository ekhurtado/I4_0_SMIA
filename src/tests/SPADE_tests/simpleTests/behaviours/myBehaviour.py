import asyncio

from aioxmpp import PresenceShow
from spade.behaviour import CyclicBehaviour

class MyBehaviour(CyclicBehaviour):
    async def on_start(self):
        print("Starting behaviour . . .")
        self.agent.presence.set_available()
        self.counter = 0

    async def run(self):
        print("Counter: {}".format(self.counter))
        print("[{}] Contacts List: {}".format(self.agent.name, self.agent.presence.get_contacts()))
        self.presence.set_available()
        self.counter += 1
        await asyncio.sleep(1)