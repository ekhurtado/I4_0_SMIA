"""
This class contains methods related to service management. It contains all type of services proposed in the
Functional View of RAMI 4.0.
"""
import inspect
import logging
import types

_logger = logging.getLogger(__name__)

class AgentServiceUtils:
    """
    This class contains utility methods related to the Agent Services.
    """

    @staticmethod
    async def get_agent_service_parameters(service_method):
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


    @staticmethod
    async def get_adapted_service_parameters(service_method, **kwargs):
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
        required_params_info = await AgentServiceUtils.get_agent_service_parameters(service_method)
        adapted_params = {}

        # The received parameters with the values are available in kwargs
        if len(required_params_info) != 0 and ((kwargs is None) or (len(kwargs) == 0)):
            raise ValueError(f"The service method cannot be executed because the required parameters have not been "
                             f"provided.")

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

    @staticmethod
    async def safe_execute_agent_service(service_method, **kwargs):
        """
        This method executes the agent service securely, regardless of the execution method, synchronous or
        asynchronous.

        Args:
            service_method: executable method of the agent service.
            **kwargs: in case the execution method has parameters, they are passed as kwargs.

        Returns:
            result of the execution of the agent service.
        """
        if inspect.iscoroutinefunction(service_method):
            return await service_method(**kwargs)
        else:
            return service_method(**kwargs)


class SubmodelServicesUtils:
    pass
