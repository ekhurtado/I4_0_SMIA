"""This module contains utils objects and method to AAS metamodel deserialization."""
from typing import Dict

from aas_class_structure.aas import AssetInformation

# Python dictionaries for concepts mapping
# ----------------------------------------
ASSET_KIND_DICT = {
    'Type': AssetInformation.AssetKind.TYPE,
    'Instance': AssetInformation.AssetKind.INSTANCE,
    'NotApplicable': AssetInformation.AssetKind.NOT_APPLICABLE
}



# Python methods for concepts mapping
# -----------------------------------
def get_text_mapped_name(text_name, dictionary):
    """
    TODO
    :param text_name:
    :param dictionary:
    :return:
    """
    if text_name not in dictionary:
        raise ValueError(f" has invalid text: {text_name}")
    return dictionary[text_name]