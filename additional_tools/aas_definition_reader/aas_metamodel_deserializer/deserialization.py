"""
This module contains useful methods for deserializing the AAS meta-model from XML.
"""
from .utils import get_text_mapped_name, ASSET_KIND_DICT
from aas_class_structure import aas,common,submodel

def deserialize_asset_information(xml_elem, xml_ns):
    """
    TODO
    :param xml_elem:
    :param xml_ns:
    :return:
    """

    asset_kind_name = xml_elem.find(xml_ns + "assetKind", xml_elem.nsmap).text
    asset_kind = get_text_mapped_name(asset_kind_name, ASSET_KIND_DICT)

    global_asset_id = xml_elem.find(xml_ns + "globalAssetId", xml_elem.nsmap).text

    # TODO

    return aas.AssetInformation(asset_kind=asset_kind, global_asset_id=global_asset_id)


def deserialize_submodel(xml_elem, xml_ns):
    """
    TODO
    :param xml_elem:
    :param xml_ns:
    :return:
    """
    sm_id = xml_elem.find(xml_ns + "id", xml_elem.nsmap).text
    sm_kind = xml_elem.find(xml_ns + "kind", xml_elem.nsmap).text
    sm_id_short = xml_elem.find(xml_ns + "idShort", xml_elem.nsmap).text

    sm_description_elem = xml_elem.find(xml_ns + "description", xml_elem.nsmap)
    sm_description = sm_description_elem.find(xml_ns + "langStringTextType", xml_elem.nsmap).find(xml_ns + "text", xml_elem.nsmap).text

    sm_admin_elem = xml_elem.find(xml_ns + "administration", xml_elem.nsmap)
    sm_admin_version = sm_admin_elem.find(xml_ns + "version", xml_elem.nsmap).text
    sm_admin_revision = sm_admin_elem.find(xml_ns + "revision", xml_elem.nsmap).text
    sm_administration = common.Identifiable.AdministrativeInformation(revision=sm_admin_revision, version=sm_admin_version)

    semantic_id_elem = xml_elem.find(xml_ns + "semanticId", xml_elem.nsmap)
    keys_elem = semantic_id_elem.find(xml_ns + "keys", semantic_id_elem.nsmap)
    semantic_id = keys_elem.find(xml_ns + "key", keys_elem.nsmap).find(xml_ns + "value", keys_elem.nsmap).text

    sm_element_list = xml_elem.find(xml_ns + "submodelElements", xml_elem.nsmap)
    sm_elements: set[submodel.SubmodelElement] = set()
    for sm_elem in sm_element_list:
        sm__elem_obj = deserialize_submodel_element(sm_elem, xml_ns)
        sm_elements.add(sm__elem_obj)

    return submodel.Submodel(id_=sm_id,
                             submodel_element=sm_elements,
                             id_short=sm_id_short,
                             description=sm_description,
                             administration=sm_administration,
                             semantic_id=semantic_id,kind=sm_kind,
                             # TODO
                             )


def deserialize_submodel_element(xml_elem, xml_ns):
    """
    TODO
    :param xml_elem:
    :param xml_ns:
    :return:
    """
    # TODO
    print("TODO")

def get_submodel_references(xml_elem, xml_ns):
    """
    TODO
    :param xml_elem:
    :param xml_ns:
    :return:
    """
    sm_references_dict = []
    for ref_elem in xml_elem:
        reference_type = ref_elem.find(xml_ns + "type", ref_elem.nsmap).text
        keys_elem = ref_elem.find(xml_ns + "keys", ref_elem.nsmap)
        key_elem = keys_elem.find(xml_ns + "key", keys_elem.nsmap)
        value = key_elem.find(xml_ns + "value", key_elem.nsmap).text
        sm_references_dict.append({reference_type, value})
    return sm_references_dict