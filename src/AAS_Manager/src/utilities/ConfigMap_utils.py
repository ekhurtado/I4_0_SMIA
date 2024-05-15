"""This file contains utility methods related to the ConfigMap file"""
import configparser
from utilities.AASarchiveInfo import AASarchiveInfo

# ----------------------------
# Methods related to submodels
# ----------------------------
def getSubModelNames():
    # Read submodels configuration
    configSM = configparser.RawConfigParser()
    configSM.read(AASarchiveInfo.configMapPath + '/' + AASarchiveInfo.cmSMPropertiesFileName)

    return configSM.sections()

def getSubModelInformation(submodelName):
    # Read submodels configuration
    configSM = configparser.RawConfigParser()
    configSM.read(AASarchiveInfo.configMapPath + '/' + AASarchiveInfo.cmSMPropertiesFileName)

    return configSM.items(submodelName)