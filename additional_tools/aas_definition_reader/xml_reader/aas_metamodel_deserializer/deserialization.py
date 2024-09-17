"""
This module contains useful methods for deserializing the AAS meta-model from XML.
"""
from lxml import etree

from . import utils
from aas_class_structure import aas, submodel


def deserialize_aas(xml_elem, xml_ns, asset_info, sm_list):
    """
    This method deserializes an AAS element of an XML definition into an AAS Python object. This object, and those
    within it, are developed following the AAS meta-model, as well as the XML definition.
    :param xml_elem: the xml element of the lxml library.
    :param xml_ns: the namespace of the XML definition.
    :param asset_info: the asset information Python object.
    :param sm_list: the list of submodels as Python objects.
    :return: the AAS in the form of a Python object.
    """

    aas_id_short = utils.get_xml_elem_text(xml_elem, "idShort", xml_ns)
    aas_id = utils.get_xml_elem_text(xml_elem, "id", xml_ns)
    aas_description = utils.get_elem_description(xml_elem, xml_ns)
    aas_administration = utils.get_elem_administration(xml_elem, xml_ns)
    aas_derived_from = utils.get_elem_reference_text(xml_elem, "derivedFrom", xml_ns)
    aas_display_name = aas_id_short  # TODO (for now same as idShort)
    aas_category = utils.get_xml_elem_text(xml_elem, "category", xml_ns)
    aas_embedded_data_specification = utils.get_elem_reference_text(xml_elem, "embeddedDataSpecification", xml_ns)
    aas_extension = None  # TODO

    # TODO DUDA: Miramos las referencias de submodelos dentro de la lista de submodelos generales definidos en el
    #  modelo de AAS?

    return aas.AssetAdministrationShell(id_=aas_id,
                                        asset_information=asset_info,
                                        id_short=aas_id_short,
                                        display_name=aas_display_name,
                                        category=aas_category,
                                        description=aas_description,
                                        administration=aas_administration,
                                        derived_from=aas_derived_from,
                                        submodel=sm_list,
                                        embedded_data_specifications=aas_embedded_data_specification,
                                        extension=aas_extension
                                        )


def deserialize_asset_information(xml_elem, xml_ns):
    """
    This method deserializes an asset information element of an XML definition into an AAS Python object. This object,
    is developed following the AAS meta-model, as well as the XML definition.
    :param xml_elem: the xml element of lxml library.
    :param xml_ns: the namespace of the XML definition.
    :return: the asset information in the form of a Python object.
    """

    asset_kind_name = utils.get_xml_elem_text(xml_elem, "assetKind", xml_ns)
    asset_kind = utils.get_text_mapped_name(asset_kind_name, utils.ASSET_KIND_DICT)
    global_asset_id = utils.get_xml_elem_text(xml_elem, "globalAssetId", xml_ns)
    asset_type_name = utils.get_xml_elem_text(xml_elem, "assetType", xml_ns)
    asset_type = utils.get_text_mapped_name(asset_type_name, utils.ASSET_TYPE_DICT)

    # TODO

    return aas.AssetInformation(asset_kind=asset_kind,
                                global_asset_id=global_asset_id,
                                asset_type=asset_type,
                                # TODO
                                )


def deserialize_submodel(xml_elem, xml_ns):
    """
    This method deserializes a Submodel element of an XML definition into an AAS Python object. This object, and those
    within it, are developed following the AAS meta-model, as well as the XML definition.
    :param xml_elem: the xml element of lxml library.
    :param xml_ns: the namespace of the XML definition.
    :return: the Submodel in the form of a Python object.
    """
    sm_id = utils.get_xml_elem_text(xml_elem, "id", xml_ns)
    sm_kind_name = utils.get_xml_elem_text(xml_elem, "kind", xml_ns)
    sm_kind = utils.get_text_mapped_name(sm_kind_name, utils.MODELING_KIND_DICT)
    sm_id_short = utils.get_xml_elem_text(xml_elem, "idShort", xml_ns)

    sm_description = utils.get_elem_description(xml_elem, xml_ns)
    sm_administration = utils.get_elem_administration(xml_elem, xml_ns)
    semantic_id = utils.get_elem_reference_text(xml_elem, "semanticId", xml_ns)

    sm_element_list = xml_elem.find(xml_ns + "submodelElements", xml_elem.nsmap)
    sm_elements: set[submodel.SubmodelElement] = set()
    if sm_element_list is not None:
        for sm_elem in sm_element_list:
            sm_elem_obj = deserialize_submodel_element(sm_elem, xml_ns)
            if sm_elem_obj is not None:
                sm_elements.add(sm_elem_obj)

    return submodel.Submodel(id_=sm_id,
                             submodel_element=sm_elements,
                             id_short=sm_id_short,
                             description=sm_description,
                             administration=sm_administration,
                             semantic_id=semantic_id, kind=sm_kind,
                             # TODO (no estan todos)
                             )


