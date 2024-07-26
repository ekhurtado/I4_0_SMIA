"""This module contains utils objects and method to AAS metamodel deserialization."""
from typing import Dict

from aas_class_structure import common,submodel
from aas_class_structure.aas import AssetInformation

# Python dictionaries for concepts mapping
# ----------------------------------------
ASSET_KIND_DICT = {
    'Type': AssetInformation.AssetKind.TYPE,
    'Instance': AssetInformation.AssetKind.INSTANCE,
    'NotApplicable': AssetInformation.AssetKind.NOT_APPLICABLE
}

ENTITY_TYPE_DICT = {
    'CoManagedEntity': submodel.Entity.EntityType.CO_MANAGED_ENTITY,
    'SelfManagedEntity': submodel.Entity.EntityType.SELF_MANAGED_ENTITY
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


# Python methods for XML reading
# ------------------------------
def get_xml_elem_text(xml_elem, tag, xml_ns):
    """
    # TODO
    :param xml_elem:
    :param tag:
    :param xml_ns:
    :return:
    """
    found_element = xml_elem.find(xml_ns + tag, xml_elem.nsmap)
    return found_element.text if found_element is not None else None


def get_elem_description(xml_elem, xml_ns):
    sm_description_elem = xml_elem.find(xml_ns + "description", xml_elem.nsmap)
    if sm_description_elem is not None:
        sm_description = get_xml_elem_text(sm_description_elem.find(xml_ns + "langStringTextType", xml_elem.nsmap),
                                           "text", xml_ns)
    else:
        sm_description = None
    return sm_description


def get_elem_administration(xml_elem, xml_ns):
    sm_admin_elem = xml_elem.find(xml_ns + "administration", xml_elem.nsmap)
    if sm_admin_elem is not None:
        sm_admin_version = get_xml_elem_text(sm_admin_elem, "version", xml_ns)
        sm_admin_revision = get_xml_elem_text(sm_admin_elem, "revision", xml_ns)
        sm_administration = common.Identifiable.AdministrativeInformation(revision=sm_admin_revision,
                                                                          version=sm_admin_version)
    else:
        sm_administration = None
    return sm_administration


def get_elem_reference_text(xml_elem, tag,xml_ns):
    semantic_id_elem = xml_elem.find(xml_ns + tag, xml_elem.nsmap)
    if semantic_id_elem is not None:
        keys_elem = semantic_id_elem.find(xml_ns + "keys", semantic_id_elem.nsmap)
        semantic_id = get_xml_elem_text(keys_elem.find(xml_ns + "key", keys_elem.nsmap), "value", xml_ns)
    else:
        semantic_id = None
    return semantic_id


def get_elem_qualifiers(xml_elem, xml_ns):
    # TODO
    return None

