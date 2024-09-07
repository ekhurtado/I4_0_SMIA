from tkinter import Tk
from tkinter.filedialog import askopenfilename

from lxml import etree

from aas_metamodel_deserializer import deserialization

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
