import random

from AssetServicesInfo import AssetServicesInfo


class AssetServices:

    def __init__(self):
        self.properties = AssetServicesInfo.PROPERTIES_DATA
        self.actions = AssetServicesInfo.ACTIONS_DATA
        self.battery = 100
        self.location = '-1.65,-0.56'   # starting coordinate of the robot

    def get_battery(self):
        self.battery = random.uniform(0.0, 100.0)
        return self.battery

    def get_property(self, property_name):
        match property_name:
            case 'battery':
                return self.get_battery()
            case 'location':
                return self.location
            case _:
                print("This property does not exist.")
                return None

    def perform_action(self, action_name):
        # TODO
        pass


