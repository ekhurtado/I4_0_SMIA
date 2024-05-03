# ------------------------
# Methods related to files
# ------------------------
import configparser
import os

from lxml import etree

configMap_path = "/aas_archive/config"
submodels_path = "/aas_archive/submodels"

# ------------------------
# Methods related to files
# ------------------------
def createSubModels():

    # Create folder to save submodels
    os.mkdir(submodels_path)

    # Read submodels configuration
    configSM = configparser.RawConfigParser()
    configSM.read(configMap_path + '/submodels.properties')
    print(configSM.sections())
    for section in configSM.sections():
        match section:
            case "technical-data-submodel":
                createTechnicalDataSM(configSM.items(section))
            case "configuration-submodel":
                createConfigurationSM(configSM.items(section))
            case _:
                print("Submodel not found")
                break

def XMLToFile(filePath, XML_content):
    # Write the content of submodel in a file
    with open(filePath, 'wb') as sm_file:
        sm_file.write(XML_content)

# -------------------------------------
# Methods related to specific submodels
# -------------------------------------
def createTechnicalDataSM(submodelData):
    # Generate the XML of the submodel
    submodel_XML_content = etree.Element("submodel", name="technical_data_submodel")
    technicalData_level = etree.SubElement(submodel_XML_content, "technical_data")

    # Add data to XML
    for (key, val) in submodelData:
        print(key + ": " + val)
        # etree.SubElement(technicalData_level, key)
        etree.SubElement(technicalData_level, key).text = val

    # Write the content of submodel in a file
    XMLToFile(submodels_path + '/Technical_data_SM.xml', etree.tostring(submodel_XML_content))


def createConfigurationSM(submodelData):
    # Generate the XML of the submodel
    submodel_XML_content = etree.Element("submodel", name="configuration_submodel")
    configuration_level = etree.SubElement(submodel_XML_content, "configuration")

    # Add data to XML
    for (key, val) in submodelData:
        print(key + ": " + val)
        # etree.SubElement(technicalData_level, key)
        etree.SubElement(configuration_level, key).text = val

    # Write the content of submodel in a file
    XMLToFile(submodels_path + '/Configuration_SM.xml', etree.tostring(submodel_XML_content))