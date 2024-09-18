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
        # aas_part_object = aasx_reader._parse_aas_part(aas_part)
        aas_part_object = aasx_reader.save_aas_xml_definition_objects(aas_part)
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




if __name__ == "__main__":
    print("Starting AAS definition reader...")
    main()
