"""File to group useful methods for accessing and managing the AAS Archive."""
import calendar
import json
import logging
import time

from src.utilities.AASarchiveInfo import AASarchiveInfo

_logger = logging.getLogger(__name__)


# ------------------------
# Methods related to files
# ------------------------
def create_status_file():
    """This method creates the status file of the AAS Manager and sets it to "initializing"."""
    initial_status_info = {'name': 'AAS_Core', 'status': 'Initializing', 'timestamp': calendar.timegm(time.gmtime())}

    # with (open(AASarchiveInfo.CORE_STATUS_FILE_PATH, 'x') as status_file):
    #     json.dump(initial_status_info, status_file)
    #     status_file.close()
    f = open(AASarchiveInfo.CORE_STATUS_FILE_PATH, 'x')
    json.dump(initial_status_info, f)
    f.close()