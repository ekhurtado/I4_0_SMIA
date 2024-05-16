"""This file contains utility methods related to submodels"""

import os
from lxml import etree

from utilities import AAS_Archive_utils, ConfigMap_utils
from utilities.AASarchiveInfo import AASarchiveInfo

# ------------------------
# Methods related to files
# ------------------------
def createSubModelFolder():
    """Create folder to save submodels"""
    os.mkdir(AASarchiveInfo.subModelFolderPath)


def createSubModelFiles(subModelNamesList):
    """This method creates all the files associated to the selected submodels."""
    for submodelName in subModelNamesList:
        # Get the submodel information from ConfigMap
        submodelData = ConfigMap_utils.getSubModelInformation(submodelName)

        match submodelName:
            case "technical-data-submodel":
                createTechnicalDataSM(submodelData)
            case "configuration-submodel":
                createConfigurationSM(submodelData)
            case _:
                print("Submodel not found")
                break


# -------------------------------------
# Methods related to specific submodels
# -------------------------------------
def createTechnicalDataSM(submodelData):
    """This method creates the 'Technical Data' submodel XML file."""

    # Generate the XML of the submodel
    submodel_XML_content = etree.Element("submodel", name="technical_data_submodel")
    technicalData_level = etree.SubElement(submodel_XML_content, "technical_data")

    # Add data to XML
    for (key, val) in submodelData:
        print(key + ": " + val)
        etree.SubElement(technicalData_level, key).text = val

    # Write the content of submodel in a file
    AAS_Archive_utils.XMLToFile(AASarchiveInfo.subModelFolderPath + '/' + AASarchiveInfo.technicalDataSMFileName,
                                etree.tostring(submodel_XML_content))


def createConfigurationSM(submodelData):
    """This method creates the 'Configuration' submodel XML file."""

    # Generate the XML of the submodel
    submodel_XML_content = etree.Element("submodel", name="configuration_submodel")
    configuration_level = etree.SubElement(submodel_XML_content, "configuration")

    # Add data to XML
    for (key, val) in submodelData:
        print(key + ": " + val)
        etree.SubElement(configuration_level, key).text = val

    # Write the content of submodel in a file
    AAS_Archive_utils.XMLToFile(AASarchiveInfo.subModelFolderPath + '/' + AASarchiveInfo.configurationSMFileName,
                                etree.tostring(submodel_XML_content))
