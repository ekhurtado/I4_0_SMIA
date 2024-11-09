import asyncio
import inspect
import math

import psutil


class AgentServices:
    """
    This class contains all the methods related to the agent services. As well as the asset has services that can be
    exposed, the agent also has services that can be exposed and used during the execution of the software.
    """

    def __init__(self, agent_object):
        """
        The constructor method adds the object of the agent to have access to its information.

        Args:
            agent_object (spade.Agent): the SPADE agent object of the AAS Manager agent.
        """

        # The SPADE agent object is stored as a variable of the behaviour class
        self.myagent = agent_object

        # The services dictionary contains all available services of the agent, with its associated executable methods
        self.services = {'RAM_memory': self.get_software_ram_memory}

        # The Lock object is used to manage the access to global service dictionary
        self.lock = asyncio.Lock()

    # Services general methods
    # ------------------------
    async def get_agent_service_by_id(self, service_id):
        """
        This method gets the agent service by its identifier. It returns None if the service is not found.

        Args:
            service_id (str): unique identifier of the agent service.

        Returns:
            method: executable method of the agent service.
        """
        async with self.lock:
            if service_id not in self.services:
                return None
            else:
                return self.services[service_id]

    async def get_agent_service_parameters(self, service_id):
        service_method = await self.get_agent_service_by_id(service_id)
        if service_method is None:
            return None
        else:
            # Obtain the signature of the method
            sig = inspect.signature(service_method)
            params = sig.parameters
            print(params)


    async def get_software_ram_memory(self):
        """
        This agent service gets the current used RAM memory of the software.

        Returns:
            float: the current used RAM memory of the software.
        """
        return psutil.virtual_memory().percent


