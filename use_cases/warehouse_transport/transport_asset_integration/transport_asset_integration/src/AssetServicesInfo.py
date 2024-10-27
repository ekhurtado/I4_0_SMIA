class AssetServicesInfo:
    PROPERTIES_DATA = {
        "battery": {"name": "Battery of the robot", "type": 'REAL_MEASURE'},
        "location": {"name": "Location of the robot", "type": 'REAL_MEASURE'},
    }

    ACTIONS_DATA = {
        "move": {"name": "Action to move the robot to a specific point", "status": "inactive", "requires": ["coordinate"]},
        "go_home": {"name": "Action to move the robot to starting point", "status": "inactive"},
        "recharge": {"name": "Action to move the robot to charging station", "status": "inactive"},
    }
    