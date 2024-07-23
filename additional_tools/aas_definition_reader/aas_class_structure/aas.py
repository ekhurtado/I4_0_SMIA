"""
This module contains the class for the implementation of the Asset Administration Shell.
"""
from enum import Enum

from aas_definition_reader.aas_class_structure import common
from aas_definition_reader.aas_class_structure.submodel import Submodel


class AssetInformation:
    """
    TODO Rellenarlo
    """

    class AssetKind(Enum):
        TYPE = 0
        INSTANCE = 1

    class SpecificAssetId:
        def __init__(self):
            self.name = None
            self.value = None
            self.external_subject_id: common.KeyTypes.Reference

    class Resource:
        def __init__(self):
            self.path = None
            self.content_type = None

    def __init__(self):
        self.asset_kind: AssetInformation.AssetKind
        self.specific_asset_id: AssetInformation.SpecificAssetId
        self.global_asset_id: common.KeyTypes.Reference
        self.default_thumbnail: AssetInformation.Resource


class AssetAdministrationShell(common.Identifiable, common.HasDataSpecification):
    """
    TODO Rellenarlo
    """

    def __init__(self, asset_information: AssetInformation, id: common.KeyTypes.Identifier, id_short, display_name,
                 category, description, parent, administration, submodel: set[Submodel], derived_from,
                 embedded_data_specifications, extension):
        super().__init__()
        self.id: common.KeyTypes.Identifier = id
        self.asset_information: AssetInformation = asset_information
        self.id_short = id_short
        self.display_name = display_name
        self.category = category
        self.description = description
        self.parent = parent
        self.administration = administration
        self.derived_from = derived_from
        self.submodel = set() if submodel is None else submodel
        self.embedded_data_specifications = set(embedded_data_specifications)
        self.extension = extension

    def cascade_print(self):
        """
        TODO Rellenarlo
        :return:
        """
        # TODO: este metodo servirá para printear toda la informacion que tenga el AAS. Para ello, se realizara en
        #  cascada, es decir, como el AAS es el elemento principal, y los demas cuelgan de el, todos tendran este metodo
        #  print. El metodo basicamente printeara toda la información de esa clase. Si es un string, lo mostrara
        #  directamente, si es un objeto, llamara a su metodo print para que muestre la informacion de dentro.
        # Al llamar al metodo por debajo, se le añadira un numero, el cual sera el nivel de profundidad (el AAS sera el 0,
        # y cuando llame al print de assetInformation le enviara un 1, este al printear specificAssetId 3, y asi
        # consecutivamente). Con ese nivel de profundidad podremos printear la informacion de forma clara y ordenada,
        # p.e: con nivel 0 nada, con nivel 1 añadir "\_" al principio, con nivel 2 , "\__", y asi consecutivamente...

