from tkinter import Tk
from tkinter.filedialog import askopenfilename

from lxml import etree

from aas_class_structure.aas import AssetInformation
# TODO arreglar error con circular import (mirar en internet o chat-gpt)

xsd_path = 'AAS_metamodel.xsd'


def main():
    # Primero, se leera un modelo XML de AAS
    # TODO Mas adelante habilitar leer tambien AASX
    # Para leer los archivos, usaremos tanto una interfaz visual como por consola
    aas_xml_definition_str = get_aas_xml_file()
    # Una vez logrado el XML en string, se validará con el metamodelo oficial de AAS
    validate_xml_definition(aas_xml_definition_str)
    print("Successful validation of the AAS XML model")

    # Ya podemos pasar a leer el modelo XML de la definicion de AAS
    read_xml_definition(aas_xml_definition_str)


def get_aas_xml_file():
    print("To enter the AAS model in XML format, select one of the following options:")
    print("\t\t -> 1: Enter the application model as a file.")
    print("\t\t -> 2: Enter the application model as text.")
    print("\t\t -> 3: Exit the program.")
    while True:
        selectedOption = int(input("Enter the option number: "))
        if 1 <= selectedOption <= 3:
            break
        else:
            print("The option selected is incorrect, please enter it again.")
    match selectedOption:
        case 1:
            window = Tk()
            window.lift()
            window.attributes("-topmost", True)  # Leihoa pantailan erakusteko
            window.after_idle(window.attributes, '-topmost', False)
            Tk().withdraw()
            archivo_xml = askopenfilename(filetypes=[("Archivos XML", "*.xml")], title="Choose the XML file")
            with open(archivo_xml, "r") as archivo:
                # Lee el contenido del archivo y almacénalo en una cadena
                content = archivo.read()
            window.destroy()
            return content
        case 2:
            print("Copy the component model and paste it here (end by pressing Enter on a blank line):")
            stringAppModel = ''
            while True:

                line = input('''''')
                if line == '':
                    break
                else:
                    stringAppModel += line + '\n'
            # print(stringAppModel)
            return stringAppModel
        case 3:
            exit()
        case _:
            print("Option not available.")


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
        # TODO
        print("XML definition is valid. Starting reading...")
        print(aas_xml_env_definition.tag)
        aas_list = aas_xml_env_definition[0]
        aas_definition = aas_list[0]  # Cogemos solo 1 AAS (ya que el manager no tendra mas definidos)
        print(aas_list.tag)
        print(aas_definition.tag)
        print(aas_definition.attrib)
        aas_id_elem = aas_definition.find(xml_ns + "id", aas_definition.nsmap)
        print(aas_id_elem.tag)
        print(aas_id_elem.text)
        asset_information_elem = aas_definition.find(xml_ns + "assetInformation", aas_definition.nsmap)
        asset_kind = asset_information_elem.find(xml_ns + "assetKind", aas_definition.nsmap).text
        global_asset_id = asset_information_elem.find(xml_ns + "globalAssetId", aas_definition.nsmap).text
        asset_information_obj = aas.AssetInformation(asset_kind=asset_kind, global_asset_id=global_asset_id)
        print(asset_information_obj)


if __name__ == "__main__":
    print("Starting AAS definition reader...")
    main()
