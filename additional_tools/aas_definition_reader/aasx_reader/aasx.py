"""
Functionality for reading and writing AASX files
"""
import io
import os
from typing import IO, Union

import pyecma376_2
from basyx.aas.adapter.json import read_aas_json_file
from basyx.aas.adapter.xml import read_aas_xml_file


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
