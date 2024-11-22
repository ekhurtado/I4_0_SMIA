import calendar
import logging
import time

from spade.message import Message
from spade.template import Template

from utilities.aas_general_info import SMIAGeneralInfo


class GeneralUtils:
    """
    This class contains some general utils to ben used by any module.
    """

    @staticmethod
    def configure_logging():
        """
        This method configures the logging to be used by all modules. It specifies different colors to improve the
        readability of the console and adds new levels to the printouts related to ACL and interaction messages.
        """

        interaction_level_num = 35
        logging.addLevelName(interaction_level_num, "INTERACTIONINFO")

        fipa_acl_level_num = 36
        logging.addLevelName(fipa_acl_level_num, "ACLINFO")

        def interactioninfo(self, message, *args, **kwargs):
            if self.isEnabledFor(interaction_level_num):
                self._log(interaction_level_num, message, args, **kwargs)

        logging.Logger.interactioninfo = interactioninfo  # TODO HACER AHORA: CAMBIARLO POR 'assetinfo'

        def aclinfo(self, message, *args, **kwargs):
            if self.isEnabledFor(fipa_acl_level_num):
                self._log(fipa_acl_level_num, message, args, **kwargs)

        logging.Logger.aclinfo = aclinfo

        handler = logging.StreamHandler()
        formatter = GeneralUtils.ColoredFormatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger('').addHandler(handler)
        logging.getLogger('').setLevel(logging.INFO)  # Set the default logging level

        # Create a file handler
        file_handler = logging.FileHandler(SMIAGeneralInfo.LOG_FOLDER_PATH + '/' + SMIAGeneralInfo.SMIA_LOG_FILENAME)
        file_handler.setFormatter(logging.Formatter(GeneralUtils.ColoredFormatter.FORMAT_COMPLEX))
        logging.getLogger('').addHandler(file_handler)

    class ColoredFormatter(logging.Formatter):
        """
        This class contains the format of all the levels of the logging, including the color of each of them.
        """
        FORMAT_SIMPLE = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
        FORMAT_COMPLEX = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s line:%(lineno)d"
        RESET = '\x1b[0m'

        COLORS = {
            logging.DEBUG: '\x1b[94m' + FORMAT_SIMPLE + RESET,  # Blue
            logging.INFO: '\x1b[39;20m' + FORMAT_SIMPLE + RESET,  # White
            logging.WARNING: '\x1b[93m' + FORMAT_COMPLEX + RESET,  # Yellow
            logging.ERROR: '\x1b[91m' + FORMAT_COMPLEX + RESET,  # Red
            logging.CRITICAL: '\x1b[41m' + FORMAT_COMPLEX + RESET,  # White on Red
            35: '\x1b[38;2;255;150;20m' + FORMAT_SIMPLE + RESET,  # Purple (for the interaction level)
            36: '\x1b[38;2;0;255;255m' + FORMAT_SIMPLE + RESET  # Cyan (for the FIP-ACL level)
        }

        def format(self, record):
            log_fmt = self.COLORS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    @staticmethod
    def print_smia_banner():
        # The banner for the SMIA is set as string, avoiding installing 'art' library (which has been used to create it)
        banner_str = ("---------------------------------------------\n" +
                      "  ______    ____    ____   _____        _\n" +
                      ".' ____ \  |_   \  /   _| |_   _|      / \      \n" +
                      "| (___ \_|   |   \/   |     | |       / _ \     \n" +
                      " _.____`.    | |\  /| |     | |      / ___ \    \n" +
                      "| \____) |  _| |_\/_| |_   _| |_   _/ /   \ \_  \n" +
                      " \______.' |_____||_____| |_____| |____| |____| \n" +
                      # "                                                \n" +
                      "---------------------------------------------\n" +
                      "                                      v0.2.0 \n" +
                      "---------------------------------------------\n")
        print(banner_str)

    @staticmethod
    def create_acl_template(performative, ontology):
        """
        This method creates a template aligned with FIPA-ACL standard.

        Args:
            performative(str): The performative of the template.
            ontology(str): The ontology of the template.

        Returns:
            spade.template.Template: a SPADE template object.
        """
        custom_template = Template()
        custom_template.set_metadata('performative', performative)
        custom_template.set_metadata('ontology', ontology)
        return custom_template

    @staticmethod
    def create_acl_msg(receiver, thread, performative, ontology, body):
        """
        This method creates an FIPA-ACL message.

        Args:
            receiver (str): The SPADE agent receiver of the ACL message.
            thread (str): The thread of the ACL message.:
            performative (str): The performative of the ACL message.
            ontology (str): The ontology of the ACL message.
            body: The body of the ACL message.

        Returns:
            spade.message.Message: SPADE message object FIPA-ACL-compliant.
        """
        msg = Message(to=receiver, thread=thread)
        msg.set_metadata('performative', performative)
        msg.set_metadata('ontology', ontology)

        msg.body = body  # TODO Pensar si iria tambien en metadatos o todo en el body
        return msg

    @staticmethod
    def get_sender_from_acl_msg(acl_msg):
        """
        This method returns the identifier of an agent from an ACL message, considering the suffixes that can be added
        by the XMPP server.

        Args:
            acl_msg (spade.message.Message): ACL message object.

        Returns:
            str: identifier of the sender of the message.
        """
        if '/' in str(acl_msg.sender):  # XMPP server can add a random string to differentiate the agent JID
            return str(acl_msg.sender).split('/')[0]
        else:
            return str(acl_msg.sender)

    @staticmethod
    def get_current_timestamp():
        """
        This method returns the current timestamp of the AAS Manager.

        Returns:
            int: current timestamp in milliseconds
        """
        return calendar.timegm(time.gmtime())
