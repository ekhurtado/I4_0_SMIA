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
        self.services = {'RAM_memory': self.get_software_ram_memory}    # TODO no hacerlo asi, rellenarlo de otra forma (p.e. por metodos de extension)

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

    async def get_agent_service_parameters(self, service_method):
        """
        This method gets the required information about the parameters of the agent service: the names and types of
        service method parameters.

        Args:
            service_method (method): method of the agent service.

        Returns:
            dict: dictionary with all information about the parameters of the agent service.
        """
        if service_method is None:
            raise KeyError(f"The service method {service_method} does not exist in this DT.")
        else:
            # Obtain the signature of the method
            sig = inspect.signature(service_method)
            params = sig.parameters
            # Construct the dictionary with the information of the parameters
            params_details = {
                nombre: {
                    'annotation': parametro.annotation,
                    'type': parametro.annotation if parametro.annotation is not inspect.Parameter.empty else str,
                }
                for nombre, parametro in params.items()
            }
            return params_details

    async def get_adapted_service_parameters(self, service_method, **kwargs):
        """
        This method adapts the received parameters values to the required types of the service method, in order to be
        correctly executed.

        Args:
            service_method (method): method of the agent service.
            **kwargs: received parameters with the values.

        Returns:
            dict: parameters correctly adapted to the method.
        """
        if service_method is None:
            ValueError(f"A null object has been offered for the {service_method} method, its parameters cannot be "
                       f"obtained.")
        # The information of the required method parameters is obtained
        required_params_info = await self.get_agent_service_parameters(service_method)
        adapted_params = {}

        # The received parameters with the values are available in kwargs
        for param_name, value in kwargs.items():
            if param_name in required_params_info:
                tipo = required_params_info[param_name]['type']
                try:
                    if tipo == bool:  # bool(value) is true as long as the string is not empty, son it cannot be used.
                        adapted_params[param_name] = value.lower() in ('yes', 'true', 't', '1')
                    else:
                        adapted_params[param_name] = tipo(value)
                except ValueError as e:
                    raise ValueError(f"Could not transform the value {value} for the parameter '{param_name}',"
                                     f" reason: {e}")
            else:
                raise ValueError(f"Parameter {param_name} not found in method {service_method}.")
        return adapted_params

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
        # First, the method of the service via its identifier is get
        service_method = await self.get_agent_service_by_id(service_id)
        if service_method is None:
            raise KeyError(f"Agent service with identifier {service_id} does not exist in this DT.")
        else:
            # Parameters adapted to the types required in the method are obtained
            adapted_params = await self.get_adapted_service_parameters(service_method, **kwargs)

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

