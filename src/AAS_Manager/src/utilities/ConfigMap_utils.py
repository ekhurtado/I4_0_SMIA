"""This file contains utility methods related to the ConfigMap file"""
import configparser
from AASarchive import AASarchive

# ----------------------------
# Methods related to submodels
# ----------------------------
def getSubModelNames():
    # Read submodels configuration
    configSM = configparser.RawConfigParser()
    configSM.read(AASarchive.configMapPath + '/' + AASarchive.cmSMPropertiesFileName)

    return configSM.sections()

def getSubModelInformation(submodelName):
    # Read submodels configuration
    configSM = configparser.RawConfigParser()
    configSM.read(AASarchive.configMapPath + '/' + AASarchive.cmSMPropertiesFileName)

    return configSM.items(submodelName)