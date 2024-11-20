import asyncio
import math

import psutil

from logic.services_utils import AgentServiceUtils


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
        self.services = {'RAM_memory_function': self.get_software_ram_memory,
                         'hola': self.prueba_agent_service_con_params}    # TODO no hacerlo asi, rellenarlo de otra forma (p.e. por metodos de extension)

        # The Lock object is used to manage the access to global service dictionary
        self.lock = asyncio.Lock()

    # ------------------------
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

    async def execute_agent_service_by_id(self, service_id, **kwargs):
        """
        This method executes the agent service by its identifier. The parameters of the method with their values are
        available in kwargs.

        Args:
            service_id (str): identifier of the agent service.
            **kwargs: received parameters with the values.

        Returns:
            object: the result of the executed agent service ('OK' if the service does not return anything).
        """
        # First, the method of the service via its identifier is got
        service_method = await self.get_agent_service_by_id(service_id)
        if service_method is None:
            raise KeyError(f"Agent service with identifier {service_id} does not exist in this DT.")
        else:
            # Parameters adapted to the types required in the method are obtained
            adapted_params = await AgentServiceUtils.get_adapted_service_parameters(service_method, **kwargs)

            # Eventually, the method with the transformed arguments is called, and it is waited for the result
            result = await service_method(**adapted_params)
            if result is not None:
                return result
            else:
                return "OK"

    # ----------------------
    # Agent Services methods
    # ----------------------
    async def get_software_ram_memory(self):
        """
        This agent service gets the current used RAM memory of the software.

        Returns:
            float: the current used RAM memory of the software.
        """
        return psutil.virtual_memory().percent

    async def prueba_agent_service_con_params(self, param1: int, param2: float, param3: bool, param4):
        # Param1 tiene que ser un integer
        aux = param1 + 1
        print(f"El valor actual de param1 es {param1} y el valor siguiente {aux}")
        aux = math.sqrt(param2)
        print(f"El valor actual de param2 es {param2} y su raiz cuadrada {aux}")
        aux = param3 is True
        print(f"El param3 es un bool {param3} y se comprueba si es true {aux}")
        print(f"El param4 es un string {param4}")

