from tkinter import Tk
from tkinter.filedialog import askopenfilename

import pyecma376_2
from lxml import etree

from aasx_reader.aasx import MyAASXReader
from aasx_reader.aasx_utils import AASXRelationshipTypes
from xml_reader.aas_metamodel_deserializer import deserialization

xsd_path = '../AAS_metamodel.xsd'


def main():
    # Se leera un modelo AAS encapsulado en AASX
    # Para leer los archivos, usaremos una interfaz visual
    aasx_file_path = get_aasx_file_path()

    # Una vez logrado el path al archivo AASX, podremos leerlo
    read_aasx_file(aasx_file_path)

    # validate_xml_definition(aasx_file_path)
    # print("Successful validation of the AAS XML model")
    #
    # # Ya podemos pasar a leer el modelo XML de la definicion de AAS
    # read_xml_definition(aasx_file_path)


def get_aasx_file_path():
    print("To enter the AASX file, select the file:")
    window = Tk()
    window.lift()
    window.attributes("-topmost", True)  # Leihoa pantailan erakusteko
    window.after_idle(window.attributes, '-topmost', False)
    Tk().withdraw()
    aasx_file = askopenfilename(filetypes=[("AASX files", "*.aasx")], title="Choose the AASX file")
    window.destroy()
    return aasx_file


def read_aasx_file(aasx_file_path):
    aasx_reader = MyAASXReader(aasx_file_path)
    print("The reader object for the AASX is created.")

    # First, we have to find the AASX-Origin part (using ZipPackageReader reader of pyecma376_2)
    core_rels = aasx_reader.reader.get_related_parts_by_type()
    if AASXRelationshipTypes.RELATIONSHIP_TYPE_AASX_ORIGIN in core_rels:
        aasx_origin_part = core_rels[AASXRelationshipTypes.RELATIONSHIP_TYPE_AASX_ORIGIN][0]
        aasx_reader.RELATIONSHIP_TYPE_AASX_ORIGIN = AASXRelationshipTypes.RELATIONSHIP_TYPE_AASX_ORIGIN
        aasx_reader.RELATIONSHIP_TYPE_AAS_SPEC = AASXRelationshipTypes.RELATIONSHIP_TYPE_AAS_SPEC
        aasx_reader.RELATIONSHIP_TYPE_AAS_SPEC_SPLIT = AASXRelationshipTypes.RELATIONSHIP_TYPE_AAS_SPEC_SPLIT
        aasx_reader.RELATIONSHIP_TYPE_AAS_SUPL = AASXRelationshipTypes.RELATIONSHIP_TYPE_AAS_SUPL
    elif AASXRelationshipTypes.RELATIONSHIP_TYPE_AASX_ORIGIN_PE in core_rels:
        aasx_origin_part = core_rels[AASXRelationshipTypes.RELATIONSHIP_TYPE_AASX_ORIGIN_PE][0]
        aasx_reader.RELATIONSHIP_TYPE_AASX_ORIGIN = AASXRelationshipTypes.RELATIONSHIP_TYPE_AASX_ORIGIN_PE
        aasx_reader.RELATIONSHIP_TYPE_AAS_SPEC = AASXRelationshipTypes.RELATIONSHIP_TYPE_AAS_SPEC_PE
        aasx_reader.RELATIONSHIP_TYPE_AAS_SPEC_SPLIT = AASXRelationshipTypes.RELATIONSHIP_TYPE_AAS_SPEC_SPLIT_PE
        aasx_reader.RELATIONSHIP_TYPE_AAS_SUPL = AASXRelationshipTypes.RELATIONSHIP_TYPE_AAS_SUPL_PE
    else:
        raise ValueError("Not a valid AASX file: aasx-origin Relationship is missing.") from e

    read_identifiables = set()

    # Iterate AAS files
    for aas_part in aasx_reader.reader.get_related_parts_by_type(aasx_origin_part)[aasx_reader.RELATIONSHIP_TYPE_AAS_SPEC]:
        # TODO, con el aas_part ya tenemos el archivo de definicion del AAS, ahora hay que hacer un programa que lea
        #  los submodelos y deje elegir cual se quiere lograr. De momento esta la lectura de la definicion del AAS de
        #  Basyx
        aas_part_object = aasx_reader._parse_aas_part(aas_part)
        print(aas_part_object)


