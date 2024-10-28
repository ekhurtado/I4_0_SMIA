from AssetServices import AssetServices


class ROSAssetIntegration:

    def __init__(self):
        self.asset_services = AssetServices()

    def get_property(self, property_name):
        return self.asset_services.get_property(property_name)

    def perform_action(self, action_name):
        return self.asset_services.perform_action(action_name)
