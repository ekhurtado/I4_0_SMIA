#!/usr/bin/env python

from aas_core import AASCore
from smia.utilities import AASArchive_utils


def main():

    # Create the AAS Core object
    aas_core = AASCore()
    # initialize_aas_archive()
    aas_core.send_status_change_to_manager('Initializing')

    # Then, the initialization tasks are performed
    aas_core.initialize_aas_core()

    # AASArchive_utils.change_status('InitializationReady')   #  Previous
    aas_core.send_status_change_to_manager('InitializationReady')

    # The AAS Core can start running
    aas_core.run_aas_core()

def initialize_aas_archive():
    """These tasks are in charge of AAS Manager, but for testing, they will be performed by the Core"""

    # First, the status file is created
    AASArchive_utils.create_status_file()

    # initial_status_info = {'name': 'AAS_Core', 'status': 'Initializing', 'timestamp': calendar.timegm(time.gmtime())}
    # f = open('/aas_archive/status/aas_core.json', 'x')
    # json.dump(initial_status_info, f)
    # f.close()

if __name__ == '__main__':
    print('AAS Core to work with ROS')
    print('AAS Core starting...')
    main()
    print('AAS ending...')