def deserialize_submodel_element(xml_elem, xml_ns):
    """
    This method deserializes a Submodel Element of an XML definition into an AAS Python object. This object, and those
    within it, are developed following the AAS meta-model, as well as the XML definition.
    :param xml_elem: the xml element of lxml library.
    :param xml_ns: the namespace of the XML definition.
    :return: the Submodel Element in the form of a Python object.
    """
    # First, we get the attributes that all Submodel Elements share
    sm_id_short = utils.get_xml_elem_text(xml_elem, "idShort", xml_ns)
    display_name_elem = sm_id_short  # TODO (for now same as idShort)
    description = utils.get_elem_description(xml_elem, xml_ns)
    semantic_id = utils.get_elem_reference_text(xml_elem, "semanticId", xml_ns)
    qualifiers = utils.get_elem_qualifiers(xml_elem, xml_ns)

    sm_elem_type = etree.QName(xml_elem).localname  # The element type is in the tag

    match sm_elem_type:
        case "dataElement":
            pass
        case "property":
            value_type = utils.get_xml_elem_text(xml_elem, "valueType", xml_ns)
            value = utils.get_xml_elem_text(xml_elem, "value", xml_ns)
            value_id = utils.get_elem_reference_text(xml_elem, "valueId", xml_ns)

            return submodel.Property(id_short=sm_id_short,
                                     value_type=value_type,
                                     value=value,
                                     value_id=value_id,
                                     display_name=display_name_elem,
                                     description=description,
                                     semantic_id=semantic_id,
                                     qualifier=qualifiers,
                                     # TODO (no estan todos)
                                     )
        case "range":
            value_type = utils.get_xml_elem_text(xml_elem, "valueType", xml_ns)
            min_ = utils.get_xml_elem_text(xml_elem, "min", xml_ns)
            max_ = utils.get_xml_elem_text(xml_elem, "max", xml_ns)

            return submodel.Range(id_short=sm_id_short,
                                  value_type=value_type,
                                  min_=min_,
                                  max_=max_,
                                  display_name=display_name_elem,
                                  description=description,
                                  semantic_id=semantic_id,
                                  qualifier=qualifiers,
                                  # TODO (no estan todos)
                                  )
        case "blob":
            value_type = utils.get_xml_elem_text(xml_elem, "valueType", xml_ns)
            content_type = utils.get_xml_elem_text(xml_elem, "contentType", xml_ns)

            return submodel.Blob(id_short=sm_id_short,
                                 value_type=value_type,
                                 content_type=content_type,
                                 display_name=display_name_elem,
                                 description=description,
                                 semantic_id=semantic_id,
                                 qualifier=qualifiers,
                                 # TODO (no estan todos)
                                 )
        case "file":
            value = utils.get_xml_elem_text(xml_elem, "value", xml_ns)
            content_type = utils.get_xml_elem_text(xml_elem, "contentType", xml_ns)

            return submodel.File(id_short=sm_id_short,
                                 value_=value,
                                 content_type=content_type,
                                 display_name=display_name_elem,
                                 description=description,
                                 semantic_id=semantic_id,
                                 qualifier=qualifiers,
                                 # TODO (no estan todos)
                                 )
        case "referenceElement":  # TODO, repasarlo porque tiene miga
            value = utils.get_elem_reference_text(xml_elem, "value", xml_ns)

            return submodel.ReferenceElement(id_short=sm_id_short,
                                             value_=value,
                                             display_name=display_name_elem,
                                             description=description,
                                             semantic_id=semantic_id,
                                             qualifier=qualifiers,
                                             # TODO (no estan todos)
                                             )
        case "submodelElementList":
            category = utils.get_xml_elem_text(xml_elem, "category", xml_ns)
            semantic_id_list_elem = utils.get_elem_reference_text(xml_elem, "semanticIdListElement", xml_ns)
            order_relevant_elem = utils.get_xml_elem_text(xml_elem, "orderRelevant", xml_ns)
            order_relevant = order_relevant_elem in ("true", "1")
            type_value_element = utils.get_xml_elem_text(xml_elem, "typeValueListElement", xml_ns)
            value_type_element = utils.get_xml_elem_text(xml_elem, "valueTypeListElement", xml_ns)

            # Get all the elements from the list
            value_elem = xml_elem.find(xml_ns + "value", xml_elem.nsmap)
            all_value_elems: set[submodel.SubmodelElement] = set()
            for sm_elem_list_value in value_elem:
                sm_elem_obj = deserialize_submodel_element(sm_elem_list_value, xml_ns)
                if sm_elem_obj is not None:  # TODO revisarlo (no se leen todos los tipos de SM Elements)
                    all_value_elems.add(sm_elem_obj)

            return submodel.SubmodelElementList(id_short=sm_id_short,
                                                order_relevant=order_relevant,
                                                semantic_id_list_element=semantic_id_list_elem,
                                                type_value_list_element=type_value_element,
                                                value_type_list_element=value_type_element,
                                                value_=all_value_elems,
                                                display_name=display_name_elem,
                                                category=category,
                                                description=description,
                                                semantic_id=semantic_id,
                                                qualifier=qualifiers,
                                                # TODO (no estan todos)
                                                )

        case "submodelElementCollection":
            category = utils.get_xml_elem_text(xml_elem, "category", xml_ns)

            # Get all the elements from the list
            value_elem = xml_elem.find(xml_ns + "value", xml_elem.nsmap)
            all_value_elems: set[submodel.SubmodelElement] = set()
            if value_elem is not None:
                for sm_elem_list_value in value_elem:
                    sm_elem_obj = deserialize_submodel_element(sm_elem_list_value, xml_ns)
                    if sm_elem_obj is not None:  # TODO revisarlo (no se leen todos los tipos de SM Elements)
                        all_value_elems.add(sm_elem_obj)

            return submodel.SubmodelElementCollection(id_short=sm_id_short,
                                                      value_=all_value_elems,
                                                      display_name=display_name_elem,
                                                      category=category,
                                                      description=description,
                                                      semantic_id=semantic_id,
                                                      qualifier=qualifiers,
                                                      # TODO (no estan todos)
                                                      )
        case "entity":
            entity_type_name = utils.get_xml_elem_text(xml_elem, "entityType", xml_ns)
            entity_type = utils.get_text_mapped_name(entity_type_name, utils.ENTITY_TYPE_DICT)
            global_asset_id = utils.get_xml_elem_text(xml_elem, "globalAssetId", xml_ns)
            specific_asset_id = None  # TODO

            statement = None  # TODO

            return submodel.Entity(id_short=sm_id_short,
                                   entity_type=entity_type,
                                   statement=statement,
                                   global_asset_id=global_asset_id,
                                   specific_asset_id=specific_asset_id,

                                   display_name=display_name_elem,
                                   description=description,
                                   semantic_id=semantic_id,
                                   qualifier=qualifiers,
                                   # TODO (no estan todos)
                                   )
        case "operation":
            input_variable = None  # TODO
            output_variable = None  # TODO
            inoutput_variable = None  # TODO

            return submodel.Operation(id_short=sm_id_short,
                                      input_variable=input_variable,
                                      output_variable=output_variable,
                                      inoutput_variable=inoutput_variable,
                                      display_name=display_name_elem,
                                      description=description,
                                      semantic_id=semantic_id,
                                      qualifier=qualifiers,
                                      # TODO (no estan todos)
                                      )
        case "relationshipElement":
            first = utils.get_elem_reference_text(xml_elem, "first", xml_ns)
            second = utils.get_elem_reference_text(xml_elem, "second", xml_ns)

            return submodel.RelationshipElement(id_short=sm_id_short,
                                                first=first,
                                                second=second,
                                                display_name=display_name_elem,
                                                description=description,
                                                semantic_id=semantic_id,
                                                qualifier=qualifiers,
                                                # TODO (no estan todos)
                                                )
        case _:
            return None


def get_submodel_references(xml_elem, xml_ns):
    """
    This method gets the Submodel references, as established in the AAS meta-model.
    :param xml_elem: the xml element of lxml library.
    :param xml_ns: the namespace of the XML definition.
    :return: the references to the submodels.
    """
    sm_references_dict = []
    for ref_elem in xml_elem:
        reference_type = ref_elem.find(xml_ns + "type", ref_elem.nsmap).text
        keys_elem = ref_elem.find(xml_ns + "keys", ref_elem.nsmap)
        key_elem = keys_elem.find(xml_ns + "key", keys_elem.nsmap)
        value = key_elem.find(xml_ns + "value", key_elem.nsmap).text
        sm_references_dict.append({reference_type, value})
    return sm_references_dict
