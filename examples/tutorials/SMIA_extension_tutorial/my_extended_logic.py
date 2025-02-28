import asyncio

import smia
from smia.assetconnection.asset_connection import AssetConnection
from spade.behaviour import CyclicBehaviour


class MyExtendedCapability(CyclicBehaviour):

    def __init__(self, agent_object):
        super().__init__()

        self.interaction_num = 0
        self.myagent = agent_object

    async def run(self) -> None:

        print("Hi! I am an extended Capability with interaction number: {}".format(self.interaction_num))
        self.interaction_num += 1

        if self.interaction_num == 5:
            # Let's execute the new agent service
            result = await self.myagent.agent_services.execute_agent_service_by_id('MyExtendedAgentService', param1=5, param2=11)
            print("The result of the new agent service MyExtendedAgentService is {}".format(result))

        try:
            if self.interaction_num == 7:
                # Let's execute the new agent service: invalid parameters
                result = await self.myagent.agent_services.execute_agent_service_by_id('MyExtendedAgentService',
                                                                                       param1='5', param2={'json':' example'})
            if self.interaction_num == 8:
                # Let's execute the new agent service: no parameters
                result = await self.myagent.agent_services.execute_agent_service_by_id('MyExtendedAgentService')
        except Exception as e:
            print("An error occurred: {}".format(e))

        if self.interaction_num == 10:
            # Let's execute an asset service using the new Asset Connection
            aas_interface_ref = await smia.AASModelUtils.create_aas_reference_object(
                reference_type='ModelReference', keys_dict=[
                    {'type': 'SUBMODEL', 'value': 'https://example.com/ids/sm/6505_6142_2052_5708'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'MyExtendedInterface'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'InteractionMetadata'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'properties'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'extended_property'},
                ])
            aas_interface_elem = await self.myagent.aas_model.get_object_by_reference(aas_interface_ref)
            new_asset_conn_ref = await smia.AASModelUtils.create_aas_reference_object(
                reference_type='ModelReference', keys_dict=[
                    {'type': 'SUBMODEL', 'value': 'https://example.com/ids/sm/6505_6142_2052_5708'},
                    {'type': 'SUBMODEL_ELEMENT_COLLECTION', 'value': 'MyExtendedInterface'},
                ])
            new_asset_conn_class = await self.myagent.get_asset_connection_class_by_ref(new_asset_conn_ref)
            result = await new_asset_conn_class.execute_asset_service(interaction_metadata=aas_interface_elem)
            print("An asset service has been executed with the new MyExtendedAssetConnection with result: {}".format(result))

        await asyncio.sleep(2)    # waits 2 seconds in every cyclic execution


def my_extended_agent_service(param1: int, param2: int):
    print("Hi! I am an extended agent service for adding two numbers...")
    print("The result of the sum of {} and {} is {}".format(param1, param2, param1 + param2))


class MyExtendedAssetConnection(AssetConnection):

    def __init__(self):
        # If the constructor will be overridden remember to add 'super().__init__()'.
        pass

    async def configure_connection_by_aas_model(self, interface_aas_elem):
        pass

    async def check_asset_connection(self):
        pass

    async def connect_with_asset(self):
        pass

    async def execute_asset_service(self, interaction_metadata, service_input_data=None):
        print("Hi! I am a new Asset Connection that can communicate with new assets.")
        print("The given AAS element is {}".format(interaction_metadata))
        return {'status': 'OK'}

    async def receive_msg_from_asset(self):
        pass