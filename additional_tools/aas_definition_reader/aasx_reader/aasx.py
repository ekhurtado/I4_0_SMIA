"""
Functionality for reading and writing AASX files
"""
import io
import os
from typing import IO, Union, Any, Optional

import pyecma376_2
from basyx.aas.adapter.json import read_aas_json_file
from basyx.aas.adapter.xml import read_aas_xml_file
from lxml import etree

# from xml_reader.aas_definition_reader import validate_xml_definition

xsd_path = '../AAS_metamodel.xsd'


class MyAASXReader:

    def __init__(self, file: Union[os.PathLike, str, IO]):
        """
        Open an AASX reader for the given filename or file handle

        The given file is opened as OPC ZIP package. Make sure to call ``AASXReader.close()`` after reading the file
        contents to close the underlying ZIP file reader. You may also use the AASXReader as a context manager to ensure
        closing under any circumstances.

        :param file: A filename, file path or an open file-like object in binary mode
        :raises FileNotFoundError: If the file does not exist
        :raises ValueError: If the file is not a valid OPC zip package
        """
        try:
            print("Opening {} as AASX pacakge for reading ...".format(file))
            self.reader = pyecma376_2.ZipPackageReader(file)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ValueError("{} is not a valid ECMA376-2 (OPC) file: {}".format(file, e)) from e

    def validate_xml_definition_file(self, xml_element):
        xsd_aas_schema_file = etree.parse(xsd_path)
        xsd_aas_schema = etree.XMLSchema(xsd_aas_schema_file)

        if not xsd_aas_schema.validate(xml_element):
            print("The XML definition is not valid. Reason:")
            for error in xsd_aas_schema.error_log:
                print("\t" + error.message)
                print("\tLine:", error.line)
                print("\tColumn:", error.column)
                return False
        else:
            return True

    def _parse_aas_part(self, part_name: str, **kwargs) -> {}:
        """
        Helper function to parse the AAS objects from a single JSON or XML part of the AASX package.

        This method chooses and calls the correct parser.

        :param part_name: The OPC part name of the part to be parsed
        :return: A DictObjectStore containing the parsed AAS objects
        """
        content_type = self.reader.get_content_type(part_name)
        extension = part_name.split("/")[-1].split(".")[-1]
        if content_type.split(";")[0] in ("text/xml", "application/xml") or content_type == "" and extension == "xml":
            print("Parsing AAS objects from XML stream in OPC part {} ...".format(part_name))
            with self.reader.open_part(part_name) as p:
                return read_aas_xml_file(p, **kwargs)
        elif content_type.split(";")[0] in ("text/json", "application/json") \
                or content_type == "" and extension == "json":
            print("Parsing AAS objects from JSON stream in OPC part {} ...".format(part_name))
            with self.reader.open_part(part_name) as p:
                return read_aas_json_file(io.TextIOWrapper(p, encoding='utf-8-sig'), **kwargs)
        else:
            print("Could not determine part format of AASX part {} (Content Type: {}, extension: {}"
                  .format(part_name, content_type, extension))
            return {}  # TODO esto lo he cambiado

    def _parse_xml_document(self, file: IO, failsafe: bool = True, **parser_kwargs: Any) -> Optional[etree.Element]:
        """
        Parse an XML document into an element tree

        :param file: A filename or file-like object to read the XML-serialized data from
        :param failsafe: If True, the file is parsed in a failsafe way: Instead of raising an Exception if the document
                         is malformed, parsing is aborted, an error is logged and None is returned
        :param parser_kwargs: Keyword arguments passed to the XMLParser constructor
        :return: The root element of the element tree
        """

        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, **parser_kwargs)

        try:
            return etree.parse(file, parser).getroot()
        except etree.XMLSyntaxError as e:
            if failsafe:
                print(e)
                return None
            raise e

    def save_aas_xml_definition_objects(self, part_name: str, **kwargs) -> {}:
        global_dict_object = []
        content_type = self.reader.get_content_type(part_name)
        extension = part_name.split("/")[-1].split(".")[-1]
        if content_type.split(";")[0] in ("text/xml", "application/xml") or content_type == "" and extension == "xml":
            print("Parsing AAS objects from XML stream in OPC part {} ...".format(part_name))
            with self.reader.open_part(part_name) as definition_file:
                root = self._parse_xml_document(definition_file, failsafe=True, **kwargs)
                if root is None:
                    return None

                # if not self.validate_xml_definition_file(root):   # TODO de momento quitado ya que falla con alguno
                #     print("The XML is not valid, it cannot be read.")

                # Recogemos el namespace para que las busquedas no fallen
                ns_aas = ''
                if len(list(root.nsmap.keys())) != 0:
                    ns_aas = '{' + list(root.nsmap.values())[0] + '}'
                    # ns_aas = list(root.nsmap.keys())[0] + ':' # TODO opcion B, pero habria que añadir el nsmap en todos los "find" de elementos xml

                print("Parsing AAS objects from XML definition...")
                for object_list in root:
                    if object_list.tag == '{https://admin-shell.io/aas/3/0}assetAdministrationShells':
                        print("Getting all AAS objects")
                        for aas_xml_object in object_list:
                            aas_dict_object = {'xml_object': aas_xml_object,
                                               'submodels': self.get_submodels_of_aas(ns_aas, aas_xml_object, root)
                                               }
                            global_dict_object.append(aas_dict_object)

                return global_dict_object

    def get_submodels_of_aas(self, ns_aas, aas_xml_object, root_object: etree.Element):
        dict_submodels_object = []
        submodels = aas_xml_object.find(ns_aas + "submodels")
        if submodels is not None:
            for submodel_ref in submodels:
                # First, get the reference of the submodel
                sm_ref_type = submodel_ref.find(ns_aas + "type")
                if sm_ref_type == "ExternalReference":
                    print("It cannot get the submodelo of an external reference")
                    break
                keys = submodel_ref.find(ns_aas + "keys")
                for key in keys:
                    key_value_text = self.get_xml_elem_text(key, ns_aas + "value")
                    # Once the reference is obtained, it will search the submodel xml element in all AAS definition
                    sm_xml_element = self.get_xml_element_by_id(root_object, ns_aas,
                                                                'submodels', key_value_text)
                    # The sm element is stored
                    dict_submodels_object.append({'xml_object': sm_xml_element,
                                                  'conceptDescriptions': self.get_conceptdescriptions_of_submodel(
                                                      ns_aas, sm_xml_element, root_object)})
        return dict_submodels_object

    def get_conceptdescriptions_of_submodel(self, ns_aas, sm_xml_object, root_object: etree.Element):
        dict_conceptdescriptions_object = []
        conceptdescriptions_ref = sm_xml_object.iterfind(".//" + ns_aas + "semanticId")
        for cd_ref in conceptdescriptions_ref:
            keys = cd_ref.find(ns_aas + "keys")
            for key in keys:
                key_type_text = self.get_xml_elem_text(key, ns_aas + "type")
                if key_type_text == 'ConceptDescription':
                    key_value_text = self.get_xml_elem_text(key, ns_aas + "value")
                    cd_xml_element = self.get_xml_element_by_id(root_object, ns_aas,
                                                                'conceptDescriptions', key_value_text)
                    if cd_xml_element is not None:
                        dict_conceptdescriptions_object.append(cd_xml_element)
        return dict_conceptdescriptions_object



    def get_xml_element_by_id(self, root, ns_aas, elem_type, sm_reference_id):
        submodels = root.find(ns_aas + elem_type)
        if submodels is not None:
            for submodel in submodels:
                # The id of the submodel is obtained
                sm_id_text = self.get_xml_elem_text(submodel, ns_aas + "id")
                if sm_id_text == sm_reference_id:
                    return submodel
            return None
        return None

    def get_xml_elem_text(self, xml_elem, ns_aas):
        found_element = xml_elem.find(ns_aas)
        return found_element.text if found_element is not None else None