def get_aasx_reader(file):
    try:
        print("Opening {} as AASX pacakge for reading ...".format(file))
        reader = pyecma376_2.ZipPackageReader(file)
        return reader
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError("{} is not a valid ECMA376-2 (OPC) file: {}".format(file, e)) from e


def validate_xml_definition(aas_xml_definition_str):
    # Para validarlo, utilizaremos el paquete lxml de Python
    # Primero, leemos el schema oficial de AAS (meta-modelo)
    xsd_aas_schema_file = etree.parse(xsd_path)
    xsd_aas_schema = etree.XMLSchema(xsd_aas_schema_file)

    aas_xml_bytes = aas_xml_definition_str.encode('utf-8')  # fromstring cannot handle strings with an encoding
    # declaration when the string is already a Unicode string,
    # it has to encode to bytes
    aas_xml_definition = etree.fromstring(aas_xml_bytes)

    # Validamos el XML contra el XSD oficial de AASs
    is_valid = xsd_aas_schema.validate(aas_xml_definition)

    if not is_valid:
        print("The XML definition is not valid. Reason:")
        for error in xsd_aas_schema.error_log:
            print("\t" + error.message)
            print("\tLine:", error.line)
            print("\tColumn:", error.column)
            exit()  # exit the program


def read_xml_definition(aas_xml_definition_str):
    # Primero, parseamos el string XML a objeto en Python
    aas_xml_bytes = aas_xml_definition_str.encode('utf-8')  # fromstring cannot handle strings with an encoding
    aas_xml_env_definition = etree.fromstring(aas_xml_bytes)

    # Recogemos el namespace para que las busquedas no fallen
    xml_ns = ''
    if list(aas_xml_env_definition.nsmap.keys())[0] is not None:
        xml_ns = list(aas_xml_env_definition.nsmap.keys())[0] + ':'

    if aas_xml_env_definition is None:
        print("XML not valid")
        exit()
    else:
        # En este caso ya podemos empezar a leer el XML
        print("XML definition is valid. Starting reading...")
        # AAS related global information
        aas_list_elem = aas_xml_env_definition.find(xml_ns + "assetAdministrationShells", aas_xml_env_definition.nsmap)
        aas_elem = aas_list_elem.find(xml_ns + "assetAdministrationShell", aas_list_elem.nsmap)

        asset_information_elem = aas_elem.find(xml_ns + "assetInformation", aas_elem.nsmap)
        asset_information_obj = deserialization.deserialize_asset_information(asset_information_elem, xml_ns)

        # Submodel related reference information
        sm_reference_list_elem = aas_elem.find(xml_ns + "submodels", aas_elem.nsmap)
        if sm_reference_list_elem is not None:
            sm_reference_dict = deserialization.get_submodel_references(sm_reference_list_elem, xml_ns)
            print("Submodels info")
            print(sm_reference_dict)

        # Submodel related information
        sm_list_elem = aas_xml_env_definition.find(xml_ns + "submodels", aas_xml_env_definition.nsmap)
        sm_obj_list = set()
        for sm_elem in sm_list_elem:
            sm_obj = deserialization.deserialize_submodel(sm_elem, xml_ns)
            sm_obj_list.add(sm_obj)

        aas_obj = deserialization.deserialize_aas(aas_elem, xml_ns, asset_information_obj, sm_obj_list)

        print("CASCADE PRINTING:")
        aas_obj.cascade_print()


if __name__ == "__main__":
    print("Starting AAS definition reader...")
    main()
