"""
This module contains the class for the implementation of the Asset Administration Shell.
"""
from enum import Enum, unique

from . import common
from .submodel import Submodel


class AssetInformation:
    """
    This class collects the meta-information of the asset being represented. The asset can be either a type or an
    instance. The asset has a globally unique identifier and, if needed, an additional domain-specific identifier.
    """

    @unique
    class AssetKind(Enum):
        TYPE = 0
        INSTANCE = 1
        NOT_APPLICABLE = 2

    @unique
    class AssetType(Enum):
        """
        This class is an own proposal to distinguish between logical and physical assets.
        """
        PHYSICAL = 0
        LOGICAL = 1
        NOT_APPLICABLE = 2

    class Resource:
        """This class represents an address to a file, either in absolute or relative path."""

        def __init__(self):
            self.path = None
            self.content_type = None

    def __init__(self,
                 asset_kind: AssetKind = None,
                 specific_asset_id: set[common.SpecificAssetId] = (),
                 global_asset_id: common.KeyTypes.Reference = None,
                 default_thumbnail: Resource = None,
                 asset_type: AssetType = None,
                 ):
        self.asset_kind: AssetInformation.AssetKind = asset_kind
        self.specific_asset_id: set[common.SpecificAssetId] = specific_asset_id
        self.global_asset_id: common.KeyTypes.Reference = global_asset_id
        self.default_thumbnail: AssetInformation.Resource = default_thumbnail
        self.asset_type: AssetInformation.AssetType = asset_type

    def cascade_print(self, depth_level):
        """
        # TODO
        :param depth_level:
        :return:
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Asset information: ")
        print(depth_string + "    asset_kind: " + str(self.asset_kind.name))
        print(depth_string + "    specific_asset_id: " + str(self.specific_asset_id))
        print(depth_string + "    global_asset_id: " + str(self.global_asset_id))
        print(depth_string + "    default_thumbnail: " + str(self.default_thumbnail))
        print(depth_string + "    asset_type: " + str(self.asset_type.name))


class AssetAdministrationShell(common.Identifiable, common.HasDataSpecification):
    """
    An AAS is uniquely identifiable because it inherits from :param: Identifiable. As it inherits from both :param:
    Identifiable (and this in turn from :param: Referable) and :param: HasDataSpecification, all these inherited
    variables are added in the constructor of the AAS.
    """

    def __init__(self,
                 asset_information: AssetInformation,
                 id_: common.KeyTypes.Identifier,
                 id_short,
                 display_name,
                 category,
                 description,
                 administration: common.Identifiable.AdministrativeInformation,
                 submodel: set[Submodel],
                 derived_from,
                 embedded_data_specifications,
                 extension):
        super().__init__()
        self.id: common.KeyTypes.Identifier = id_
        self.asset_information: AssetInformation = asset_information
        self.id_short = id_short
        self.display_name = display_name
        self.category = category
        self.description = description
        self.administration: common.Identifiable.AdministrativeInformation = administration
        self.derived_from = derived_from
        self.submodel = set() if submodel is None else submodel
        self.embedded_data_specifications = embedded_data_specifications
        self.extension = extension

    def cascade_print(self):
        """
        TODO Rellenarlo
        """
        # TODO: este metodo servirá para printear toda la informacion que tenga el AAS. Para ello, se realizara en
        #  cascada, es decir, como el AAS es el elemento principal, y los demas cuelgan de el, todos tendran este metodo
        #  print. El metodo basicamente printeara toda la información de esa clase. Si es un string, lo mostrara
        #  directamente, si es un objeto, llamara a su metodo print para que muestre la informacion de dentro.
        # Al llamar al metodo por debajo, se le añadira un numero, el cual sera el nivel de profundidad (el AAS sera el 0,
        # y cuando llame al print de assetInformation le enviara un 1, este al printear specificAssetId 3, y asi
        # consecutivamente). Con ese nivel de profundidad podremos printear la informacion de forma clara y ordenada,
        # p.e: con nivel 0 nada, con nivel 1 añadir "\_" al principio, con nivel 2 , "\__", y asi consecutivamente...
        # TODO
        print("\_ AAS information: ")
        print("    id: " + str(self.id))
        self.asset_information.cascade_print(depth_level=1)
        print("    id_short: " + str(self.id_short))
        print("    display_name: " + str(self.display_name))
        print("    category: " + str(self.category))
        print("    description: " + str(self.description))
        if self.administration is not None:
            self.administration.cascade_print(depth_level=1)
        print("    derived_from: " + str(self.derived_from))
        print("    \_ Submodels:")
        for submodel in self.submodel:
            submodel.cascade_print(depth_level=2)
        print("        embedded_data_specifications: " + str(self.embedded_data_specifications))
        print("        extension: " + str(self.extension))
