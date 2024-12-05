"""
This class contains methods related to service management. It contains all type of services proposed in the
Functional View of RAMI 4.0.
"""
import inspect
import logging

import basyx.aas.model
import jsonschema
from jsonschema.exceptions import ValidationError

from logic.exceptions import RequestDataError, ServiceRequestExecutionError, AASModelReadingError
from utilities.fipa_acl_info import ACLJSONSchemas

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


class SubmodelServicesUtils:

    @staticmethod
    async def get_key_type_by_string(key_type_string):
        """
        This method gets the KeyType defined in BaSyx SDK related to the given string.

        Args:
            key_type_string (str): string of the desired KeyType.

        Returns:
            basyx.aas.model.KeyTypes: object of the KeyType defined in BaSyx.
        """
        try:
            return getattr(basyx.aas.model.KeyTypes, key_type_string)
        except AttributeError as e:
            raise AASModelReadingError("The KeyType with string {} does not exist in the AAS model defined"
                                   " types".format(key_type_string), sme_class=None, reason='KeyTypeAttributeError')

    @staticmethod
    async def get_model_type_by_key_type(key_type):
        """
        This method gets the AAS model class by a given KeyType defined in BaSyx SDK.

        Args:
            key_type (basyx.aas.model.KeyTypes): desired KeyType.

        Returns:
            object of the AAS model class.
        """
        for model_class, key_type_class in basyx.aas.model.KEY_TYPES_CLASSES.items():
            if key_type_class == key_type:
                return model_class
        return None